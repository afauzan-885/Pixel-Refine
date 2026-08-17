; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bm_grid_track_kernel_c702_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 12
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 8
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 56
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 60
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

define void @_bm_grid_track_kernel_c702_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 108
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 104
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 72
  %26 = getelementptr i8, ptr %19, i64 60
  %27 = getelementptr i8, ptr %19, i64 64
  %28 = getelementptr i8, ptr %19, i64 96
  %29 = getelementptr i8, ptr %19, i64 84
  %30 = getelementptr i8, ptr %19, i64 88
  %31 = mul i32 %23, %23
  %32 = sitofp i32 %31 to float
  %33 = fmul reassoc ninf nsz float %32, 0x3FA47AE140000000
  %34 = fmul reassoc ninf nsz float %32, 0x3FC99999A0000000
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.0244445 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %133, %after_if3 ]
  %35 = load ptr, ptr %3, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 4
  %39 = load i32, ptr %38, align 4
  %40 = sdiv i32 %.0244445, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.0244445
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %41, %.0244445
  %45 = and i1 %43, %44
  %.neg250 = sext i1 %45 to i32
  %46 = add i32 %40, %.neg250
  %47 = mul i32 %46, %39
  %48 = sub i32 %.0244445, %47
  %49 = mul i32 %48, %23
  %50 = add i32 %49, %21
  %51 = sitofp i32 %50 to float
  %52 = mul i32 %46, %23
  %53 = add i32 %52, %21
  %54 = load ptr, ptr %25, align 8
  %55 = load i32, ptr %26, align 4
  %56 = load i32, ptr %27, align 4
  %57 = mul i32 %46, %55
  %58 = add i32 %48, %57
  %59 = mul i32 %58, %56
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %54, i64 %60
  store float 0.000000e+00, ptr %61, align 4
  %62 = load ptr, ptr %25, align 8
  %63 = load i32, ptr %26, align 4
  %64 = load i32, ptr %27, align 4
  %65 = mul i32 %63, %46
  %66 = add i32 %65, %48
  %67 = mul i32 %66, %64
  %68 = add i32 %67, 1
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, ptr %62, i64 %69
  store float 0.000000e+00, ptr %70, align 4
  %71 = load ptr, ptr %25, align 8
  %72 = load i32, ptr %26, align 4
  %73 = load i32, ptr %27, align 4
  %74 = mul i32 %72, %46
  %75 = add i32 %74, %48
  %76 = mul i32 %75, %73
  %77 = add i32 %76, 2
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, ptr %71, i64 %78
  store float 0.000000e+00, ptr %79, align 4
  %80 = load ptr, ptr %28, align 8
  %81 = load i32, ptr %29, align 4
  %82 = load i32, ptr %30, align 4
  %83 = mul i32 %81, %46
  %84 = add i32 %83, %48
  %85 = mul i32 %84, %82
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %80, i64 %86
  store float 0.000000e+00, ptr %87, align 4
  %88 = load ptr, ptr %28, align 8
  %89 = load i32, ptr %29, align 4
  %90 = load i32, ptr %30, align 4
  %91 = mul i32 %89, %46
  %92 = add i32 %91, %48
  %93 = mul i32 %92, %90
  %94 = add i32 %93, 1
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %88, i64 %95
  store float 0.000000e+00, ptr %96, align 4
  %97 = load ptr, ptr %28, align 8
  %98 = load i32, ptr %29, align 4
  %99 = load i32, ptr %30, align 4
  %100 = mul i32 %98, %46
  %101 = add i32 %100, %48
  %102 = mul i32 %101, %99
  %103 = add i32 %102, 2
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %97, i64 %104
  store float 2.000000e+00, ptr %105, align 4
  %106 = load ptr, ptr %28, align 8
  %107 = load i32, ptr %29, align 4
  %108 = load i32, ptr %30, align 4
  %109 = mul i32 %107, %46
  %110 = add i32 %109, %48
  %111 = mul i32 %110, %108
  %112 = add i32 %111, 3
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %106, i64 %113
  store float 0.000000e+00, ptr %114, align 4
  %115 = load ptr, ptr %3, align 8
  %116 = getelementptr inbounds nuw i8, ptr %115, i64 32872
  %117 = load ptr, ptr %116, align 8
  %118 = getelementptr inbounds nuw i8, ptr %117, i64 8
  %119 = load i32, ptr %118, align 4
  %120 = sub i32 %119, %21
  %121 = sitofp i32 %120 to float
  %122 = fcmp reassoc ninf nsz olt float %51, %121
  br i1 %122, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %123 = sitofp i32 %53 to float
  %124 = getelementptr inbounds nuw i8, ptr %117, i64 12
  %125 = load i32, ptr %124, align 4
  %126 = sub i32 %125, %21
  %127 = sitofp i32 %126 to float
  %128 = fcmp reassoc ninf nsz olt float %123, %127
  br i1 %128, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %129 = load ptr, ptr %0, align 8
  %130 = getelementptr i8, ptr %129, i64 116
  %131 = load i32, ptr %130, align 4
  %132 = icmp eq i32 %131, 1
  br i1 %132, label %true_block4, label %after_if6

after_if3:                                        ; preds = %after_if207, %true_block, %for_loop_body
  %133 = add nsw i32 %.0244445, 1
  %exitcond.not = icmp eq i32 %133, %18
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %134 = getelementptr i8, ptr %129, i64 36
  %135 = load i32, ptr %134, align 4
  %136 = add i32 %135, -1
  %137 = tail call i32 @llvm.smin.i32(i32 %48, i32 %136)
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  %139 = getelementptr i8, ptr %129, i64 32
  %140 = load i32, ptr %139, align 4
  %141 = add i32 %140, -1
  %142 = tail call i32 @llvm.smin.i32(i32 %46, i32 %141)
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = getelementptr i8, ptr %129, i64 48
  %145 = load ptr, ptr %144, align 8
  %146 = getelementptr i8, ptr %129, i64 40
  %147 = load i32, ptr %146, align 4
  %148 = mul i32 %143, %135
  %149 = add i32 %148, %138
  %150 = mul i32 %149, %147
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %145, i64 %151
  %153 = load float, ptr %152, align 4
  %factor = fmul reassoc ninf nsz float %153, 2.000000e+00
  %154 = tail call reassoc ninf nsz float @llvm.round.f32(float %factor)
  %155 = fptosi float %154 to i32
  %156 = add i32 %150, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %145, i64 %157
  %159 = load float, ptr %158, align 4
  %factor278 = fmul reassoc ninf nsz float %159, 2.000000e+00
  %160 = tail call reassoc ninf nsz float @llvm.round.f32(float %factor278)
  %161 = fptosi float %160 to i32
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.0242 = phi i32 [ %155, %true_block4 ], [ 0, %true_block1 ]
  %.0241 = phi i32 [ %161, %true_block4 ], [ 0, %true_block1 ]
  %162 = getelementptr i8, ptr %129, i64 112
  %163 = load i32, ptr %162, align 4
  %neg = sub i32 0, %163
  %164 = add i32 %125, -1
  %165 = add i32 %119, -1
  %invariant.op283 = add i32 %53, %.0241
  %.not285 = icmp slt i32 %163, %neg
  br i1 %.not285, label %false_block193, label %while_loop_body10.preheader.lr.ph

while_loop_body10.preheader.lr.ph:                ; preds = %after_if6
  %invariant.op = add i32 %50, %.0242
  %166 = getelementptr i8, ptr %129, i64 24
  %167 = getelementptr i8, ptr %129, i64 20
  %168 = getelementptr i8, ptr %129, i64 8
  %169 = getelementptr i8, ptr %129, i64 4
  %.pre = load ptr, ptr %166, align 8
  %.pre459 = load i32, ptr %167, align 4
  %.pre460 = load ptr, ptr %168, align 8
  %.pre461 = load i32, ptr %169, align 4
  %170 = sext i32 %163 to i64
  %171 = add nsw i64 %170, 1
  %172 = sub i32 2, %163
  %173 = sext i32 %172 to i64
  %smax1120 = tail call i64 @llvm.smax.i64(i64 %171, i64 %173)
  %174 = add i64 %smax1120, 1
  %175 = sub i64 %174, %173
  %176 = lshr i64 %175, 1
  %177 = trunc i64 %176 to i32
  %178 = add i32 %177, 1
  %min.iters.check1127 = icmp ult i32 %178, 8
  %mul.result1122 = shl i32 %177, 1
  %mul.overflow1123 = icmp slt i32 %177, 0
  %179 = add i32 %172, %mul.result1122
  %180 = icmp slt i32 %179, %172
  %181 = or i1 %180, %mul.overflow1123
  %182 = icmp ugt i64 %175, 8589934591
  %183 = or i1 %181, %182
  %n.vec1130 = and i32 %178, -8
  %184 = shl i32 %n.vec1130, 1
  %185 = sub i32 %184, %163
  %.splatinsert1133 = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat1134 = shufflevector <8 x i32> %.splatinsert1133, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction1135 = add <8 x i32> %.splat1134, <i32 0, i32 2, i32 4, i32 6, i32 8, i32 10, i32 12, i32 14>
  %broadcast.splatinsert1139 = insertelement <8 x i32> poison, i32 %50, i64 0
  %broadcast.splat1140 = shufflevector <8 x i32> %broadcast.splatinsert1139, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1141 = insertelement <8 x i32> poison, i32 %invariant.op, i64 0
  %broadcast.splat1142 = shufflevector <8 x i32> %broadcast.splatinsert1141, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1143 = insertelement <8 x i32> poison, i32 %165, i64 0
  %broadcast.splat1144 = shufflevector <8 x i32> %broadcast.splatinsert1143, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n1152 = icmp eq i32 %178, %n.vec1130
  %186 = add i32 %21, %.0242
  %187 = add i32 %186, %49
  br label %while_loop_body10.preheader

while_loop_body10.preheader:                      ; preds = %false_block13, %while_loop_body10.preheader.lr.ph
  %.0226287 = phi i32 [ %neg, %while_loop_body10.preheader.lr.ph ], [ %215, %false_block13 ]
  %.0227286 = phi float [ 0.000000e+00, %while_loop_body10.preheader.lr.ph ], [ %.lcssa, %false_block13 ]
  %188 = add i32 %.0226287, %53
  %.reass284 = add i32 %.0226287, %invariant.op283
  %189 = tail call i32 @llvm.smin.i32(i32 %.reass284, i32 %164)
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %191 = tail call i32 @llvm.smin.i32(i32 %188, i32 %164)
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = mul i32 %.pre459, %190
  %194 = mul i32 %.pre461, %192
  %brmerge = select i1 %min.iters.check1127, i1 true, i1 %183
  br i1 %brmerge, label %after_if14.preheader, label %vector.ph1128

vector.ph1128:                                    ; preds = %while_loop_body10.preheader
  %195 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0227286, i64 0
  %broadcast.splatinsert1145 = insertelement <8 x i32> poison, i32 %193, i64 0
  %broadcast.splat1146 = shufflevector <8 x i32> %broadcast.splatinsert1145, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1148 = insertelement <8 x i32> poison, i32 %194, i64 0
  %broadcast.splat1149 = shufflevector <8 x i32> %broadcast.splatinsert1148, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body1131

vector.body1131:                                  ; preds = %vector.body1131, %vector.ph1128
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body1131 ], [ %n.vec1130, %vector.ph1128 ]
  %vec.ind1136 = phi <8 x i32> [ %induction1135, %vector.ph1128 ], [ %vec.ind.next1137, %vector.body1131 ]
  %vec.phi1138 = phi <8 x float> [ %195, %vector.ph1128 ], [ %210, %vector.body1131 ]
  %196 = add <8 x i32> %vec.ind1136, %broadcast.splat1140
  %197 = add <8 x i32> %vec.ind1136, %broadcast.splat1142
  %198 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %197, <8 x i32> %broadcast.splat1144)
  %199 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %198, <8 x i32> zeroinitializer)
  %200 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %196, <8 x i32> %broadcast.splat1144)
  %201 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %200, <8 x i32> zeroinitializer)
  %202 = add <8 x i32> %broadcast.splat1146, %199
  %203 = sext <8 x i32> %202 to <8 x i64>
  %204 = getelementptr float, ptr %.pre, <8 x i64> %203
  %wide.masked.gather1147 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %204, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %205 = add <8 x i32> %broadcast.splat1149, %201
  %206 = sext <8 x i32> %205 to <8 x i64>
  %207 = getelementptr float, ptr %.pre460, <8 x i64> %206
  %wide.masked.gather1150 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %207, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %208 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather1147, %wide.masked.gather1150
  %209 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %208)
  %210 = fadd reassoc ninf nsz <8 x float> %209, %vec.phi1138
  %vec.ind.next1137 = add <8 x i32> %vec.ind1136, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %211 = icmp eq i32 %lsr.iv.next, 0
  br i1 %211, label %middle.block1125, label %vector.body1131, !llvm.loop !11

middle.block1125:                                 ; preds = %vector.body1131
  %212 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %210)
  br i1 %cmp.n1152, label %false_block13, label %after_if14.preheader

after_if14.preheader:                             ; preds = %middle.block1125, %while_loop_body10.preheader
  %.0225282.ph = phi i32 [ %neg, %while_loop_body10.preheader ], [ %185, %middle.block1125 ]
  %.1228281.ph = phi float [ %.0227286, %while_loop_body10.preheader ], [ %212, %middle.block1125 ]
  br label %after_if14

false_block8:                                     ; preds = %false_block13
  %213 = fcmp reassoc ninf nsz olt float %.lcssa, 0x46293E5940000000
  %.0229 = select i1 %213, float %.lcssa, float 0x46293E5940000000
  %214 = add i32 %.0241, -2
  %invariant.op295 = add i32 %53, %214
  br label %while_loop_body25.preheader

false_block13.loopexit:                           ; preds = %after_if14
  br label %false_block13

false_block13:                                    ; preds = %false_block13.loopexit, %middle.block1125
  %.lcssa = phi float [ %212, %middle.block1125 ], [ %232, %false_block13.loopexit ]
  %215 = add i32 %.0226287, 2
  %.not = icmp sgt i32 %215, %163
  br i1 %.not, label %false_block8, label %while_loop_body10.preheader

after_if14:                                       ; preds = %after_if14, %after_if14.preheader
  %.0225282 = phi i32 [ %233, %after_if14 ], [ %.0225282.ph, %after_if14.preheader ]
  %.1228281 = phi float [ %232, %after_if14 ], [ %.1228281.ph, %after_if14.preheader ]
  %216 = add i32 %50, %.0225282
  %217 = add i32 %187, %.0225282
  %218 = tail call i32 @llvm.smin.i32(i32 %217, i32 %165)
  %219 = tail call i32 @llvm.smax.i32(i32 %218, i32 0)
  %220 = tail call i32 @llvm.smin.i32(i32 %216, i32 %165)
  %221 = tail call i32 @llvm.smax.i32(i32 %220, i32 0)
  %222 = add i32 %193, %219
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %.pre, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = add i32 %194, %221
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %.pre460, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = fsub reassoc ninf nsz float %225, %229
  %231 = tail call noundef float @llvm.fabs.f32(float %230)
  %232 = fadd reassoc ninf nsz float %231, %.1228281
  %233 = add i32 %.0225282, 2
  %.not277 = icmp sgt i32 %233, %163
  br i1 %.not277, label %false_block13.loopexit, label %after_if14, !llvm.loop !14

while_loop_body25.preheader:                      ; preds = %false_block28, %false_block8
  %.0222299 = phi i32 [ %neg, %false_block8 ], [ %261, %false_block28 ]
  %.0223298 = phi float [ 0.000000e+00, %false_block8 ], [ %.lcssa664, %false_block28 ]
  %234 = add i32 %.0222299, %53
  %.reass296 = add i32 %.0222299, %invariant.op295
  %235 = tail call i32 @llvm.smin.i32(i32 %.reass296, i32 %164)
  %236 = tail call i32 @llvm.smax.i32(i32 %235, i32 0)
  %237 = tail call i32 @llvm.smin.i32(i32 %234, i32 %164)
  %238 = tail call i32 @llvm.smax.i32(i32 %237, i32 0)
  %239 = mul i32 %.pre459, %236
  %240 = mul i32 %.pre461, %238
  br i1 %brmerge, label %after_if29.preheader, label %vector.ph1092

vector.ph1092:                                    ; preds = %while_loop_body25.preheader
  %241 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0223298, i64 0
  %broadcast.splatinsert1109 = insertelement <8 x i32> poison, i32 %239, i64 0
  %broadcast.splat1110 = shufflevector <8 x i32> %broadcast.splatinsert1109, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1112 = insertelement <8 x i32> poison, i32 %240, i64 0
  %broadcast.splat1113 = shufflevector <8 x i32> %broadcast.splatinsert1112, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body1095

vector.body1095:                                  ; preds = %vector.body1095, %vector.ph1092
  %lsr.iv1224 = phi i32 [ %lsr.iv.next1225, %vector.body1095 ], [ %n.vec1130, %vector.ph1092 ]
  %vec.ind1100 = phi <8 x i32> [ %induction1135, %vector.ph1092 ], [ %vec.ind.next1101, %vector.body1095 ]
  %vec.phi1102 = phi <8 x float> [ %241, %vector.ph1092 ], [ %256, %vector.body1095 ]
  %242 = add <8 x i32> %vec.ind1100, %broadcast.splat1140
  %243 = add <8 x i32> %vec.ind1100, %broadcast.splat1142
  %244 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %243, <8 x i32> %broadcast.splat1144)
  %245 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %244, <8 x i32> zeroinitializer)
  %246 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %242, <8 x i32> %broadcast.splat1144)
  %247 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %246, <8 x i32> zeroinitializer)
  %248 = add <8 x i32> %broadcast.splat1110, %245
  %249 = sext <8 x i32> %248 to <8 x i64>
  %250 = getelementptr float, ptr %.pre, <8 x i64> %249
  %wide.masked.gather1111 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %250, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %251 = add <8 x i32> %broadcast.splat1113, %247
  %252 = sext <8 x i32> %251 to <8 x i64>
  %253 = getelementptr float, ptr %.pre460, <8 x i64> %252
  %wide.masked.gather1114 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %253, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %254 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather1111, %wide.masked.gather1114
  %255 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %254)
  %256 = fadd reassoc ninf nsz <8 x float> %255, %vec.phi1102
  %vec.ind.next1101 = add <8 x i32> %vec.ind1100, splat (i32 16)
  %lsr.iv.next1225 = add i32 %lsr.iv1224, -8
  %257 = icmp eq i32 %lsr.iv.next1225, 0
  br i1 %257, label %middle.block1089, label %vector.body1095, !llvm.loop !15

middle.block1089:                                 ; preds = %vector.body1095
  %258 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %256)
  br i1 %cmp.n1152, label %false_block28, label %after_if29.preheader

after_if29.preheader:                             ; preds = %middle.block1089, %while_loop_body25.preheader
  %.0221293.ph = phi i32 [ %neg, %while_loop_body25.preheader ], [ %185, %middle.block1089 ]
  %.1224292.ph = phi float [ %.0223298, %while_loop_body25.preheader ], [ %258, %middle.block1089 ]
  br label %after_if29

false_block22:                                    ; preds = %false_block28
  %259 = fcmp reassoc ninf nsz olt float %.lcssa664, %.0229
  %.0237 = select i1 %259, i32 %214, i32 %.0241
  %.1230 = select i1 %259, float %.lcssa664, float %.0229
  %260 = add i32 %.0241, 2
  %invariant.op307 = add i32 %53, %260
  br label %while_loop_body40.preheader

false_block28.loopexit:                           ; preds = %after_if29
  br label %false_block28

false_block28:                                    ; preds = %false_block28.loopexit, %middle.block1089
  %.lcssa664 = phi float [ %258, %middle.block1089 ], [ %278, %false_block28.loopexit ]
  %261 = add i32 %.0222299, 2
  %.not251 = icmp sgt i32 %261, %163
  br i1 %.not251, label %false_block22, label %while_loop_body25.preheader

after_if29:                                       ; preds = %after_if29, %after_if29.preheader
  %.0221293 = phi i32 [ %279, %after_if29 ], [ %.0221293.ph, %after_if29.preheader ]
  %.1224292 = phi float [ %278, %after_if29 ], [ %.1224292.ph, %after_if29.preheader ]
  %262 = add i32 %50, %.0221293
  %263 = add i32 %187, %.0221293
  %264 = tail call i32 @llvm.smin.i32(i32 %263, i32 %165)
  %265 = tail call i32 @llvm.smax.i32(i32 %264, i32 0)
  %266 = tail call i32 @llvm.smin.i32(i32 %262, i32 %165)
  %267 = tail call i32 @llvm.smax.i32(i32 %266, i32 0)
  %268 = add i32 %239, %265
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, ptr %.pre, i64 %269
  %271 = load float, ptr %270, align 4
  %272 = add i32 %240, %267
  %273 = sext i32 %272 to i64
  %274 = getelementptr float, ptr %.pre460, i64 %273
  %275 = load float, ptr %274, align 4
  %276 = fsub reassoc ninf nsz float %271, %275
  %277 = tail call noundef float @llvm.fabs.f32(float %276)
  %278 = fadd reassoc ninf nsz float %277, %.1224292
  %279 = add i32 %.0221293, 2
  %.not276 = icmp sgt i32 %279, %163
  br i1 %.not276, label %false_block28.loopexit, label %after_if29, !llvm.loop !16

while_loop_body40.preheader:                      ; preds = %false_block43, %false_block22
  %.0218311 = phi i32 [ %neg, %false_block22 ], [ %307, %false_block43 ]
  %.0219310 = phi float [ 0.000000e+00, %false_block22 ], [ %.lcssa665, %false_block43 ]
  %280 = add i32 %.0218311, %53
  %.reass308 = add i32 %.0218311, %invariant.op307
  %281 = tail call i32 @llvm.smin.i32(i32 %.reass308, i32 %164)
  %282 = tail call i32 @llvm.smax.i32(i32 %281, i32 0)
  %283 = tail call i32 @llvm.smin.i32(i32 %280, i32 %164)
  %284 = tail call i32 @llvm.smax.i32(i32 %283, i32 0)
  %285 = mul i32 %.pre459, %282
  %286 = mul i32 %.pre461, %284
  br i1 %brmerge, label %after_if44.preheader, label %vector.ph1056

vector.ph1056:                                    ; preds = %while_loop_body40.preheader
  %287 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0219310, i64 0
  %broadcast.splatinsert1073 = insertelement <8 x i32> poison, i32 %285, i64 0
  %broadcast.splat1074 = shufflevector <8 x i32> %broadcast.splatinsert1073, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1076 = insertelement <8 x i32> poison, i32 %286, i64 0
  %broadcast.splat1077 = shufflevector <8 x i32> %broadcast.splatinsert1076, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body1059

vector.body1059:                                  ; preds = %vector.body1059, %vector.ph1056
  %lsr.iv1226 = phi i32 [ %lsr.iv.next1227, %vector.body1059 ], [ %n.vec1130, %vector.ph1056 ]
  %vec.ind1064 = phi <8 x i32> [ %induction1135, %vector.ph1056 ], [ %vec.ind.next1065, %vector.body1059 ]
  %vec.phi1066 = phi <8 x float> [ %287, %vector.ph1056 ], [ %302, %vector.body1059 ]
  %288 = add <8 x i32> %vec.ind1064, %broadcast.splat1140
  %289 = add <8 x i32> %vec.ind1064, %broadcast.splat1142
  %290 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %289, <8 x i32> %broadcast.splat1144)
  %291 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %290, <8 x i32> zeroinitializer)
  %292 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %288, <8 x i32> %broadcast.splat1144)
  %293 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %292, <8 x i32> zeroinitializer)
  %294 = add <8 x i32> %broadcast.splat1074, %291
  %295 = sext <8 x i32> %294 to <8 x i64>
  %296 = getelementptr float, ptr %.pre, <8 x i64> %295
  %wide.masked.gather1075 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %296, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %297 = add <8 x i32> %broadcast.splat1077, %293
  %298 = sext <8 x i32> %297 to <8 x i64>
  %299 = getelementptr float, ptr %.pre460, <8 x i64> %298
  %wide.masked.gather1078 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %299, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %300 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather1075, %wide.masked.gather1078
  %301 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %300)
  %302 = fadd reassoc ninf nsz <8 x float> %301, %vec.phi1066
  %vec.ind.next1065 = add <8 x i32> %vec.ind1064, splat (i32 16)
  %lsr.iv.next1227 = add i32 %lsr.iv1226, -8
  %303 = icmp eq i32 %lsr.iv.next1227, 0
  br i1 %303, label %middle.block1053, label %vector.body1059, !llvm.loop !17

middle.block1053:                                 ; preds = %vector.body1059
  %304 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %302)
  br i1 %cmp.n1152, label %false_block43, label %after_if44.preheader

after_if44.preheader:                             ; preds = %middle.block1053, %while_loop_body40.preheader
  %.0217305.ph = phi i32 [ %neg, %while_loop_body40.preheader ], [ %185, %middle.block1053 ]
  %.1220304.ph = phi float [ %.0219310, %while_loop_body40.preheader ], [ %304, %middle.block1053 ]
  br label %after_if44

false_block37:                                    ; preds = %false_block43
  %305 = fcmp reassoc ninf nsz olt float %.lcssa665, %.1230
  %.1238 = select i1 %305, i32 %260, i32 %.0237
  %.2231 = select i1 %305, float %.lcssa665, float %.1230
  %306 = add i32 %.0242, -2
  %invariant.op313 = add i32 %50, %306
  %broadcast.splatinsert1033 = insertelement <8 x i32> poison, i32 %invariant.op313, i64 0
  %broadcast.splat1034 = shufflevector <8 x i32> %broadcast.splatinsert1033, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body55.preheader

false_block43.loopexit:                           ; preds = %after_if44
  br label %false_block43

false_block43:                                    ; preds = %false_block43.loopexit, %middle.block1053
  %.lcssa665 = phi float [ %304, %middle.block1053 ], [ %324, %false_block43.loopexit ]
  %307 = add i32 %.0218311, 2
  %.not252 = icmp sgt i32 %307, %163
  br i1 %.not252, label %false_block37, label %while_loop_body40.preheader

after_if44:                                       ; preds = %after_if44, %after_if44.preheader
  %.0217305 = phi i32 [ %325, %after_if44 ], [ %.0217305.ph, %after_if44.preheader ]
  %.1220304 = phi float [ %324, %after_if44 ], [ %.1220304.ph, %after_if44.preheader ]
  %308 = add i32 %50, %.0217305
  %309 = add i32 %187, %.0217305
  %310 = tail call i32 @llvm.smin.i32(i32 %309, i32 %165)
  %311 = tail call i32 @llvm.smax.i32(i32 %310, i32 0)
  %312 = tail call i32 @llvm.smin.i32(i32 %308, i32 %165)
  %313 = tail call i32 @llvm.smax.i32(i32 %312, i32 0)
  %314 = add i32 %285, %311
  %315 = sext i32 %314 to i64
  %316 = getelementptr float, ptr %.pre, i64 %315
  %317 = load float, ptr %316, align 4
  %318 = add i32 %286, %313
  %319 = sext i32 %318 to i64
  %320 = getelementptr float, ptr %.pre460, i64 %319
  %321 = load float, ptr %320, align 4
  %322 = fsub reassoc ninf nsz float %317, %321
  %323 = tail call noundef float @llvm.fabs.f32(float %322)
  %324 = fadd reassoc ninf nsz float %323, %.1220304
  %325 = add i32 %.0217305, 2
  %.not275 = icmp sgt i32 %325, %163
  br i1 %.not275, label %false_block43.loopexit, label %after_if44, !llvm.loop !18

while_loop_body55.preheader:                      ; preds = %false_block58, %false_block37
  %.0214323 = phi i32 [ %neg, %false_block37 ], [ %353, %false_block58 ]
  %.0215322 = phi float [ 0.000000e+00, %false_block37 ], [ %.lcssa666, %false_block58 ]
  %326 = add i32 %.0214323, %53
  %.reass320 = add i32 %.0214323, %invariant.op283
  %327 = tail call i32 @llvm.smin.i32(i32 %.reass320, i32 %164)
  %328 = tail call i32 @llvm.smax.i32(i32 %327, i32 0)
  %329 = tail call i32 @llvm.smin.i32(i32 %326, i32 %164)
  %330 = tail call i32 @llvm.smax.i32(i32 %329, i32 0)
  %331 = mul i32 %.pre459, %328
  %332 = mul i32 %.pre461, %330
  br i1 %brmerge, label %after_if59.preheader, label %vector.ph1020

vector.ph1020:                                    ; preds = %while_loop_body55.preheader
  %333 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0215322, i64 0
  %broadcast.splatinsert1037 = insertelement <8 x i32> poison, i32 %331, i64 0
  %broadcast.splat1038 = shufflevector <8 x i32> %broadcast.splatinsert1037, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1040 = insertelement <8 x i32> poison, i32 %332, i64 0
  %broadcast.splat1041 = shufflevector <8 x i32> %broadcast.splatinsert1040, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body1023

vector.body1023:                                  ; preds = %vector.body1023, %vector.ph1020
  %lsr.iv1228 = phi i32 [ %lsr.iv.next1229, %vector.body1023 ], [ %n.vec1130, %vector.ph1020 ]
  %vec.ind1028 = phi <8 x i32> [ %induction1135, %vector.ph1020 ], [ %vec.ind.next1029, %vector.body1023 ]
  %vec.phi1030 = phi <8 x float> [ %333, %vector.ph1020 ], [ %348, %vector.body1023 ]
  %334 = add <8 x i32> %vec.ind1028, %broadcast.splat1140
  %335 = add <8 x i32> %vec.ind1028, %broadcast.splat1034
  %336 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %335, <8 x i32> %broadcast.splat1144)
  %337 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %336, <8 x i32> zeroinitializer)
  %338 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %334, <8 x i32> %broadcast.splat1144)
  %339 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %338, <8 x i32> zeroinitializer)
  %340 = add <8 x i32> %broadcast.splat1038, %337
  %341 = sext <8 x i32> %340 to <8 x i64>
  %342 = getelementptr float, ptr %.pre, <8 x i64> %341
  %wide.masked.gather1039 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %342, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %343 = add <8 x i32> %broadcast.splat1041, %339
  %344 = sext <8 x i32> %343 to <8 x i64>
  %345 = getelementptr float, ptr %.pre460, <8 x i64> %344
  %wide.masked.gather1042 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %345, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %346 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather1039, %wide.masked.gather1042
  %347 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %346)
  %348 = fadd reassoc ninf nsz <8 x float> %347, %vec.phi1030
  %vec.ind.next1029 = add <8 x i32> %vec.ind1028, splat (i32 16)
  %lsr.iv.next1229 = add i32 %lsr.iv1228, -8
  %349 = icmp eq i32 %lsr.iv.next1229, 0
  br i1 %349, label %middle.block1017, label %vector.body1023, !llvm.loop !19

middle.block1017:                                 ; preds = %vector.body1023
  %350 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %348)
  br i1 %cmp.n1152, label %false_block58, label %after_if59.preheader

after_if59.preheader:                             ; preds = %middle.block1017, %while_loop_body55.preheader
  %.0213317.ph = phi i32 [ %neg, %while_loop_body55.preheader ], [ %185, %middle.block1017 ]
  %.1216316.ph = phi float [ %.0215322, %while_loop_body55.preheader ], [ %350, %middle.block1017 ]
  br label %after_if59

false_block52:                                    ; preds = %false_block58
  %351 = fcmp reassoc ninf nsz olt float %.lcssa666, %.2231
  %.2235 = select i1 %351, i32 %306, i32 %.0242
  %.3232 = select i1 %351, float %.lcssa666, float %.2231
  %352 = add i32 %.0242, 2
  %invariant.op325 = add i32 %50, %352
  %broadcast.splatinsert997 = insertelement <8 x i32> poison, i32 %invariant.op325, i64 0
  %broadcast.splat998 = shufflevector <8 x i32> %broadcast.splatinsert997, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body70.preheader

false_block58.loopexit:                           ; preds = %after_if59
  br label %false_block58

false_block58:                                    ; preds = %false_block58.loopexit, %middle.block1017
  %.lcssa666 = phi float [ %350, %middle.block1017 ], [ %371, %false_block58.loopexit ]
  %353 = add i32 %.0214323, 2
  %.not253 = icmp sgt i32 %353, %163
  br i1 %.not253, label %false_block52, label %while_loop_body55.preheader

after_if59:                                       ; preds = %after_if59, %after_if59.preheader
  %.0213317 = phi i32 [ %372, %after_if59 ], [ %.0213317.ph, %after_if59.preheader ]
  %.1216316 = phi float [ %371, %after_if59 ], [ %.1216316.ph, %after_if59.preheader ]
  %354 = add i32 %50, %.0213317
  %355 = add i32 %187, %.0213317
  %356 = add i32 %355, -2
  %357 = tail call i32 @llvm.smin.i32(i32 %356, i32 %165)
  %358 = tail call i32 @llvm.smax.i32(i32 %357, i32 0)
  %359 = tail call i32 @llvm.smin.i32(i32 %354, i32 %165)
  %360 = tail call i32 @llvm.smax.i32(i32 %359, i32 0)
  %361 = add i32 %331, %358
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %.pre, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = add i32 %332, %360
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, ptr %.pre460, i64 %366
  %368 = load float, ptr %367, align 4
  %369 = fsub reassoc ninf nsz float %364, %368
  %370 = tail call noundef float @llvm.fabs.f32(float %369)
  %371 = fadd reassoc ninf nsz float %370, %.1216316
  %372 = add i32 %.0213317, 2
  %.not274 = icmp sgt i32 %372, %163
  br i1 %.not274, label %false_block58.loopexit, label %after_if59, !llvm.loop !20

while_loop_body70.preheader:                      ; preds = %false_block73, %false_block52
  %.0210335 = phi i32 [ %neg, %false_block52 ], [ %402, %false_block73 ]
  %.0211334 = phi float [ 0.000000e+00, %false_block52 ], [ %.lcssa667, %false_block73 ]
  %373 = add i32 %.0210335, %53
  %.reass332 = add i32 %.0210335, %invariant.op283
  %374 = tail call i32 @llvm.smin.i32(i32 %.reass332, i32 %164)
  %375 = tail call i32 @llvm.smax.i32(i32 %374, i32 0)
  %376 = tail call i32 @llvm.smin.i32(i32 %373, i32 %164)
  %377 = tail call i32 @llvm.smax.i32(i32 %376, i32 0)
  %378 = mul i32 %.pre459, %375
  %379 = mul i32 %.pre461, %377
  br i1 %brmerge, label %after_if74.preheader, label %vector.ph984

vector.ph984:                                     ; preds = %while_loop_body70.preheader
  %380 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0211334, i64 0
  %broadcast.splatinsert1001 = insertelement <8 x i32> poison, i32 %378, i64 0
  %broadcast.splat1002 = shufflevector <8 x i32> %broadcast.splatinsert1001, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert1004 = insertelement <8 x i32> poison, i32 %379, i64 0
  %broadcast.splat1005 = shufflevector <8 x i32> %broadcast.splatinsert1004, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body987

vector.body987:                                   ; preds = %vector.body987, %vector.ph984
  %lsr.iv1230 = phi i32 [ %lsr.iv.next1231, %vector.body987 ], [ %n.vec1130, %vector.ph984 ]
  %vec.ind992 = phi <8 x i32> [ %induction1135, %vector.ph984 ], [ %vec.ind.next993, %vector.body987 ]
  %vec.phi994 = phi <8 x float> [ %380, %vector.ph984 ], [ %395, %vector.body987 ]
  %381 = add <8 x i32> %vec.ind992, %broadcast.splat1140
  %382 = add <8 x i32> %vec.ind992, %broadcast.splat998
  %383 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %382, <8 x i32> %broadcast.splat1144)
  %384 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %383, <8 x i32> zeroinitializer)
  %385 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %381, <8 x i32> %broadcast.splat1144)
  %386 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %385, <8 x i32> zeroinitializer)
  %387 = add <8 x i32> %broadcast.splat1002, %384
  %388 = sext <8 x i32> %387 to <8 x i64>
  %389 = getelementptr float, ptr %.pre, <8 x i64> %388
  %wide.masked.gather1003 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %389, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %390 = add <8 x i32> %broadcast.splat1005, %386
  %391 = sext <8 x i32> %390 to <8 x i64>
  %392 = getelementptr float, ptr %.pre460, <8 x i64> %391
  %wide.masked.gather1006 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %392, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %393 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather1003, %wide.masked.gather1006
  %394 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %393)
  %395 = fadd reassoc ninf nsz <8 x float> %394, %vec.phi994
  %vec.ind.next993 = add <8 x i32> %vec.ind992, splat (i32 16)
  %lsr.iv.next1231 = add i32 %lsr.iv1230, -8
  %396 = icmp eq i32 %lsr.iv.next1231, 0
  br i1 %396, label %middle.block981, label %vector.body987, !llvm.loop !21

middle.block981:                                  ; preds = %vector.body987
  %397 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %395)
  br i1 %cmp.n1152, label %false_block73, label %after_if74.preheader

after_if74.preheader:                             ; preds = %middle.block981, %while_loop_body70.preheader
  %.0209329.ph = phi i32 [ %neg, %while_loop_body70.preheader ], [ %185, %middle.block981 ]
  %.1212328.ph = phi float [ %.0211334, %while_loop_body70.preheader ], [ %397, %middle.block981 ]
  br label %after_if74

false_block67:                                    ; preds = %false_block73
  %398 = fcmp reassoc ninf nsz olt float %.lcssa667, %.3232
  %399 = or i1 %351, %398
  %.3240 = select i1 %399, i32 %.0241, i32 %.1238
  %.3236 = select i1 %398, i32 %352, i32 %.2235
  %invariant.op343 = add i32 %53, %.3240
  %invariant.op337 = add i32 %50, %.3236
  %broadcast.splatinsert961 = insertelement <8 x i32> poison, i32 %invariant.op337, i64 0
  %broadcast.splat962 = shufflevector <8 x i32> %broadcast.splatinsert961, <8 x i32> poison, <8 x i32> zeroinitializer
  %400 = add i32 %21, %.3236
  %401 = add i32 %400, %49
  br label %while_loop_body85.preheader

false_block73.loopexit:                           ; preds = %after_if74
  br label %false_block73

false_block73:                                    ; preds = %false_block73.loopexit, %middle.block981
  %.lcssa667 = phi float [ %397, %middle.block981 ], [ %420, %false_block73.loopexit ]
  %402 = add i32 %.0210335, 2
  %.not254 = icmp sgt i32 %402, %163
  br i1 %.not254, label %false_block67, label %while_loop_body70.preheader

after_if74:                                       ; preds = %after_if74, %after_if74.preheader
  %.0209329 = phi i32 [ %421, %after_if74 ], [ %.0209329.ph, %after_if74.preheader ]
  %.1212328 = phi float [ %420, %after_if74 ], [ %.1212328.ph, %after_if74.preheader ]
  %403 = add i32 %50, %.0209329
  %404 = add i32 %187, %.0209329
  %405 = add i32 %404, 2
  %406 = tail call i32 @llvm.smin.i32(i32 %405, i32 %165)
  %407 = tail call i32 @llvm.smax.i32(i32 %406, i32 0)
  %408 = tail call i32 @llvm.smin.i32(i32 %403, i32 %165)
  %409 = tail call i32 @llvm.smax.i32(i32 %408, i32 0)
  %410 = add i32 %378, %407
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, ptr %.pre, i64 %411
  %413 = load float, ptr %412, align 4
  %414 = add i32 %379, %409
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, ptr %.pre460, i64 %415
  %417 = load float, ptr %416, align 4
  %418 = fsub reassoc ninf nsz float %413, %417
  %419 = tail call noundef float @llvm.fabs.f32(float %418)
  %420 = fadd reassoc ninf nsz float %419, %.1212328
  %421 = add i32 %.0209329, 2
  %.not273 = icmp sgt i32 %421, %163
  br i1 %.not273, label %false_block73.loopexit, label %after_if74, !llvm.loop !22

while_loop_body85.preheader:                      ; preds = %false_block88, %false_block67
  %.0194347 = phi i32 [ %neg, %false_block67 ], [ %449, %false_block88 ]
  %.0195346 = phi float [ 0.000000e+00, %false_block67 ], [ %.lcssa668, %false_block88 ]
  %422 = add i32 %.0194347, %53
  %.reass344 = add i32 %.0194347, %invariant.op343
  %423 = tail call i32 @llvm.smin.i32(i32 %.reass344, i32 %164)
  %424 = tail call i32 @llvm.smax.i32(i32 %423, i32 0)
  %425 = tail call i32 @llvm.smin.i32(i32 %422, i32 %164)
  %426 = tail call i32 @llvm.smax.i32(i32 %425, i32 0)
  %427 = mul i32 %.pre459, %424
  %428 = mul i32 %.pre461, %426
  br i1 %brmerge, label %after_if89.preheader, label %vector.ph948

vector.ph948:                                     ; preds = %while_loop_body85.preheader
  %429 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0195346, i64 0
  %broadcast.splatinsert965 = insertelement <8 x i32> poison, i32 %427, i64 0
  %broadcast.splat966 = shufflevector <8 x i32> %broadcast.splatinsert965, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert968 = insertelement <8 x i32> poison, i32 %428, i64 0
  %broadcast.splat969 = shufflevector <8 x i32> %broadcast.splatinsert968, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body951

vector.body951:                                   ; preds = %vector.body951, %vector.ph948
  %lsr.iv1232 = phi i32 [ %lsr.iv.next1233, %vector.body951 ], [ %n.vec1130, %vector.ph948 ]
  %vec.ind956 = phi <8 x i32> [ %induction1135, %vector.ph948 ], [ %vec.ind.next957, %vector.body951 ]
  %vec.phi958 = phi <8 x float> [ %429, %vector.ph948 ], [ %444, %vector.body951 ]
  %430 = add <8 x i32> %vec.ind956, %broadcast.splat1140
  %431 = add <8 x i32> %vec.ind956, %broadcast.splat962
  %432 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %431, <8 x i32> %broadcast.splat1144)
  %433 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %432, <8 x i32> zeroinitializer)
  %434 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %430, <8 x i32> %broadcast.splat1144)
  %435 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %434, <8 x i32> zeroinitializer)
  %436 = add <8 x i32> %broadcast.splat966, %433
  %437 = sext <8 x i32> %436 to <8 x i64>
  %438 = getelementptr float, ptr %.pre, <8 x i64> %437
  %wide.masked.gather967 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %438, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %439 = add <8 x i32> %broadcast.splat969, %435
  %440 = sext <8 x i32> %439 to <8 x i64>
  %441 = getelementptr float, ptr %.pre460, <8 x i64> %440
  %wide.masked.gather970 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %441, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %442 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather967, %wide.masked.gather970
  %443 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %442)
  %444 = fadd reassoc ninf nsz <8 x float> %443, %vec.phi958
  %vec.ind.next957 = add <8 x i32> %vec.ind956, splat (i32 16)
  %lsr.iv.next1233 = add i32 %lsr.iv1232, -8
  %445 = icmp eq i32 %lsr.iv.next1233, 0
  br i1 %445, label %middle.block945, label %vector.body951, !llvm.loop !23

middle.block945:                                  ; preds = %vector.body951
  %446 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %444)
  br i1 %cmp.n1152, label %false_block88, label %after_if89.preheader

after_if89.preheader:                             ; preds = %middle.block945, %while_loop_body85.preheader
  %.0193341.ph = phi i32 [ %neg, %while_loop_body85.preheader ], [ %185, %middle.block945 ]
  %.1196340.ph = phi float [ %.0195346, %while_loop_body85.preheader ], [ %446, %middle.block945 ]
  br label %after_if89

false_block82:                                    ; preds = %false_block88
  %447 = fcmp reassoc ninf nsz olt float %.lcssa668, 0x46293E5940000000
  %.0197 = select i1 %447, float %.lcssa668, float 0x46293E5940000000
  %448 = add i32 %.3240, -1
  %invariant.op355 = add i32 %53, %448
  br label %while_loop_body100.preheader

false_block88.loopexit:                           ; preds = %after_if89
  br label %false_block88

false_block88:                                    ; preds = %false_block88.loopexit, %middle.block945
  %.lcssa668 = phi float [ %446, %middle.block945 ], [ %466, %false_block88.loopexit ]
  %449 = add i32 %.0194347, 2
  %.not255 = icmp sgt i32 %449, %163
  br i1 %.not255, label %false_block82, label %while_loop_body85.preheader

after_if89:                                       ; preds = %after_if89, %after_if89.preheader
  %.0193341 = phi i32 [ %467, %after_if89 ], [ %.0193341.ph, %after_if89.preheader ]
  %.1196340 = phi float [ %466, %after_if89 ], [ %.1196340.ph, %after_if89.preheader ]
  %450 = add i32 %50, %.0193341
  %451 = add i32 %401, %.0193341
  %452 = tail call i32 @llvm.smin.i32(i32 %451, i32 %165)
  %453 = tail call i32 @llvm.smax.i32(i32 %452, i32 0)
  %454 = tail call i32 @llvm.smin.i32(i32 %450, i32 %165)
  %455 = tail call i32 @llvm.smax.i32(i32 %454, i32 0)
  %456 = add i32 %427, %453
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, ptr %.pre, i64 %457
  %459 = load float, ptr %458, align 4
  %460 = add i32 %428, %455
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %.pre460, i64 %461
  %463 = load float, ptr %462, align 4
  %464 = fsub reassoc ninf nsz float %459, %463
  %465 = tail call noundef float @llvm.fabs.f32(float %464)
  %466 = fadd reassoc ninf nsz float %465, %.1196340
  %467 = add i32 %.0193341, 2
  %.not272 = icmp sgt i32 %467, %163
  br i1 %.not272, label %false_block88.loopexit, label %after_if89, !llvm.loop !24

while_loop_body100.preheader:                     ; preds = %false_block103, %false_block82
  %.0190359 = phi i32 [ %neg, %false_block82 ], [ %495, %false_block103 ]
  %.0191358 = phi float [ 0.000000e+00, %false_block82 ], [ %.lcssa669, %false_block103 ]
  %468 = add i32 %.0190359, %53
  %.reass356 = add i32 %.0190359, %invariant.op355
  %469 = tail call i32 @llvm.smin.i32(i32 %.reass356, i32 %164)
  %470 = tail call i32 @llvm.smax.i32(i32 %469, i32 0)
  %471 = tail call i32 @llvm.smin.i32(i32 %468, i32 %164)
  %472 = tail call i32 @llvm.smax.i32(i32 %471, i32 0)
  %473 = mul i32 %.pre459, %470
  %474 = mul i32 %.pre461, %472
  br i1 %brmerge, label %after_if104.preheader, label %vector.ph912

vector.ph912:                                     ; preds = %while_loop_body100.preheader
  %475 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0191358, i64 0
  %broadcast.splatinsert929 = insertelement <8 x i32> poison, i32 %473, i64 0
  %broadcast.splat930 = shufflevector <8 x i32> %broadcast.splatinsert929, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert932 = insertelement <8 x i32> poison, i32 %474, i64 0
  %broadcast.splat933 = shufflevector <8 x i32> %broadcast.splatinsert932, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body915

vector.body915:                                   ; preds = %vector.body915, %vector.ph912
  %lsr.iv1234 = phi i32 [ %lsr.iv.next1235, %vector.body915 ], [ %n.vec1130, %vector.ph912 ]
  %vec.ind920 = phi <8 x i32> [ %induction1135, %vector.ph912 ], [ %vec.ind.next921, %vector.body915 ]
  %vec.phi922 = phi <8 x float> [ %475, %vector.ph912 ], [ %490, %vector.body915 ]
  %476 = add <8 x i32> %vec.ind920, %broadcast.splat1140
  %477 = add <8 x i32> %vec.ind920, %broadcast.splat962
  %478 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %477, <8 x i32> %broadcast.splat1144)
  %479 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %478, <8 x i32> zeroinitializer)
  %480 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %476, <8 x i32> %broadcast.splat1144)
  %481 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %480, <8 x i32> zeroinitializer)
  %482 = add <8 x i32> %broadcast.splat930, %479
  %483 = sext <8 x i32> %482 to <8 x i64>
  %484 = getelementptr float, ptr %.pre, <8 x i64> %483
  %wide.masked.gather931 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %484, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %485 = add <8 x i32> %broadcast.splat933, %481
  %486 = sext <8 x i32> %485 to <8 x i64>
  %487 = getelementptr float, ptr %.pre460, <8 x i64> %486
  %wide.masked.gather934 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %487, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %488 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather931, %wide.masked.gather934
  %489 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %488)
  %490 = fadd reassoc ninf nsz <8 x float> %489, %vec.phi922
  %vec.ind.next921 = add <8 x i32> %vec.ind920, splat (i32 16)
  %lsr.iv.next1235 = add i32 %lsr.iv1234, -8
  %491 = icmp eq i32 %lsr.iv.next1235, 0
  br i1 %491, label %middle.block909, label %vector.body915, !llvm.loop !25

middle.block909:                                  ; preds = %vector.body915
  %492 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %490)
  br i1 %cmp.n1152, label %false_block103, label %after_if104.preheader

after_if104.preheader:                            ; preds = %middle.block909, %while_loop_body100.preheader
  %.0189353.ph = phi i32 [ %neg, %while_loop_body100.preheader ], [ %185, %middle.block909 ]
  %.1192352.ph = phi float [ %.0191358, %while_loop_body100.preheader ], [ %492, %middle.block909 ]
  br label %after_if104

false_block97:                                    ; preds = %false_block103
  %493 = fcmp reassoc ninf nsz olt float %.lcssa669, %.0197
  %.0205 = select i1 %493, i32 %448, i32 %.3240
  %.1198 = select i1 %493, float %.lcssa669, float %.0197
  %494 = add i32 %.3240, 1
  %invariant.op367 = add i32 %53, %494
  br label %while_loop_body115.preheader

false_block103.loopexit:                          ; preds = %after_if104
  br label %false_block103

false_block103:                                   ; preds = %false_block103.loopexit, %middle.block909
  %.lcssa669 = phi float [ %492, %middle.block909 ], [ %512, %false_block103.loopexit ]
  %495 = add i32 %.0190359, 2
  %.not256 = icmp sgt i32 %495, %163
  br i1 %.not256, label %false_block97, label %while_loop_body100.preheader

after_if104:                                      ; preds = %after_if104, %after_if104.preheader
  %.0189353 = phi i32 [ %513, %after_if104 ], [ %.0189353.ph, %after_if104.preheader ]
  %.1192352 = phi float [ %512, %after_if104 ], [ %.1192352.ph, %after_if104.preheader ]
  %496 = add i32 %50, %.0189353
  %497 = add i32 %401, %.0189353
  %498 = tail call i32 @llvm.smin.i32(i32 %497, i32 %165)
  %499 = tail call i32 @llvm.smax.i32(i32 %498, i32 0)
  %500 = tail call i32 @llvm.smin.i32(i32 %496, i32 %165)
  %501 = tail call i32 @llvm.smax.i32(i32 %500, i32 0)
  %502 = add i32 %473, %499
  %503 = sext i32 %502 to i64
  %504 = getelementptr float, ptr %.pre, i64 %503
  %505 = load float, ptr %504, align 4
  %506 = add i32 %474, %501
  %507 = sext i32 %506 to i64
  %508 = getelementptr float, ptr %.pre460, i64 %507
  %509 = load float, ptr %508, align 4
  %510 = fsub reassoc ninf nsz float %505, %509
  %511 = tail call noundef float @llvm.fabs.f32(float %510)
  %512 = fadd reassoc ninf nsz float %511, %.1192352
  %513 = add i32 %.0189353, 2
  %.not271 = icmp sgt i32 %513, %163
  br i1 %.not271, label %false_block103.loopexit, label %after_if104, !llvm.loop !26

while_loop_body115.preheader:                     ; preds = %false_block118, %false_block97
  %.0186371 = phi i32 [ %neg, %false_block97 ], [ %541, %false_block118 ]
  %.0187370 = phi float [ 0.000000e+00, %false_block97 ], [ %.lcssa670, %false_block118 ]
  %514 = add i32 %.0186371, %53
  %.reass368 = add i32 %.0186371, %invariant.op367
  %515 = tail call i32 @llvm.smin.i32(i32 %.reass368, i32 %164)
  %516 = tail call i32 @llvm.smax.i32(i32 %515, i32 0)
  %517 = tail call i32 @llvm.smin.i32(i32 %514, i32 %164)
  %518 = tail call i32 @llvm.smax.i32(i32 %517, i32 0)
  %519 = mul i32 %.pre459, %516
  %520 = mul i32 %.pre461, %518
  br i1 %brmerge, label %after_if119.preheader, label %vector.ph876

vector.ph876:                                     ; preds = %while_loop_body115.preheader
  %521 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0187370, i64 0
  %broadcast.splatinsert893 = insertelement <8 x i32> poison, i32 %519, i64 0
  %broadcast.splat894 = shufflevector <8 x i32> %broadcast.splatinsert893, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert896 = insertelement <8 x i32> poison, i32 %520, i64 0
  %broadcast.splat897 = shufflevector <8 x i32> %broadcast.splatinsert896, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body879

vector.body879:                                   ; preds = %vector.body879, %vector.ph876
  %lsr.iv1236 = phi i32 [ %lsr.iv.next1237, %vector.body879 ], [ %n.vec1130, %vector.ph876 ]
  %vec.ind884 = phi <8 x i32> [ %induction1135, %vector.ph876 ], [ %vec.ind.next885, %vector.body879 ]
  %vec.phi886 = phi <8 x float> [ %521, %vector.ph876 ], [ %536, %vector.body879 ]
  %522 = add <8 x i32> %vec.ind884, %broadcast.splat1140
  %523 = add <8 x i32> %vec.ind884, %broadcast.splat962
  %524 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %523, <8 x i32> %broadcast.splat1144)
  %525 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %524, <8 x i32> zeroinitializer)
  %526 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %522, <8 x i32> %broadcast.splat1144)
  %527 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %526, <8 x i32> zeroinitializer)
  %528 = add <8 x i32> %broadcast.splat894, %525
  %529 = sext <8 x i32> %528 to <8 x i64>
  %530 = getelementptr float, ptr %.pre, <8 x i64> %529
  %wide.masked.gather895 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %530, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %531 = add <8 x i32> %broadcast.splat897, %527
  %532 = sext <8 x i32> %531 to <8 x i64>
  %533 = getelementptr float, ptr %.pre460, <8 x i64> %532
  %wide.masked.gather898 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %533, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %534 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather895, %wide.masked.gather898
  %535 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %534)
  %536 = fadd reassoc ninf nsz <8 x float> %535, %vec.phi886
  %vec.ind.next885 = add <8 x i32> %vec.ind884, splat (i32 16)
  %lsr.iv.next1237 = add i32 %lsr.iv1236, -8
  %537 = icmp eq i32 %lsr.iv.next1237, 0
  br i1 %537, label %middle.block873, label %vector.body879, !llvm.loop !27

middle.block873:                                  ; preds = %vector.body879
  %538 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %536)
  br i1 %cmp.n1152, label %false_block118, label %after_if119.preheader

after_if119.preheader:                            ; preds = %middle.block873, %while_loop_body115.preheader
  %.0185365.ph = phi i32 [ %neg, %while_loop_body115.preheader ], [ %185, %middle.block873 ]
  %.1188364.ph = phi float [ %.0187370, %while_loop_body115.preheader ], [ %538, %middle.block873 ]
  br label %after_if119

false_block112:                                   ; preds = %false_block118
  %539 = fcmp reassoc ninf nsz olt float %.lcssa670, %.1198
  %.1206 = select i1 %539, i32 %494, i32 %.0205
  %.2199 = select i1 %539, float %.lcssa670, float %.1198
  %540 = add i32 %.3236, -1
  %invariant.op373 = add i32 %50, %540
  %broadcast.splatinsert853 = insertelement <8 x i32> poison, i32 %invariant.op373, i64 0
  %broadcast.splat854 = shufflevector <8 x i32> %broadcast.splatinsert853, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body130.preheader

false_block118.loopexit:                          ; preds = %after_if119
  br label %false_block118

false_block118:                                   ; preds = %false_block118.loopexit, %middle.block873
  %.lcssa670 = phi float [ %538, %middle.block873 ], [ %558, %false_block118.loopexit ]
  %541 = add i32 %.0186371, 2
  %.not257 = icmp sgt i32 %541, %163
  br i1 %.not257, label %false_block112, label %while_loop_body115.preheader

after_if119:                                      ; preds = %after_if119, %after_if119.preheader
  %.0185365 = phi i32 [ %559, %after_if119 ], [ %.0185365.ph, %after_if119.preheader ]
  %.1188364 = phi float [ %558, %after_if119 ], [ %.1188364.ph, %after_if119.preheader ]
  %542 = add i32 %50, %.0185365
  %543 = add i32 %401, %.0185365
  %544 = tail call i32 @llvm.smin.i32(i32 %543, i32 %165)
  %545 = tail call i32 @llvm.smax.i32(i32 %544, i32 0)
  %546 = tail call i32 @llvm.smin.i32(i32 %542, i32 %165)
  %547 = tail call i32 @llvm.smax.i32(i32 %546, i32 0)
  %548 = add i32 %519, %545
  %549 = sext i32 %548 to i64
  %550 = getelementptr float, ptr %.pre, i64 %549
  %551 = load float, ptr %550, align 4
  %552 = add i32 %520, %547
  %553 = sext i32 %552 to i64
  %554 = getelementptr float, ptr %.pre460, i64 %553
  %555 = load float, ptr %554, align 4
  %556 = fsub reassoc ninf nsz float %551, %555
  %557 = tail call noundef float @llvm.fabs.f32(float %556)
  %558 = fadd reassoc ninf nsz float %557, %.1188364
  %559 = add i32 %.0185365, 2
  %.not270 = icmp sgt i32 %559, %163
  br i1 %.not270, label %false_block118.loopexit, label %after_if119, !llvm.loop !28

while_loop_body130.preheader:                     ; preds = %false_block133, %false_block112
  %.0182383 = phi i32 [ %neg, %false_block112 ], [ %587, %false_block133 ]
  %.0183382 = phi float [ 0.000000e+00, %false_block112 ], [ %.lcssa671, %false_block133 ]
  %560 = add i32 %.0182383, %53
  %.reass380 = add i32 %.0182383, %invariant.op343
  %561 = tail call i32 @llvm.smin.i32(i32 %.reass380, i32 %164)
  %562 = tail call i32 @llvm.smax.i32(i32 %561, i32 0)
  %563 = tail call i32 @llvm.smin.i32(i32 %560, i32 %164)
  %564 = tail call i32 @llvm.smax.i32(i32 %563, i32 0)
  %565 = mul i32 %.pre459, %562
  %566 = mul i32 %.pre461, %564
  br i1 %brmerge, label %after_if134.preheader, label %vector.ph840

vector.ph840:                                     ; preds = %while_loop_body130.preheader
  %567 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0183382, i64 0
  %broadcast.splatinsert857 = insertelement <8 x i32> poison, i32 %565, i64 0
  %broadcast.splat858 = shufflevector <8 x i32> %broadcast.splatinsert857, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert860 = insertelement <8 x i32> poison, i32 %566, i64 0
  %broadcast.splat861 = shufflevector <8 x i32> %broadcast.splatinsert860, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body843

vector.body843:                                   ; preds = %vector.body843, %vector.ph840
  %lsr.iv1238 = phi i32 [ %lsr.iv.next1239, %vector.body843 ], [ %n.vec1130, %vector.ph840 ]
  %vec.ind848 = phi <8 x i32> [ %induction1135, %vector.ph840 ], [ %vec.ind.next849, %vector.body843 ]
  %vec.phi850 = phi <8 x float> [ %567, %vector.ph840 ], [ %582, %vector.body843 ]
  %568 = add <8 x i32> %vec.ind848, %broadcast.splat1140
  %569 = add <8 x i32> %vec.ind848, %broadcast.splat854
  %570 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %569, <8 x i32> %broadcast.splat1144)
  %571 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %570, <8 x i32> zeroinitializer)
  %572 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %568, <8 x i32> %broadcast.splat1144)
  %573 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %572, <8 x i32> zeroinitializer)
  %574 = add <8 x i32> %broadcast.splat858, %571
  %575 = sext <8 x i32> %574 to <8 x i64>
  %576 = getelementptr float, ptr %.pre, <8 x i64> %575
  %wide.masked.gather859 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %576, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %577 = add <8 x i32> %broadcast.splat861, %573
  %578 = sext <8 x i32> %577 to <8 x i64>
  %579 = getelementptr float, ptr %.pre460, <8 x i64> %578
  %wide.masked.gather862 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %579, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %580 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather859, %wide.masked.gather862
  %581 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %580)
  %582 = fadd reassoc ninf nsz <8 x float> %581, %vec.phi850
  %vec.ind.next849 = add <8 x i32> %vec.ind848, splat (i32 16)
  %lsr.iv.next1239 = add i32 %lsr.iv1238, -8
  %583 = icmp eq i32 %lsr.iv.next1239, 0
  br i1 %583, label %middle.block837, label %vector.body843, !llvm.loop !29

middle.block837:                                  ; preds = %vector.body843
  %584 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %582)
  br i1 %cmp.n1152, label %false_block133, label %after_if134.preheader

after_if134.preheader:                            ; preds = %middle.block837, %while_loop_body130.preheader
  %.0181377.ph = phi i32 [ %neg, %while_loop_body130.preheader ], [ %185, %middle.block837 ]
  %.1184376.ph = phi float [ %.0183382, %while_loop_body130.preheader ], [ %584, %middle.block837 ]
  br label %after_if134

false_block127:                                   ; preds = %false_block133
  %585 = fcmp reassoc ninf nsz olt float %.lcssa671, %.2199
  %.2203 = select i1 %585, i32 %540, i32 %.3236
  %.3200 = select i1 %585, float %.lcssa671, float %.2199
  %586 = add i32 %.3236, 1
  %invariant.op385 = add i32 %50, %586
  %broadcast.splatinsert817 = insertelement <8 x i32> poison, i32 %invariant.op385, i64 0
  %broadcast.splat818 = shufflevector <8 x i32> %broadcast.splatinsert817, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body145.preheader

false_block133.loopexit:                          ; preds = %after_if134
  br label %false_block133

false_block133:                                   ; preds = %false_block133.loopexit, %middle.block837
  %.lcssa671 = phi float [ %584, %middle.block837 ], [ %605, %false_block133.loopexit ]
  %587 = add i32 %.0182383, 2
  %.not258 = icmp sgt i32 %587, %163
  br i1 %.not258, label %false_block127, label %while_loop_body130.preheader

after_if134:                                      ; preds = %after_if134, %after_if134.preheader
  %.0181377 = phi i32 [ %606, %after_if134 ], [ %.0181377.ph, %after_if134.preheader ]
  %.1184376 = phi float [ %605, %after_if134 ], [ %.1184376.ph, %after_if134.preheader ]
  %588 = add i32 %50, %.0181377
  %589 = add i32 %401, %.0181377
  %590 = add i32 %589, -1
  %591 = tail call i32 @llvm.smin.i32(i32 %590, i32 %165)
  %592 = tail call i32 @llvm.smax.i32(i32 %591, i32 0)
  %593 = tail call i32 @llvm.smin.i32(i32 %588, i32 %165)
  %594 = tail call i32 @llvm.smax.i32(i32 %593, i32 0)
  %595 = add i32 %565, %592
  %596 = sext i32 %595 to i64
  %597 = getelementptr float, ptr %.pre, i64 %596
  %598 = load float, ptr %597, align 4
  %599 = add i32 %566, %594
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %.pre460, i64 %600
  %602 = load float, ptr %601, align 4
  %603 = fsub reassoc ninf nsz float %598, %602
  %604 = tail call noundef float @llvm.fabs.f32(float %603)
  %605 = fadd reassoc ninf nsz float %604, %.1184376
  %606 = add i32 %.0181377, 2
  %.not269 = icmp sgt i32 %606, %163
  br i1 %.not269, label %false_block133.loopexit, label %after_if134, !llvm.loop !30

while_loop_body145.preheader:                     ; preds = %false_block148, %false_block127
  %.0178395 = phi i32 [ %neg, %false_block127 ], [ %635, %false_block148 ]
  %.0179394 = phi float [ 0.000000e+00, %false_block127 ], [ %.lcssa672, %false_block148 ]
  %607 = add i32 %.0178395, %53
  %.reass392 = add i32 %.0178395, %invariant.op343
  %608 = tail call i32 @llvm.smin.i32(i32 %.reass392, i32 %164)
  %609 = tail call i32 @llvm.smax.i32(i32 %608, i32 0)
  %610 = tail call i32 @llvm.smin.i32(i32 %607, i32 %164)
  %611 = tail call i32 @llvm.smax.i32(i32 %610, i32 0)
  %612 = mul i32 %.pre459, %609
  %613 = mul i32 %.pre461, %611
  br i1 %brmerge, label %after_if149.preheader, label %vector.ph804

vector.ph804:                                     ; preds = %while_loop_body145.preheader
  %614 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0179394, i64 0
  %broadcast.splatinsert821 = insertelement <8 x i32> poison, i32 %612, i64 0
  %broadcast.splat822 = shufflevector <8 x i32> %broadcast.splatinsert821, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert824 = insertelement <8 x i32> poison, i32 %613, i64 0
  %broadcast.splat825 = shufflevector <8 x i32> %broadcast.splatinsert824, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body807

vector.body807:                                   ; preds = %vector.body807, %vector.ph804
  %lsr.iv1240 = phi i32 [ %lsr.iv.next1241, %vector.body807 ], [ %n.vec1130, %vector.ph804 ]
  %vec.ind812 = phi <8 x i32> [ %induction1135, %vector.ph804 ], [ %vec.ind.next813, %vector.body807 ]
  %vec.phi814 = phi <8 x float> [ %614, %vector.ph804 ], [ %629, %vector.body807 ]
  %615 = add <8 x i32> %vec.ind812, %broadcast.splat1140
  %616 = add <8 x i32> %vec.ind812, %broadcast.splat818
  %617 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %616, <8 x i32> %broadcast.splat1144)
  %618 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %617, <8 x i32> zeroinitializer)
  %619 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %615, <8 x i32> %broadcast.splat1144)
  %620 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %619, <8 x i32> zeroinitializer)
  %621 = add <8 x i32> %broadcast.splat822, %618
  %622 = sext <8 x i32> %621 to <8 x i64>
  %623 = getelementptr float, ptr %.pre, <8 x i64> %622
  %wide.masked.gather823 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %623, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %624 = add <8 x i32> %broadcast.splat825, %620
  %625 = sext <8 x i32> %624 to <8 x i64>
  %626 = getelementptr float, ptr %.pre460, <8 x i64> %625
  %wide.masked.gather826 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %626, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %627 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather823, %wide.masked.gather826
  %628 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %627)
  %629 = fadd reassoc ninf nsz <8 x float> %628, %vec.phi814
  %vec.ind.next813 = add <8 x i32> %vec.ind812, splat (i32 16)
  %lsr.iv.next1241 = add i32 %lsr.iv1240, -8
  %630 = icmp eq i32 %lsr.iv.next1241, 0
  br i1 %630, label %middle.block801, label %vector.body807, !llvm.loop !31

middle.block801:                                  ; preds = %vector.body807
  %631 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %629)
  br i1 %cmp.n1152, label %false_block148, label %after_if149.preheader

after_if149.preheader:                            ; preds = %middle.block801, %while_loop_body145.preheader
  %.0177389.ph = phi i32 [ %neg, %while_loop_body145.preheader ], [ %185, %middle.block801 ]
  %.1180388.ph = phi float [ %.0179394, %while_loop_body145.preheader ], [ %631, %middle.block801 ]
  br label %after_if149

false_block142:                                   ; preds = %false_block148
  %632 = fcmp reassoc ninf nsz olt float %.lcssa672, %.3200
  %633 = or i1 %585, %632
  %.3208 = select i1 %633, i32 %.3240, i32 %.1206
  %.3204 = select i1 %632, i32 %586, i32 %.2203
  %.4 = select i1 %632, float %.lcssa672, float %.3200
  %invariant.op403 = add i32 %53, %.3208
  %634 = add i32 %.3204, -1
  %invariant.op401 = add i32 %50, %634
  %broadcast.splatinsert781 = insertelement <8 x i32> poison, i32 %invariant.op401, i64 0
  %broadcast.splat782 = shufflevector <8 x i32> %broadcast.splatinsert781, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body160.preheader

false_block148.loopexit:                          ; preds = %after_if149
  br label %false_block148

false_block148:                                   ; preds = %false_block148.loopexit, %middle.block801
  %.lcssa672 = phi float [ %631, %middle.block801 ], [ %653, %false_block148.loopexit ]
  %635 = add i32 %.0178395, 2
  %.not259 = icmp sgt i32 %635, %163
  br i1 %.not259, label %false_block142, label %while_loop_body145.preheader

after_if149:                                      ; preds = %after_if149, %after_if149.preheader
  %.0177389 = phi i32 [ %654, %after_if149 ], [ %.0177389.ph, %after_if149.preheader ]
  %.1180388 = phi float [ %653, %after_if149 ], [ %.1180388.ph, %after_if149.preheader ]
  %636 = add i32 %50, %.0177389
  %637 = add i32 %401, %.0177389
  %638 = add i32 %637, 1
  %639 = tail call i32 @llvm.smin.i32(i32 %638, i32 %165)
  %640 = tail call i32 @llvm.smax.i32(i32 %639, i32 0)
  %641 = tail call i32 @llvm.smin.i32(i32 %636, i32 %165)
  %642 = tail call i32 @llvm.smax.i32(i32 %641, i32 0)
  %643 = add i32 %612, %640
  %644 = sext i32 %643 to i64
  %645 = getelementptr float, ptr %.pre, i64 %644
  %646 = load float, ptr %645, align 4
  %647 = add i32 %613, %642
  %648 = sext i32 %647 to i64
  %649 = getelementptr float, ptr %.pre460, i64 %648
  %650 = load float, ptr %649, align 4
  %651 = fsub reassoc ninf nsz float %646, %650
  %652 = tail call noundef float @llvm.fabs.f32(float %651)
  %653 = fadd reassoc ninf nsz float %652, %.1180388
  %654 = add i32 %.0177389, 2
  %.not268 = icmp sgt i32 %654, %163
  br i1 %.not268, label %false_block148.loopexit, label %after_if149, !llvm.loop !32

while_loop_body172.preheader.lr.ph:               ; preds = %false_block163
  %655 = add i32 %.3204, 1
  %invariant.op413 = add i32 %50, %655
  %broadcast.splatinsert745 = insertelement <8 x i32> poison, i32 %invariant.op413, i64 0
  %broadcast.splat746 = shufflevector <8 x i32> %broadcast.splatinsert745, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body172.preheader

while_loop_body160.preheader:                     ; preds = %false_block163, %false_block142
  %.0167407 = phi i32 [ %neg, %false_block142 ], [ %682, %false_block163 ]
  %.0175406 = phi float [ 0.000000e+00, %false_block142 ], [ %.lcssa673, %false_block163 ]
  %656 = add i32 %.0167407, %53
  %.reass404 = add i32 %.0167407, %invariant.op403
  %657 = tail call i32 @llvm.smin.i32(i32 %.reass404, i32 %164)
  %658 = tail call i32 @llvm.smax.i32(i32 %657, i32 0)
  %659 = tail call i32 @llvm.smin.i32(i32 %656, i32 %164)
  %660 = tail call i32 @llvm.smax.i32(i32 %659, i32 0)
  %661 = mul i32 %.pre459, %658
  %662 = mul i32 %.pre461, %660
  br i1 %brmerge, label %after_if164.preheader, label %vector.ph768

vector.ph768:                                     ; preds = %while_loop_body160.preheader
  %663 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0175406, i64 0
  %broadcast.splatinsert785 = insertelement <8 x i32> poison, i32 %661, i64 0
  %broadcast.splat786 = shufflevector <8 x i32> %broadcast.splatinsert785, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert788 = insertelement <8 x i32> poison, i32 %662, i64 0
  %broadcast.splat789 = shufflevector <8 x i32> %broadcast.splatinsert788, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body771

vector.body771:                                   ; preds = %vector.body771, %vector.ph768
  %lsr.iv1242 = phi i32 [ %lsr.iv.next1243, %vector.body771 ], [ %n.vec1130, %vector.ph768 ]
  %vec.ind776 = phi <8 x i32> [ %induction1135, %vector.ph768 ], [ %vec.ind.next777, %vector.body771 ]
  %vec.phi778 = phi <8 x float> [ %663, %vector.ph768 ], [ %678, %vector.body771 ]
  %664 = add <8 x i32> %vec.ind776, %broadcast.splat1140
  %665 = add <8 x i32> %vec.ind776, %broadcast.splat782
  %666 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %665, <8 x i32> %broadcast.splat1144)
  %667 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %666, <8 x i32> zeroinitializer)
  %668 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %664, <8 x i32> %broadcast.splat1144)
  %669 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %668, <8 x i32> zeroinitializer)
  %670 = add <8 x i32> %broadcast.splat786, %667
  %671 = sext <8 x i32> %670 to <8 x i64>
  %672 = getelementptr float, ptr %.pre, <8 x i64> %671
  %wide.masked.gather787 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %672, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %673 = add <8 x i32> %broadcast.splat789, %669
  %674 = sext <8 x i32> %673 to <8 x i64>
  %675 = getelementptr float, ptr %.pre460, <8 x i64> %674
  %wide.masked.gather790 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %675, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %676 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather787, %wide.masked.gather790
  %677 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %676)
  %678 = fadd reassoc ninf nsz <8 x float> %677, %vec.phi778
  %vec.ind.next777 = add <8 x i32> %vec.ind776, splat (i32 16)
  %lsr.iv.next1243 = add i32 %lsr.iv1242, -8
  %679 = icmp eq i32 %lsr.iv.next1243, 0
  br i1 %679, label %middle.block765, label %vector.body771, !llvm.loop !33

middle.block765:                                  ; preds = %vector.body771
  %680 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %678)
  br i1 %cmp.n1152, label %false_block163, label %after_if164.preheader

after_if164.preheader:                            ; preds = %middle.block765, %while_loop_body160.preheader
  %.0166399.ph = phi i32 [ %neg, %while_loop_body160.preheader ], [ %185, %middle.block765 ]
  %.1176398.ph = phi float [ %.0175406, %while_loop_body160.preheader ], [ %680, %middle.block765 ]
  %681 = add i32 %50, %.0166399.ph
  br label %after_if164

false_block163.loopexit:                          ; preds = %after_if164
  br label %false_block163

false_block163:                                   ; preds = %false_block163.loopexit, %middle.block765
  %.lcssa673 = phi float [ %680, %middle.block765 ], [ %698, %false_block163.loopexit ]
  %682 = add i32 %.0167407, 2
  %.not260 = icmp sgt i32 %682, %163
  br i1 %.not260, label %while_loop_body172.preheader.lr.ph, label %while_loop_body160.preheader

after_if164:                                      ; preds = %after_if164, %after_if164.preheader
  %lsr.iv1244 = phi i32 [ %681, %after_if164.preheader ], [ %lsr.iv.next1245, %after_if164 ]
  %.0166399 = phi i32 [ %699, %after_if164 ], [ %.0166399.ph, %after_if164.preheader ]
  %.1176398 = phi float [ %698, %after_if164 ], [ %.1176398.ph, %after_if164.preheader ]
  %683 = add i32 %634, %lsr.iv1244
  %684 = tail call i32 @llvm.smin.i32(i32 %683, i32 %165)
  %685 = tail call i32 @llvm.smax.i32(i32 %684, i32 0)
  %686 = tail call i32 @llvm.smin.i32(i32 %lsr.iv1244, i32 %165)
  %687 = tail call i32 @llvm.smax.i32(i32 %686, i32 0)
  %688 = add i32 %661, %685
  %689 = sext i32 %688 to i64
  %690 = getelementptr float, ptr %.pre, i64 %689
  %691 = load float, ptr %690, align 4
  %692 = add i32 %662, %687
  %693 = sext i32 %692 to i64
  %694 = getelementptr float, ptr %.pre460, i64 %693
  %695 = load float, ptr %694, align 4
  %696 = fsub reassoc ninf nsz float %691, %695
  %697 = tail call noundef float @llvm.fabs.f32(float %696)
  %698 = fadd reassoc ninf nsz float %697, %.1176398
  %699 = add i32 %.0166399, 2
  %lsr.iv.next1245 = add i32 %lsr.iv1244, 2
  %.not267 = icmp sgt i32 %699, %163
  br i1 %.not267, label %false_block163.loopexit, label %after_if164, !llvm.loop !34

while_loop_body184.preheader.lr.ph:               ; preds = %false_block175
  %invariant.op421 = add i32 %50, %.3204
  %700 = add i32 %.3208, -1
  %invariant.op431 = add i32 %53, %700
  %broadcast.splatinsert709 = insertelement <8 x i32> poison, i32 %invariant.op421, i64 0
  %broadcast.splat710 = shufflevector <8 x i32> %broadcast.splatinsert709, <8 x i32> poison, <8 x i32> zeroinitializer
  %701 = add i32 %21, %.3204
  %702 = add i32 %701, %49
  br label %while_loop_body184.preheader

while_loop_body172.preheader:                     ; preds = %false_block175, %while_loop_body172.preheader.lr.ph
  %.1168419 = phi i32 [ %neg, %while_loop_body172.preheader.lr.ph ], [ %729, %false_block175 ]
  %.0173418 = phi float [ 0.000000e+00, %while_loop_body172.preheader.lr.ph ], [ %.lcssa674, %false_block175 ]
  %703 = add i32 %.1168419, %53
  %.reass416 = add i32 %.1168419, %invariant.op403
  %704 = tail call i32 @llvm.smin.i32(i32 %.reass416, i32 %164)
  %705 = tail call i32 @llvm.smax.i32(i32 %704, i32 0)
  %706 = tail call i32 @llvm.smin.i32(i32 %703, i32 %164)
  %707 = tail call i32 @llvm.smax.i32(i32 %706, i32 0)
  %708 = mul i32 %.pre459, %705
  %709 = mul i32 %.pre461, %707
  br i1 %brmerge, label %after_if176.preheader, label %vector.ph732

vector.ph732:                                     ; preds = %while_loop_body172.preheader
  %710 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0173418, i64 0
  %broadcast.splatinsert749 = insertelement <8 x i32> poison, i32 %708, i64 0
  %broadcast.splat750 = shufflevector <8 x i32> %broadcast.splatinsert749, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert752 = insertelement <8 x i32> poison, i32 %709, i64 0
  %broadcast.splat753 = shufflevector <8 x i32> %broadcast.splatinsert752, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body735

vector.body735:                                   ; preds = %vector.body735, %vector.ph732
  %lsr.iv1246 = phi i32 [ %lsr.iv.next1247, %vector.body735 ], [ %n.vec1130, %vector.ph732 ]
  %vec.ind740 = phi <8 x i32> [ %induction1135, %vector.ph732 ], [ %vec.ind.next741, %vector.body735 ]
  %vec.phi742 = phi <8 x float> [ %710, %vector.ph732 ], [ %725, %vector.body735 ]
  %711 = add <8 x i32> %vec.ind740, %broadcast.splat1140
  %712 = add <8 x i32> %vec.ind740, %broadcast.splat746
  %713 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %712, <8 x i32> %broadcast.splat1144)
  %714 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %713, <8 x i32> zeroinitializer)
  %715 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %711, <8 x i32> %broadcast.splat1144)
  %716 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %715, <8 x i32> zeroinitializer)
  %717 = add <8 x i32> %broadcast.splat750, %714
  %718 = sext <8 x i32> %717 to <8 x i64>
  %719 = getelementptr float, ptr %.pre, <8 x i64> %718
  %wide.masked.gather751 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %719, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %720 = add <8 x i32> %broadcast.splat753, %716
  %721 = sext <8 x i32> %720 to <8 x i64>
  %722 = getelementptr float, ptr %.pre460, <8 x i64> %721
  %wide.masked.gather754 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %722, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %723 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather751, %wide.masked.gather754
  %724 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %723)
  %725 = fadd reassoc ninf nsz <8 x float> %724, %vec.phi742
  %vec.ind.next741 = add <8 x i32> %vec.ind740, splat (i32 16)
  %lsr.iv.next1247 = add i32 %lsr.iv1246, -8
  %726 = icmp eq i32 %lsr.iv.next1247, 0
  br i1 %726, label %middle.block729, label %vector.body735, !llvm.loop !35

middle.block729:                                  ; preds = %vector.body735
  %727 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %725)
  br i1 %cmp.n1152, label %false_block175, label %after_if176.preheader

after_if176.preheader:                            ; preds = %middle.block729, %while_loop_body172.preheader
  %.0165411.ph = phi i32 [ %neg, %while_loop_body172.preheader ], [ %185, %middle.block729 ]
  %.1174410.ph = phi float [ %.0173418, %while_loop_body172.preheader ], [ %727, %middle.block729 ]
  %728 = add i32 %50, %.0165411.ph
  br label %after_if176

false_block175.loopexit:                          ; preds = %after_if176
  br label %false_block175

false_block175:                                   ; preds = %false_block175.loopexit, %middle.block729
  %.lcssa674 = phi float [ %727, %middle.block729 ], [ %745, %false_block175.loopexit ]
  %729 = add i32 %.1168419, 2
  %.not261 = icmp sgt i32 %729, %163
  br i1 %.not261, label %while_loop_body184.preheader.lr.ph, label %while_loop_body172.preheader

after_if176:                                      ; preds = %after_if176, %after_if176.preheader
  %lsr.iv1248 = phi i32 [ %728, %after_if176.preheader ], [ %lsr.iv.next1249, %after_if176 ]
  %.0165411 = phi i32 [ %746, %after_if176 ], [ %.0165411.ph, %after_if176.preheader ]
  %.1174410 = phi float [ %745, %after_if176 ], [ %.1174410.ph, %after_if176.preheader ]
  %730 = add i32 %655, %lsr.iv1248
  %731 = tail call i32 @llvm.smin.i32(i32 %730, i32 %165)
  %732 = tail call i32 @llvm.smax.i32(i32 %731, i32 0)
  %733 = tail call i32 @llvm.smin.i32(i32 %lsr.iv1248, i32 %165)
  %734 = tail call i32 @llvm.smax.i32(i32 %733, i32 0)
  %735 = add i32 %708, %732
  %736 = sext i32 %735 to i64
  %737 = getelementptr float, ptr %.pre, i64 %736
  %738 = load float, ptr %737, align 4
  %739 = add i32 %709, %734
  %740 = sext i32 %739 to i64
  %741 = getelementptr float, ptr %.pre460, i64 %740
  %742 = load float, ptr %741, align 4
  %743 = fsub reassoc ninf nsz float %738, %742
  %744 = tail call noundef float @llvm.fabs.f32(float %743)
  %745 = fadd reassoc ninf nsz float %744, %.1174410
  %746 = add i32 %.0165411, 2
  %lsr.iv.next1249 = add i32 %lsr.iv1248, 2
  %.not266 = icmp sgt i32 %746, %163
  br i1 %.not266, label %false_block175.loopexit, label %after_if176, !llvm.loop !36

while_loop_body196.preheader.lr.ph:               ; preds = %false_block187
  %747 = add i32 %.3208, 1
  %invariant.op443 = add i32 %53, %747
  br label %while_loop_body196.preheader

while_loop_body184.preheader:                     ; preds = %false_block187, %while_loop_body184.preheader.lr.ph
  %.2429 = phi i32 [ %neg, %while_loop_body184.preheader.lr.ph ], [ %773, %false_block187 ]
  %.0171428 = phi float [ 0.000000e+00, %while_loop_body184.preheader.lr.ph ], [ %.lcssa675, %false_block187 ]
  %748 = add i32 %.2429, %53
  %.reass432 = add i32 %.2429, %invariant.op431
  %749 = tail call i32 @llvm.smin.i32(i32 %.reass432, i32 %164)
  %750 = tail call i32 @llvm.smax.i32(i32 %749, i32 0)
  %751 = tail call i32 @llvm.smin.i32(i32 %748, i32 %164)
  %752 = tail call i32 @llvm.smax.i32(i32 %751, i32 0)
  %753 = mul i32 %.pre459, %750
  %754 = mul i32 %.pre461, %752
  br i1 %brmerge, label %after_if188.preheader, label %vector.ph696

vector.ph696:                                     ; preds = %while_loop_body184.preheader
  %755 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0171428, i64 0
  %broadcast.splatinsert713 = insertelement <8 x i32> poison, i32 %753, i64 0
  %broadcast.splat714 = shufflevector <8 x i32> %broadcast.splatinsert713, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert716 = insertelement <8 x i32> poison, i32 %754, i64 0
  %broadcast.splat717 = shufflevector <8 x i32> %broadcast.splatinsert716, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body699

vector.body699:                                   ; preds = %vector.body699, %vector.ph696
  %lsr.iv1250 = phi i32 [ %lsr.iv.next1251, %vector.body699 ], [ %n.vec1130, %vector.ph696 ]
  %vec.ind704 = phi <8 x i32> [ %induction1135, %vector.ph696 ], [ %vec.ind.next705, %vector.body699 ]
  %vec.phi706 = phi <8 x float> [ %755, %vector.ph696 ], [ %770, %vector.body699 ]
  %756 = add <8 x i32> %vec.ind704, %broadcast.splat1140
  %757 = add <8 x i32> %vec.ind704, %broadcast.splat710
  %758 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %757, <8 x i32> %broadcast.splat1144)
  %759 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %758, <8 x i32> zeroinitializer)
  %760 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %756, <8 x i32> %broadcast.splat1144)
  %761 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %760, <8 x i32> zeroinitializer)
  %762 = add <8 x i32> %broadcast.splat714, %759
  %763 = sext <8 x i32> %762 to <8 x i64>
  %764 = getelementptr float, ptr %.pre, <8 x i64> %763
  %wide.masked.gather715 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %764, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %765 = add <8 x i32> %broadcast.splat717, %761
  %766 = sext <8 x i32> %765 to <8 x i64>
  %767 = getelementptr float, ptr %.pre460, <8 x i64> %766
  %wide.masked.gather718 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %767, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %768 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather715, %wide.masked.gather718
  %769 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %768)
  %770 = fadd reassoc ninf nsz <8 x float> %769, %vec.phi706
  %vec.ind.next705 = add <8 x i32> %vec.ind704, splat (i32 16)
  %lsr.iv.next1251 = add i32 %lsr.iv1250, -8
  %771 = icmp eq i32 %lsr.iv.next1251, 0
  br i1 %771, label %middle.block693, label %vector.body699, !llvm.loop !37

middle.block693:                                  ; preds = %vector.body699
  %772 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %770)
  br i1 %cmp.n1152, label %false_block187, label %after_if188.preheader

after_if188.preheader:                            ; preds = %middle.block693, %while_loop_body184.preheader
  %.0164425.ph = phi i32 [ %neg, %while_loop_body184.preheader ], [ %185, %middle.block693 ]
  %.1172424.ph = phi float [ %.0171428, %while_loop_body184.preheader ], [ %772, %middle.block693 ]
  br label %after_if188

false_block187.loopexit:                          ; preds = %after_if188
  br label %false_block187

false_block187:                                   ; preds = %false_block187.loopexit, %middle.block693
  %.lcssa675 = phi float [ %772, %middle.block693 ], [ %790, %false_block187.loopexit ]
  %773 = add i32 %.2429, 2
  %.not262 = icmp sgt i32 %773, %163
  br i1 %.not262, label %while_loop_body196.preheader.lr.ph, label %while_loop_body184.preheader

after_if188:                                      ; preds = %after_if188, %after_if188.preheader
  %.0164425 = phi i32 [ %791, %after_if188 ], [ %.0164425.ph, %after_if188.preheader ]
  %.1172424 = phi float [ %790, %after_if188 ], [ %.1172424.ph, %after_if188.preheader ]
  %774 = add i32 %50, %.0164425
  %775 = add i32 %702, %.0164425
  %776 = tail call i32 @llvm.smin.i32(i32 %775, i32 %165)
  %777 = tail call i32 @llvm.smax.i32(i32 %776, i32 0)
  %778 = tail call i32 @llvm.smin.i32(i32 %774, i32 %165)
  %779 = tail call i32 @llvm.smax.i32(i32 %778, i32 0)
  %780 = add i32 %753, %777
  %781 = sext i32 %780 to i64
  %782 = getelementptr float, ptr %.pre, i64 %781
  %783 = load float, ptr %782, align 4
  %784 = add i32 %754, %779
  %785 = sext i32 %784 to i64
  %786 = getelementptr float, ptr %.pre460, i64 %785
  %787 = load float, ptr %786, align 4
  %788 = fsub reassoc ninf nsz float %783, %787
  %789 = tail call noundef float @llvm.fabs.f32(float %788)
  %790 = fadd reassoc ninf nsz float %789, %.1172424
  %791 = add i32 %.0164425, 2
  %.not265 = icmp sgt i32 %791, %163
  br i1 %.not265, label %false_block187.loopexit, label %after_if188, !llvm.loop !38

while_loop_body196.preheader:                     ; preds = %false_block199, %while_loop_body196.preheader.lr.ph
  %.3441 = phi i32 [ %neg, %while_loop_body196.preheader.lr.ph ], [ %821, %false_block199 ]
  %.0169440 = phi float [ 0.000000e+00, %while_loop_body196.preheader.lr.ph ], [ %.lcssa676, %false_block199 ]
  %792 = add i32 %.3441, %53
  %.reass444 = add i32 %.3441, %invariant.op443
  %793 = tail call i32 @llvm.smin.i32(i32 %.reass444, i32 %164)
  %794 = tail call i32 @llvm.smax.i32(i32 %793, i32 0)
  %795 = tail call i32 @llvm.smin.i32(i32 %792, i32 %164)
  %796 = tail call i32 @llvm.smax.i32(i32 %795, i32 0)
  %797 = mul i32 %.pre459, %794
  %798 = mul i32 %.pre461, %796
  br i1 %brmerge, label %after_if200.preheader, label %vector.ph

vector.ph:                                        ; preds = %while_loop_body196.preheader
  %799 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0169440, i64 0
  %broadcast.splatinsert682 = insertelement <8 x i32> poison, i32 %797, i64 0
  %broadcast.splat683 = shufflevector <8 x i32> %broadcast.splatinsert682, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert684 = insertelement <8 x i32> poison, i32 %798, i64 0
  %broadcast.splat685 = shufflevector <8 x i32> %broadcast.splatinsert684, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv1252 = phi i32 [ %lsr.iv.next1253, %vector.body ], [ %n.vec1130, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction1135, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ %799, %vector.ph ], [ %814, %vector.body ]
  %800 = add <8 x i32> %vec.ind, %broadcast.splat1140
  %801 = add <8 x i32> %vec.ind, %broadcast.splat710
  %802 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %801, <8 x i32> %broadcast.splat1144)
  %803 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %802, <8 x i32> zeroinitializer)
  %804 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %800, <8 x i32> %broadcast.splat1144)
  %805 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %804, <8 x i32> zeroinitializer)
  %806 = add <8 x i32> %broadcast.splat683, %803
  %807 = sext <8 x i32> %806 to <8 x i64>
  %808 = getelementptr float, ptr %.pre, <8 x i64> %807
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %808, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %809 = add <8 x i32> %broadcast.splat685, %805
  %810 = sext <8 x i32> %809 to <8 x i64>
  %811 = getelementptr float, ptr %.pre460, <8 x i64> %810
  %wide.masked.gather686 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %811, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %812 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather686
  %813 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %812)
  %814 = fadd reassoc ninf nsz <8 x float> %813, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next1253 = add i32 %lsr.iv1252, -8
  %815 = icmp eq i32 %lsr.iv.next1253, 0
  br i1 %815, label %middle.block, label %vector.body, !llvm.loop !39

middle.block:                                     ; preds = %vector.body
  %816 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %814)
  br i1 %cmp.n1152, label %false_block199, label %after_if200.preheader

after_if200.preheader:                            ; preds = %middle.block, %while_loop_body196.preheader
  %.0163437.ph = phi i32 [ %neg, %while_loop_body196.preheader ], [ %185, %middle.block ]
  %.1170436.ph = phi float [ %.0169440, %while_loop_body196.preheader ], [ %816, %middle.block ]
  br label %after_if200

false_block193.loopexit:                          ; preds = %false_block199
  br label %false_block193

false_block193:                                   ; preds = %false_block193.loopexit, %after_if6
  %.0171.lcssa650 = phi float [ 0.000000e+00, %after_if6 ], [ %.lcssa675, %false_block193.loopexit ]
  %.0175.lcssa628634649 = phi float [ 0.000000e+00, %after_if6 ], [ %.lcssa673, %false_block193.loopexit ]
  %.3208616627635648 = phi i32 [ %.0241, %after_if6 ], [ %.3208, %false_block193.loopexit ]
  %.3204617626636647 = phi i32 [ %.0242, %after_if6 ], [ %.3204, %false_block193.loopexit ]
  %.4618625637646 = phi float [ 0.000000e+00, %after_if6 ], [ %.4, %false_block193.loopexit ]
  %.0173.lcssa638645 = phi float [ 0.000000e+00, %after_if6 ], [ %.lcssa674, %false_block193.loopexit ]
  %.0169.lcssa = phi float [ 0.000000e+00, %after_if6 ], [ %.lcssa676, %false_block193.loopexit ]
  %factor279 = fmul reassoc ninf nsz float %.4618625637646, 2.000000e+00
  %817 = fsub reassoc ninf nsz float %.0173.lcssa638645, %factor279
  %818 = fadd reassoc ninf nsz float %817, %.0175.lcssa628634649
  %819 = tail call noundef float @llvm.fabs.f32(float %818)
  %820 = fcmp reassoc ninf nsz ogt float %819, 0x3F1A36E2E0000000
  br i1 %820, label %true_block202, label %after_if204

false_block199.loopexit:                          ; preds = %after_if200
  br label %false_block199

false_block199:                                   ; preds = %false_block199.loopexit, %middle.block
  %.lcssa676 = phi float [ %816, %middle.block ], [ %838, %false_block199.loopexit ]
  %821 = add i32 %.3441, 2
  %.not263 = icmp sgt i32 %821, %163
  br i1 %.not263, label %false_block193.loopexit, label %while_loop_body196.preheader

after_if200:                                      ; preds = %after_if200, %after_if200.preheader
  %.0163437 = phi i32 [ %839, %after_if200 ], [ %.0163437.ph, %after_if200.preheader ]
  %.1170436 = phi float [ %838, %after_if200 ], [ %.1170436.ph, %after_if200.preheader ]
  %822 = add i32 %50, %.0163437
  %823 = add i32 %702, %.0163437
  %824 = tail call i32 @llvm.smin.i32(i32 %823, i32 %165)
  %825 = tail call i32 @llvm.smax.i32(i32 %824, i32 0)
  %826 = tail call i32 @llvm.smin.i32(i32 %822, i32 %165)
  %827 = tail call i32 @llvm.smax.i32(i32 %826, i32 0)
  %828 = add i32 %797, %825
  %829 = sext i32 %828 to i64
  %830 = getelementptr float, ptr %.pre, i64 %829
  %831 = load float, ptr %830, align 4
  %832 = add i32 %798, %827
  %833 = sext i32 %832 to i64
  %834 = getelementptr float, ptr %.pre460, i64 %833
  %835 = load float, ptr %834, align 4
  %836 = fsub reassoc ninf nsz float %831, %835
  %837 = tail call noundef float @llvm.fabs.f32(float %836)
  %838 = fadd reassoc ninf nsz float %837, %.1170436
  %839 = add i32 %.0163437, 2
  %.not264 = icmp sgt i32 %839, %163
  br i1 %.not264, label %false_block199.loopexit, label %after_if200, !llvm.loop !40

true_block202:                                    ; preds = %false_block193
  %840 = fsub reassoc ninf nsz float %.0173.lcssa638645, %.0175.lcssa628634649
  %841 = fmul reassoc ninf nsz float %840, -5.000000e-01
  %842 = fdiv reassoc ninf nsz float %841, %818
  %843 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %842, float 5.000000e-01)
  %844 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %843, float -5.000000e-01)
  br label %after_if204

after_if204:                                      ; preds = %true_block202, %false_block193
  %.0162 = phi float [ %844, %true_block202 ], [ 0.000000e+00, %false_block193 ]
  %845 = fsub reassoc ninf nsz float %.0169.lcssa, %factor279
  %846 = fadd reassoc ninf nsz float %845, %.0171.lcssa650
  %847 = tail call noundef float @llvm.fabs.f32(float %846)
  %848 = fcmp reassoc ninf nsz ogt float %847, 0x3F1A36E2E0000000
  br i1 %848, label %true_block205, label %after_if207

true_block205:                                    ; preds = %after_if204
  %849 = fsub reassoc ninf nsz float %.0169.lcssa, %.0171.lcssa650
  %850 = fmul reassoc ninf nsz float %849, -5.000000e-01
  %851 = fdiv reassoc ninf nsz float %850, %846
  %852 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %851, float 5.000000e-01)
  %853 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %852, float -5.000000e-01)
  br label %after_if207

after_if207:                                      ; preds = %true_block205, %after_if204
  %.0161 = phi float [ %853, %true_block205 ], [ 0.000000e+00, %after_if204 ]
  %854 = sitofp i32 %.3204617626636647 to float
  %855 = fadd reassoc ninf nsz float %.0162, %854
  %856 = sitofp i32 %.3208616627635648 to float
  %857 = fadd reassoc ninf nsz float %.0161, %856
  %858 = shl i32 %163, 1
  %859 = add i32 %163, %23
  %860 = shl i32 %859, 1
  %861 = sitofp i32 %860 to float
  %neg208 = fneg reassoc ninf nsz float %861
  %862 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %861, float %855)
  %863 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg208, float %862)
  %864 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %861, float %857)
  %865 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg208, float %864)
  %866 = ashr exact i32 %858, 1
  %867 = add nsw i32 %866, 1
  %868 = mul i32 %867, %867
  %869 = sitofp i32 %868 to float
  %870 = fdiv reassoc ninf nsz float %.4618625637646, %869
  store float %863, ptr %61, align 4
  store float %865, ptr %70, align 4
  store float 1.000000e+00, ptr %79, align 4
  %871 = fmul reassoc ninf nsz float %863, %863
  %872 = fmul reassoc ninf nsz float %865, %865
  %873 = fadd reassoc ninf nsz float %872, %871
  %874 = fcmp reassoc ninf nsz ogt float %873, %33
  %875 = fcmp reassoc ninf nsz ogt float %870, 1.000000e+01
  %.0159 = select i1 %874, i1 true, i1 %875
  %.0160 = select i1 %.0159, float 1.000000e+00, float 0.000000e+00
  %876 = fcmp reassoc ninf nsz ogt float %873, %34
  %877 = fcmp reassoc ninf nsz ogt float %870, 2.200000e+01
  %.0 = select i1 %876, i1 true, i1 %877
  %.1 = select i1 %.0, float 2.000000e+00, float %.0160
  store float %870, ptr %87, align 4
  store float 1.000000e+00, ptr %96, align 4
  store float %.1, ptr %105, align 4
  store float %873, ptr %114, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.round.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !41

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !43

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
declare i64 @llvm.smax.i64(i64, i64) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #8 = { nounwind }

!llvm.linker.options = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}
!llvm.module.flags = !{!7, !8, !9, !10}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"/alternatename:_Avx2WmemEnabled=_Avx2WmemEnabledWeakValue"}
!6 = !{!"clang version 20.1.5"}
!7 = !{i32 1, !"wchar_size", i32 2}
!8 = !{i32 8, !"PIC Level", i32 2}
!9 = !{i32 7, !"uwtable", i32 2}
!10 = !{i32 1, !"MaxTLSAlign", i32 65536}
!11 = distinct !{!11, !12, !13}
!12 = !{!"llvm.loop.isvectorized", i32 1}
!13 = !{!"llvm.loop.unroll.runtime.disable"}
!14 = distinct !{!14, !12}
!15 = distinct !{!15, !12, !13}
!16 = distinct !{!16, !12}
!17 = distinct !{!17, !12, !13}
!18 = distinct !{!18, !12}
!19 = distinct !{!19, !12, !13}
!20 = distinct !{!20, !12}
!21 = distinct !{!21, !12, !13}
!22 = distinct !{!22, !12}
!23 = distinct !{!23, !12, !13}
!24 = distinct !{!24, !12}
!25 = distinct !{!25, !12, !13}
!26 = distinct !{!26, !12}
!27 = distinct !{!27, !12, !13}
!28 = distinct !{!28, !12}
!29 = distinct !{!29, !12, !13}
!30 = distinct !{!30, !12}
!31 = distinct !{!31, !12, !13}
!32 = distinct !{!32, !12}
!33 = distinct !{!33, !12, !13}
!34 = distinct !{!34, !12}
!35 = distinct !{!35, !12, !13}
!36 = distinct !{!36, !12}
!37 = distinct !{!37, !12, !13}
!38 = distinct !{!38, !12}
!39 = distinct !{!39, !12, !13}
!40 = distinct !{!40, !12}
!41 = distinct !{!41, !42}
!42 = !{!"llvm.loop.mustprogress"}
!43 = distinct !{!43, !42}
