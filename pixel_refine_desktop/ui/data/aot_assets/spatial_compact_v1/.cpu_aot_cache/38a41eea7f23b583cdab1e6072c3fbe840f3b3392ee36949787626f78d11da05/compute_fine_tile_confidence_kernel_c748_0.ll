; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.62 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @compute_fine_tile_confidence_kernel_c748_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 64
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 68
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 4
  store i32 %6, ptr %11, align 4
  %12 = mul i32 %6, %3
  %13 = load ptr, ptr %7, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  store i32 %12, ptr %15, align 4
  ret void
}

define void @compute_fine_tile_confidence_kernel_c748_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #9
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree nounwind memory(readwrite, inaccessiblemem: write)
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
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 120
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 116
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 124
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 88
  %30 = getelementptr i8, ptr %19, i64 104
  %31 = add i32 %27, -1
  %32 = add i32 %23, -1
  %33 = getelementptr i8, ptr %19, i64 72
  %34 = getelementptr i8, ptr %19, i64 68
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.050116 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %89, %after_if3 ]
  %35 = load ptr, ptr %3, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 4
  %39 = load i32, ptr %38, align 4
  %40 = sdiv i32 %.050116, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.050116
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %41, %.050116
  %45 = and i1 %43, %44
  %.neg79 = sext i1 %45 to i32
  %46 = add i32 %40, %.neg79
  %47 = mul i32 %46, %39
  %48 = sub i32 %.050116, %47
  %49 = load ptr, ptr %29, align 8
  %50 = sext i32 %46 to i64
  %51 = getelementptr i32, ptr %49, i64 %50
  %52 = load i32, ptr %51, align 4
  %53 = load ptr, ptr %30, align 8
  %54 = sext i32 %48 to i64
  %55 = getelementptr i32, ptr %53, i64 %54
  %56 = load i32, ptr %55, align 4
  %57 = sub i32 %23, %52
  %58 = tail call i32 @llvm.smin.i32(i32 %21, i32 %57)
  %59 = sub i32 %27, %56
  %60 = tail call i32 @llvm.smin.i32(i32 %25, i32 %59)
  %61 = icmp sgt i32 %58, 0
  %62 = icmp sgt i32 %60, 0
  %spec.select = select i1 %61, i1 %62, i1 false
  br i1 %spec.select, label %true_block1, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %63 = load ptr, ptr %0, align 8
  %64 = getelementptr i8, ptr %63, i64 128
  %65 = load float, ptr %64, align 4
  %66 = getelementptr i8, ptr %63, i64 132
  %67 = load float, ptr %66, align 4
  %68 = getelementptr i8, ptr %63, i64 136
  %69 = load float, ptr %68, align 4
  %70 = getelementptr i8, ptr %63, i64 140
  %71 = load i32, ptr %70, align 4
  %72 = getelementptr i8, ptr %63, i64 144
  %73 = load i32, ptr %72, align 4
  %74 = getelementptr i8, ptr %63, i64 148
  %75 = load float, ptr %74, align 4
  %76 = lshr i32 %60, 1
  %77 = add i32 %76, %56
  %78 = tail call i32 @llvm.smin.i32(i32 %77, i32 %31)
  %79 = lshr i32 %58, 1
  %80 = add i32 %79, %52
  %81 = tail call i32 @llvm.smin.i32(i32 %80, i32 %32)
  %82 = icmp eq i32 %73, 1
  br i1 %82, label %true_block4, label %after_if6

after_if3:                                        ; preds = %after_if65, %after_if9, %for_loop_body
  %.051 = phi float [ 0.000000e+00, %for_loop_body ], [ %spec.store.select2, %after_if65 ], [ 0.000000e+00, %after_if9 ]
  %83 = load ptr, ptr %33, align 8
  %84 = load i32, ptr %34, align 4
  %85 = mul i32 %84, %46
  %86 = add i32 %85, %48
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, ptr %83, i64 %87
  store float %.051, ptr %88, align 4
  %89 = add nsw i32 %.050116, 1
  %exitcond131.not = icmp eq i32 %89, %18
  br i1 %exitcond131.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %90 = getelementptr i8, ptr %63, i64 40
  %91 = load ptr, ptr %90, align 8
  %92 = getelementptr i8, ptr %63, i64 36
  %93 = load i32, ptr %92, align 4
  %94 = mul i32 %93, %81
  %95 = add i32 %94, %78
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %91, i64 %96
  %98 = load float, ptr %97, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.063 = phi float [ %98, %true_block4 ], [ 1.000000e+00, %true_block1 ]
  %99 = icmp eq i32 %71, 1
  br i1 %99, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %100 = getelementptr i8, ptr %63, i64 56
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr i8, ptr %63, i64 52
  %103 = load i32, ptr %102, align 4
  %104 = mul i32 %103, %81
  %105 = add i32 %104, %78
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %101, i64 %106
  %108 = load float, ptr %107, align 4
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.062 = phi float [ %108, %true_block7 ], [ 1.000000e+00, %after_if6 ]
  %109 = fcmp reassoc ninf nsz oge float %.063, %75
  %110 = fcmp reassoc ninf nsz oge float %.062, %75
  %.060 = select i1 %109, i1 %110, i1 false
  br i1 %.060, label %true_block13, label %after_if3

true_block13:                                     ; preds = %after_if9
  %111 = getelementptr i8, ptr %63, i64 24
  %112 = load ptr, ptr %111, align 8
  %113 = getelementptr i8, ptr %63, i64 20
  %114 = load i32, ptr %113, align 4
  %115 = mul i32 %114, %80
  %116 = add i32 %115, %77
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %112, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = mul i32 %114, %52
  %121 = add i32 %120, %56
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %112, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = add nsw i32 %60, -1
  %126 = add i32 %125, %56
  %127 = add i32 %120, %126
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %112, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = add nsw i32 %58, -1
  %132 = add i32 %131, %52
  %133 = mul i32 %114, %132
  %134 = add i32 %133, %56
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %112, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = add i32 %133, %126
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, ptr %112, i64 %139
  %141 = load float, ptr %140, align 4
  %142 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %137, float %141)
  %143 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %130, float %142)
  %144 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float %143)
  %145 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %119, float %144)
  %146 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %137, float %141)
  %147 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %130, float %146)
  %148 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %124, float %147)
  %149 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %119, float %148)
  %150 = fadd reassoc ninf nsz float %124, %119
  %151 = fadd reassoc ninf nsz float %150, %130
  %152 = fadd reassoc ninf nsz float %151, %137
  %153 = fadd reassoc ninf nsz float %152, %141
  %154 = fmul reassoc ninf nsz float %153, 0x3FC99999A0000000
  %155 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %154, float 0x3FA99999A0000000)
  %156 = fmul reassoc ninf nsz float %155, 0x3FBEB851E0000000
  %157 = fmul reassoc ninf nsz float %155, 0x3FB47AE140000000
  %158 = fsub reassoc ninf nsz float %145, %149
  %159 = fadd reassoc ninf nsz float %158, %156
  %160 = fdiv reassoc ninf nsz float %159, %157
  %161 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %160, float 1.000000e+00)
  %162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0.000000e+00)
  %163 = fmul reassoc ninf nsz float %162, 6.075000e+02
  %164 = fadd reassoc ninf nsz float %163, 2.025000e+02
  %165 = fmul reassoc ninf nsz float %65, 0x3FC99999A0000000
  %166 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %165, float 0x3F747AE140000000)
  %167 = fcmp reassoc ninf nsz ogt float %65, 0x3EB0C6F7A0000000
  %168 = lshr i32 %131, 1
  %169 = add i32 %52, 1
  %170 = lshr i32 %125, 1
  %171 = add i32 %56, 1
  %.not = icmp samesign ult i32 %58, 3
  br i1 %.not, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph

for_loop_body16.lr.ph:                            ; preds = %true_block13
  %172 = fadd reassoc ninf nsz float %162, 1.000000e+00
  %173 = fmul reassoc ninf nsz float %65, %65
  %174 = fmul reassoc ninf nsz float %173, 4.000000e+00
  %175 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %174, float 0x3F62E62140000000)
  %.not117 = icmp samesign ult i32 %60, 3
  %176 = fmul reassoc ninf nsz float %172, %175
  br i1 %.not117, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %for_loop_body16.lr.ph
  %177 = getelementptr i8, ptr %63, i64 4
  %178 = getelementptr i8, ptr %63, i64 8
  %179 = load ptr, ptr %178, align 8
  %180 = load i32, ptr %177, align 4
  %wide.trip.count = zext i32 %170 to i64
  %181 = add nsw i64 %wide.trip.count, -1
  %182 = mul i32 %180, %169
  %183 = add i32 %171, %182
  %184 = shl i32 %180, 1
  %185 = mul i32 %114, %169
  %186 = add i32 %171, %185
  %187 = shl i32 %114, 1
  %188 = add i32 %56, 2
  %189 = add i32 %188, %182
  %190 = add i32 %56, %182
  %191 = mul i32 %52, %180
  %192 = add i32 %188, %191
  %193 = add i32 %56, %191
  %194 = add i32 %52, 2
  %195 = mul i32 %180, %194
  %196 = add i32 %188, %195
  %197 = add i32 %56, %195
  %198 = add i32 %171, %195
  %199 = add i32 %171, %191
  %200 = add i32 %188, %185
  %201 = add i32 %56, %185
  %202 = add i32 %188, %120
  %203 = mul i32 %114, %194
  %204 = add i32 %188, %203
  %205 = add i32 %56, %203
  %206 = add i32 %171, %203
  %207 = add i32 %171, %120
  %min.iters.check213 = icmp ult i32 %60, 17
  %208 = trunc nsw i64 %181 to i32
  %mul.result = shl i32 %208, 1
  %invariant.op531 = add i32 %183, %mul.result
  %invariant.op533 = add i32 %186, %mul.result
  %209 = icmp ugt i64 %181, 4294967295
  %invariant.op535 = add i32 %189, %mul.result
  %invariant.op537 = add i32 %190, %mul.result
  %invariant.op539 = add i32 %192, %mul.result
  %invariant.op541 = add i32 %193, %mul.result
  %invariant.op543 = add i32 %196, %mul.result
  %invariant.op545 = add i32 %197, %mul.result
  %invariant.op547 = add i32 %198, %mul.result
  %invariant.op549 = add i32 %199, %mul.result
  %invariant.op551 = add i32 %200, %mul.result
  %invariant.op553 = add i32 %201, %mul.result
  %invariant.op555 = add i32 %202, %mul.result
  %invariant.op557 = add i32 %121, %mul.result
  %invariant.op559 = add i32 %204, %mul.result
  %invariant.op561 = add i32 %205, %mul.result
  %invariant.op563 = add i32 %206, %mul.result
  %invariant.op565 = add i32 %207, %mul.result
  %min.iters.check216 = icmp ult i32 %60, 65
  %n.vec220 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %167, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %210 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert231 = insertelement <8 x i32> poison, i32 %171, i64 0
  %broadcast.splat232 = shufflevector <8 x i32> %broadcast.splatinsert231, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert248 = insertelement <8 x i32> poison, i32 %56, i64 0
  %broadcast.splat249 = shufflevector <8 x i32> %broadcast.splatinsert248, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert318 = insertelement <8 x float> poison, float %166, i64 0
  %broadcast.splat319 = shufflevector <8 x float> %broadcast.splatinsert318, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert320 = insertelement <8 x float> poison, float %176, i64 0
  %broadcast.splat321 = shufflevector <8 x float> %broadcast.splatinsert320, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert337 = insertelement <8 x float> poison, float %164, i64 0
  %broadcast.splat338 = shufflevector <8 x float> %broadcast.splatinsert337, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat232
  %invariant.op521 = add <8 x i32> splat (i32 32), %broadcast.splat232
  %invariant.op523 = add <8 x i32> splat (i32 48), %broadcast.splat232
  %invariant.op525 = add <8 x i32> splat (i32 16), %broadcast.splat249
  %invariant.op527 = add <8 x i32> splat (i32 32), %broadcast.splat249
  %invariant.op529 = add <8 x i32> splat (i32 48), %broadcast.splat249
  %cmp.n386 = icmp eq i64 %n.vec220, %wide.trip.count
  %n.vec.remaining394 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check395 = icmp eq i64 %n.vec.remaining394, 0
  %n.vec397 = and i64 %wide.trip.count, 2147483640
  %cmp.n461 = icmp eq i64 %n.vec397, %wide.trip.count
  %211 = zext i32 %125 to i64
  %212 = lshr i64 %211, 4
  %213 = mul nsw i64 %212, -8
  %214 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check215

iter.check215:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %lsr.iv599 = phi i32 [ %lsr.iv.next600, %for_loop_test23.after_for22_crit_edge.us ], [ %190, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv595 = phi i32 [ %lsr.iv.next596, %for_loop_test23.after_for22_crit_edge.us ], [ %201, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv591 = phi i32 [ %lsr.iv.next592, %for_loop_test23.after_for22_crit_edge.us ], [ %197, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv587 = phi i32 [ %lsr.iv.next588, %for_loop_test23.after_for22_crit_edge.us ], [ %193, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv583 = phi i32 [ %lsr.iv.next584, %for_loop_test23.after_for22_crit_edge.us ], [ %205, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv579 = phi i32 [ %lsr.iv.next580, %for_loop_test23.after_for22_crit_edge.us ], [ %121, %for_loop_body16.lr.ph.split.us ]
  %.055103.us = phi i32 [ 0, %for_loop_body16.lr.ph.split.us ], [ %1330, %for_loop_test23.after_for22_crit_edge.us ]
  %.056102.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ]
  %.058101.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa136, %for_loop_test23.after_for22_crit_edge.us ]
  %215 = shl nuw i32 %.055103.us, 1
  %216 = add i32 %169, %215
  %217 = add i32 %215, %52
  %218 = add i32 %216, 1
  %219 = mul i32 %180, %216
  %220 = mul i32 %216, %114
  %221 = mul i32 %180, %217
  %222 = mul i32 %180, %218
  %223 = mul i32 %217, %114
  %224 = mul i32 %218, %114
  br i1 %min.iters.check213, label %for_loop_body20.us.preheader, label %vector.scevcheck160

vector.scevcheck160:                              ; preds = %iter.check215
  %225 = mul i32 %187, %.055103.us
  %226 = add i32 %207, %225
  %227 = add i32 %206, %225
  %228 = add i32 %205, %225
  %229 = add i32 %204, %225
  %230 = add i32 %121, %225
  %231 = add i32 %202, %225
  %232 = add i32 %201, %225
  %233 = add i32 %200, %225
  %234 = mul i32 %184, %.055103.us
  %235 = add i32 %199, %234
  %236 = add i32 %198, %234
  %237 = add i32 %197, %234
  %238 = add i32 %196, %234
  %239 = add i32 %193, %234
  %240 = add i32 %192, %234
  %241 = add i32 %190, %234
  %242 = add i32 %189, %234
  %243 = add i32 %186, %225
  %244 = add i32 %183, %234
  %.reass532 = add i32 %234, %invariant.op531
  %245 = icmp slt i32 %.reass532, %244
  %.reass534 = add i32 %225, %invariant.op533
  %246 = icmp slt i32 %.reass534, %243
  %247 = or i1 %246, %209
  %.reass536 = add i32 %234, %invariant.op535
  %248 = icmp slt i32 %.reass536, %242
  %.reass538 = add i32 %234, %invariant.op537
  %249 = icmp slt i32 %.reass538, %241
  %.reass540 = add i32 %234, %invariant.op539
  %250 = icmp slt i32 %.reass540, %240
  %.reass542 = add i32 %234, %invariant.op541
  %251 = icmp slt i32 %.reass542, %239
  %.reass544 = add i32 %234, %invariant.op543
  %252 = icmp slt i32 %.reass544, %238
  %.reass546 = add i32 %234, %invariant.op545
  %253 = icmp slt i32 %.reass546, %237
  %.reass548 = add i32 %234, %invariant.op547
  %254 = icmp slt i32 %.reass548, %236
  %.reass550 = add i32 %234, %invariant.op549
  %255 = icmp slt i32 %.reass550, %235
  %256 = or i1 %255, %209
  %.reass552 = add i32 %225, %invariant.op551
  %257 = icmp slt i32 %.reass552, %233
  %.reass554 = add i32 %225, %invariant.op553
  %258 = icmp slt i32 %.reass554, %232
  %.reass556 = add i32 %225, %invariant.op555
  %259 = icmp slt i32 %.reass556, %231
  %.reass558 = add i32 %225, %invariant.op557
  %260 = icmp slt i32 %.reass558, %230
  %.reass560 = add i32 %225, %invariant.op559
  %261 = icmp slt i32 %.reass560, %229
  %.reass562 = add i32 %225, %invariant.op561
  %262 = icmp slt i32 %.reass562, %228
  %.reass564 = add i32 %225, %invariant.op563
  %263 = icmp slt i32 %.reass564, %227
  %.reass566 = add i32 %225, %invariant.op565
  %264 = icmp slt i32 %.reass566, %226
  %265 = or i1 %264, %209
  %266 = or i1 %245, %247
  %267 = or i1 %248, %266
  %268 = or i1 %249, %267
  %269 = or i1 %250, %268
  %270 = or i1 %251, %269
  %271 = or i1 %252, %270
  %272 = or i1 %253, %271
  %273 = or i1 %254, %272
  %274 = or i1 %273, %256
  %275 = or i1 %257, %274
  %276 = or i1 %258, %275
  %277 = or i1 %259, %276
  %278 = or i1 %260, %277
  %279 = or i1 %261, %278
  %280 = or i1 %262, %279
  %281 = or i1 %263, %280
  %282 = or i1 %281, %265
  br i1 %282, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check217

vector.main.loop.iter.check217:                   ; preds = %vector.scevcheck160
  br i1 %min.iters.check216, label %vec.epilog.ph392, label %vector.ph218

vector.ph218:                                     ; preds = %vector.main.loop.iter.check217
  %283 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.056102.us, i64 0
  %284 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.058101.us, i64 0
  %broadcast.splatinsert233 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat234 = shufflevector <8 x i32> %broadcast.splatinsert233, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert238 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat239 = shufflevector <8 x i32> %broadcast.splatinsert238, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert254 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat255 = shufflevector <8 x i32> %broadcast.splatinsert254, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert264 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat265 = shufflevector <8 x i32> %broadcast.splatinsert264, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert290 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat291 = shufflevector <8 x i32> %broadcast.splatinsert290, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert300 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat301 = shufflevector <8 x i32> %broadcast.splatinsert300, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body221

vector.body221:                                   ; preds = %vector.body221, %vector.ph218
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body221 ], [ %n.vec220, %vector.ph218 ]
  %vec.phi223 = phi <8 x float> [ %283, %vector.ph218 ], [ %976, %vector.body221 ]
  %vec.phi224 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %977, %vector.body221 ]
  %vec.phi225 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %978, %vector.body221 ]
  %vec.phi226 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %979, %vector.body221 ]
  %vec.phi227 = phi <8 x float> [ %284, %vector.ph218 ], [ %972, %vector.body221 ]
  %vec.phi228 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %973, %vector.body221 ]
  %vec.phi229 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %974, %vector.body221 ]
  %vec.phi230 = phi <8 x float> [ zeroinitializer, %vector.ph218 ], [ %975, %vector.body221 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph218 ], [ %vec.ind.next, %vector.body221 ]
  %285 = shl <8 x i32> %vec.ind, splat (i32 1)
  %286 = add <8 x i32> %broadcast.splat232, %285
  %.reass = add <8 x i32> %285, %invariant.op
  %.reass522 = add <8 x i32> %285, %invariant.op521
  %.reass524 = add <8 x i32> %285, %invariant.op523
  %287 = add <8 x i32> %broadcast.splat234, %286
  %288 = add <8 x i32> %broadcast.splat234, %.reass
  %289 = add <8 x i32> %broadcast.splat234, %.reass522
  %290 = add <8 x i32> %broadcast.splat234, %.reass524
  %291 = sext <8 x i32> %287 to <8 x i64>
  %292 = sext <8 x i32> %288 to <8 x i64>
  %293 = sext <8 x i32> %289 to <8 x i64>
  %294 = sext <8 x i32> %290 to <8 x i64>
  %295 = getelementptr float, ptr %179, <8 x i64> %291
  %296 = getelementptr float, ptr %179, <8 x i64> %292
  %297 = getelementptr float, ptr %179, <8 x i64> %293
  %298 = getelementptr float, ptr %179, <8 x i64> %294
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %295, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather235 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %296, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather236 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %297, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather237 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %298, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %299 = add <8 x i32> %286, %broadcast.splat239
  %300 = add <8 x i32> %.reass, %broadcast.splat239
  %301 = add <8 x i32> %.reass522, %broadcast.splat239
  %302 = add <8 x i32> %.reass524, %broadcast.splat239
  %303 = sext <8 x i32> %299 to <8 x i64>
  %304 = sext <8 x i32> %300 to <8 x i64>
  %305 = sext <8 x i32> %301 to <8 x i64>
  %306 = sext <8 x i32> %302 to <8 x i64>
  %307 = getelementptr float, ptr %112, <8 x i64> %303
  %308 = getelementptr float, ptr %112, <8 x i64> %304
  %309 = getelementptr float, ptr %112, <8 x i64> %305
  %310 = getelementptr float, ptr %112, <8 x i64> %306
  %wide.masked.gather240 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %307, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather241 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %308, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather242 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %309, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather243 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %310, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %311 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather240
  %312 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather235, %wide.masked.gather241
  %313 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather236, %wide.masked.gather242
  %314 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather237, %wide.masked.gather243
  %315 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %311)
  %316 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %312)
  %317 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %313)
  %318 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %314)
  %319 = add <8 x i32> %286, splat (i32 1)
  %320 = add <8 x i32> %.reass, splat (i32 1)
  %321 = add <8 x i32> %.reass522, splat (i32 1)
  %322 = add <8 x i32> %.reass524, splat (i32 1)
  %323 = add <8 x i32> %broadcast.splat234, %319
  %324 = add <8 x i32> %broadcast.splat234, %320
  %325 = add <8 x i32> %broadcast.splat234, %321
  %326 = add <8 x i32> %broadcast.splat234, %322
  %327 = sext <8 x i32> %323 to <8 x i64>
  %328 = sext <8 x i32> %324 to <8 x i64>
  %329 = sext <8 x i32> %325 to <8 x i64>
  %330 = sext <8 x i32> %326 to <8 x i64>
  %331 = getelementptr float, ptr %179, <8 x i64> %327
  %332 = getelementptr float, ptr %179, <8 x i64> %328
  %333 = getelementptr float, ptr %179, <8 x i64> %329
  %334 = getelementptr float, ptr %179, <8 x i64> %330
  %wide.masked.gather244 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %331, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather245 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %332, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather246 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %333, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather247 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %334, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %335 = add <8 x i32> %285, %broadcast.splat249
  %.reass526 = add <8 x i32> %285, %invariant.op525
  %.reass528 = add <8 x i32> %285, %invariant.op527
  %.reass530 = add <8 x i32> %285, %invariant.op529
  %336 = add <8 x i32> %broadcast.splat234, %335
  %337 = add <8 x i32> %broadcast.splat234, %.reass526
  %338 = add <8 x i32> %broadcast.splat234, %.reass528
  %339 = add <8 x i32> %broadcast.splat234, %.reass530
  %340 = sext <8 x i32> %336 to <8 x i64>
  %341 = sext <8 x i32> %337 to <8 x i64>
  %342 = sext <8 x i32> %338 to <8 x i64>
  %343 = sext <8 x i32> %339 to <8 x i64>
  %344 = getelementptr float, ptr %179, <8 x i64> %340
  %345 = getelementptr float, ptr %179, <8 x i64> %341
  %346 = getelementptr float, ptr %179, <8 x i64> %342
  %347 = getelementptr float, ptr %179, <8 x i64> %343
  %wide.masked.gather250 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %344, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather251 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %345, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather252 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %346, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather253 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %347, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %348 = add <8 x i32> %broadcast.splat255, %319
  %349 = add <8 x i32> %broadcast.splat255, %320
  %350 = add <8 x i32> %broadcast.splat255, %321
  %351 = add <8 x i32> %broadcast.splat255, %322
  %352 = sext <8 x i32> %348 to <8 x i64>
  %353 = sext <8 x i32> %349 to <8 x i64>
  %354 = sext <8 x i32> %350 to <8 x i64>
  %355 = sext <8 x i32> %351 to <8 x i64>
  %356 = getelementptr float, ptr %179, <8 x i64> %352
  %357 = getelementptr float, ptr %179, <8 x i64> %353
  %358 = getelementptr float, ptr %179, <8 x i64> %354
  %359 = getelementptr float, ptr %179, <8 x i64> %355
  %wide.masked.gather256 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %356, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather257 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %357, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather258 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %358, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather259 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %359, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %360 = add <8 x i32> %broadcast.splat255, %335
  %361 = add <8 x i32> %broadcast.splat255, %.reass526
  %362 = add <8 x i32> %broadcast.splat255, %.reass528
  %363 = add <8 x i32> %broadcast.splat255, %.reass530
  %364 = sext <8 x i32> %360 to <8 x i64>
  %365 = sext <8 x i32> %361 to <8 x i64>
  %366 = sext <8 x i32> %362 to <8 x i64>
  %367 = sext <8 x i32> %363 to <8 x i64>
  %368 = getelementptr float, ptr %179, <8 x i64> %364
  %369 = getelementptr float, ptr %179, <8 x i64> %365
  %370 = getelementptr float, ptr %179, <8 x i64> %366
  %371 = getelementptr float, ptr %179, <8 x i64> %367
  %wide.masked.gather260 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %368, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather261 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %369, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather262 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %370, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather263 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %371, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %372 = add <8 x i32> %broadcast.splat265, %319
  %373 = add <8 x i32> %broadcast.splat265, %320
  %374 = add <8 x i32> %broadcast.splat265, %321
  %375 = add <8 x i32> %broadcast.splat265, %322
  %376 = sext <8 x i32> %372 to <8 x i64>
  %377 = sext <8 x i32> %373 to <8 x i64>
  %378 = sext <8 x i32> %374 to <8 x i64>
  %379 = sext <8 x i32> %375 to <8 x i64>
  %380 = getelementptr float, ptr %179, <8 x i64> %376
  %381 = getelementptr float, ptr %179, <8 x i64> %377
  %382 = getelementptr float, ptr %179, <8 x i64> %378
  %383 = getelementptr float, ptr %179, <8 x i64> %379
  %wide.masked.gather266 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %380, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather267 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %381, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather268 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %382, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather269 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %383, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %384 = add <8 x i32> %broadcast.splat265, %335
  %385 = add <8 x i32> %broadcast.splat265, %.reass526
  %386 = add <8 x i32> %broadcast.splat265, %.reass528
  %387 = add <8 x i32> %broadcast.splat265, %.reass530
  %388 = sext <8 x i32> %384 to <8 x i64>
  %389 = sext <8 x i32> %385 to <8 x i64>
  %390 = sext <8 x i32> %386 to <8 x i64>
  %391 = sext <8 x i32> %387 to <8 x i64>
  %392 = getelementptr float, ptr %179, <8 x i64> %388
  %393 = getelementptr float, ptr %179, <8 x i64> %389
  %394 = getelementptr float, ptr %179, <8 x i64> %390
  %395 = getelementptr float, ptr %179, <8 x i64> %391
  %wide.masked.gather270 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %392, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather271 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %393, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather272 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %394, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather273 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %395, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %396 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather244, %wide.masked.gather256
  %397 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather245, %wide.masked.gather257
  %398 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather246, %wide.masked.gather258
  %399 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather247, %wide.masked.gather259
  %400 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather250, %wide.masked.gather260
  %401 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather251, %wide.masked.gather261
  %402 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather252, %wide.masked.gather262
  %403 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather253, %wide.masked.gather263
  %404 = fadd reassoc ninf nsz <8 x float> %396, %wide.masked.gather266
  %405 = fadd reassoc ninf nsz <8 x float> %397, %wide.masked.gather267
  %406 = fadd reassoc ninf nsz <8 x float> %398, %wide.masked.gather268
  %407 = fadd reassoc ninf nsz <8 x float> %399, %wide.masked.gather269
  %408 = fadd reassoc ninf nsz <8 x float> %400, %wide.masked.gather270
  %409 = fadd reassoc ninf nsz <8 x float> %401, %wide.masked.gather271
  %410 = fadd reassoc ninf nsz <8 x float> %402, %wide.masked.gather272
  %411 = fadd reassoc ninf nsz <8 x float> %403, %wide.masked.gather273
  %412 = fsub reassoc ninf nsz <8 x float> %404, %408
  %413 = fsub reassoc ninf nsz <8 x float> %405, %409
  %414 = fsub reassoc ninf nsz <8 x float> %406, %410
  %415 = fsub reassoc ninf nsz <8 x float> %407, %411
  %416 = fmul reassoc ninf nsz <8 x float> %412, splat (float 0x3FD5555560000000)
  %417 = fmul reassoc ninf nsz <8 x float> %413, splat (float 0x3FD5555560000000)
  %418 = fmul reassoc ninf nsz <8 x float> %414, splat (float 0x3FD5555560000000)
  %419 = fmul reassoc ninf nsz <8 x float> %415, splat (float 0x3FD5555560000000)
  %420 = add <8 x i32> %broadcast.splat265, %286
  %421 = add <8 x i32> %broadcast.splat265, %.reass
  %422 = add <8 x i32> %broadcast.splat265, %.reass522
  %423 = add <8 x i32> %broadcast.splat265, %.reass524
  %424 = sext <8 x i32> %420 to <8 x i64>
  %425 = sext <8 x i32> %421 to <8 x i64>
  %426 = sext <8 x i32> %422 to <8 x i64>
  %427 = sext <8 x i32> %423 to <8 x i64>
  %428 = getelementptr float, ptr %179, <8 x i64> %424
  %429 = getelementptr float, ptr %179, <8 x i64> %425
  %430 = getelementptr float, ptr %179, <8 x i64> %426
  %431 = getelementptr float, ptr %179, <8 x i64> %427
  %wide.masked.gather274 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %428, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather275 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %429, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather276 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %430, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather277 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %431, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %432 = add <8 x i32> %broadcast.splat255, %286
  %433 = add <8 x i32> %broadcast.splat255, %.reass
  %434 = add <8 x i32> %broadcast.splat255, %.reass522
  %435 = add <8 x i32> %broadcast.splat255, %.reass524
  %436 = sext <8 x i32> %432 to <8 x i64>
  %437 = sext <8 x i32> %433 to <8 x i64>
  %438 = sext <8 x i32> %434 to <8 x i64>
  %439 = sext <8 x i32> %435 to <8 x i64>
  %440 = getelementptr float, ptr %179, <8 x i64> %436
  %441 = getelementptr float, ptr %179, <8 x i64> %437
  %442 = getelementptr float, ptr %179, <8 x i64> %438
  %443 = getelementptr float, ptr %179, <8 x i64> %439
  %wide.masked.gather278 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %440, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather279 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %441, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather280 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %442, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather281 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %443, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %444 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather256, %wide.masked.gather260
  %445 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather257, %wide.masked.gather261
  %446 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather258, %wide.masked.gather262
  %447 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather259, %wide.masked.gather263
  %448 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather266, %444
  %449 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather267, %445
  %450 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather268, %446
  %451 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather269, %447
  %452 = fadd reassoc ninf nsz <8 x float> %448, %wide.masked.gather270
  %453 = fadd reassoc ninf nsz <8 x float> %449, %wide.masked.gather271
  %454 = fadd reassoc ninf nsz <8 x float> %450, %wide.masked.gather272
  %455 = fadd reassoc ninf nsz <8 x float> %451, %wide.masked.gather273
  %456 = fadd reassoc ninf nsz <8 x float> %452, %wide.masked.gather274
  %457 = fadd reassoc ninf nsz <8 x float> %453, %wide.masked.gather275
  %458 = fadd reassoc ninf nsz <8 x float> %454, %wide.masked.gather276
  %459 = fadd reassoc ninf nsz <8 x float> %455, %wide.masked.gather277
  %460 = fsub reassoc ninf nsz <8 x float> %456, %wide.masked.gather278
  %461 = fsub reassoc ninf nsz <8 x float> %457, %wide.masked.gather279
  %462 = fsub reassoc ninf nsz <8 x float> %458, %wide.masked.gather280
  %463 = fsub reassoc ninf nsz <8 x float> %459, %wide.masked.gather281
  %464 = fmul reassoc ninf nsz <8 x float> %460, splat (float 0x3FD5555560000000)
  %465 = fmul reassoc ninf nsz <8 x float> %461, splat (float 0x3FD5555560000000)
  %466 = fmul reassoc ninf nsz <8 x float> %462, splat (float 0x3FD5555560000000)
  %467 = fmul reassoc ninf nsz <8 x float> %463, splat (float 0x3FD5555560000000)
  %468 = add <8 x i32> %319, %broadcast.splat239
  %469 = add <8 x i32> %320, %broadcast.splat239
  %470 = add <8 x i32> %321, %broadcast.splat239
  %471 = add <8 x i32> %322, %broadcast.splat239
  %472 = sext <8 x i32> %468 to <8 x i64>
  %473 = sext <8 x i32> %469 to <8 x i64>
  %474 = sext <8 x i32> %470 to <8 x i64>
  %475 = sext <8 x i32> %471 to <8 x i64>
  %476 = getelementptr float, ptr %112, <8 x i64> %472
  %477 = getelementptr float, ptr %112, <8 x i64> %473
  %478 = getelementptr float, ptr %112, <8 x i64> %474
  %479 = getelementptr float, ptr %112, <8 x i64> %475
  %wide.masked.gather282 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %476, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather283 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %477, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather284 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %478, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather285 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %479, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %480 = add <8 x i32> %335, %broadcast.splat239
  %481 = add <8 x i32> %.reass526, %broadcast.splat239
  %482 = add <8 x i32> %.reass528, %broadcast.splat239
  %483 = add <8 x i32> %.reass530, %broadcast.splat239
  %484 = sext <8 x i32> %480 to <8 x i64>
  %485 = sext <8 x i32> %481 to <8 x i64>
  %486 = sext <8 x i32> %482 to <8 x i64>
  %487 = sext <8 x i32> %483 to <8 x i64>
  %488 = getelementptr float, ptr %112, <8 x i64> %484
  %489 = getelementptr float, ptr %112, <8 x i64> %485
  %490 = getelementptr float, ptr %112, <8 x i64> %486
  %491 = getelementptr float, ptr %112, <8 x i64> %487
  %wide.masked.gather286 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %488, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather287 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %489, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather288 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %490, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather289 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %491, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %492 = add <8 x i32> %319, %broadcast.splat291
  %493 = add <8 x i32> %320, %broadcast.splat291
  %494 = add <8 x i32> %321, %broadcast.splat291
  %495 = add <8 x i32> %322, %broadcast.splat291
  %496 = sext <8 x i32> %492 to <8 x i64>
  %497 = sext <8 x i32> %493 to <8 x i64>
  %498 = sext <8 x i32> %494 to <8 x i64>
  %499 = sext <8 x i32> %495 to <8 x i64>
  %500 = getelementptr float, ptr %112, <8 x i64> %496
  %501 = getelementptr float, ptr %112, <8 x i64> %497
  %502 = getelementptr float, ptr %112, <8 x i64> %498
  %503 = getelementptr float, ptr %112, <8 x i64> %499
  %wide.masked.gather292 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %500, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather293 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %501, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather294 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %502, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather295 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %503, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %504 = add <8 x i32> %335, %broadcast.splat291
  %505 = add <8 x i32> %.reass526, %broadcast.splat291
  %506 = add <8 x i32> %.reass528, %broadcast.splat291
  %507 = add <8 x i32> %.reass530, %broadcast.splat291
  %508 = sext <8 x i32> %504 to <8 x i64>
  %509 = sext <8 x i32> %505 to <8 x i64>
  %510 = sext <8 x i32> %506 to <8 x i64>
  %511 = sext <8 x i32> %507 to <8 x i64>
  %512 = getelementptr float, ptr %112, <8 x i64> %508
  %513 = getelementptr float, ptr %112, <8 x i64> %509
  %514 = getelementptr float, ptr %112, <8 x i64> %510
  %515 = getelementptr float, ptr %112, <8 x i64> %511
  %wide.masked.gather296 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %512, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather297 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %513, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather298 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %514, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather299 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %515, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %516 = add <8 x i32> %319, %broadcast.splat301
  %517 = add <8 x i32> %320, %broadcast.splat301
  %518 = add <8 x i32> %321, %broadcast.splat301
  %519 = add <8 x i32> %322, %broadcast.splat301
  %520 = sext <8 x i32> %516 to <8 x i64>
  %521 = sext <8 x i32> %517 to <8 x i64>
  %522 = sext <8 x i32> %518 to <8 x i64>
  %523 = sext <8 x i32> %519 to <8 x i64>
  %524 = getelementptr float, ptr %112, <8 x i64> %520
  %525 = getelementptr float, ptr %112, <8 x i64> %521
  %526 = getelementptr float, ptr %112, <8 x i64> %522
  %527 = getelementptr float, ptr %112, <8 x i64> %523
  %wide.masked.gather302 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %524, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather303 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %525, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather304 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %526, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather305 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %527, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %528 = add <8 x i32> %335, %broadcast.splat301
  %529 = add <8 x i32> %.reass526, %broadcast.splat301
  %530 = add <8 x i32> %.reass528, %broadcast.splat301
  %531 = add <8 x i32> %.reass530, %broadcast.splat301
  %532 = sext <8 x i32> %528 to <8 x i64>
  %533 = sext <8 x i32> %529 to <8 x i64>
  %534 = sext <8 x i32> %530 to <8 x i64>
  %535 = sext <8 x i32> %531 to <8 x i64>
  %536 = getelementptr float, ptr %112, <8 x i64> %532
  %537 = getelementptr float, ptr %112, <8 x i64> %533
  %538 = getelementptr float, ptr %112, <8 x i64> %534
  %539 = getelementptr float, ptr %112, <8 x i64> %535
  %wide.masked.gather306 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %536, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather307 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %537, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather308 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %538, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather309 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %539, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %540 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather282, %wide.masked.gather292
  %541 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather283, %wide.masked.gather293
  %542 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather284, %wide.masked.gather294
  %543 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather285, %wide.masked.gather295
  %544 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather286, %wide.masked.gather296
  %545 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather287, %wide.masked.gather297
  %546 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather288, %wide.masked.gather298
  %547 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather289, %wide.masked.gather299
  %548 = fadd reassoc ninf nsz <8 x float> %540, %wide.masked.gather302
  %549 = fadd reassoc ninf nsz <8 x float> %541, %wide.masked.gather303
  %550 = fadd reassoc ninf nsz <8 x float> %542, %wide.masked.gather304
  %551 = fadd reassoc ninf nsz <8 x float> %543, %wide.masked.gather305
  %552 = fadd reassoc ninf nsz <8 x float> %544, %wide.masked.gather306
  %553 = fadd reassoc ninf nsz <8 x float> %545, %wide.masked.gather307
  %554 = fadd reassoc ninf nsz <8 x float> %546, %wide.masked.gather308
  %555 = fadd reassoc ninf nsz <8 x float> %547, %wide.masked.gather309
  %556 = fsub reassoc ninf nsz <8 x float> %548, %552
  %557 = fsub reassoc ninf nsz <8 x float> %549, %553
  %558 = fsub reassoc ninf nsz <8 x float> %550, %554
  %559 = fsub reassoc ninf nsz <8 x float> %551, %555
  %560 = fmul reassoc ninf nsz <8 x float> %556, splat (float 0x3FD5555560000000)
  %561 = fmul reassoc ninf nsz <8 x float> %557, splat (float 0x3FD5555560000000)
  %562 = fmul reassoc ninf nsz <8 x float> %558, splat (float 0x3FD5555560000000)
  %563 = fmul reassoc ninf nsz <8 x float> %559, splat (float 0x3FD5555560000000)
  %564 = add <8 x i32> %286, %broadcast.splat301
  %565 = add <8 x i32> %.reass, %broadcast.splat301
  %566 = add <8 x i32> %.reass522, %broadcast.splat301
  %567 = add <8 x i32> %.reass524, %broadcast.splat301
  %568 = sext <8 x i32> %564 to <8 x i64>
  %569 = sext <8 x i32> %565 to <8 x i64>
  %570 = sext <8 x i32> %566 to <8 x i64>
  %571 = sext <8 x i32> %567 to <8 x i64>
  %572 = getelementptr float, ptr %112, <8 x i64> %568
  %573 = getelementptr float, ptr %112, <8 x i64> %569
  %574 = getelementptr float, ptr %112, <8 x i64> %570
  %575 = getelementptr float, ptr %112, <8 x i64> %571
  %wide.masked.gather310 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %572, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather311 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %573, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather312 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %574, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather313 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %575, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %576 = add <8 x i32> %286, %broadcast.splat291
  %577 = add <8 x i32> %.reass, %broadcast.splat291
  %578 = add <8 x i32> %.reass522, %broadcast.splat291
  %579 = add <8 x i32> %.reass524, %broadcast.splat291
  %580 = sext <8 x i32> %576 to <8 x i64>
  %581 = sext <8 x i32> %577 to <8 x i64>
  %582 = sext <8 x i32> %578 to <8 x i64>
  %583 = sext <8 x i32> %579 to <8 x i64>
  %584 = getelementptr float, ptr %112, <8 x i64> %580
  %585 = getelementptr float, ptr %112, <8 x i64> %581
  %586 = getelementptr float, ptr %112, <8 x i64> %582
  %587 = getelementptr float, ptr %112, <8 x i64> %583
  %wide.masked.gather314 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %584, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather315 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %585, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather316 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %586, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather317 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %587, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %588 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather292, %wide.masked.gather296
  %589 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather293, %wide.masked.gather297
  %590 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather294, %wide.masked.gather298
  %591 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather295, %wide.masked.gather299
  %592 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather302, %588
  %593 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather303, %589
  %594 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather304, %590
  %595 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather305, %591
  %596 = fadd reassoc ninf nsz <8 x float> %592, %wide.masked.gather306
  %597 = fadd reassoc ninf nsz <8 x float> %593, %wide.masked.gather307
  %598 = fadd reassoc ninf nsz <8 x float> %594, %wide.masked.gather308
  %599 = fadd reassoc ninf nsz <8 x float> %595, %wide.masked.gather309
  %600 = fadd reassoc ninf nsz <8 x float> %596, %wide.masked.gather310
  %601 = fadd reassoc ninf nsz <8 x float> %597, %wide.masked.gather311
  %602 = fadd reassoc ninf nsz <8 x float> %598, %wide.masked.gather312
  %603 = fadd reassoc ninf nsz <8 x float> %599, %wide.masked.gather313
  %604 = fsub reassoc ninf nsz <8 x float> %600, %wide.masked.gather314
  %605 = fsub reassoc ninf nsz <8 x float> %601, %wide.masked.gather315
  %606 = fsub reassoc ninf nsz <8 x float> %602, %wide.masked.gather316
  %607 = fsub reassoc ninf nsz <8 x float> %603, %wide.masked.gather317
  %608 = fmul reassoc ninf nsz <8 x float> %604, splat (float 0x3FD5555560000000)
  %609 = fmul reassoc ninf nsz <8 x float> %605, splat (float 0x3FD5555560000000)
  %610 = fmul reassoc ninf nsz <8 x float> %606, splat (float 0x3FD5555560000000)
  %611 = fmul reassoc ninf nsz <8 x float> %607, splat (float 0x3FD5555560000000)
  %612 = fmul reassoc ninf nsz <8 x float> %416, %416
  %613 = fmul reassoc ninf nsz <8 x float> %417, %417
  %614 = fmul reassoc ninf nsz <8 x float> %418, %418
  %615 = fmul reassoc ninf nsz <8 x float> %419, %419
  %616 = fmul reassoc ninf nsz <8 x float> %464, %464
  %617 = fmul reassoc ninf nsz <8 x float> %465, %465
  %618 = fmul reassoc ninf nsz <8 x float> %466, %466
  %619 = fmul reassoc ninf nsz <8 x float> %467, %467
  %620 = fadd reassoc ninf nsz <8 x float> %616, %612
  %621 = fadd reassoc ninf nsz <8 x float> %617, %613
  %622 = fadd reassoc ninf nsz <8 x float> %618, %614
  %623 = fadd reassoc ninf nsz <8 x float> %619, %615
  %624 = fmul reassoc ninf nsz <8 x float> %560, %560
  %625 = fmul reassoc ninf nsz <8 x float> %561, %561
  %626 = fmul reassoc ninf nsz <8 x float> %562, %562
  %627 = fmul reassoc ninf nsz <8 x float> %563, %563
  %628 = fmul reassoc ninf nsz <8 x float> %608, %608
  %629 = fmul reassoc ninf nsz <8 x float> %609, %609
  %630 = fmul reassoc ninf nsz <8 x float> %610, %610
  %631 = fmul reassoc ninf nsz <8 x float> %611, %611
  %632 = fadd reassoc ninf nsz <8 x float> %628, %624
  %633 = fadd reassoc ninf nsz <8 x float> %629, %625
  %634 = fadd reassoc ninf nsz <8 x float> %630, %626
  %635 = fadd reassoc ninf nsz <8 x float> %631, %627
  %636 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %620, <8 x float> %632)
  %637 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %621, <8 x float> %633)
  %638 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %622, <8 x float> %634)
  %639 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %623, <8 x float> %635)
  %640 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather240, splat (float -2.000000e+00)
  %641 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather241, splat (float -2.000000e+00)
  %642 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather242, splat (float -2.000000e+00)
  %643 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather243, splat (float -2.000000e+00)
  %644 = fadd reassoc ninf nsz <8 x float> %640, splat (float 3.000000e+00)
  %645 = fadd reassoc ninf nsz <8 x float> %641, splat (float 3.000000e+00)
  %646 = fadd reassoc ninf nsz <8 x float> %642, splat (float 3.000000e+00)
  %647 = fadd reassoc ninf nsz <8 x float> %643, splat (float 3.000000e+00)
  %648 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %644, <8 x float> splat (float 3.000000e+00))
  %649 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %645, <8 x float> splat (float 3.000000e+00))
  %650 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %646, <8 x float> splat (float 3.000000e+00))
  %651 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %647, <8 x float> splat (float 3.000000e+00))
  %652 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %648, <8 x float> splat (float 1.000000e+00))
  %653 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %649, <8 x float> splat (float 1.000000e+00))
  %654 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %650, <8 x float> splat (float 1.000000e+00))
  %655 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %651, <8 x float> splat (float 1.000000e+00))
  %656 = fmul reassoc ninf nsz <8 x float> %652, %broadcast.splat319
  %657 = fmul reassoc ninf nsz <8 x float> %653, %broadcast.splat319
  %658 = fmul reassoc ninf nsz <8 x float> %654, %broadcast.splat319
  %659 = fmul reassoc ninf nsz <8 x float> %655, %broadcast.splat319
  %660 = fmul reassoc ninf nsz <8 x float> %652, %652
  %661 = fmul reassoc ninf nsz <8 x float> %653, %653
  %662 = fmul reassoc ninf nsz <8 x float> %654, %654
  %663 = fmul reassoc ninf nsz <8 x float> %655, %655
  %664 = fmul reassoc ninf nsz <8 x float> %660, %broadcast.splat321
  %665 = fmul reassoc ninf nsz <8 x float> %661, %broadcast.splat321
  %666 = fmul reassoc ninf nsz <8 x float> %662, %broadcast.splat321
  %667 = fmul reassoc ninf nsz <8 x float> %663, %broadcast.splat321
  %668 = fcmp reassoc ninf nsz olt <8 x float> %636, %664
  %669 = fcmp reassoc ninf nsz olt <8 x float> %637, %665
  %670 = fcmp reassoc ninf nsz olt <8 x float> %638, %666
  %671 = fcmp reassoc ninf nsz olt <8 x float> %639, %667
  %672 = xor <8 x i1> %668, splat (i1 true)
  %673 = xor <8 x i1> %669, splat (i1 true)
  %674 = xor <8 x i1> %670, splat (i1 true)
  %675 = xor <8 x i1> %671, splat (i1 true)
  %676 = select <8 x i1> %broadcast.splat, <8 x i1> %672, <8 x i1> zeroinitializer
  %677 = select <8 x i1> %broadcast.splat, <8 x i1> %673, <8 x i1> zeroinitializer
  %678 = select <8 x i1> %broadcast.splat, <8 x i1> %674, <8 x i1> zeroinitializer
  %679 = select <8 x i1> %broadcast.splat, <8 x i1> %675, <8 x i1> zeroinitializer
  %680 = fcmp reassoc ninf nsz olt <8 x float> %315, %656
  %681 = fcmp reassoc ninf nsz olt <8 x float> %316, %657
  %682 = fcmp reassoc ninf nsz olt <8 x float> %317, %658
  %683 = fcmp reassoc ninf nsz olt <8 x float> %318, %659
  %684 = xor <8 x i1> %680, splat (i1 true)
  %685 = xor <8 x i1> %681, splat (i1 true)
  %686 = xor <8 x i1> %682, splat (i1 true)
  %687 = xor <8 x i1> %683, splat (i1 true)
  %688 = select <8 x i1> %676, <8 x i1> %684, <8 x i1> zeroinitializer
  %689 = select <8 x i1> %677, <8 x i1> %685, <8 x i1> zeroinitializer
  %690 = select <8 x i1> %678, <8 x i1> %686, <8 x i1> zeroinitializer
  %691 = select <8 x i1> %679, <8 x i1> %687, <8 x i1> zeroinitializer
  %692 = fmul reassoc ninf nsz <8 x float> %656, splat (float 4.000000e+00)
  %693 = fmul reassoc ninf nsz <8 x float> %657, splat (float 4.000000e+00)
  %694 = fmul reassoc ninf nsz <8 x float> %658, splat (float 4.000000e+00)
  %695 = fmul reassoc ninf nsz <8 x float> %659, splat (float 4.000000e+00)
  %696 = fdiv reassoc ninf nsz <8 x float> %315, %692
  %697 = fdiv reassoc ninf nsz <8 x float> %316, %693
  %698 = fdiv reassoc ninf nsz <8 x float> %317, %694
  %699 = fdiv reassoc ninf nsz <8 x float> %318, %695
  %700 = fcmp reassoc ninf nsz ogt <8 x float> %696, splat (float 1.000000e+00)
  %701 = fcmp reassoc ninf nsz ogt <8 x float> %697, splat (float 1.000000e+00)
  %702 = fcmp reassoc ninf nsz ogt <8 x float> %698, splat (float 1.000000e+00)
  %703 = fcmp reassoc ninf nsz ogt <8 x float> %699, splat (float 1.000000e+00)
  %704 = select <8 x i1> %700, <8 x float> splat (float 1.000000e+00), <8 x float> %696
  %705 = select <8 x i1> %701, <8 x float> splat (float 1.000000e+00), <8 x float> %697
  %706 = select <8 x i1> %702, <8 x float> splat (float 1.000000e+00), <8 x float> %698
  %707 = select <8 x i1> %703, <8 x float> splat (float 1.000000e+00), <8 x float> %699
  %708 = fmul reassoc ninf nsz <8 x float> %704, splat (float 0x3FD99999A0000000)
  %709 = fmul reassoc ninf nsz <8 x float> %705, splat (float 0x3FD99999A0000000)
  %710 = fmul reassoc ninf nsz <8 x float> %706, splat (float 0x3FD99999A0000000)
  %711 = fmul reassoc ninf nsz <8 x float> %707, splat (float 0x3FD99999A0000000)
  %712 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %708
  %713 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %709
  %714 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %710
  %715 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %711
  %716 = select <8 x i1> %676, <8 x i1> %680, <8 x i1> zeroinitializer
  %717 = select <8 x i1> %677, <8 x i1> %681, <8 x i1> zeroinitializer
  %718 = select <8 x i1> %678, <8 x i1> %682, <8 x i1> zeroinitializer
  %719 = select <8 x i1> %679, <8 x i1> %683, <8 x i1> zeroinitializer
  %720 = fmul reassoc ninf nsz <8 x float> %315, splat (float 0x3FC3333340000000)
  %721 = fmul reassoc ninf nsz <8 x float> %316, splat (float 0x3FC3333340000000)
  %722 = fmul reassoc ninf nsz <8 x float> %317, splat (float 0x3FC3333340000000)
  %723 = fmul reassoc ninf nsz <8 x float> %318, splat (float 0x3FC3333340000000)
  %724 = fdiv reassoc ninf nsz <8 x float> %720, %656
  %725 = fdiv reassoc ninf nsz <8 x float> %721, %657
  %726 = fdiv reassoc ninf nsz <8 x float> %722, %658
  %727 = fdiv reassoc ninf nsz <8 x float> %723, %659
  %728 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %724
  %729 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %725
  %730 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %726
  %731 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %727
  %732 = select <8 x i1> %broadcast.splat, <8 x i1> %668, <8 x i1> zeroinitializer
  %733 = select <8 x i1> %broadcast.splat, <8 x i1> %669, <8 x i1> zeroinitializer
  %734 = select <8 x i1> %broadcast.splat, <8 x i1> %670, <8 x i1> zeroinitializer
  %735 = select <8 x i1> %broadcast.splat, <8 x i1> %671, <8 x i1> zeroinitializer
  %736 = fmul reassoc ninf nsz <8 x float> %656, splat (float 1.500000e+00)
  %737 = fmul reassoc ninf nsz <8 x float> %657, splat (float 1.500000e+00)
  %738 = fmul reassoc ninf nsz <8 x float> %658, splat (float 1.500000e+00)
  %739 = fmul reassoc ninf nsz <8 x float> %659, splat (float 1.500000e+00)
  %740 = fcmp reassoc ninf nsz uge <8 x float> %315, %736
  %741 = fcmp reassoc ninf nsz uge <8 x float> %316, %737
  %742 = fcmp reassoc ninf nsz uge <8 x float> %317, %738
  %743 = fcmp reassoc ninf nsz uge <8 x float> %318, %739
  %744 = select <8 x i1> %732, <8 x i1> %740, <8 x i1> zeroinitializer
  %745 = select <8 x i1> %733, <8 x i1> %741, <8 x i1> zeroinitializer
  %746 = select <8 x i1> %734, <8 x i1> %742, <8 x i1> zeroinitializer
  %747 = select <8 x i1> %735, <8 x i1> %743, <8 x i1> zeroinitializer
  %748 = fsub reassoc ninf nsz <8 x float> %315, %736
  %749 = fsub reassoc ninf nsz <8 x float> %316, %737
  %750 = fsub reassoc ninf nsz <8 x float> %317, %738
  %751 = fsub reassoc ninf nsz <8 x float> %318, %739
  %752 = fdiv reassoc ninf nsz <8 x float> %748, %736
  %753 = fdiv reassoc ninf nsz <8 x float> %749, %737
  %754 = fdiv reassoc ninf nsz <8 x float> %750, %738
  %755 = fdiv reassoc ninf nsz <8 x float> %751, %739
  %756 = fcmp reassoc ninf nsz ogt <8 x float> %752, splat (float 1.000000e+00)
  %757 = fcmp reassoc ninf nsz ogt <8 x float> %753, splat (float 1.000000e+00)
  %758 = fcmp reassoc ninf nsz ogt <8 x float> %754, splat (float 1.000000e+00)
  %759 = fcmp reassoc ninf nsz ogt <8 x float> %755, splat (float 1.000000e+00)
  %760 = select <8 x i1> %756, <8 x float> splat (float 1.000000e+00), <8 x float> %752
  %761 = select <8 x i1> %757, <8 x float> splat (float 1.000000e+00), <8 x float> %753
  %762 = select <8 x i1> %758, <8 x float> splat (float 1.000000e+00), <8 x float> %754
  %763 = select <8 x i1> %759, <8 x float> splat (float 1.000000e+00), <8 x float> %755
  %764 = fmul reassoc ninf nsz <8 x float> %760, splat (float 0x3FC99999A0000000)
  %765 = fmul reassoc ninf nsz <8 x float> %761, splat (float 0x3FC99999A0000000)
  %766 = fmul reassoc ninf nsz <8 x float> %762, splat (float 0x3FC99999A0000000)
  %767 = fmul reassoc ninf nsz <8 x float> %763, splat (float 0x3FC99999A0000000)
  %768 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %764
  %769 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %765
  %770 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %766
  %771 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %767
  %772 = fmul reassoc ninf nsz <8 x float> %315, splat (float 0x3FEE666660000000)
  %773 = fmul reassoc ninf nsz <8 x float> %316, splat (float 0x3FEE666660000000)
  %774 = fmul reassoc ninf nsz <8 x float> %317, splat (float 0x3FEE666660000000)
  %775 = fmul reassoc ninf nsz <8 x float> %318, splat (float 0x3FEE666660000000)
  %776 = fdiv reassoc ninf nsz <8 x float> %772, %736
  %777 = fdiv reassoc ninf nsz <8 x float> %773, %737
  %778 = fdiv reassoc ninf nsz <8 x float> %774, %738
  %779 = fdiv reassoc ninf nsz <8 x float> %775, %739
  %780 = fadd reassoc ninf nsz <8 x float> %776, splat (float 0x3FA99999A0000000)
  %781 = fadd reassoc ninf nsz <8 x float> %777, splat (float 0x3FA99999A0000000)
  %782 = fadd reassoc ninf nsz <8 x float> %778, splat (float 0x3FA99999A0000000)
  %783 = fadd reassoc ninf nsz <8 x float> %779, splat (float 0x3FA99999A0000000)
  %784 = or <8 x i1> %732, %716
  %785 = or <8 x i1> %733, %717
  %786 = or <8 x i1> %734, %718
  %787 = or <8 x i1> %735, %719
  %788 = or <8 x i1> %784, %688
  %789 = or <8 x i1> %785, %689
  %790 = or <8 x i1> %786, %690
  %791 = or <8 x i1> %787, %691
  %792 = or <8 x i1> %788, %210
  %793 = or <8 x i1> %789, %210
  %794 = or <8 x i1> %790, %210
  %795 = or <8 x i1> %791, %210
  %predphi = select <8 x i1> %744, <8 x float> %768, <8 x float> %780
  %predphi322 = select <8 x i1> %716, <8 x float> %728, <8 x float> %predphi
  %predphi323 = select <8 x i1> %688, <8 x float> %712, <8 x float> %predphi322
  %predphi324 = select <8 x i1> %broadcast.splat, <8 x float> %predphi323, <8 x float> splat (float 1.000000e+00)
  %predphi325 = select <8 x i1> %745, <8 x float> %769, <8 x float> %781
  %predphi326 = select <8 x i1> %717, <8 x float> %729, <8 x float> %predphi325
  %predphi327 = select <8 x i1> %689, <8 x float> %713, <8 x float> %predphi326
  %predphi328 = select <8 x i1> %broadcast.splat, <8 x float> %predphi327, <8 x float> splat (float 1.000000e+00)
  %predphi329 = select <8 x i1> %746, <8 x float> %770, <8 x float> %782
  %predphi330 = select <8 x i1> %718, <8 x float> %730, <8 x float> %predphi329
  %predphi331 = select <8 x i1> %690, <8 x float> %714, <8 x float> %predphi330
  %predphi332 = select <8 x i1> %broadcast.splat, <8 x float> %predphi331, <8 x float> splat (float 1.000000e+00)
  %predphi333 = select <8 x i1> %747, <8 x float> %771, <8 x float> %783
  %predphi334 = select <8 x i1> %719, <8 x float> %731, <8 x float> %predphi333
  %predphi335 = select <8 x i1> %691, <8 x float> %715, <8 x float> %predphi334
  %predphi336 = select <8 x i1> %broadcast.splat, <8 x float> %predphi335, <8 x float> splat (float 1.000000e+00)
  %796 = fcmp reassoc ninf nsz ogt <8 x float> %636, splat (float 0x3EB0C6F7A0000000)
  %797 = fcmp reassoc ninf nsz ogt <8 x float> %637, splat (float 0x3EB0C6F7A0000000)
  %798 = fcmp reassoc ninf nsz ogt <8 x float> %638, splat (float 0x3EB0C6F7A0000000)
  %799 = fcmp reassoc ninf nsz ogt <8 x float> %639, splat (float 0x3EB0C6F7A0000000)
  %800 = select <8 x i1> %792, <8 x i1> %796, <8 x i1> zeroinitializer
  %801 = select <8 x i1> %793, <8 x i1> %797, <8 x i1> zeroinitializer
  %802 = select <8 x i1> %794, <8 x i1> %798, <8 x i1> zeroinitializer
  %803 = select <8 x i1> %795, <8 x i1> %799, <8 x i1> zeroinitializer
  %804 = fcmp reassoc ninf nsz ogt <8 x float> %620, splat (float 0x3EB0C6F7A0000000)
  %805 = fcmp reassoc ninf nsz ogt <8 x float> %621, splat (float 0x3EB0C6F7A0000000)
  %806 = fcmp reassoc ninf nsz ogt <8 x float> %622, splat (float 0x3EB0C6F7A0000000)
  %807 = fcmp reassoc ninf nsz ogt <8 x float> %623, splat (float 0x3EB0C6F7A0000000)
  %808 = fcmp reassoc ninf nsz ogt <8 x float> %632, splat (float 0x3EB0C6F7A0000000)
  %809 = fcmp reassoc ninf nsz ogt <8 x float> %633, splat (float 0x3EB0C6F7A0000000)
  %810 = fcmp reassoc ninf nsz ogt <8 x float> %634, splat (float 0x3EB0C6F7A0000000)
  %811 = fcmp reassoc ninf nsz ogt <8 x float> %635, splat (float 0x3EB0C6F7A0000000)
  %812 = select <8 x i1> %804, <8 x i1> %808, <8 x i1> zeroinitializer
  %813 = select <8 x i1> %805, <8 x i1> %809, <8 x i1> zeroinitializer
  %814 = select <8 x i1> %806, <8 x i1> %810, <8 x i1> zeroinitializer
  %815 = select <8 x i1> %807, <8 x i1> %811, <8 x i1> zeroinitializer
  %816 = select <8 x i1> %800, <8 x i1> %812, <8 x i1> zeroinitializer
  %817 = select <8 x i1> %801, <8 x i1> %813, <8 x i1> zeroinitializer
  %818 = select <8 x i1> %802, <8 x i1> %814, <8 x i1> zeroinitializer
  %819 = select <8 x i1> %803, <8 x i1> %815, <8 x i1> zeroinitializer
  %820 = fmul reassoc ninf nsz <8 x float> %560, %416
  %821 = fmul reassoc ninf nsz <8 x float> %561, %417
  %822 = fmul reassoc ninf nsz <8 x float> %562, %418
  %823 = fmul reassoc ninf nsz <8 x float> %563, %419
  %824 = fmul reassoc ninf nsz <8 x float> %608, %464
  %825 = fmul reassoc ninf nsz <8 x float> %609, %465
  %826 = fmul reassoc ninf nsz <8 x float> %610, %466
  %827 = fmul reassoc ninf nsz <8 x float> %611, %467
  %828 = fadd reassoc ninf nsz <8 x float> %824, %820
  %829 = fadd reassoc ninf nsz <8 x float> %825, %821
  %830 = fadd reassoc ninf nsz <8 x float> %826, %822
  %831 = fadd reassoc ninf nsz <8 x float> %827, %823
  %832 = fmul reassoc ninf nsz <8 x float> %632, %620
  %833 = fmul reassoc ninf nsz <8 x float> %633, %621
  %834 = fmul reassoc ninf nsz <8 x float> %634, %622
  %835 = fmul reassoc ninf nsz <8 x float> %635, %623
  %836 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %832)
  %837 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %833)
  %838 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %834)
  %839 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %835)
  %840 = fdiv reassoc ninf nsz <8 x float> %828, %836
  %841 = fdiv reassoc ninf nsz <8 x float> %829, %837
  %842 = fdiv reassoc ninf nsz <8 x float> %830, %838
  %843 = fdiv reassoc ninf nsz <8 x float> %831, %839
  %844 = fcmp reassoc ninf nsz ule <8 x float> %636, %664
  %845 = fcmp reassoc ninf nsz ule <8 x float> %637, %665
  %846 = fcmp reassoc ninf nsz ule <8 x float> %638, %666
  %847 = fcmp reassoc ninf nsz ule <8 x float> %639, %667
  %848 = fcmp reassoc ninf nsz uge <8 x float> %840, splat (float 0x3FC99999A0000000)
  %849 = fcmp reassoc ninf nsz uge <8 x float> %841, splat (float 0x3FC99999A0000000)
  %850 = fcmp reassoc ninf nsz uge <8 x float> %842, splat (float 0x3FC99999A0000000)
  %851 = fcmp reassoc ninf nsz uge <8 x float> %843, splat (float 0x3FC99999A0000000)
  %.not467 = select <8 x i1> %844, <8 x i1> splat (i1 true), <8 x i1> %848
  %.not470 = select <8 x i1> %845, <8 x i1> splat (i1 true), <8 x i1> %849
  %.not473 = select <8 x i1> %846, <8 x i1> splat (i1 true), <8 x i1> %850
  %.not476 = select <8 x i1> %847, <8 x i1> splat (i1 true), <8 x i1> %851
  %852 = select <8 x i1> %816, <8 x i1> %.not467, <8 x i1> zeroinitializer
  %853 = select <8 x i1> %817, <8 x i1> %.not470, <8 x i1> zeroinitializer
  %854 = select <8 x i1> %818, <8 x i1> %.not473, <8 x i1> zeroinitializer
  %855 = select <8 x i1> %819, <8 x i1> %.not476, <8 x i1> zeroinitializer
  %856 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %840, <8 x float> zeroinitializer)
  %857 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %841, <8 x float> zeroinitializer)
  %858 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %842, <8 x float> zeroinitializer)
  %859 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %843, <8 x float> zeroinitializer)
  %860 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %636)
  %861 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %637)
  %862 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %638)
  %863 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %639)
  %864 = fmul reassoc ninf nsz <8 x float> %860, %broadcast.splat338
  %865 = fmul reassoc ninf nsz <8 x float> %861, %broadcast.splat338
  %866 = fmul reassoc ninf nsz <8 x float> %862, %broadcast.splat338
  %867 = fmul reassoc ninf nsz <8 x float> %863, %broadcast.splat338
  %868 = fmul reassoc ninf nsz <8 x float> %864, %856
  %.fr = freeze <8 x float> %868
  %869 = fmul reassoc ninf nsz <8 x float> %865, %857
  %.fr477 = freeze <8 x float> %869
  %870 = fmul reassoc ninf nsz <8 x float> %866, %858
  %.fr478 = freeze <8 x float> %870
  %871 = fmul reassoc ninf nsz <8 x float> %867, %859
  %.fr479 = freeze <8 x float> %871
  %872 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %873 = fcmp reassoc nsz ogt <8 x float> %.fr477, splat (float 3.000000e+00)
  %874 = fcmp reassoc nsz ogt <8 x float> %.fr478, splat (float 3.000000e+00)
  %875 = fcmp reassoc nsz ogt <8 x float> %.fr479, splat (float 3.000000e+00)
  %876 = xor <8 x i1> %872, splat (i1 true)
  %877 = xor <8 x i1> %873, splat (i1 true)
  %878 = xor <8 x i1> %874, splat (i1 true)
  %879 = xor <8 x i1> %875, splat (i1 true)
  %880 = and <8 x i1> %852, %876
  %881 = and <8 x i1> %853, %877
  %882 = and <8 x i1> %854, %878
  %883 = and <8 x i1> %855, %879
  %884 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %885 = fcmp reassoc nsz olt <8 x float> %.fr477, splat (float -3.000000e+00)
  %886 = fcmp reassoc nsz olt <8 x float> %.fr478, splat (float -3.000000e+00)
  %887 = fcmp reassoc nsz olt <8 x float> %.fr479, splat (float -3.000000e+00)
  %888 = xor <8 x i1> %884, splat (i1 true)
  %889 = xor <8 x i1> %885, splat (i1 true)
  %890 = xor <8 x i1> %886, splat (i1 true)
  %891 = xor <8 x i1> %887, splat (i1 true)
  %892 = and <8 x i1> %880, %888
  %893 = and <8 x i1> %881, %889
  %894 = and <8 x i1> %882, %890
  %895 = and <8 x i1> %883, %891
  %896 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %897 = fmul reassoc ninf nsz <8 x float> %.fr477, %.fr477
  %898 = fmul reassoc ninf nsz <8 x float> %.fr478, %.fr478
  %899 = fmul reassoc ninf nsz <8 x float> %.fr479, %.fr479
  %900 = fadd reassoc ninf nsz <8 x float> %896, splat (float 2.700000e+01)
  %901 = fadd reassoc ninf nsz <8 x float> %897, splat (float 2.700000e+01)
  %902 = fadd reassoc ninf nsz <8 x float> %898, splat (float 2.700000e+01)
  %903 = fadd reassoc ninf nsz <8 x float> %899, splat (float 2.700000e+01)
  %904 = fmul reassoc ninf nsz <8 x float> %900, %.fr
  %905 = fmul reassoc ninf nsz <8 x float> %901, %.fr477
  %906 = fmul reassoc ninf nsz <8 x float> %902, %.fr478
  %907 = fmul reassoc ninf nsz <8 x float> %903, %.fr479
  %908 = fmul reassoc ninf nsz <8 x float> %896, splat (float 9.000000e+00)
  %909 = fmul reassoc ninf nsz <8 x float> %897, splat (float 9.000000e+00)
  %910 = fmul reassoc ninf nsz <8 x float> %898, splat (float 9.000000e+00)
  %911 = fmul reassoc ninf nsz <8 x float> %899, splat (float 9.000000e+00)
  %912 = fadd reassoc ninf nsz <8 x float> %908, splat (float 2.700000e+01)
  %913 = fadd reassoc ninf nsz <8 x float> %909, splat (float 2.700000e+01)
  %914 = fadd reassoc ninf nsz <8 x float> %910, splat (float 2.700000e+01)
  %915 = fadd reassoc ninf nsz <8 x float> %911, splat (float 2.700000e+01)
  %916 = fdiv reassoc ninf nsz <8 x float> %904, %912
  %917 = fdiv reassoc ninf nsz <8 x float> %905, %913
  %918 = fdiv reassoc ninf nsz <8 x float> %906, %914
  %919 = fdiv reassoc ninf nsz <8 x float> %907, %915
  %920 = fadd reassoc ninf nsz <8 x float> %916, splat (float 1.000000e+00)
  %921 = fadd reassoc ninf nsz <8 x float> %917, splat (float 1.000000e+00)
  %922 = fadd reassoc ninf nsz <8 x float> %918, splat (float 1.000000e+00)
  %923 = fadd reassoc ninf nsz <8 x float> %919, splat (float 1.000000e+00)
  %924 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %840
  %925 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %841
  %926 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %842
  %927 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %843
  %928 = fmul reassoc ninf nsz <8 x float> %924, %315
  %929 = fmul reassoc ninf nsz <8 x float> %925, %316
  %930 = fmul reassoc ninf nsz <8 x float> %926, %317
  %931 = fmul reassoc ninf nsz <8 x float> %927, %318
  %932 = and <8 x i1> %880, %884
  %933 = and <8 x i1> %881, %885
  %934 = and <8 x i1> %882, %886
  %935 = and <8 x i1> %883, %887
  %936 = and <8 x i1> %852, %872
  %937 = and <8 x i1> %853, %873
  %938 = and <8 x i1> %854, %874
  %939 = and <8 x i1> %855, %875
  %940 = xor <8 x i1> %812, splat (i1 true)
  %941 = xor <8 x i1> %813, splat (i1 true)
  %942 = xor <8 x i1> %814, splat (i1 true)
  %943 = xor <8 x i1> %815, splat (i1 true)
  %944 = select <8 x i1> %800, <8 x i1> %940, <8 x i1> zeroinitializer
  %945 = select <8 x i1> %801, <8 x i1> %941, <8 x i1> zeroinitializer
  %946 = select <8 x i1> %802, <8 x i1> %942, <8 x i1> zeroinitializer
  %947 = select <8 x i1> %803, <8 x i1> %943, <8 x i1> zeroinitializer
  %948 = xor <8 x i1> %796, splat (i1 true)
  %949 = xor <8 x i1> %797, splat (i1 true)
  %950 = xor <8 x i1> %798, splat (i1 true)
  %951 = xor <8 x i1> %799, splat (i1 true)
  %952 = select <8 x i1> %792, <8 x i1> %948, <8 x i1> zeroinitializer
  %953 = select <8 x i1> %793, <8 x i1> %949, <8 x i1> zeroinitializer
  %954 = select <8 x i1> %794, <8 x i1> %950, <8 x i1> zeroinitializer
  %955 = select <8 x i1> %795, <8 x i1> %951, <8 x i1> zeroinitializer
  %956 = select <8 x i1> %852, <8 x i1> splat (i1 true), <8 x i1> %952
  %957 = select <8 x i1> %956, <8 x i1> splat (i1 true), <8 x i1> %944
  %predphi343 = select <8 x i1> %957, <8 x float> %315, <8 x float> %928
  %958 = select <8 x i1> %853, <8 x i1> splat (i1 true), <8 x i1> %953
  %959 = select <8 x i1> %958, <8 x i1> splat (i1 true), <8 x i1> %945
  %predphi348 = select <8 x i1> %959, <8 x float> %316, <8 x float> %929
  %960 = select <8 x i1> %854, <8 x i1> splat (i1 true), <8 x i1> %954
  %961 = select <8 x i1> %960, <8 x i1> splat (i1 true), <8 x i1> %946
  %predphi353 = select <8 x i1> %961, <8 x float> %317, <8 x float> %930
  %962 = select <8 x i1> %855, <8 x i1> splat (i1 true), <8 x i1> %955
  %963 = select <8 x i1> %962, <8 x i1> splat (i1 true), <8 x i1> %947
  %predphi358 = select <8 x i1> %963, <8 x float> %318, <8 x float> %931
  %predphi361 = select <8 x i1> %936, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi362 = select <8 x i1> %892, <8 x float> %920, <8 x float> %predphi361
  %predphi363 = select <8 x i1> %932, <8 x float> zeroinitializer, <8 x float> %predphi362
  %predphi366 = select <8 x i1> %937, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi367 = select <8 x i1> %893, <8 x float> %921, <8 x float> %predphi366
  %predphi368 = select <8 x i1> %933, <8 x float> zeroinitializer, <8 x float> %predphi367
  %predphi371 = select <8 x i1> %938, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi372 = select <8 x i1> %894, <8 x float> %922, <8 x float> %predphi371
  %predphi373 = select <8 x i1> %934, <8 x float> zeroinitializer, <8 x float> %predphi372
  %predphi376 = select <8 x i1> %939, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi377 = select <8 x i1> %895, <8 x float> %923, <8 x float> %predphi376
  %predphi378 = select <8 x i1> %935, <8 x float> zeroinitializer, <8 x float> %predphi377
  %964 = fmul reassoc ninf nsz <8 x float> %predphi363, %predphi324
  %965 = fmul reassoc ninf nsz <8 x float> %predphi368, %predphi328
  %966 = fmul reassoc ninf nsz <8 x float> %predphi373, %predphi332
  %967 = fmul reassoc ninf nsz <8 x float> %predphi378, %predphi336
  %968 = fmul reassoc ninf nsz <8 x float> %964, %predphi343
  %969 = fmul reassoc ninf nsz <8 x float> %965, %predphi348
  %970 = fmul reassoc ninf nsz <8 x float> %966, %predphi353
  %971 = fmul reassoc ninf nsz <8 x float> %967, %predphi358
  %972 = fadd reassoc ninf nsz <8 x float> %968, %vec.phi227
  %973 = fadd reassoc ninf nsz <8 x float> %969, %vec.phi228
  %974 = fadd reassoc ninf nsz <8 x float> %970, %vec.phi229
  %975 = fadd reassoc ninf nsz <8 x float> %971, %vec.phi230
  %976 = fadd reassoc ninf nsz <8 x float> %964, %vec.phi223
  %977 = fadd reassoc ninf nsz <8 x float> %965, %vec.phi224
  %978 = fadd reassoc ninf nsz <8 x float> %966, %vec.phi225
  %979 = fadd reassoc ninf nsz <8 x float> %967, %vec.phi226
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %980 = icmp eq i64 %lsr.iv.next, 0
  br i1 %980, label %middle.block212, label %vector.body221, !llvm.loop !11

middle.block212:                                  ; preds = %vector.body221
  %bin.rdx380 = fadd reassoc ninf nsz <8 x float> %977, %976
  %bin.rdx381 = fadd reassoc ninf nsz <8 x float> %978, %bin.rdx380
  %bin.rdx382 = fadd reassoc ninf nsz <8 x float> %979, %bin.rdx381
  %981 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx382)
  %bin.rdx383 = fadd reassoc ninf nsz <8 x float> %973, %972
  %bin.rdx384 = fadd reassoc ninf nsz <8 x float> %974, %bin.rdx383
  %bin.rdx385 = fadd reassoc ninf nsz <8 x float> %975, %bin.rdx384
  %982 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx385)
  br i1 %cmp.n386, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check393

vec.epilog.iter.check393:                         ; preds = %middle.block212
  br i1 %min.epilog.iters.check395, label %for_loop_body20.us.preheader, label %vec.epilog.ph392

vec.epilog.ph392:                                 ; preds = %vec.epilog.iter.check393, %vector.main.loop.iter.check217
  %bc.resume.val387 = phi i64 [ %n.vec220, %vec.epilog.iter.check393 ], [ 0, %vector.main.loop.iter.check217 ]
  %bc.merge.rdx388 = phi float [ %981, %vec.epilog.iter.check393 ], [ %.056102.us, %vector.main.loop.iter.check217 ]
  %bc.merge.rdx389 = phi float [ %982, %vec.epilog.iter.check393 ], [ %.058101.us, %vector.main.loop.iter.check217 ]
  %983 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx388, i64 0
  %984 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx389, i64 0
  %985 = trunc nuw nsw i64 %bc.resume.val387 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %985, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert408 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat409 = shufflevector <8 x i32> %broadcast.splatinsert408, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert411 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat412 = shufflevector <8 x i32> %broadcast.splatinsert411, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert418 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat419 = shufflevector <8 x i32> %broadcast.splatinsert418, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert422 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat423 = shufflevector <8 x i32> %broadcast.splatinsert422, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert430 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat431 = shufflevector <8 x i32> %broadcast.splatinsert430, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert434 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat435 = shufflevector <8 x i32> %broadcast.splatinsert434, <8 x i32> poison, <8 x i32> zeroinitializer
  %986 = add i64 %213, %bc.resume.val387
  br label %vec.epilog.vector.body400

vec.epilog.vector.body400:                        ; preds = %vec.epilog.vector.body400, %vec.epilog.ph392
  %lsr.iv577 = phi i64 [ %lsr.iv.next578, %vec.epilog.vector.body400 ], [ %986, %vec.epilog.ph392 ]
  %vec.phi402 = phi <8 x float> [ %983, %vec.epilog.ph392 ], [ %1162, %vec.epilog.vector.body400 ]
  %vec.phi403 = phi <8 x float> [ %984, %vec.epilog.ph392 ], [ %1161, %vec.epilog.vector.body400 ]
  %vec.ind404 = phi <8 x i32> [ %induction, %vec.epilog.ph392 ], [ %vec.ind.next405, %vec.epilog.vector.body400 ]
  %987 = shl <8 x i32> %vec.ind404, splat (i32 1)
  %988 = add <8 x i32> %broadcast.splat232, %987
  %989 = add <8 x i32> %broadcast.splat409, %988
  %990 = sext <8 x i32> %989 to <8 x i64>
  %991 = getelementptr float, ptr %179, <8 x i64> %990
  %wide.masked.gather410 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %991, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %992 = add <8 x i32> %988, %broadcast.splat412
  %993 = sext <8 x i32> %992 to <8 x i64>
  %994 = getelementptr float, ptr %112, <8 x i64> %993
  %wide.masked.gather413 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %994, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %995 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather410, %wide.masked.gather413
  %996 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %995)
  %997 = add <8 x i32> %988, splat (i32 1)
  %998 = add <8 x i32> %broadcast.splat409, %997
  %999 = sext <8 x i32> %998 to <8 x i64>
  %1000 = getelementptr float, ptr %179, <8 x i64> %999
  %wide.masked.gather414 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1000, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1001 = add <8 x i32> %987, %broadcast.splat249
  %1002 = add <8 x i32> %broadcast.splat409, %1001
  %1003 = sext <8 x i32> %1002 to <8 x i64>
  %1004 = getelementptr float, ptr %179, <8 x i64> %1003
  %wide.masked.gather417 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1004, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1005 = add <8 x i32> %broadcast.splat419, %997
  %1006 = sext <8 x i32> %1005 to <8 x i64>
  %1007 = getelementptr float, ptr %179, <8 x i64> %1006
  %wide.masked.gather420 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1007, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1008 = add <8 x i32> %broadcast.splat419, %1001
  %1009 = sext <8 x i32> %1008 to <8 x i64>
  %1010 = getelementptr float, ptr %179, <8 x i64> %1009
  %wide.masked.gather421 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1010, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1011 = add <8 x i32> %broadcast.splat423, %997
  %1012 = sext <8 x i32> %1011 to <8 x i64>
  %1013 = getelementptr float, ptr %179, <8 x i64> %1012
  %wide.masked.gather424 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1013, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1014 = add <8 x i32> %broadcast.splat423, %1001
  %1015 = sext <8 x i32> %1014 to <8 x i64>
  %1016 = getelementptr float, ptr %179, <8 x i64> %1015
  %wide.masked.gather425 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1016, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1017 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather414, %wide.masked.gather420
  %1018 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather417, %wide.masked.gather421
  %1019 = fadd reassoc ninf nsz <8 x float> %1017, %wide.masked.gather424
  %1020 = fadd reassoc ninf nsz <8 x float> %1018, %wide.masked.gather425
  %1021 = fsub reassoc ninf nsz <8 x float> %1019, %1020
  %1022 = fmul reassoc ninf nsz <8 x float> %1021, splat (float 0x3FD5555560000000)
  %1023 = add <8 x i32> %broadcast.splat423, %988
  %1024 = sext <8 x i32> %1023 to <8 x i64>
  %1025 = getelementptr float, ptr %179, <8 x i64> %1024
  %wide.masked.gather426 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1025, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1026 = add <8 x i32> %broadcast.splat419, %988
  %1027 = sext <8 x i32> %1026 to <8 x i64>
  %1028 = getelementptr float, ptr %179, <8 x i64> %1027
  %wide.masked.gather427 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1028, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1029 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather420, %wide.masked.gather421
  %1030 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather424, %1029
  %1031 = fadd reassoc ninf nsz <8 x float> %1030, %wide.masked.gather425
  %1032 = fadd reassoc ninf nsz <8 x float> %1031, %wide.masked.gather426
  %1033 = fsub reassoc ninf nsz <8 x float> %1032, %wide.masked.gather427
  %1034 = fmul reassoc ninf nsz <8 x float> %1033, splat (float 0x3FD5555560000000)
  %1035 = add <8 x i32> %997, %broadcast.splat412
  %1036 = sext <8 x i32> %1035 to <8 x i64>
  %1037 = getelementptr float, ptr %112, <8 x i64> %1036
  %wide.masked.gather428 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1037, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1038 = add <8 x i32> %1001, %broadcast.splat412
  %1039 = sext <8 x i32> %1038 to <8 x i64>
  %1040 = getelementptr float, ptr %112, <8 x i64> %1039
  %wide.masked.gather429 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1040, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1041 = add <8 x i32> %997, %broadcast.splat431
  %1042 = sext <8 x i32> %1041 to <8 x i64>
  %1043 = getelementptr float, ptr %112, <8 x i64> %1042
  %wide.masked.gather432 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1043, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1044 = add <8 x i32> %1001, %broadcast.splat431
  %1045 = sext <8 x i32> %1044 to <8 x i64>
  %1046 = getelementptr float, ptr %112, <8 x i64> %1045
  %wide.masked.gather433 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1046, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1047 = add <8 x i32> %997, %broadcast.splat435
  %1048 = sext <8 x i32> %1047 to <8 x i64>
  %1049 = getelementptr float, ptr %112, <8 x i64> %1048
  %wide.masked.gather436 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1049, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1050 = add <8 x i32> %1001, %broadcast.splat435
  %1051 = sext <8 x i32> %1050 to <8 x i64>
  %1052 = getelementptr float, ptr %112, <8 x i64> %1051
  %wide.masked.gather437 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1052, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1053 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather428, %wide.masked.gather432
  %1054 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather429, %wide.masked.gather433
  %1055 = fadd reassoc ninf nsz <8 x float> %1053, %wide.masked.gather436
  %1056 = fadd reassoc ninf nsz <8 x float> %1054, %wide.masked.gather437
  %1057 = fsub reassoc ninf nsz <8 x float> %1055, %1056
  %1058 = fmul reassoc ninf nsz <8 x float> %1057, splat (float 0x3FD5555560000000)
  %1059 = add <8 x i32> %988, %broadcast.splat435
  %1060 = sext <8 x i32> %1059 to <8 x i64>
  %1061 = getelementptr float, ptr %112, <8 x i64> %1060
  %wide.masked.gather438 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1061, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1062 = add <8 x i32> %988, %broadcast.splat431
  %1063 = sext <8 x i32> %1062 to <8 x i64>
  %1064 = getelementptr float, ptr %112, <8 x i64> %1063
  %wide.masked.gather439 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1064, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1065 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather432, %wide.masked.gather433
  %1066 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather436, %1065
  %1067 = fadd reassoc ninf nsz <8 x float> %1066, %wide.masked.gather437
  %1068 = fadd reassoc ninf nsz <8 x float> %1067, %wide.masked.gather438
  %1069 = fsub reassoc ninf nsz <8 x float> %1068, %wide.masked.gather439
  %1070 = fmul reassoc ninf nsz <8 x float> %1069, splat (float 0x3FD5555560000000)
  %1071 = fmul reassoc ninf nsz <8 x float> %1022, %1022
  %1072 = fmul reassoc ninf nsz <8 x float> %1034, %1034
  %1073 = fadd reassoc ninf nsz <8 x float> %1072, %1071
  %1074 = fmul reassoc ninf nsz <8 x float> %1058, %1058
  %1075 = fmul reassoc ninf nsz <8 x float> %1070, %1070
  %1076 = fadd reassoc ninf nsz <8 x float> %1075, %1074
  %1077 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %1073, <8 x float> %1076)
  %1078 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather413, splat (float -2.000000e+00)
  %1079 = fadd reassoc ninf nsz <8 x float> %1078, splat (float 3.000000e+00)
  %1080 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %1079, <8 x float> splat (float 3.000000e+00))
  %1081 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %1080, <8 x float> splat (float 1.000000e+00))
  %1082 = fmul reassoc ninf nsz <8 x float> %1081, %broadcast.splat319
  %1083 = fmul reassoc ninf nsz <8 x float> %1081, %1081
  %1084 = fmul reassoc ninf nsz <8 x float> %1083, %broadcast.splat321
  %1085 = fcmp reassoc ninf nsz olt <8 x float> %1077, %1084
  %1086 = xor <8 x i1> %1085, splat (i1 true)
  %1087 = select <8 x i1> %broadcast.splat, <8 x i1> %1086, <8 x i1> zeroinitializer
  %1088 = fcmp reassoc ninf nsz olt <8 x float> %996, %1082
  %1089 = xor <8 x i1> %1088, splat (i1 true)
  %1090 = select <8 x i1> %1087, <8 x i1> %1089, <8 x i1> zeroinitializer
  %1091 = fmul reassoc ninf nsz <8 x float> %1082, splat (float 4.000000e+00)
  %1092 = fdiv reassoc ninf nsz <8 x float> %996, %1091
  %1093 = fcmp reassoc ninf nsz ogt <8 x float> %1092, splat (float 1.000000e+00)
  %1094 = select <8 x i1> %1093, <8 x float> splat (float 1.000000e+00), <8 x float> %1092
  %1095 = fmul reassoc ninf nsz <8 x float> %1094, splat (float 0x3FD99999A0000000)
  %1096 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %1095
  %1097 = select <8 x i1> %1087, <8 x i1> %1088, <8 x i1> zeroinitializer
  %1098 = fmul reassoc ninf nsz <8 x float> %996, splat (float 0x3FC3333340000000)
  %1099 = fdiv reassoc ninf nsz <8 x float> %1098, %1082
  %1100 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %1099
  %1101 = select <8 x i1> %broadcast.splat, <8 x i1> %1085, <8 x i1> zeroinitializer
  %1102 = fmul reassoc ninf nsz <8 x float> %1082, splat (float 1.500000e+00)
  %1103 = fcmp reassoc ninf nsz uge <8 x float> %996, %1102
  %1104 = select <8 x i1> %1101, <8 x i1> %1103, <8 x i1> zeroinitializer
  %1105 = fsub reassoc ninf nsz <8 x float> %996, %1102
  %1106 = fdiv reassoc ninf nsz <8 x float> %1105, %1102
  %1107 = fcmp reassoc ninf nsz ogt <8 x float> %1106, splat (float 1.000000e+00)
  %1108 = select <8 x i1> %1107, <8 x float> splat (float 1.000000e+00), <8 x float> %1106
  %1109 = fmul reassoc ninf nsz <8 x float> %1108, splat (float 0x3FC99999A0000000)
  %1110 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %1109
  %1111 = fmul reassoc ninf nsz <8 x float> %996, splat (float 0x3FEE666660000000)
  %1112 = fdiv reassoc ninf nsz <8 x float> %1111, %1102
  %1113 = fadd reassoc ninf nsz <8 x float> %1112, splat (float 0x3FA99999A0000000)
  %1114 = or <8 x i1> %1097, %210
  %1115 = or <8 x i1> %1114, %1101
  %1116 = or <8 x i1> %1115, %1090
  %predphi444 = select <8 x i1> %1104, <8 x float> %1110, <8 x float> %1113
  %predphi445 = select <8 x i1> %1097, <8 x float> %1100, <8 x float> %predphi444
  %predphi446 = select <8 x i1> %1090, <8 x float> %1096, <8 x float> %predphi445
  %predphi447 = select <8 x i1> %broadcast.splat, <8 x float> %predphi446, <8 x float> splat (float 1.000000e+00)
  %1117 = fcmp reassoc ninf nsz ogt <8 x float> %1077, splat (float 0x3EB0C6F7A0000000)
  %1118 = select <8 x i1> %1116, <8 x i1> %1117, <8 x i1> zeroinitializer
  %1119 = fcmp reassoc ninf nsz ogt <8 x float> %1073, splat (float 0x3EB0C6F7A0000000)
  %1120 = fcmp reassoc ninf nsz ogt <8 x float> %1076, splat (float 0x3EB0C6F7A0000000)
  %1121 = select <8 x i1> %1119, <8 x i1> %1120, <8 x i1> zeroinitializer
  %1122 = select <8 x i1> %1118, <8 x i1> %1121, <8 x i1> zeroinitializer
  %1123 = fmul reassoc ninf nsz <8 x float> %1058, %1022
  %1124 = fmul reassoc ninf nsz <8 x float> %1070, %1034
  %1125 = fadd reassoc ninf nsz <8 x float> %1124, %1123
  %1126 = fmul reassoc ninf nsz <8 x float> %1076, %1073
  %1127 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %1126)
  %1128 = fdiv reassoc ninf nsz <8 x float> %1125, %1127
  %1129 = fcmp reassoc ninf nsz ule <8 x float> %1077, %1084
  %1130 = fcmp reassoc ninf nsz uge <8 x float> %1128, splat (float 0x3FC99999A0000000)
  %.not482 = select <8 x i1> %1129, <8 x i1> splat (i1 true), <8 x i1> %1130
  %1131 = select <8 x i1> %1122, <8 x i1> %.not482, <8 x i1> zeroinitializer
  %1132 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %1128, <8 x float> zeroinitializer)
  %1133 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %1077)
  %1134 = fmul reassoc ninf nsz <8 x float> %1133, %broadcast.splat338
  %1135 = fmul reassoc ninf nsz <8 x float> %1134, %1132
  %.fr483 = freeze <8 x float> %1135
  %1136 = fcmp reassoc nsz ogt <8 x float> %.fr483, splat (float 3.000000e+00)
  %1137 = xor <8 x i1> %1136, splat (i1 true)
  %1138 = and <8 x i1> %1131, %1137
  %1139 = fcmp reassoc nsz olt <8 x float> %.fr483, splat (float -3.000000e+00)
  %1140 = xor <8 x i1> %1139, splat (i1 true)
  %1141 = and <8 x i1> %1138, %1140
  %1142 = fmul reassoc ninf nsz <8 x float> %.fr483, %.fr483
  %1143 = fadd reassoc ninf nsz <8 x float> %1142, splat (float 2.700000e+01)
  %1144 = fmul reassoc ninf nsz <8 x float> %1143, %.fr483
  %1145 = fmul reassoc ninf nsz <8 x float> %1142, splat (float 9.000000e+00)
  %1146 = fadd reassoc ninf nsz <8 x float> %1145, splat (float 2.700000e+01)
  %1147 = fdiv reassoc ninf nsz <8 x float> %1144, %1146
  %1148 = fadd reassoc ninf nsz <8 x float> %1147, splat (float 1.000000e+00)
  %1149 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %1128
  %1150 = fmul reassoc ninf nsz <8 x float> %1149, %996
  %1151 = and <8 x i1> %1138, %1139
  %1152 = and <8 x i1> %1131, %1136
  %1153 = xor <8 x i1> %1121, splat (i1 true)
  %1154 = select <8 x i1> %1118, <8 x i1> %1153, <8 x i1> zeroinitializer
  %1155 = xor <8 x i1> %1117, splat (i1 true)
  %1156 = select <8 x i1> %1116, <8 x i1> %1155, <8 x i1> zeroinitializer
  %1157 = select <8 x i1> %1131, <8 x i1> splat (i1 true), <8 x i1> %1156
  %1158 = select <8 x i1> %1157, <8 x i1> splat (i1 true), <8 x i1> %1154
  %predphi454 = select <8 x i1> %1158, <8 x float> %996, <8 x float> %1150
  %predphi457 = select <8 x i1> %1152, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi458 = select <8 x i1> %1141, <8 x float> %1148, <8 x float> %predphi457
  %predphi459 = select <8 x i1> %1151, <8 x float> zeroinitializer, <8 x float> %predphi458
  %1159 = fmul reassoc ninf nsz <8 x float> %predphi459, %predphi447
  %1160 = fmul reassoc ninf nsz <8 x float> %1159, %predphi454
  %1161 = fadd reassoc ninf nsz <8 x float> %1160, %vec.phi403
  %1162 = fadd reassoc ninf nsz <8 x float> %1159, %vec.phi402
  %vec.ind.next405 = add <8 x i32> %vec.ind404, splat (i32 8)
  %lsr.iv.next578 = add i64 %lsr.iv577, 8
  %1163 = icmp eq i64 %lsr.iv.next578, 0
  br i1 %1163, label %vec.epilog.middle.block390, label %vec.epilog.vector.body400, !llvm.loop !14

vec.epilog.middle.block390:                       ; preds = %vec.epilog.vector.body400
  %1164 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1162)
  %1165 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1161)
  br i1 %cmp.n461, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block390, %vec.epilog.iter.check393, %vector.scevcheck160, %iter.check215
  %indvars.iv.ph = phi i64 [ %n.vec220, %vec.epilog.iter.check393 ], [ 0, %iter.check215 ], [ 0, %vector.scevcheck160 ], [ %n.vec397, %vec.epilog.middle.block390 ]
  %.15798.us.ph = phi float [ %981, %vec.epilog.iter.check393 ], [ %.056102.us, %iter.check215 ], [ %.056102.us, %vector.scevcheck160 ], [ %1164, %vec.epilog.middle.block390 ]
  %.15997.us.ph = phi float [ %982, %vec.epilog.iter.check393 ], [ %.058101.us, %iter.check215 ], [ %.058101.us, %vector.scevcheck160 ], [ %1165, %vec.epilog.middle.block390 ]
  %1166 = trunc i64 %indvars.iv.ph to i32
  %1167 = shl nuw i32 %1166, 1
  %1168 = add i64 %214, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv603 = phi i64 [ %1168, %for_loop_body20.us.preheader ], [ %lsr.iv.next604, %after_if50.us ]
  %lsr.iv601 = phi i32 [ %lsr.iv599, %for_loop_body20.us.preheader ], [ %lsr.iv.next602, %after_if50.us ]
  %lsr.iv597 = phi i32 [ %lsr.iv595, %for_loop_body20.us.preheader ], [ %lsr.iv.next598, %after_if50.us ]
  %lsr.iv593 = phi i32 [ %lsr.iv591, %for_loop_body20.us.preheader ], [ %lsr.iv.next594, %after_if50.us ]
  %lsr.iv589 = phi i32 [ %lsr.iv587, %for_loop_body20.us.preheader ], [ %lsr.iv.next590, %after_if50.us ]
  %lsr.iv585 = phi i32 [ %lsr.iv583, %for_loop_body20.us.preheader ], [ %lsr.iv.next586, %after_if50.us ]
  %lsr.iv581 = phi i32 [ %lsr.iv579, %for_loop_body20.us.preheader ], [ %lsr.iv.next582, %after_if50.us ]
  %.15798.us = phi float [ %1329, %after_if50.us ], [ %.15798.us.ph, %for_loop_body20.us.preheader ]
  %.15997.us = phi float [ %1328, %after_if50.us ], [ %.15997.us.ph, %for_loop_body20.us.preheader ]
  %1169 = add i32 %1167, %lsr.iv601
  %1170 = add i32 %1169, 1
  %1171 = sext i32 %1170 to i64
  %1172 = getelementptr float, ptr %179, i64 %1171
  %1173 = load float, ptr %1172, align 4
  %1174 = add i32 %1167, %lsr.iv597
  %1175 = add i32 %1174, 1
  %1176 = sext i32 %1175 to i64
  %1177 = getelementptr float, ptr %112, i64 %1176
  %1178 = load float, ptr %1177, align 4
  %1179 = fsub reassoc ninf nsz float %1173, %1178
  %1180 = tail call noundef float @llvm.fabs.f32(float %1179)
  %1181 = add i32 %1169, 2
  %1182 = sext i32 %1181 to i64
  %1183 = getelementptr float, ptr %179, i64 %1182
  %1184 = load float, ptr %1183, align 4
  %1185 = sext i32 %1169 to i64
  %1186 = getelementptr float, ptr %179, i64 %1185
  %1187 = load float, ptr %1186, align 4
  %1188 = add i32 %1167, %lsr.iv589
  %1189 = add i32 %1188, 2
  %1190 = sext i32 %1189 to i64
  %1191 = getelementptr float, ptr %179, i64 %1190
  %1192 = load float, ptr %1191, align 4
  %1193 = sext i32 %1188 to i64
  %1194 = getelementptr float, ptr %179, i64 %1193
  %1195 = load float, ptr %1194, align 4
  %1196 = add i32 %1167, %lsr.iv593
  %1197 = add i32 %1196, 2
  %1198 = sext i32 %1197 to i64
  %1199 = getelementptr float, ptr %179, i64 %1198
  %1200 = load float, ptr %1199, align 4
  %1201 = sext i32 %1196 to i64
  %1202 = getelementptr float, ptr %179, i64 %1201
  %1203 = load float, ptr %1202, align 4
  %1204 = fadd reassoc ninf nsz float %1184, %1192
  %1205 = fadd reassoc ninf nsz float %1187, %1195
  %1206 = fadd reassoc ninf nsz float %1204, %1200
  %1207 = fadd reassoc ninf nsz float %1205, %1203
  %1208 = fsub reassoc ninf nsz float %1206, %1207
  %1209 = fmul reassoc ninf nsz float %1208, 0x3FD5555560000000
  %1210 = add i32 %1196, 1
  %1211 = sext i32 %1210 to i64
  %1212 = getelementptr float, ptr %179, i64 %1211
  %1213 = load float, ptr %1212, align 4
  %1214 = add i32 %1188, 1
  %1215 = sext i32 %1214 to i64
  %1216 = getelementptr float, ptr %179, i64 %1215
  %1217 = load float, ptr %1216, align 4
  %1218 = fadd reassoc ninf nsz float %1192, %1195
  %1219 = fsub reassoc ninf nsz float %1200, %1218
  %1220 = fadd reassoc ninf nsz float %1219, %1203
  %1221 = fadd reassoc ninf nsz float %1220, %1213
  %1222 = fsub reassoc ninf nsz float %1221, %1217
  %1223 = fmul reassoc ninf nsz float %1222, 0x3FD5555560000000
  %1224 = add i32 %1174, 2
  %1225 = sext i32 %1224 to i64
  %1226 = getelementptr float, ptr %112, i64 %1225
  %1227 = load float, ptr %1226, align 4
  %1228 = sext i32 %1174 to i64
  %1229 = getelementptr float, ptr %112, i64 %1228
  %1230 = load float, ptr %1229, align 4
  %1231 = add i32 %1167, %lsr.iv581
  %1232 = add i32 %1231, 2
  %1233 = sext i32 %1232 to i64
  %1234 = getelementptr float, ptr %112, i64 %1233
  %1235 = load float, ptr %1234, align 4
  %1236 = sext i32 %1231 to i64
  %1237 = getelementptr float, ptr %112, i64 %1236
  %1238 = load float, ptr %1237, align 4
  %1239 = add i32 %1167, %lsr.iv585
  %1240 = add i32 %1239, 2
  %1241 = sext i32 %1240 to i64
  %1242 = getelementptr float, ptr %112, i64 %1241
  %1243 = load float, ptr %1242, align 4
  %1244 = sext i32 %1239 to i64
  %1245 = getelementptr float, ptr %112, i64 %1244
  %1246 = load float, ptr %1245, align 4
  %1247 = fadd reassoc ninf nsz float %1227, %1235
  %1248 = fadd reassoc ninf nsz float %1230, %1238
  %1249 = fadd reassoc ninf nsz float %1247, %1243
  %1250 = fadd reassoc ninf nsz float %1248, %1246
  %1251 = fsub reassoc ninf nsz float %1249, %1250
  %1252 = fmul reassoc ninf nsz float %1251, 0x3FD5555560000000
  %1253 = add i32 %1239, 1
  %1254 = sext i32 %1253 to i64
  %1255 = getelementptr float, ptr %112, i64 %1254
  %1256 = load float, ptr %1255, align 4
  %1257 = add i32 %1231, 1
  %1258 = sext i32 %1257 to i64
  %1259 = getelementptr float, ptr %112, i64 %1258
  %1260 = load float, ptr %1259, align 4
  %1261 = fadd reassoc ninf nsz float %1235, %1238
  %1262 = fsub reassoc ninf nsz float %1243, %1261
  %1263 = fadd reassoc ninf nsz float %1262, %1246
  %1264 = fadd reassoc ninf nsz float %1263, %1256
  %1265 = fsub reassoc ninf nsz float %1264, %1260
  %1266 = fmul reassoc ninf nsz float %1265, 0x3FD5555560000000
  %1267 = fmul reassoc ninf nsz float %1209, %1209
  %1268 = fmul reassoc ninf nsz float %1223, %1223
  %1269 = fadd reassoc ninf nsz float %1268, %1267
  %1270 = fmul reassoc ninf nsz float %1252, %1252
  %1271 = fmul reassoc ninf nsz float %1266, %1266
  %1272 = fadd reassoc ninf nsz float %1271, %1270
  %1273 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1269, float %1272)
  %factor.us = fmul reassoc ninf nsz float %1178, -2.000000e+00
  %1274 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %1275 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1274, float 3.000000e+00)
  %1276 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1275, float 1.000000e+00)
  %1277 = fmul reassoc ninf nsz float %1276, %166
  %1278 = fmul reassoc ninf nsz float %1276, %1276
  %1279 = fmul reassoc ninf nsz float %1278, %176
  br i1 %167, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %1280 = fcmp reassoc ninf nsz olt float %1273, %1279
  br i1 %1280, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %1281 = fcmp reassoc ninf nsz olt float %1180, %1277
  br i1 %1281, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %1282 = fmul reassoc ninf nsz float %1277, 4.000000e+00
  %1283 = fdiv reassoc ninf nsz float %1180, %1282
  %1284 = fcmp reassoc ninf nsz ogt float %1283, 1.000000e+00
  %spec.store.select1.us = select i1 %1284, float 1.000000e+00, float %1283
  %1285 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %1286 = fsub reassoc ninf nsz float 0x3FE6666680000000, %1285
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %1287 = fmul reassoc ninf nsz float %1180, 0x3FC3333340000000
  %1288 = fdiv reassoc ninf nsz float %1287, %1277
  %1289 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %1288
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %1290 = fmul reassoc ninf nsz float %1277, 1.500000e+00
  %1291 = fcmp reassoc ninf nsz olt float %1180, %1290
  br i1 %1291, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %1292 = fsub reassoc ninf nsz float %1180, %1290
  %1293 = fdiv reassoc ninf nsz float %1292, %1290
  %1294 = fcmp reassoc ninf nsz ogt float %1293, 1.000000e+00
  %spec.store.select.us = select i1 %1294, float 1.000000e+00, float %1293
  %1295 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %1296 = fsub reassoc ninf nsz float 1.000000e+00, %1295
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %1297 = fmul reassoc ninf nsz float %1180, 0x3FEE666660000000
  %1298 = fdiv reassoc ninf nsz float %1297, %1290
  %1299 = fadd reassoc ninf nsz float %1298, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.052.us = phi float [ %1299, %true_block30.us ], [ %1296, %false_block31.us ], [ %1289, %true_block36.us ], [ %1286, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %1300 = fcmp reassoc ninf nsz ogt float %1273, 0x3EB0C6F7A0000000
  br i1 %1300, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %1301 = fcmp reassoc ninf nsz ogt float %1269, 0x3EB0C6F7A0000000
  %1302 = fcmp reassoc ninf nsz ogt float %1272, 0x3EB0C6F7A0000000
  %.047.us = select i1 %1301, i1 %1302, i1 false
  br i1 %.047.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %1303 = fmul reassoc ninf nsz float %1252, %1209
  %1304 = fmul reassoc ninf nsz float %1266, %1223
  %1305 = fadd reassoc ninf nsz float %1304, %1303
  %1306 = fmul reassoc ninf nsz float %1272, %1269
  %1307 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1306)
  %1308 = fdiv reassoc ninf nsz float %1305, %1307
  %1309 = fcmp reassoc ninf nsz ogt float %1273, %1279
  %1310 = fcmp reassoc ninf nsz olt float %1308, 0x3FC99999A0000000
  %.046.us = select i1 %1309, i1 %1310, i1 false
  br i1 %.046.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %1311 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1308, float 0.000000e+00)
  %1312 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1273)
  %1313 = fmul reassoc ninf nsz float %1312, %164
  %1314 = fmul reassoc ninf nsz float %1313, %1311
  %1315 = fcmp reassoc ninf nsz ogt float %1314, 3.000000e+00
  br i1 %1315, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %1316 = fcmp reassoc ninf nsz olt float %1314, -3.000000e+00
  br i1 %1316, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %1317 = fmul reassoc ninf nsz float %1314, %1314
  %1318 = fadd reassoc ninf nsz float %1317, 2.700000e+01
  %1319 = fmul reassoc ninf nsz float %1318, %1314
  %1320 = fmul reassoc ninf nsz float %1317, 9.000000e+00
  %1321 = fadd reassoc ninf nsz float %1320, 2.700000e+01
  %1322 = fdiv reassoc ninf nsz float %1319, %1321
  %1323 = fadd reassoc ninf nsz float %1322, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %1324 = fsub reassoc ninf nsz float 1.500000e+00, %1308
  %1325 = fmul reassoc ninf nsz float %1324, %1180
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.053.us = phi float [ %1325, %true_block54.us ], [ %1180, %true_block42.us ], [ %1180, %after_if26.us ], [ %1180, %false_block55.us ], [ %1180, %false_block61.us ], [ %1180, %false_block58.us ]
  %.049.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %1323, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %1326 = fmul reassoc ninf nsz float %.049.us, %.052.us
  %1327 = fmul reassoc ninf nsz float %1326, %.053.us
  %1328 = fadd reassoc ninf nsz float %1327, %.15997.us
  %1329 = fadd reassoc ninf nsz float %1326, %.15798.us
  %lsr.iv.next582 = add i32 %lsr.iv581, 2
  %lsr.iv.next586 = add i32 %lsr.iv585, 2
  %lsr.iv.next590 = add i32 %lsr.iv589, 2
  %lsr.iv.next594 = add i32 %lsr.iv593, 2
  %lsr.iv.next598 = add i32 %lsr.iv597, 2
  %lsr.iv.next602 = add i32 %lsr.iv601, 2
  %lsr.iv.next604 = add i64 %lsr.iv603, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next604, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block390, %middle.block212
  %.lcssa136 = phi float [ %982, %middle.block212 ], [ %1165, %vec.epilog.middle.block390 ], [ %1328, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %981, %middle.block212 ], [ %1164, %vec.epilog.middle.block390 ], [ %1329, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %1330 = add nuw nsw i32 %.055103.us, 1
  %lsr.iv.next580 = add i32 %lsr.iv579, %187
  %lsr.iv.next584 = add i32 %lsr.iv583, %187
  %lsr.iv.next588 = add i32 %lsr.iv587, %184
  %lsr.iv.next592 = add i32 %lsr.iv591, %184
  %lsr.iv.next596 = add i32 %lsr.iv595, %187
  %lsr.iv.next600 = add i32 %lsr.iv599, %184
  %exitcond123.not = icmp eq i32 %1330, %168
  br i1 %exitcond123.not, label %after_for18, label %iter.check215

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %1331 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %1331, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %for_loop_body16.lr.ph, %true_block13
  %1332 = getelementptr i8, ptr %63, i64 4
  %1333 = getelementptr i8, ptr %63, i64 8
  %1334 = load ptr, ptr %1333, align 8
  %1335 = load i32, ptr %1332, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %60, i32 1)
  %smax129 = tail call i32 @llvm.smax.i32(i32 %58, i32 1)
  %wide.trip.count127 = zext i32 %smax to i64
  %1336 = add nsw i64 %wide.trip.count127, -1
  %1337 = mul i32 %52, %1335
  %1338 = add i32 %56, %1337
  %min.iters.check = icmp slt i32 %60, 4
  %1339 = trunc nsw i64 %1336 to i32
  %invariant.op573 = add i32 %1338, %1339
  %invariant.op575 = add i32 %121, %1339
  %1340 = icmp ugt i64 %1336, 4294967295
  %min.iters.check138 = icmp slt i32 %60, 32
  %n.vec = and i64 %wide.trip.count127, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count127
  %n.vec.remaining = and i64 %wide.trip.count127, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec152 = and i64 %wide.trip.count127, 2147483644
  %cmp.n158 = icmp eq i64 %n.vec152, %wide.trip.count127
  %xtraiter = and i64 %wide.trip.count127, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %1341 = lshr i64 %wide.trip.count127, 2
  %1342 = mul nsw i64 %1341, -4
  %1343 = zext i32 %121 to i64
  %1344 = zext i32 %114 to i64
  %1345 = zext i32 %1338 to i64
  %1346 = zext i32 %1335 to i64
  %1347 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %lsr.iv623 = phi i64 [ %lsr.iv.next624, %for_loop_test73.after_for72_crit_edge.us ], [ %1345, %for_loop_body66.lr.ph.split.us ]
  %lsr.iv621 = phi i64 [ %lsr.iv.next622, %for_loop_test73.after_for72_crit_edge.us ], [ %1343, %for_loop_body66.lr.ph.split.us ]
  %.042112.us = phi i32 [ 0, %for_loop_body66.lr.ph.split.us ], [ %1452, %for_loop_test73.after_for72_crit_edge.us ]
  %.043111.us = phi float [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ], [ %.lcssa137, %for_loop_test73.after_for72_crit_edge.us ]
  %lsr638 = trunc i64 %lsr.iv623 to i32
  %lsr636 = trunc i64 %lsr.iv621 to i32
  br i1 %min.iters.check, label %for_loop_body70.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %1348 = mul i32 %114, %.042112.us
  %1349 = add i32 %121, %1348
  %1350 = mul i32 %1335, %.042112.us
  %1351 = add i32 %1338, %1350
  %.reass574 = add i32 %1350, %invariant.op573
  %1352 = icmp slt i32 %.reass574, %1351
  %.reass576 = add i32 %1348, %invariant.op575
  %1353 = icmp slt i32 %.reass576, %1349
  %1354 = or i1 %1353, %1340
  %1355 = or i1 %1352, %1354
  br i1 %1355, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check138, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %1356 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.043111.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv613 = phi i32 [ %lsr.iv.next614, %vector.body ], [ %lsr636, %vector.ph ]
  %lsr.iv609 = phi i32 [ %lsr.iv.next610, %vector.body ], [ %lsr638, %vector.ph ]
  %lsr.iv605 = phi i64 [ %lsr.iv.next606, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %1356, %vector.ph ], [ %1375, %vector.body ]
  %vec.phi139 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1376, %vector.body ]
  %vec.phi140 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1377, %vector.body ]
  %vec.phi141 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1378, %vector.body ]
  %1357 = sext i32 %lsr.iv609 to i64
  %1358 = getelementptr float, ptr %1334, i64 %1357
  %1359 = getelementptr i8, ptr %1358, i64 32
  %1360 = getelementptr i8, ptr %1358, i64 64
  %1361 = getelementptr i8, ptr %1358, i64 96
  %wide.load = load <8 x float>, ptr %1358, align 4
  %wide.load142 = load <8 x float>, ptr %1359, align 4
  %wide.load143 = load <8 x float>, ptr %1360, align 4
  %wide.load144 = load <8 x float>, ptr %1361, align 4
  %1362 = sext i32 %lsr.iv613 to i64
  %1363 = getelementptr float, ptr %112, i64 %1362
  %1364 = getelementptr i8, ptr %1363, i64 32
  %1365 = getelementptr i8, ptr %1363, i64 64
  %1366 = getelementptr i8, ptr %1363, i64 96
  %wide.load145 = load <8 x float>, ptr %1363, align 4
  %wide.load146 = load <8 x float>, ptr %1364, align 4
  %wide.load147 = load <8 x float>, ptr %1365, align 4
  %wide.load148 = load <8 x float>, ptr %1366, align 4
  %1367 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load145
  %1368 = fsub reassoc ninf nsz <8 x float> %wide.load142, %wide.load146
  %1369 = fsub reassoc ninf nsz <8 x float> %wide.load143, %wide.load147
  %1370 = fsub reassoc ninf nsz <8 x float> %wide.load144, %wide.load148
  %1371 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1367)
  %1372 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1368)
  %1373 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1369)
  %1374 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1370)
  %1375 = fadd reassoc ninf nsz <8 x float> %1371, %vec.phi
  %1376 = fadd reassoc ninf nsz <8 x float> %1372, %vec.phi139
  %1377 = fadd reassoc ninf nsz <8 x float> %1373, %vec.phi140
  %1378 = fadd reassoc ninf nsz <8 x float> %1374, %vec.phi141
  %lsr.iv.next606 = add nsw i64 %lsr.iv605, -32
  %lsr.iv.next610 = add i32 %lsr.iv609, 32
  %lsr.iv.next614 = add i32 %lsr.iv613, 32
  %1379 = icmp eq i64 %lsr.iv.next606, 0
  br i1 %1379, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %1376, %1375
  %bin.rdx149 = fadd reassoc ninf nsz <8 x float> %1377, %bin.rdx
  %bin.rdx150 = fadd reassoc ninf nsz <8 x float> %1378, %bin.rdx149
  %1380 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx150)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %1380, %vec.epilog.iter.check ], [ %.043111.us, %vector.main.loop.iter.check ]
  %1381 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %1382 = add i64 %1342, %vec.epilog.resume.val
  %1383 = trunc i64 %vec.epilog.resume.val to i32
  %1384 = add i32 %lsr638, %1383
  %1385 = add i32 %lsr636, %1383
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv619 = phi i32 [ %lsr.iv.next620, %vec.epilog.vector.body ], [ %1385, %vec.epilog.ph ]
  %lsr.iv617 = phi i32 [ %lsr.iv.next618, %vec.epilog.vector.body ], [ %1384, %vec.epilog.ph ]
  %lsr.iv615 = phi i64 [ %lsr.iv.next616, %vec.epilog.vector.body ], [ %1382, %vec.epilog.ph ]
  %vec.phi154 = phi <4 x float> [ %1381, %vec.epilog.ph ], [ %1392, %vec.epilog.vector.body ]
  %1386 = sext i32 %lsr.iv617 to i64
  %1387 = getelementptr float, ptr %1334, i64 %1386
  %wide.load155 = load <4 x float>, ptr %1387, align 4
  %1388 = sext i32 %lsr.iv619 to i64
  %1389 = getelementptr float, ptr %112, i64 %1388
  %wide.load156 = load <4 x float>, ptr %1389, align 4
  %1390 = fsub reassoc ninf nsz <4 x float> %wide.load155, %wide.load156
  %1391 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %1390)
  %1392 = fadd reassoc ninf nsz <4 x float> %1391, %vec.phi154
  %lsr.iv.next616 = add i64 %lsr.iv615, 4
  %lsr.iv.next618 = add i32 %lsr.iv617, 4
  %lsr.iv.next620 = add i32 %lsr.iv619, 4
  %1393 = icmp eq i64 %lsr.iv.next616, 0
  br i1 %1393, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %1394 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %1392)
  br i1 %cmp.n158, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv124.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec152, %vec.epilog.middle.block ]
  %.1107.us.ph = phi float [ %1380, %vec.epilog.iter.check ], [ %.043111.us, %iter.check ], [ %.043111.us, %vector.scevcheck ], [ %1394, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv626 = phi i64 [ %1347, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next627, %for_loop_body70.us.prol ]
  %indvars.iv124.prol = phi i64 [ %indvars.iv.next125.prol, %for_loop_body70.us.prol ], [ %indvars.iv124.ph, %for_loop_body70.us.prol.preheader ]
  %.1107.us.prol = phi float [ %1405, %for_loop_body70.us.prol ], [ %.1107.us.ph, %for_loop_body70.us.prol.preheader ]
  %1395 = add i64 %lsr.iv623, %indvars.iv124.prol
  %tmp625 = trunc i64 %1395 to i32
  %1396 = sext i32 %tmp625 to i64
  %1397 = getelementptr float, ptr %1334, i64 %1396
  %1398 = load float, ptr %1397, align 4
  %1399 = add i64 %lsr.iv621, %indvars.iv124.prol
  %tmp = trunc i64 %1399 to i32
  %1400 = sext i32 %tmp to i64
  %1401 = getelementptr float, ptr %112, i64 %1400
  %1402 = load float, ptr %1401, align 4
  %1403 = fsub reassoc ninf nsz float %1398, %1402
  %1404 = tail call noundef float @llvm.fabs.f32(float %1403)
  %1405 = fadd reassoc ninf nsz float %1404, %.1107.us.prol
  %indvars.iv.next125.prol = add nuw nsw i64 %indvars.iv124.prol, 1
  %lsr.iv.next627 = add nsw i64 %lsr.iv626, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next627, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa501.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %1405, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv124.unr = phi i64 [ %indvars.iv124.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next125.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1107.us.unr = phi float [ %.1107.us.ph, %for_loop_body70.us.preheader ], [ %1405, %for_loop_body70.us.prol.loopexit.loopexit ]
  %1406 = sub nsw i64 %indvars.iv124.ph, %wide.trip.count127
  %1407 = icmp ugt i64 %1406, -4
  br i1 %1407, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader.new

for_loop_body70.us.preheader.new:                 ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader.new
  %indvars.iv124 = phi i64 [ %indvars.iv124.unr, %for_loop_body70.us.preheader.new ], [ %indvars.iv.next125.3, %for_loop_body70.us ]
  %.1107.us = phi float [ %.1107.us.unr, %for_loop_body70.us.preheader.new ], [ %1451, %for_loop_body70.us ]
  %1408 = add i64 %lsr.iv623, %indvars.iv124
  %tmp635 = trunc i64 %1408 to i32
  %1409 = sext i32 %tmp635 to i64
  %1410 = getelementptr float, ptr %1334, i64 %1409
  %1411 = load float, ptr %1410, align 4
  %1412 = add i64 %lsr.iv621, %indvars.iv124
  %tmp634 = trunc i64 %1412 to i32
  %1413 = sext i32 %tmp634 to i64
  %1414 = getelementptr float, ptr %112, i64 %1413
  %1415 = load float, ptr %1414, align 4
  %1416 = fsub reassoc ninf nsz float %1411, %1415
  %1417 = tail call noundef float @llvm.fabs.f32(float %1416)
  %1418 = fadd reassoc ninf nsz float %1417, %.1107.us
  %1419 = add i64 %1408, 1
  %tmp633 = trunc i64 %1419 to i32
  %1420 = sext i32 %tmp633 to i64
  %1421 = getelementptr float, ptr %1334, i64 %1420
  %1422 = load float, ptr %1421, align 4
  %1423 = add i64 %1412, 1
  %tmp632 = trunc i64 %1423 to i32
  %1424 = sext i32 %tmp632 to i64
  %1425 = getelementptr float, ptr %112, i64 %1424
  %1426 = load float, ptr %1425, align 4
  %1427 = fsub reassoc ninf nsz float %1422, %1426
  %1428 = tail call noundef float @llvm.fabs.f32(float %1427)
  %1429 = fadd reassoc ninf nsz float %1428, %1418
  %1430 = add i64 %1408, 2
  %tmp631 = trunc i64 %1430 to i32
  %1431 = sext i32 %tmp631 to i64
  %1432 = getelementptr float, ptr %1334, i64 %1431
  %1433 = load float, ptr %1432, align 4
  %1434 = add i64 %1412, 2
  %tmp630 = trunc i64 %1434 to i32
  %1435 = sext i32 %tmp630 to i64
  %1436 = getelementptr float, ptr %112, i64 %1435
  %1437 = load float, ptr %1436, align 4
  %1438 = fsub reassoc ninf nsz float %1433, %1437
  %1439 = tail call noundef float @llvm.fabs.f32(float %1438)
  %1440 = fadd reassoc ninf nsz float %1439, %1429
  %1441 = add i64 %1408, 3
  %tmp629 = trunc i64 %1441 to i32
  %1442 = sext i32 %tmp629 to i64
  %1443 = getelementptr float, ptr %1334, i64 %1442
  %1444 = load float, ptr %1443, align 4
  %1445 = add i64 %1412, 3
  %tmp628 = trunc i64 %1445 to i32
  %1446 = sext i32 %tmp628 to i64
  %1447 = getelementptr float, ptr %112, i64 %1446
  %1448 = load float, ptr %1447, align 4
  %1449 = fsub reassoc ninf nsz float %1444, %1448
  %1450 = tail call noundef float @llvm.fabs.f32(float %1449)
  %1451 = fadd reassoc ninf nsz float %1450, %1440
  %indvars.iv.next125.3 = add nuw nsw i64 %indvars.iv124, 4
  %exitcond128.not.3 = icmp eq i64 %wide.trip.count127, %indvars.iv.next125.3
  br i1 %exitcond128.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa137 = phi float [ %1380, %middle.block ], [ %1394, %vec.epilog.middle.block ], [ %.lcssa501.unr, %for_loop_body70.us.prol.loopexit ], [ %1451, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %1452 = add nuw nsw i32 %.042112.us, 1
  %lsr.iv.next624 = add i64 %lsr.iv623, %1346
  %lsr.iv.next622 = add i64 %lsr.iv621, %1344
  %exitcond130.not = icmp eq i32 %1452, %smax129
  br i1 %exitcond130.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %1453 = fdiv reassoc ninf nsz float %.lcssa136, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.044 = phi float [ %1464, %after_for68 ], [ %1453, %false_block64 ]
  %1454 = fmul reassoc ninf nsz float %69, %65
  %1455 = fsub reassoc ninf nsz float %.044, %1454
  %1456 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1455, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %67
  %1457 = fmul reassoc ninf nsz float %1456, %neg
  %1458 = tail call noundef float @expf(float noundef %1457) #9
  %1459 = fmul reassoc ninf nsz float %.062, %.063
  %1460 = fmul reassoc ninf nsz float %1459, %1458
  %1461 = fcmp reassoc ninf nsz olt float %1460, 0x3EB0C6F7A0000000
  %spec.store.select2 = select i1 %1461, float 0.000000e+00, float %1460
  br label %after_if3

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %1462 = mul i32 %60, %58
  %1463 = sitofp i32 %1462 to float
  %1464 = fdiv reassoc ninf nsz float %.lcssa137, %1463
  br label %after_if65
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.62, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #9
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !21

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #9
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !23

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <4 x float> @llvm.fabs.v4f32(<4 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.sqrt.v8f32(<8 x float>) #6

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #9 = { nounwind }

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
!14 = distinct !{!14, !12, !13}
!15 = distinct !{!15, !12}
!16 = distinct !{!16, !12, !13}
!17 = distinct !{!17, !12, !13}
!18 = distinct !{!18, !19}
!19 = !{!"llvm.loop.unroll.disable"}
!20 = distinct !{!20, !12}
!21 = distinct !{!21, !22}
!22 = !{!"llvm.loop.mustprogress"}
!23 = distinct !{!23, !22}
