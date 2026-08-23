; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase2_fine_analysis_kernel_c86_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 184
  %2 = load i32, ptr %1, align 4
  %3 = sdiv i32 %2, 2
  %4 = icmp slt i32 %2, 0
  %5 = shl nsw i32 %3, 1
  %6 = icmp ne i32 %5, %2
  %7 = and i1 %4, %6
  %.neg = sext i1 %7 to i32
  %8 = add nsw i32 %3, %.neg
  %9 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 8
  store i32 %8, ptr %13, align 4
  %14 = and i32 %2, 1
  %15 = load ptr, ptr %9, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 32872
  %17 = load ptr, ptr %16, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 12
  store i32 %14, ptr %18, align 4
  %19 = load ptr, ptr %context, align 8
  %20 = getelementptr i8, ptr %19, i64 152
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 168
  %23 = load i32, ptr %22, align 4
  %24 = sub i32 %21, %8
  %25 = add i32 %24, 1
  %26 = sdiv i32 %25, 2
  %27 = icmp slt i32 %25, 0
  %28 = shl nsw i32 %26, 1
  %29 = icmp ne i32 %28, %25
  %30 = and i1 %27, %29
  %.neg1 = sext i1 %30 to i32
  %31 = add nsw i32 %26, %.neg1
  %32 = sub i32 %23, %14
  %33 = add i32 %32, 1
  %34 = sdiv i32 %33, 2
  %35 = icmp slt i32 %33, 0
  %36 = shl nsw i32 %34, 1
  %37 = icmp ne i32 %36, %33
  %38 = and i1 %35, %37
  %.neg2 = sext i1 %38 to i32
  %39 = add nsw i32 %34, %.neg2
  %40 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %41 = tail call i32 @llvm.smax.i32(i32 %39, i32 0)
  %42 = load ptr, ptr %9, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 4
  store i32 %41, ptr %45, align 4
  %46 = mul i32 %41, %40
  %47 = load ptr, ptr %9, align 8
  %48 = getelementptr inbounds nuw i8, ptr %47, i64 32872
  %49 = load ptr, ptr %48, align 8
  store i32 %46, ptr %49, align 4
  ret void
}

define void @phase2_fine_analysis_kernel_c86_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 188
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 196
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 192
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 200
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 160
  %30 = getelementptr i8, ptr %19, i64 176
  %31 = add i32 %27, -1
  %32 = add i32 %23, -1
  %33 = icmp sgt i32 %21, 1
  %34 = icmp sgt i32 %25, 1
  %35 = add nsw i32 %21, -1
  %36 = uitofp nneg i32 %35 to float
  %37 = add nsw i32 %25, -1
  %38 = uitofp nneg i32 %37 to float
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.055110 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %85, %after_if3 ]
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 4
  %43 = load i32, ptr %42, align 4
  %44 = sdiv i32 %.055110, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.055110
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %45, %.055110
  %49 = and i1 %47, %48
  %.neg83 = sext i1 %49 to i32
  %50 = add i32 %44, %.neg83
  %51 = mul i32 %50, %43
  %52 = sub i32 %.055110, %51
  %53 = shl i32 %50, 1
  %54 = getelementptr inbounds nuw i8, ptr %41, i64 8
  %55 = load i32, ptr %54, align 4
  %56 = add i32 %53, %55
  %57 = shl i32 %52, 1
  %58 = getelementptr inbounds nuw i8, ptr %41, i64 12
  %59 = load i32, ptr %58, align 4
  %60 = add i32 %57, %59
  %61 = load ptr, ptr %29, align 8
  %62 = sext i32 %56 to i64
  %63 = getelementptr i32, ptr %61, i64 %62
  %64 = load i32, ptr %63, align 4
  %65 = load ptr, ptr %30, align 8
  %66 = sext i32 %60 to i64
  %67 = getelementptr i32, ptr %65, i64 %66
  %68 = load i32, ptr %67, align 4
  %69 = sub i32 %23, %64
  %70 = tail call i32 @llvm.smin.i32(i32 %21, i32 %69)
  %71 = sub i32 %27, %68
  %72 = tail call i32 @llvm.smin.i32(i32 %25, i32 %71)
  %73 = icmp sgt i32 %70, 0
  %74 = icmp sgt i32 %72, 0
  %spec.select = select i1 %73, i1 %74, i1 false
  br i1 %spec.select, label %true_block1, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %75 = lshr i32 %72, 1
  %76 = add i32 %75, %68
  %77 = tail call i32 @llvm.smin.i32(i32 %76, i32 %31)
  %78 = lshr i32 %70, 1
  %79 = add i32 %78, %64
  %80 = tail call i32 @llvm.smin.i32(i32 %79, i32 %32)
  %81 = load ptr, ptr %0, align 8
  %82 = getelementptr i8, ptr %81, i64 220
  %83 = load i32, ptr %82, align 4
  %84 = icmp eq i32 %83, 1
  br i1 %84, label %true_block4, label %after_if6

after_if3.loopexit:                               ; preds = %after_if86
  br label %after_if3

after_if3:                                        ; preds = %true_block74, %after_if65, %after_if9, %after_if3.loopexit, %for_loop_body
  %85 = add nsw i32 %.055110, 1
  %exitcond134.not = icmp eq i32 %85, %18
  br i1 %exitcond134.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %86 = getelementptr i8, ptr %81, i64 104
  %87 = load ptr, ptr %86, align 8
  %88 = getelementptr i8, ptr %81, i64 100
  %89 = load i32, ptr %88, align 4
  %90 = sext i32 %89 to i64
  %91 = sext i32 %80 to i64
  %92 = mul nsw i64 %90, %91
  %93 = sext i32 %77 to i64
  %94 = getelementptr float, ptr %87, i64 %92
  %95 = getelementptr float, ptr %94, i64 %93
  %96 = load float, ptr %95, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.067 = phi float [ %96, %true_block4 ], [ 1.000000e+00, %true_block1 ]
  %97 = getelementptr i8, ptr %81, i64 216
  %98 = load i32, ptr %97, align 4
  %99 = icmp eq i32 %98, 1
  br i1 %99, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %100 = getelementptr i8, ptr %81, i64 120
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr i8, ptr %81, i64 116
  %103 = load i32, ptr %102, align 4
  %104 = sext i32 %103 to i64
  %105 = sext i32 %80 to i64
  %106 = mul nsw i64 %104, %105
  %107 = sext i32 %77 to i64
  %108 = getelementptr float, ptr %101, i64 %106
  %109 = getelementptr float, ptr %108, i64 %107
  %110 = load float, ptr %109, align 4
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.066 = phi float [ %110, %true_block7 ], [ 1.000000e+00, %after_if6 ]
  %111 = getelementptr i8, ptr %81, i64 224
  %112 = load float, ptr %111, align 4
  %113 = fcmp reassoc ninf nsz oge float %.067, %112
  %114 = fcmp reassoc ninf nsz oge float %.066, %112
  %.065 = select i1 %113, i1 %114, i1 false
  br i1 %.065, label %true_block13, label %after_if3

true_block13:                                     ; preds = %after_if9
  %115 = getelementptr i8, ptr %81, i64 24
  %116 = load ptr, ptr %115, align 8
  %117 = getelementptr i8, ptr %81, i64 20
  %118 = load i32, ptr %117, align 4
  %119 = sext i32 %118 to i64
  %120 = sext i32 %79 to i64
  %121 = mul nsw i64 %119, %120
  %122 = sext i32 %76 to i64
  %123 = getelementptr float, ptr %116, i64 %121
  %124 = getelementptr float, ptr %123, i64 %122
  %125 = load float, ptr %124, align 4
  %126 = sext i32 %64 to i64
  %127 = mul nsw i64 %119, %126
  %128 = sext i32 %68 to i64
  %129 = getelementptr float, ptr %116, i64 %127
  %130 = getelementptr float, ptr %129, i64 %128
  %131 = load float, ptr %130, align 4
  %132 = add nsw i32 %72, -1
  %133 = add i32 %132, %68
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %129, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add nsw i32 %70, -1
  %138 = add i32 %137, %64
  %139 = sext i32 %138 to i64
  %140 = mul nsw i64 %119, %139
  %141 = getelementptr float, ptr %116, i64 %140
  %142 = getelementptr float, ptr %141, i64 %128
  %143 = load float, ptr %142, align 4
  %144 = getelementptr float, ptr %141, i64 %134
  %145 = load float, ptr %144, align 4
  %146 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %143, float %145)
  %147 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %136, float %146)
  %148 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float %147)
  %149 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %125, float %148)
  %150 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %143, float %145)
  %151 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %136, float %150)
  %152 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float %151)
  %153 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %125, float %152)
  %154 = fadd reassoc ninf nsz float %131, %125
  %155 = fadd reassoc ninf nsz float %154, %136
  %156 = fadd reassoc ninf nsz float %155, %143
  %157 = fadd reassoc ninf nsz float %156, %145
  %158 = fmul reassoc ninf nsz float %157, 0x3FC99999A0000000
  %159 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %158, float 0x3FA99999A0000000)
  %160 = fmul reassoc ninf nsz float %159, 0x3FBEB851E0000000
  %161 = fmul reassoc ninf nsz float %159, 0x3FB47AE140000000
  %162 = fsub reassoc ninf nsz float %149, %153
  %163 = fadd reassoc ninf nsz float %162, %160
  %164 = fdiv reassoc ninf nsz float %163, %161
  %165 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %164, float 1.000000e+00)
  %166 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %165, float 0.000000e+00)
  %167 = getelementptr i8, ptr %81, i64 204
  %168 = load float, ptr %167, align 4
  %169 = fmul reassoc ninf nsz float %166, 6.075000e+02
  %170 = fadd reassoc ninf nsz float %169, 2.025000e+02
  %171 = fmul reassoc ninf nsz float %168, 0x3FC99999A0000000
  %172 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %171, float 0x3F747AE140000000)
  %173 = fcmp reassoc ninf nsz ogt float %168, 0x3EB0C6F7A0000000
  %174 = add i32 %64, 1
  %175 = add i32 %68, 1
  %.not = icmp samesign ult i32 %70, 3
  %.not111 = icmp samesign ult i32 %72, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not111
  br i1 %or.cond, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %true_block13
  %176 = lshr i32 %132, 1
  %177 = lshr i32 %137, 1
  %178 = getelementptr i8, ptr %81, i64 84
  %179 = getelementptr i8, ptr %81, i64 88
  %180 = getelementptr i8, ptr %81, i64 68
  %181 = getelementptr i8, ptr %81, i64 72
  %182 = getelementptr i8, ptr %81, i64 52
  %183 = getelementptr i8, ptr %81, i64 56
  %184 = getelementptr i8, ptr %81, i64 36
  %185 = getelementptr i8, ptr %81, i64 40
  %186 = getelementptr i8, ptr %81, i64 4
  %187 = getelementptr i8, ptr %81, i64 8
  %188 = load ptr, ptr %187, align 8
  %189 = load i32, ptr %186, align 4
  %190 = sext i32 %189 to i64
  %191 = load ptr, ptr %185, align 8
  %192 = load i32, ptr %184, align 4
  %193 = sext i32 %192 to i64
  %194 = load ptr, ptr %183, align 8
  %195 = load i32, ptr %182, align 4
  %196 = sext i32 %195 to i64
  %197 = load ptr, ptr %181, align 8
  %198 = load i32, ptr %180, align 4
  %199 = sext i32 %198 to i64
  %200 = load ptr, ptr %179, align 8
  %201 = load i32, ptr %178, align 4
  %202 = sext i32 %201 to i64
  %wide.trip.count120 = zext nneg i32 %177 to i64
  %wide.trip.count = zext i32 %176 to i64
  %203 = add nsw i64 %wide.trip.count, -1
  %min.iters.check165 = icmp ult i32 %72, 17
  %204 = trunc nsw i64 %203 to i32
  %mul.result = shl i32 %204, 1
  %205 = add i32 %175, %mul.result
  %206 = icmp slt i32 %205, %175
  %207 = icmp ugt i64 %203, 4294967295
  %208 = or i1 %206, %207
  %min.iters.check168 = icmp ult i32 %72, 65
  %n.vec172 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %173, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %209 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert183 = insertelement <8 x i32> poison, i32 %175, i64 0
  %broadcast.splat184 = shufflevector <8 x i32> %broadcast.splatinsert183, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert208 = insertelement <8 x float> poison, float %172, i64 0
  %broadcast.splat209 = shufflevector <8 x float> %broadcast.splatinsert208, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert225 = insertelement <8 x float> poison, float %170, i64 0
  %broadcast.splat226 = shufflevector <8 x float> %broadcast.splatinsert225, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat184
  %invariant.op381 = add <8 x i32> splat (i32 32), %broadcast.splat184
  %invariant.op383 = add <8 x i32> splat (i32 48), %broadcast.splat184
  %cmp.n274 = icmp eq i64 %n.vec172, %wide.trip.count
  %n.vec.remaining282 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check283 = icmp eq i64 %n.vec.remaining282, 0
  %n.vec285 = and i64 %wide.trip.count, 2147483640
  %cmp.n321 = icmp eq i64 %n.vec285, %wide.trip.count
  %210 = zext i32 %132 to i64
  %211 = lshr i64 %210, 4
  %212 = mul nsw i64 %211, -8
  %213 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check167

iter.check167:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %indvars.iv117 = phi i64 [ %indvars.iv.next118, %for_loop_test23.after_for22_crit_edge.us ], [ 0, %for_loop_body16.lr.ph.split.us ]
  %.06197.us = phi float [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ], [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ]
  %.06396.us = phi float [ %.lcssa139, %for_loop_test23.after_for22_crit_edge.us ], [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ]
  %indvars.iv117.tr = trunc i64 %indvars.iv117 to i32
  %214 = shl i32 %indvars.iv117.tr, 1
  %215 = add i32 %174, %214
  %216 = sext i32 %215 to i64
  %217 = mul nsw i64 %190, %216
  %218 = getelementptr float, ptr %188, i64 %217
  %219 = mul nsw i64 %216, %119
  %220 = getelementptr float, ptr %116, i64 %219
  %221 = mul nsw i64 %193, %216
  %222 = getelementptr float, ptr %191, i64 %221
  %223 = mul nsw i64 %196, %216
  %224 = getelementptr float, ptr %194, i64 %223
  %225 = mul nsw i64 %199, %216
  %226 = getelementptr float, ptr %197, i64 %225
  %227 = mul nsw i64 %202, %216
  %228 = getelementptr float, ptr %200, i64 %227
  %brmerge = select i1 %min.iters.check165, i1 true, i1 %208
  br i1 %brmerge, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check169

vector.main.loop.iter.check169:                   ; preds = %iter.check167
  br i1 %min.iters.check168, label %vec.epilog.ph280, label %vector.ph170

vector.ph170:                                     ; preds = %vector.main.loop.iter.check169
  %229 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06197.us, i64 0
  %230 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06396.us, i64 0
  br label %vector.body173

vector.body173:                                   ; preds = %vector.body173, %vector.ph170
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body173 ], [ %n.vec172, %vector.ph170 ]
  %vec.phi175 = phi <8 x float> [ %229, %vector.ph170 ], [ %625, %vector.body173 ]
  %vec.phi176 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %626, %vector.body173 ]
  %vec.phi177 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %627, %vector.body173 ]
  %vec.phi178 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %628, %vector.body173 ]
  %vec.phi179 = phi <8 x float> [ %230, %vector.ph170 ], [ %621, %vector.body173 ]
  %vec.phi180 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %622, %vector.body173 ]
  %vec.phi181 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %623, %vector.body173 ]
  %vec.phi182 = phi <8 x float> [ zeroinitializer, %vector.ph170 ], [ %624, %vector.body173 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph170 ], [ %vec.ind.next, %vector.body173 ]
  %231 = shl <8 x i32> %vec.ind, splat (i32 1)
  %232 = add <8 x i32> %broadcast.splat184, %231
  %.reass = add <8 x i32> %231, %invariant.op
  %.reass382 = add <8 x i32> %231, %invariant.op381
  %.reass384 = add <8 x i32> %231, %invariant.op383
  %233 = sext <8 x i32> %232 to <8 x i64>
  %234 = sext <8 x i32> %.reass to <8 x i64>
  %235 = sext <8 x i32> %.reass382 to <8 x i64>
  %236 = sext <8 x i32> %.reass384 to <8 x i64>
  %237 = getelementptr float, ptr %218, <8 x i64> %233
  %238 = getelementptr float, ptr %218, <8 x i64> %234
  %239 = getelementptr float, ptr %218, <8 x i64> %235
  %240 = getelementptr float, ptr %218, <8 x i64> %236
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %237, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather185 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %238, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather186 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %239, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather187 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %240, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %241 = getelementptr float, ptr %220, <8 x i64> %233
  %242 = getelementptr float, ptr %220, <8 x i64> %234
  %243 = getelementptr float, ptr %220, <8 x i64> %235
  %244 = getelementptr float, ptr %220, <8 x i64> %236
  %wide.masked.gather188 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %241, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather189 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %242, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather190 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %243, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather191 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %244, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %245 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather188
  %246 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather185, %wide.masked.gather189
  %247 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather186, %wide.masked.gather190
  %248 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather187, %wide.masked.gather191
  %249 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %245)
  %250 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %246)
  %251 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %247)
  %252 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %248)
  %253 = getelementptr float, ptr %222, <8 x i64> %233
  %254 = getelementptr float, ptr %222, <8 x i64> %234
  %255 = getelementptr float, ptr %222, <8 x i64> %235
  %256 = getelementptr float, ptr %222, <8 x i64> %236
  %wide.masked.gather192 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %253, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather193 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %254, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather194 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %255, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather195 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %256, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %257 = getelementptr float, ptr %224, <8 x i64> %233
  %258 = getelementptr float, ptr %224, <8 x i64> %234
  %259 = getelementptr float, ptr %224, <8 x i64> %235
  %260 = getelementptr float, ptr %224, <8 x i64> %236
  %wide.masked.gather196 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %257, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather197 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %258, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather198 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %259, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather199 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %260, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %261 = getelementptr float, ptr %226, <8 x i64> %233
  %262 = getelementptr float, ptr %226, <8 x i64> %234
  %263 = getelementptr float, ptr %226, <8 x i64> %235
  %264 = getelementptr float, ptr %226, <8 x i64> %236
  %wide.masked.gather200 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %261, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather201 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %262, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather202 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %263, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %264, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %265 = getelementptr float, ptr %228, <8 x i64> %233
  %266 = getelementptr float, ptr %228, <8 x i64> %234
  %267 = getelementptr float, ptr %228, <8 x i64> %235
  %268 = getelementptr float, ptr %228, <8 x i64> %236
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %265, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather205 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %266, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather206 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %267, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather207 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %268, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %269 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather192, %wide.masked.gather192
  %270 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather193, %wide.masked.gather193
  %271 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather194, %wide.masked.gather194
  %272 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather195, %wide.masked.gather195
  %273 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather196, %wide.masked.gather196
  %274 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather197, %wide.masked.gather197
  %275 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather198, %wide.masked.gather198
  %276 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather199, %wide.masked.gather199
  %277 = fadd reassoc ninf nsz <8 x float> %273, %269
  %278 = fadd reassoc ninf nsz <8 x float> %274, %270
  %279 = fadd reassoc ninf nsz <8 x float> %275, %271
  %280 = fadd reassoc ninf nsz <8 x float> %276, %272
  %281 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather200, %wide.masked.gather200
  %282 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather201, %wide.masked.gather201
  %283 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather202
  %284 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather203
  %285 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather204
  %286 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather205
  %287 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather206, %wide.masked.gather206
  %288 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather207, %wide.masked.gather207
  %289 = fadd reassoc ninf nsz <8 x float> %285, %281
  %290 = fadd reassoc ninf nsz <8 x float> %286, %282
  %291 = fadd reassoc ninf nsz <8 x float> %287, %283
  %292 = fadd reassoc ninf nsz <8 x float> %288, %284
  %293 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %277, <8 x float> %289)
  %294 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %278, <8 x float> %290)
  %295 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %279, <8 x float> %291)
  %296 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %280, <8 x float> %292)
  %297 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather188, splat (float -2.000000e+00)
  %298 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather189, splat (float -2.000000e+00)
  %299 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather190, splat (float -2.000000e+00)
  %300 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather191, splat (float -2.000000e+00)
  %301 = fadd reassoc ninf nsz <8 x float> %297, splat (float 3.000000e+00)
  %302 = fadd reassoc ninf nsz <8 x float> %298, splat (float 3.000000e+00)
  %303 = fadd reassoc ninf nsz <8 x float> %299, splat (float 3.000000e+00)
  %304 = fadd reassoc ninf nsz <8 x float> %300, splat (float 3.000000e+00)
  %305 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %301, <8 x float> splat (float 3.000000e+00))
  %306 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %302, <8 x float> splat (float 3.000000e+00))
  %307 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %303, <8 x float> splat (float 3.000000e+00))
  %308 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %304, <8 x float> splat (float 3.000000e+00))
  %309 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %305, <8 x float> splat (float 1.000000e+00))
  %310 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %306, <8 x float> splat (float 1.000000e+00))
  %311 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %307, <8 x float> splat (float 1.000000e+00))
  %312 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %308, <8 x float> splat (float 1.000000e+00))
  %313 = fmul reassoc ninf nsz <8 x float> %309, %broadcast.splat209
  %314 = fmul reassoc ninf nsz <8 x float> %310, %broadcast.splat209
  %315 = fmul reassoc ninf nsz <8 x float> %311, %broadcast.splat209
  %316 = fmul reassoc ninf nsz <8 x float> %312, %broadcast.splat209
  %317 = fcmp reassoc ninf nsz olt <8 x float> %293, splat (float 1.500000e+02)
  %318 = fcmp reassoc ninf nsz olt <8 x float> %294, splat (float 1.500000e+02)
  %319 = fcmp reassoc ninf nsz olt <8 x float> %295, splat (float 1.500000e+02)
  %320 = fcmp reassoc ninf nsz olt <8 x float> %296, splat (float 1.500000e+02)
  %321 = xor <8 x i1> %317, splat (i1 true)
  %322 = xor <8 x i1> %318, splat (i1 true)
  %323 = xor <8 x i1> %319, splat (i1 true)
  %324 = xor <8 x i1> %320, splat (i1 true)
  %325 = select <8 x i1> %broadcast.splat, <8 x i1> %321, <8 x i1> zeroinitializer
  %326 = select <8 x i1> %broadcast.splat, <8 x i1> %322, <8 x i1> zeroinitializer
  %327 = select <8 x i1> %broadcast.splat, <8 x i1> %323, <8 x i1> zeroinitializer
  %328 = select <8 x i1> %broadcast.splat, <8 x i1> %324, <8 x i1> zeroinitializer
  %329 = fcmp reassoc ninf nsz olt <8 x float> %249, %313
  %330 = fcmp reassoc ninf nsz olt <8 x float> %250, %314
  %331 = fcmp reassoc ninf nsz olt <8 x float> %251, %315
  %332 = fcmp reassoc ninf nsz olt <8 x float> %252, %316
  %333 = xor <8 x i1> %329, splat (i1 true)
  %334 = xor <8 x i1> %330, splat (i1 true)
  %335 = xor <8 x i1> %331, splat (i1 true)
  %336 = xor <8 x i1> %332, splat (i1 true)
  %337 = select <8 x i1> %325, <8 x i1> %333, <8 x i1> zeroinitializer
  %338 = select <8 x i1> %326, <8 x i1> %334, <8 x i1> zeroinitializer
  %339 = select <8 x i1> %327, <8 x i1> %335, <8 x i1> zeroinitializer
  %340 = select <8 x i1> %328, <8 x i1> %336, <8 x i1> zeroinitializer
  %341 = fmul reassoc ninf nsz <8 x float> %313, splat (float 4.000000e+00)
  %342 = fmul reassoc ninf nsz <8 x float> %314, splat (float 4.000000e+00)
  %343 = fmul reassoc ninf nsz <8 x float> %315, splat (float 4.000000e+00)
  %344 = fmul reassoc ninf nsz <8 x float> %316, splat (float 4.000000e+00)
  %345 = fdiv reassoc ninf nsz <8 x float> %249, %341
  %346 = fdiv reassoc ninf nsz <8 x float> %250, %342
  %347 = fdiv reassoc ninf nsz <8 x float> %251, %343
  %348 = fdiv reassoc ninf nsz <8 x float> %252, %344
  %349 = fcmp reassoc ninf nsz ogt <8 x float> %345, splat (float 1.000000e+00)
  %350 = fcmp reassoc ninf nsz ogt <8 x float> %346, splat (float 1.000000e+00)
  %351 = fcmp reassoc ninf nsz ogt <8 x float> %347, splat (float 1.000000e+00)
  %352 = fcmp reassoc ninf nsz ogt <8 x float> %348, splat (float 1.000000e+00)
  %353 = select <8 x i1> %349, <8 x float> splat (float 1.000000e+00), <8 x float> %345
  %354 = select <8 x i1> %350, <8 x float> splat (float 1.000000e+00), <8 x float> %346
  %355 = select <8 x i1> %351, <8 x float> splat (float 1.000000e+00), <8 x float> %347
  %356 = select <8 x i1> %352, <8 x float> splat (float 1.000000e+00), <8 x float> %348
  %357 = fmul reassoc ninf nsz <8 x float> %353, splat (float 0x3FD99999A0000000)
  %358 = fmul reassoc ninf nsz <8 x float> %354, splat (float 0x3FD99999A0000000)
  %359 = fmul reassoc ninf nsz <8 x float> %355, splat (float 0x3FD99999A0000000)
  %360 = fmul reassoc ninf nsz <8 x float> %356, splat (float 0x3FD99999A0000000)
  %361 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %357
  %362 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %358
  %363 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %359
  %364 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %360
  %365 = select <8 x i1> %325, <8 x i1> %329, <8 x i1> zeroinitializer
  %366 = select <8 x i1> %326, <8 x i1> %330, <8 x i1> zeroinitializer
  %367 = select <8 x i1> %327, <8 x i1> %331, <8 x i1> zeroinitializer
  %368 = select <8 x i1> %328, <8 x i1> %332, <8 x i1> zeroinitializer
  %369 = fmul reassoc ninf nsz <8 x float> %249, splat (float 0x3FC3333340000000)
  %370 = fmul reassoc ninf nsz <8 x float> %250, splat (float 0x3FC3333340000000)
  %371 = fmul reassoc ninf nsz <8 x float> %251, splat (float 0x3FC3333340000000)
  %372 = fmul reassoc ninf nsz <8 x float> %252, splat (float 0x3FC3333340000000)
  %373 = fdiv reassoc ninf nsz <8 x float> %369, %313
  %374 = fdiv reassoc ninf nsz <8 x float> %370, %314
  %375 = fdiv reassoc ninf nsz <8 x float> %371, %315
  %376 = fdiv reassoc ninf nsz <8 x float> %372, %316
  %377 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %373
  %378 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %374
  %379 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %375
  %380 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %376
  %381 = select <8 x i1> %broadcast.splat, <8 x i1> %317, <8 x i1> zeroinitializer
  %382 = select <8 x i1> %broadcast.splat, <8 x i1> %318, <8 x i1> zeroinitializer
  %383 = select <8 x i1> %broadcast.splat, <8 x i1> %319, <8 x i1> zeroinitializer
  %384 = select <8 x i1> %broadcast.splat, <8 x i1> %320, <8 x i1> zeroinitializer
  %385 = fmul reassoc ninf nsz <8 x float> %313, splat (float 1.500000e+00)
  %386 = fmul reassoc ninf nsz <8 x float> %314, splat (float 1.500000e+00)
  %387 = fmul reassoc ninf nsz <8 x float> %315, splat (float 1.500000e+00)
  %388 = fmul reassoc ninf nsz <8 x float> %316, splat (float 1.500000e+00)
  %389 = fcmp reassoc ninf nsz uge <8 x float> %249, %385
  %390 = fcmp reassoc ninf nsz uge <8 x float> %250, %386
  %391 = fcmp reassoc ninf nsz uge <8 x float> %251, %387
  %392 = fcmp reassoc ninf nsz uge <8 x float> %252, %388
  %393 = select <8 x i1> %381, <8 x i1> %389, <8 x i1> zeroinitializer
  %394 = select <8 x i1> %382, <8 x i1> %390, <8 x i1> zeroinitializer
  %395 = select <8 x i1> %383, <8 x i1> %391, <8 x i1> zeroinitializer
  %396 = select <8 x i1> %384, <8 x i1> %392, <8 x i1> zeroinitializer
  %397 = fsub reassoc ninf nsz <8 x float> %249, %385
  %398 = fsub reassoc ninf nsz <8 x float> %250, %386
  %399 = fsub reassoc ninf nsz <8 x float> %251, %387
  %400 = fsub reassoc ninf nsz <8 x float> %252, %388
  %401 = fdiv reassoc ninf nsz <8 x float> %397, %385
  %402 = fdiv reassoc ninf nsz <8 x float> %398, %386
  %403 = fdiv reassoc ninf nsz <8 x float> %399, %387
  %404 = fdiv reassoc ninf nsz <8 x float> %400, %388
  %405 = fcmp reassoc ninf nsz ogt <8 x float> %401, splat (float 1.000000e+00)
  %406 = fcmp reassoc ninf nsz ogt <8 x float> %402, splat (float 1.000000e+00)
  %407 = fcmp reassoc ninf nsz ogt <8 x float> %403, splat (float 1.000000e+00)
  %408 = fcmp reassoc ninf nsz ogt <8 x float> %404, splat (float 1.000000e+00)
  %409 = select <8 x i1> %405, <8 x float> splat (float 1.000000e+00), <8 x float> %401
  %410 = select <8 x i1> %406, <8 x float> splat (float 1.000000e+00), <8 x float> %402
  %411 = select <8 x i1> %407, <8 x float> splat (float 1.000000e+00), <8 x float> %403
  %412 = select <8 x i1> %408, <8 x float> splat (float 1.000000e+00), <8 x float> %404
  %413 = fmul reassoc ninf nsz <8 x float> %409, splat (float 0x3FC99999A0000000)
  %414 = fmul reassoc ninf nsz <8 x float> %410, splat (float 0x3FC99999A0000000)
  %415 = fmul reassoc ninf nsz <8 x float> %411, splat (float 0x3FC99999A0000000)
  %416 = fmul reassoc ninf nsz <8 x float> %412, splat (float 0x3FC99999A0000000)
  %417 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %413
  %418 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %414
  %419 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %415
  %420 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %416
  %421 = fmul reassoc ninf nsz <8 x float> %249, splat (float 0x3FEE666660000000)
  %422 = fmul reassoc ninf nsz <8 x float> %250, splat (float 0x3FEE666660000000)
  %423 = fmul reassoc ninf nsz <8 x float> %251, splat (float 0x3FEE666660000000)
  %424 = fmul reassoc ninf nsz <8 x float> %252, splat (float 0x3FEE666660000000)
  %425 = fdiv reassoc ninf nsz <8 x float> %421, %385
  %426 = fdiv reassoc ninf nsz <8 x float> %422, %386
  %427 = fdiv reassoc ninf nsz <8 x float> %423, %387
  %428 = fdiv reassoc ninf nsz <8 x float> %424, %388
  %429 = fadd reassoc ninf nsz <8 x float> %425, splat (float 0x3FA99999A0000000)
  %430 = fadd reassoc ninf nsz <8 x float> %426, splat (float 0x3FA99999A0000000)
  %431 = fadd reassoc ninf nsz <8 x float> %427, splat (float 0x3FA99999A0000000)
  %432 = fadd reassoc ninf nsz <8 x float> %428, splat (float 0x3FA99999A0000000)
  %433 = or <8 x i1> %381, %365
  %434 = or <8 x i1> %382, %366
  %435 = or <8 x i1> %383, %367
  %436 = or <8 x i1> %384, %368
  %437 = or <8 x i1> %433, %337
  %438 = or <8 x i1> %434, %338
  %439 = or <8 x i1> %435, %339
  %440 = or <8 x i1> %436, %340
  %441 = or <8 x i1> %437, %209
  %442 = or <8 x i1> %438, %209
  %443 = or <8 x i1> %439, %209
  %444 = or <8 x i1> %440, %209
  %predphi = select <8 x i1> %393, <8 x float> %417, <8 x float> %429
  %predphi210 = select <8 x i1> %365, <8 x float> %377, <8 x float> %predphi
  %predphi211 = select <8 x i1> %337, <8 x float> %361, <8 x float> %predphi210
  %predphi212 = select <8 x i1> %broadcast.splat, <8 x float> %predphi211, <8 x float> splat (float 1.000000e+00)
  %predphi213 = select <8 x i1> %394, <8 x float> %418, <8 x float> %430
  %predphi214 = select <8 x i1> %366, <8 x float> %378, <8 x float> %predphi213
  %predphi215 = select <8 x i1> %338, <8 x float> %362, <8 x float> %predphi214
  %predphi216 = select <8 x i1> %broadcast.splat, <8 x float> %predphi215, <8 x float> splat (float 1.000000e+00)
  %predphi217 = select <8 x i1> %395, <8 x float> %419, <8 x float> %431
  %predphi218 = select <8 x i1> %367, <8 x float> %379, <8 x float> %predphi217
  %predphi219 = select <8 x i1> %339, <8 x float> %363, <8 x float> %predphi218
  %predphi220 = select <8 x i1> %broadcast.splat, <8 x float> %predphi219, <8 x float> splat (float 1.000000e+00)
  %predphi221 = select <8 x i1> %396, <8 x float> %420, <8 x float> %432
  %predphi222 = select <8 x i1> %368, <8 x float> %380, <8 x float> %predphi221
  %predphi223 = select <8 x i1> %340, <8 x float> %364, <8 x float> %predphi222
  %predphi224 = select <8 x i1> %broadcast.splat, <8 x float> %predphi223, <8 x float> splat (float 1.000000e+00)
  %445 = fcmp reassoc ninf nsz ogt <8 x float> %293, splat (float 0x3EB0C6F7A0000000)
  %446 = fcmp reassoc ninf nsz ogt <8 x float> %294, splat (float 0x3EB0C6F7A0000000)
  %447 = fcmp reassoc ninf nsz ogt <8 x float> %295, splat (float 0x3EB0C6F7A0000000)
  %448 = fcmp reassoc ninf nsz ogt <8 x float> %296, splat (float 0x3EB0C6F7A0000000)
  %449 = select <8 x i1> %441, <8 x i1> %445, <8 x i1> zeroinitializer
  %450 = select <8 x i1> %442, <8 x i1> %446, <8 x i1> zeroinitializer
  %451 = select <8 x i1> %443, <8 x i1> %447, <8 x i1> zeroinitializer
  %452 = select <8 x i1> %444, <8 x i1> %448, <8 x i1> zeroinitializer
  %453 = fcmp reassoc ninf nsz ogt <8 x float> %277, splat (float 0x3EB0C6F7A0000000)
  %454 = fcmp reassoc ninf nsz ogt <8 x float> %278, splat (float 0x3EB0C6F7A0000000)
  %455 = fcmp reassoc ninf nsz ogt <8 x float> %279, splat (float 0x3EB0C6F7A0000000)
  %456 = fcmp reassoc ninf nsz ogt <8 x float> %280, splat (float 0x3EB0C6F7A0000000)
  %457 = fcmp reassoc ninf nsz ogt <8 x float> %289, splat (float 0x3EB0C6F7A0000000)
  %458 = fcmp reassoc ninf nsz ogt <8 x float> %290, splat (float 0x3EB0C6F7A0000000)
  %459 = fcmp reassoc ninf nsz ogt <8 x float> %291, splat (float 0x3EB0C6F7A0000000)
  %460 = fcmp reassoc ninf nsz ogt <8 x float> %292, splat (float 0x3EB0C6F7A0000000)
  %461 = select <8 x i1> %453, <8 x i1> %457, <8 x i1> zeroinitializer
  %462 = select <8 x i1> %454, <8 x i1> %458, <8 x i1> zeroinitializer
  %463 = select <8 x i1> %455, <8 x i1> %459, <8 x i1> zeroinitializer
  %464 = select <8 x i1> %456, <8 x i1> %460, <8 x i1> zeroinitializer
  %465 = select <8 x i1> %449, <8 x i1> %461, <8 x i1> zeroinitializer
  %466 = select <8 x i1> %450, <8 x i1> %462, <8 x i1> zeroinitializer
  %467 = select <8 x i1> %451, <8 x i1> %463, <8 x i1> zeroinitializer
  %468 = select <8 x i1> %452, <8 x i1> %464, <8 x i1> zeroinitializer
  %469 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather200, %wide.masked.gather192
  %470 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather201, %wide.masked.gather193
  %471 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather194
  %472 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather195
  %473 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather196
  %474 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather197
  %475 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather206, %wide.masked.gather198
  %476 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather207, %wide.masked.gather199
  %477 = fadd reassoc ninf nsz <8 x float> %473, %469
  %478 = fadd reassoc ninf nsz <8 x float> %474, %470
  %479 = fadd reassoc ninf nsz <8 x float> %475, %471
  %480 = fadd reassoc ninf nsz <8 x float> %476, %472
  %481 = fmul reassoc ninf nsz <8 x float> %289, %277
  %482 = fmul reassoc ninf nsz <8 x float> %290, %278
  %483 = fmul reassoc ninf nsz <8 x float> %291, %279
  %484 = fmul reassoc ninf nsz <8 x float> %292, %280
  %485 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %481)
  %486 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %482)
  %487 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %483)
  %488 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %484)
  %489 = fdiv reassoc ninf nsz <8 x float> %477, %485
  %490 = fdiv reassoc ninf nsz <8 x float> %478, %486
  %491 = fdiv reassoc ninf nsz <8 x float> %479, %487
  %492 = fdiv reassoc ninf nsz <8 x float> %480, %488
  %493 = fcmp reassoc ninf nsz ule <8 x float> %293, splat (float 1.500000e+02)
  %494 = fcmp reassoc ninf nsz ule <8 x float> %294, splat (float 1.500000e+02)
  %495 = fcmp reassoc ninf nsz ule <8 x float> %295, splat (float 1.500000e+02)
  %496 = fcmp reassoc ninf nsz ule <8 x float> %296, splat (float 1.500000e+02)
  %497 = fcmp reassoc ninf nsz uge <8 x float> %489, splat (float 0x3FC99999A0000000)
  %498 = fcmp reassoc ninf nsz uge <8 x float> %490, splat (float 0x3FC99999A0000000)
  %499 = fcmp reassoc ninf nsz uge <8 x float> %491, splat (float 0x3FC99999A0000000)
  %500 = fcmp reassoc ninf nsz uge <8 x float> %492, splat (float 0x3FC99999A0000000)
  %.not327 = select <8 x i1> %493, <8 x i1> splat (i1 true), <8 x i1> %497
  %.not330 = select <8 x i1> %494, <8 x i1> splat (i1 true), <8 x i1> %498
  %.not333 = select <8 x i1> %495, <8 x i1> splat (i1 true), <8 x i1> %499
  %.not336 = select <8 x i1> %496, <8 x i1> splat (i1 true), <8 x i1> %500
  %501 = select <8 x i1> %465, <8 x i1> %.not327, <8 x i1> zeroinitializer
  %502 = select <8 x i1> %466, <8 x i1> %.not330, <8 x i1> zeroinitializer
  %503 = select <8 x i1> %467, <8 x i1> %.not333, <8 x i1> zeroinitializer
  %504 = select <8 x i1> %468, <8 x i1> %.not336, <8 x i1> zeroinitializer
  %505 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %489, <8 x float> zeroinitializer)
  %506 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %490, <8 x float> zeroinitializer)
  %507 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %491, <8 x float> zeroinitializer)
  %508 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %492, <8 x float> zeroinitializer)
  %509 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %293)
  %510 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %294)
  %511 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %295)
  %512 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %296)
  %513 = fmul reassoc ninf nsz <8 x float> %509, %broadcast.splat226
  %514 = fmul reassoc ninf nsz <8 x float> %510, %broadcast.splat226
  %515 = fmul reassoc ninf nsz <8 x float> %511, %broadcast.splat226
  %516 = fmul reassoc ninf nsz <8 x float> %512, %broadcast.splat226
  %517 = fmul reassoc ninf nsz <8 x float> %513, %505
  %.fr = freeze <8 x float> %517
  %518 = fmul reassoc ninf nsz <8 x float> %514, %506
  %.fr337 = freeze <8 x float> %518
  %519 = fmul reassoc ninf nsz <8 x float> %515, %507
  %.fr338 = freeze <8 x float> %519
  %520 = fmul reassoc ninf nsz <8 x float> %516, %508
  %.fr339 = freeze <8 x float> %520
  %521 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %522 = fcmp reassoc nsz ogt <8 x float> %.fr337, splat (float 3.000000e+00)
  %523 = fcmp reassoc nsz ogt <8 x float> %.fr338, splat (float 3.000000e+00)
  %524 = fcmp reassoc nsz ogt <8 x float> %.fr339, splat (float 3.000000e+00)
  %525 = xor <8 x i1> %521, splat (i1 true)
  %526 = xor <8 x i1> %522, splat (i1 true)
  %527 = xor <8 x i1> %523, splat (i1 true)
  %528 = xor <8 x i1> %524, splat (i1 true)
  %529 = and <8 x i1> %501, %525
  %530 = and <8 x i1> %502, %526
  %531 = and <8 x i1> %503, %527
  %532 = and <8 x i1> %504, %528
  %533 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %534 = fcmp reassoc nsz olt <8 x float> %.fr337, splat (float -3.000000e+00)
  %535 = fcmp reassoc nsz olt <8 x float> %.fr338, splat (float -3.000000e+00)
  %536 = fcmp reassoc nsz olt <8 x float> %.fr339, splat (float -3.000000e+00)
  %537 = xor <8 x i1> %533, splat (i1 true)
  %538 = xor <8 x i1> %534, splat (i1 true)
  %539 = xor <8 x i1> %535, splat (i1 true)
  %540 = xor <8 x i1> %536, splat (i1 true)
  %541 = and <8 x i1> %529, %537
  %542 = and <8 x i1> %530, %538
  %543 = and <8 x i1> %531, %539
  %544 = and <8 x i1> %532, %540
  %545 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %546 = fmul reassoc ninf nsz <8 x float> %.fr337, %.fr337
  %547 = fmul reassoc ninf nsz <8 x float> %.fr338, %.fr338
  %548 = fmul reassoc ninf nsz <8 x float> %.fr339, %.fr339
  %549 = fadd reassoc ninf nsz <8 x float> %545, splat (float 2.700000e+01)
  %550 = fadd reassoc ninf nsz <8 x float> %546, splat (float 2.700000e+01)
  %551 = fadd reassoc ninf nsz <8 x float> %547, splat (float 2.700000e+01)
  %552 = fadd reassoc ninf nsz <8 x float> %548, splat (float 2.700000e+01)
  %553 = fmul reassoc ninf nsz <8 x float> %549, %.fr
  %554 = fmul reassoc ninf nsz <8 x float> %550, %.fr337
  %555 = fmul reassoc ninf nsz <8 x float> %551, %.fr338
  %556 = fmul reassoc ninf nsz <8 x float> %552, %.fr339
  %557 = fmul reassoc ninf nsz <8 x float> %545, splat (float 9.000000e+00)
  %558 = fmul reassoc ninf nsz <8 x float> %546, splat (float 9.000000e+00)
  %559 = fmul reassoc ninf nsz <8 x float> %547, splat (float 9.000000e+00)
  %560 = fmul reassoc ninf nsz <8 x float> %548, splat (float 9.000000e+00)
  %561 = fadd reassoc ninf nsz <8 x float> %557, splat (float 2.700000e+01)
  %562 = fadd reassoc ninf nsz <8 x float> %558, splat (float 2.700000e+01)
  %563 = fadd reassoc ninf nsz <8 x float> %559, splat (float 2.700000e+01)
  %564 = fadd reassoc ninf nsz <8 x float> %560, splat (float 2.700000e+01)
  %565 = fdiv reassoc ninf nsz <8 x float> %553, %561
  %566 = fdiv reassoc ninf nsz <8 x float> %554, %562
  %567 = fdiv reassoc ninf nsz <8 x float> %555, %563
  %568 = fdiv reassoc ninf nsz <8 x float> %556, %564
  %569 = fadd reassoc ninf nsz <8 x float> %565, splat (float 1.000000e+00)
  %570 = fadd reassoc ninf nsz <8 x float> %566, splat (float 1.000000e+00)
  %571 = fadd reassoc ninf nsz <8 x float> %567, splat (float 1.000000e+00)
  %572 = fadd reassoc ninf nsz <8 x float> %568, splat (float 1.000000e+00)
  %573 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %489
  %574 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %490
  %575 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %491
  %576 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %492
  %577 = fmul reassoc ninf nsz <8 x float> %573, %249
  %578 = fmul reassoc ninf nsz <8 x float> %574, %250
  %579 = fmul reassoc ninf nsz <8 x float> %575, %251
  %580 = fmul reassoc ninf nsz <8 x float> %576, %252
  %581 = and <8 x i1> %529, %533
  %582 = and <8 x i1> %530, %534
  %583 = and <8 x i1> %531, %535
  %584 = and <8 x i1> %532, %536
  %585 = and <8 x i1> %501, %521
  %586 = and <8 x i1> %502, %522
  %587 = and <8 x i1> %503, %523
  %588 = and <8 x i1> %504, %524
  %589 = xor <8 x i1> %461, splat (i1 true)
  %590 = xor <8 x i1> %462, splat (i1 true)
  %591 = xor <8 x i1> %463, splat (i1 true)
  %592 = xor <8 x i1> %464, splat (i1 true)
  %593 = select <8 x i1> %449, <8 x i1> %589, <8 x i1> zeroinitializer
  %594 = select <8 x i1> %450, <8 x i1> %590, <8 x i1> zeroinitializer
  %595 = select <8 x i1> %451, <8 x i1> %591, <8 x i1> zeroinitializer
  %596 = select <8 x i1> %452, <8 x i1> %592, <8 x i1> zeroinitializer
  %597 = xor <8 x i1> %445, splat (i1 true)
  %598 = xor <8 x i1> %446, splat (i1 true)
  %599 = xor <8 x i1> %447, splat (i1 true)
  %600 = xor <8 x i1> %448, splat (i1 true)
  %601 = select <8 x i1> %441, <8 x i1> %597, <8 x i1> zeroinitializer
  %602 = select <8 x i1> %442, <8 x i1> %598, <8 x i1> zeroinitializer
  %603 = select <8 x i1> %443, <8 x i1> %599, <8 x i1> zeroinitializer
  %604 = select <8 x i1> %444, <8 x i1> %600, <8 x i1> zeroinitializer
  %605 = select <8 x i1> %501, <8 x i1> splat (i1 true), <8 x i1> %601
  %606 = select <8 x i1> %605, <8 x i1> splat (i1 true), <8 x i1> %593
  %predphi231 = select <8 x i1> %606, <8 x float> %249, <8 x float> %577
  %607 = select <8 x i1> %502, <8 x i1> splat (i1 true), <8 x i1> %602
  %608 = select <8 x i1> %607, <8 x i1> splat (i1 true), <8 x i1> %594
  %predphi236 = select <8 x i1> %608, <8 x float> %250, <8 x float> %578
  %609 = select <8 x i1> %503, <8 x i1> splat (i1 true), <8 x i1> %603
  %610 = select <8 x i1> %609, <8 x i1> splat (i1 true), <8 x i1> %595
  %predphi241 = select <8 x i1> %610, <8 x float> %251, <8 x float> %579
  %611 = select <8 x i1> %504, <8 x i1> splat (i1 true), <8 x i1> %604
  %612 = select <8 x i1> %611, <8 x i1> splat (i1 true), <8 x i1> %596
  %predphi246 = select <8 x i1> %612, <8 x float> %252, <8 x float> %580
  %predphi249 = select <8 x i1> %585, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi250 = select <8 x i1> %541, <8 x float> %569, <8 x float> %predphi249
  %predphi251 = select <8 x i1> %581, <8 x float> zeroinitializer, <8 x float> %predphi250
  %predphi254 = select <8 x i1> %586, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi255 = select <8 x i1> %542, <8 x float> %570, <8 x float> %predphi254
  %predphi256 = select <8 x i1> %582, <8 x float> zeroinitializer, <8 x float> %predphi255
  %predphi259 = select <8 x i1> %587, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi260 = select <8 x i1> %543, <8 x float> %571, <8 x float> %predphi259
  %predphi261 = select <8 x i1> %583, <8 x float> zeroinitializer, <8 x float> %predphi260
  %predphi264 = select <8 x i1> %588, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi265 = select <8 x i1> %544, <8 x float> %572, <8 x float> %predphi264
  %predphi266 = select <8 x i1> %584, <8 x float> zeroinitializer, <8 x float> %predphi265
  %613 = fmul reassoc ninf nsz <8 x float> %predphi251, %predphi212
  %614 = fmul reassoc ninf nsz <8 x float> %predphi256, %predphi216
  %615 = fmul reassoc ninf nsz <8 x float> %predphi261, %predphi220
  %616 = fmul reassoc ninf nsz <8 x float> %predphi266, %predphi224
  %617 = fmul reassoc ninf nsz <8 x float> %613, %predphi231
  %618 = fmul reassoc ninf nsz <8 x float> %614, %predphi236
  %619 = fmul reassoc ninf nsz <8 x float> %615, %predphi241
  %620 = fmul reassoc ninf nsz <8 x float> %616, %predphi246
  %621 = fadd reassoc ninf nsz <8 x float> %617, %vec.phi179
  %622 = fadd reassoc ninf nsz <8 x float> %618, %vec.phi180
  %623 = fadd reassoc ninf nsz <8 x float> %619, %vec.phi181
  %624 = fadd reassoc ninf nsz <8 x float> %620, %vec.phi182
  %625 = fadd reassoc ninf nsz <8 x float> %613, %vec.phi175
  %626 = fadd reassoc ninf nsz <8 x float> %614, %vec.phi176
  %627 = fadd reassoc ninf nsz <8 x float> %615, %vec.phi177
  %628 = fadd reassoc ninf nsz <8 x float> %616, %vec.phi178
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %629 = icmp eq i64 %lsr.iv.next, 0
  br i1 %629, label %middle.block164, label %vector.body173, !llvm.loop !11

middle.block164:                                  ; preds = %vector.body173
  %bin.rdx268 = fadd reassoc ninf nsz <8 x float> %626, %625
  %bin.rdx269 = fadd reassoc ninf nsz <8 x float> %627, %bin.rdx268
  %bin.rdx270 = fadd reassoc ninf nsz <8 x float> %628, %bin.rdx269
  %630 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx270)
  %bin.rdx271 = fadd reassoc ninf nsz <8 x float> %622, %621
  %bin.rdx272 = fadd reassoc ninf nsz <8 x float> %623, %bin.rdx271
  %bin.rdx273 = fadd reassoc ninf nsz <8 x float> %624, %bin.rdx272
  %631 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx273)
  br i1 %cmp.n274, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check281

vec.epilog.iter.check281:                         ; preds = %middle.block164
  br i1 %min.epilog.iters.check283, label %for_loop_body20.us.preheader, label %vec.epilog.ph280

vec.epilog.ph280:                                 ; preds = %vec.epilog.iter.check281, %vector.main.loop.iter.check169
  %bc.resume.val275 = phi i64 [ %n.vec172, %vec.epilog.iter.check281 ], [ 0, %vector.main.loop.iter.check169 ]
  %bc.merge.rdx276 = phi float [ %630, %vec.epilog.iter.check281 ], [ %.06197.us, %vector.main.loop.iter.check169 ]
  %bc.merge.rdx277 = phi float [ %631, %vec.epilog.iter.check281 ], [ %.06396.us, %vector.main.loop.iter.check169 ]
  %632 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx276, i64 0
  %633 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx277, i64 0
  %634 = trunc nuw nsw i64 %bc.resume.val275 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %634, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %635 = add i64 %212, %bc.resume.val275
  br label %vec.epilog.vector.body288

vec.epilog.vector.body288:                        ; preds = %vec.epilog.vector.body288, %vec.epilog.ph280
  %lsr.iv393 = phi i64 [ %lsr.iv.next394, %vec.epilog.vector.body288 ], [ %635, %vec.epilog.ph280 ]
  %vec.phi290 = phi <8 x float> [ %632, %vec.epilog.ph280 ], [ %736, %vec.epilog.vector.body288 ]
  %vec.phi291 = phi <8 x float> [ %633, %vec.epilog.ph280 ], [ %735, %vec.epilog.vector.body288 ]
  %vec.ind292 = phi <8 x i32> [ %induction, %vec.epilog.ph280 ], [ %vec.ind.next293, %vec.epilog.vector.body288 ]
  %636 = shl <8 x i32> %vec.ind292, splat (i32 1)
  %637 = add <8 x i32> %broadcast.splat184, %636
  %638 = sext <8 x i32> %637 to <8 x i64>
  %639 = getelementptr float, ptr %218, <8 x i64> %638
  %wide.masked.gather296 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %639, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %640 = getelementptr float, ptr %220, <8 x i64> %638
  %wide.masked.gather297 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %640, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %641 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather296, %wide.masked.gather297
  %642 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %641)
  %643 = getelementptr float, ptr %222, <8 x i64> %638
  %wide.masked.gather298 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %643, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %644 = getelementptr float, ptr %224, <8 x i64> %638
  %wide.masked.gather299 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %644, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %645 = getelementptr float, ptr %226, <8 x i64> %638
  %wide.masked.gather300 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %645, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %646 = getelementptr float, ptr %228, <8 x i64> %638
  %wide.masked.gather301 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %646, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %647 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather298, %wide.masked.gather298
  %648 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather299, %wide.masked.gather299
  %649 = fadd reassoc ninf nsz <8 x float> %648, %647
  %650 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather300, %wide.masked.gather300
  %651 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather301, %wide.masked.gather301
  %652 = fadd reassoc ninf nsz <8 x float> %651, %650
  %653 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %649, <8 x float> %652)
  %654 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather297, splat (float -2.000000e+00)
  %655 = fadd reassoc ninf nsz <8 x float> %654, splat (float 3.000000e+00)
  %656 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %655, <8 x float> splat (float 3.000000e+00))
  %657 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %656, <8 x float> splat (float 1.000000e+00))
  %658 = fmul reassoc ninf nsz <8 x float> %657, %broadcast.splat209
  %659 = fcmp reassoc ninf nsz olt <8 x float> %653, splat (float 1.500000e+02)
  %660 = xor <8 x i1> %659, splat (i1 true)
  %661 = select <8 x i1> %broadcast.splat, <8 x i1> %660, <8 x i1> zeroinitializer
  %662 = fcmp reassoc ninf nsz olt <8 x float> %642, %658
  %663 = xor <8 x i1> %662, splat (i1 true)
  %664 = select <8 x i1> %661, <8 x i1> %663, <8 x i1> zeroinitializer
  %665 = fmul reassoc ninf nsz <8 x float> %658, splat (float 4.000000e+00)
  %666 = fdiv reassoc ninf nsz <8 x float> %642, %665
  %667 = fcmp reassoc ninf nsz ogt <8 x float> %666, splat (float 1.000000e+00)
  %668 = select <8 x i1> %667, <8 x float> splat (float 1.000000e+00), <8 x float> %666
  %669 = fmul reassoc ninf nsz <8 x float> %668, splat (float 0x3FD99999A0000000)
  %670 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %669
  %671 = select <8 x i1> %661, <8 x i1> %662, <8 x i1> zeroinitializer
  %672 = fmul reassoc ninf nsz <8 x float> %642, splat (float 0x3FC3333340000000)
  %673 = fdiv reassoc ninf nsz <8 x float> %672, %658
  %674 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %673
  %675 = select <8 x i1> %broadcast.splat, <8 x i1> %659, <8 x i1> zeroinitializer
  %676 = fmul reassoc ninf nsz <8 x float> %658, splat (float 1.500000e+00)
  %677 = fcmp reassoc ninf nsz uge <8 x float> %642, %676
  %678 = select <8 x i1> %675, <8 x i1> %677, <8 x i1> zeroinitializer
  %679 = fsub reassoc ninf nsz <8 x float> %642, %676
  %680 = fdiv reassoc ninf nsz <8 x float> %679, %676
  %681 = fcmp reassoc ninf nsz ogt <8 x float> %680, splat (float 1.000000e+00)
  %682 = select <8 x i1> %681, <8 x float> splat (float 1.000000e+00), <8 x float> %680
  %683 = fmul reassoc ninf nsz <8 x float> %682, splat (float 0x3FC99999A0000000)
  %684 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %683
  %685 = fmul reassoc ninf nsz <8 x float> %642, splat (float 0x3FEE666660000000)
  %686 = fdiv reassoc ninf nsz <8 x float> %685, %676
  %687 = fadd reassoc ninf nsz <8 x float> %686, splat (float 0x3FA99999A0000000)
  %688 = or <8 x i1> %671, %209
  %689 = or <8 x i1> %688, %675
  %690 = or <8 x i1> %689, %664
  %predphi304 = select <8 x i1> %678, <8 x float> %684, <8 x float> %687
  %predphi305 = select <8 x i1> %671, <8 x float> %674, <8 x float> %predphi304
  %predphi306 = select <8 x i1> %664, <8 x float> %670, <8 x float> %predphi305
  %predphi307 = select <8 x i1> %broadcast.splat, <8 x float> %predphi306, <8 x float> splat (float 1.000000e+00)
  %691 = fcmp reassoc ninf nsz ogt <8 x float> %653, splat (float 0x3EB0C6F7A0000000)
  %692 = select <8 x i1> %690, <8 x i1> %691, <8 x i1> zeroinitializer
  %693 = fcmp reassoc ninf nsz ogt <8 x float> %649, splat (float 0x3EB0C6F7A0000000)
  %694 = fcmp reassoc ninf nsz ogt <8 x float> %652, splat (float 0x3EB0C6F7A0000000)
  %695 = select <8 x i1> %693, <8 x i1> %694, <8 x i1> zeroinitializer
  %696 = select <8 x i1> %692, <8 x i1> %695, <8 x i1> zeroinitializer
  %697 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather300, %wide.masked.gather298
  %698 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather301, %wide.masked.gather299
  %699 = fadd reassoc ninf nsz <8 x float> %698, %697
  %700 = fmul reassoc ninf nsz <8 x float> %652, %649
  %701 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %700)
  %702 = fdiv reassoc ninf nsz <8 x float> %699, %701
  %703 = fcmp reassoc ninf nsz ule <8 x float> %653, splat (float 1.500000e+02)
  %704 = fcmp reassoc ninf nsz uge <8 x float> %702, splat (float 0x3FC99999A0000000)
  %.not342 = select <8 x i1> %703, <8 x i1> splat (i1 true), <8 x i1> %704
  %705 = select <8 x i1> %696, <8 x i1> %.not342, <8 x i1> zeroinitializer
  %706 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %702, <8 x float> zeroinitializer)
  %707 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %653)
  %708 = fmul reassoc ninf nsz <8 x float> %707, %broadcast.splat226
  %709 = fmul reassoc ninf nsz <8 x float> %708, %706
  %.fr343 = freeze <8 x float> %709
  %710 = fcmp reassoc nsz ogt <8 x float> %.fr343, splat (float 3.000000e+00)
  %711 = xor <8 x i1> %710, splat (i1 true)
  %712 = and <8 x i1> %705, %711
  %713 = fcmp reassoc nsz olt <8 x float> %.fr343, splat (float -3.000000e+00)
  %714 = xor <8 x i1> %713, splat (i1 true)
  %715 = and <8 x i1> %712, %714
  %716 = fmul reassoc ninf nsz <8 x float> %.fr343, %.fr343
  %717 = fadd reassoc ninf nsz <8 x float> %716, splat (float 2.700000e+01)
  %718 = fmul reassoc ninf nsz <8 x float> %717, %.fr343
  %719 = fmul reassoc ninf nsz <8 x float> %716, splat (float 9.000000e+00)
  %720 = fadd reassoc ninf nsz <8 x float> %719, splat (float 2.700000e+01)
  %721 = fdiv reassoc ninf nsz <8 x float> %718, %720
  %722 = fadd reassoc ninf nsz <8 x float> %721, splat (float 1.000000e+00)
  %723 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %702
  %724 = fmul reassoc ninf nsz <8 x float> %723, %642
  %725 = and <8 x i1> %712, %713
  %726 = and <8 x i1> %705, %710
  %727 = xor <8 x i1> %695, splat (i1 true)
  %728 = select <8 x i1> %692, <8 x i1> %727, <8 x i1> zeroinitializer
  %729 = xor <8 x i1> %691, splat (i1 true)
  %730 = select <8 x i1> %690, <8 x i1> %729, <8 x i1> zeroinitializer
  %731 = select <8 x i1> %705, <8 x i1> splat (i1 true), <8 x i1> %730
  %732 = select <8 x i1> %731, <8 x i1> splat (i1 true), <8 x i1> %728
  %predphi314 = select <8 x i1> %732, <8 x float> %642, <8 x float> %724
  %predphi317 = select <8 x i1> %726, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi318 = select <8 x i1> %715, <8 x float> %722, <8 x float> %predphi317
  %predphi319 = select <8 x i1> %725, <8 x float> zeroinitializer, <8 x float> %predphi318
  %733 = fmul reassoc ninf nsz <8 x float> %predphi319, %predphi307
  %734 = fmul reassoc ninf nsz <8 x float> %733, %predphi314
  %735 = fadd reassoc ninf nsz <8 x float> %734, %vec.phi291
  %736 = fadd reassoc ninf nsz <8 x float> %733, %vec.phi290
  %vec.ind.next293 = add <8 x i32> %vec.ind292, splat (i32 8)
  %lsr.iv.next394 = add i64 %lsr.iv393, 8
  %737 = icmp eq i64 %lsr.iv.next394, 0
  br i1 %737, label %vec.epilog.middle.block278, label %vec.epilog.vector.body288, !llvm.loop !14

vec.epilog.middle.block278:                       ; preds = %vec.epilog.vector.body288
  %738 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %736)
  %739 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %735)
  br i1 %cmp.n321, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block278, %vec.epilog.iter.check281, %iter.check167
  %indvars.iv.ph = phi i64 [ %n.vec172, %vec.epilog.iter.check281 ], [ 0, %iter.check167 ], [ %n.vec285, %vec.epilog.middle.block278 ]
  %.16293.us.ph = phi float [ %630, %vec.epilog.iter.check281 ], [ %.06197.us, %iter.check167 ], [ %738, %vec.epilog.middle.block278 ]
  %.16492.us.ph = phi float [ %631, %vec.epilog.iter.check281 ], [ %.06396.us, %iter.check167 ], [ %739, %vec.epilog.middle.block278 ]
  %740 = trunc i64 %indvars.iv.ph to i32
  %741 = shl nuw i32 %740, 1
  %742 = add i32 %175, %741
  %743 = add i64 %213, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv397 = phi i64 [ %743, %for_loop_body20.us.preheader ], [ %lsr.iv.next398, %after_if50.us ]
  %lsr.iv395 = phi i32 [ %742, %for_loop_body20.us.preheader ], [ %lsr.iv.next396, %after_if50.us ]
  %.16293.us = phi float [ %819, %after_if50.us ], [ %.16293.us.ph, %for_loop_body20.us.preheader ]
  %.16492.us = phi float [ %818, %after_if50.us ], [ %.16492.us.ph, %for_loop_body20.us.preheader ]
  %744 = sext i32 %lsr.iv395 to i64
  %745 = getelementptr float, ptr %218, i64 %744
  %746 = load float, ptr %745, align 4
  %747 = getelementptr float, ptr %220, i64 %744
  %748 = load float, ptr %747, align 4
  %749 = fsub reassoc ninf nsz float %746, %748
  %750 = tail call noundef float @llvm.fabs.f32(float %749)
  %751 = getelementptr float, ptr %222, i64 %744
  %752 = load float, ptr %751, align 4
  %753 = getelementptr float, ptr %224, i64 %744
  %754 = load float, ptr %753, align 4
  %755 = getelementptr float, ptr %226, i64 %744
  %756 = load float, ptr %755, align 4
  %757 = getelementptr float, ptr %228, i64 %744
  %758 = load float, ptr %757, align 4
  %759 = fmul reassoc ninf nsz float %752, %752
  %760 = fmul reassoc ninf nsz float %754, %754
  %761 = fadd reassoc ninf nsz float %760, %759
  %762 = fmul reassoc ninf nsz float %756, %756
  %763 = fmul reassoc ninf nsz float %758, %758
  %764 = fadd reassoc ninf nsz float %763, %762
  %765 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %761, float %764)
  %factor.us = fmul reassoc ninf nsz float %748, -2.000000e+00
  %766 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %767 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %766, float 3.000000e+00)
  %768 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %767, float 1.000000e+00)
  %769 = fmul reassoc ninf nsz float %768, %172
  br i1 %173, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %770 = fcmp reassoc ninf nsz olt float %765, 1.500000e+02
  br i1 %770, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %771 = fcmp reassoc ninf nsz olt float %750, %769
  br i1 %771, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %772 = fmul reassoc ninf nsz float %769, 4.000000e+00
  %773 = fdiv reassoc ninf nsz float %750, %772
  %774 = fcmp reassoc ninf nsz ogt float %773, 1.000000e+00
  %spec.store.select1.us = select i1 %774, float 1.000000e+00, float %773
  %775 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %776 = fsub reassoc ninf nsz float 0x3FE6666680000000, %775
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %777 = fmul reassoc ninf nsz float %750, 0x3FC3333340000000
  %778 = fdiv reassoc ninf nsz float %777, %769
  %779 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %778
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %780 = fmul reassoc ninf nsz float %769, 1.500000e+00
  %781 = fcmp reassoc ninf nsz olt float %750, %780
  br i1 %781, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %782 = fsub reassoc ninf nsz float %750, %780
  %783 = fdiv reassoc ninf nsz float %782, %780
  %784 = fcmp reassoc ninf nsz ogt float %783, 1.000000e+00
  %spec.store.select.us = select i1 %784, float 1.000000e+00, float %783
  %785 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %786 = fsub reassoc ninf nsz float 1.000000e+00, %785
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %787 = fmul reassoc ninf nsz float %750, 0x3FEE666660000000
  %788 = fdiv reassoc ninf nsz float %787, %780
  %789 = fadd reassoc ninf nsz float %788, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.057.us = phi float [ %789, %true_block30.us ], [ %786, %false_block31.us ], [ %779, %true_block36.us ], [ %776, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %790 = fcmp reassoc ninf nsz ogt float %765, 0x3EB0C6F7A0000000
  br i1 %790, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %791 = fcmp reassoc ninf nsz ogt float %761, 0x3EB0C6F7A0000000
  %792 = fcmp reassoc ninf nsz ogt float %764, 0x3EB0C6F7A0000000
  %.052.us = select i1 %791, i1 %792, i1 false
  br i1 %.052.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %793 = fmul reassoc ninf nsz float %756, %752
  %794 = fmul reassoc ninf nsz float %758, %754
  %795 = fadd reassoc ninf nsz float %794, %793
  %796 = fmul reassoc ninf nsz float %764, %761
  %797 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %796)
  %798 = fdiv reassoc ninf nsz float %795, %797
  %799 = fcmp reassoc ninf nsz ogt float %765, 1.500000e+02
  %800 = fcmp reassoc ninf nsz olt float %798, 0x3FC99999A0000000
  %.051.us = select i1 %799, i1 %800, i1 false
  br i1 %.051.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %801 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %798, float 0.000000e+00)
  %802 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %765)
  %803 = fmul reassoc ninf nsz float %802, %170
  %804 = fmul reassoc ninf nsz float %803, %801
  %805 = fcmp reassoc ninf nsz ogt float %804, 3.000000e+00
  br i1 %805, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %806 = fcmp reassoc ninf nsz olt float %804, -3.000000e+00
  br i1 %806, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %807 = fmul reassoc ninf nsz float %804, %804
  %808 = fadd reassoc ninf nsz float %807, 2.700000e+01
  %809 = fmul reassoc ninf nsz float %808, %804
  %810 = fmul reassoc ninf nsz float %807, 9.000000e+00
  %811 = fadd reassoc ninf nsz float %810, 2.700000e+01
  %812 = fdiv reassoc ninf nsz float %809, %811
  %813 = fadd reassoc ninf nsz float %812, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %814 = fsub reassoc ninf nsz float 1.500000e+00, %798
  %815 = fmul reassoc ninf nsz float %814, %750
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.058.us = phi float [ %815, %true_block54.us ], [ %750, %true_block42.us ], [ %750, %after_if26.us ], [ %750, %false_block55.us ], [ %750, %false_block61.us ], [ %750, %false_block58.us ]
  %.054.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %813, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %816 = fmul reassoc ninf nsz float %.054.us, %.057.us
  %817 = fmul reassoc ninf nsz float %816, %.058.us
  %818 = fadd reassoc ninf nsz float %817, %.16492.us
  %819 = fadd reassoc ninf nsz float %816, %.16293.us
  %lsr.iv.next396 = add i32 %lsr.iv395, 2
  %lsr.iv.next398 = add i64 %lsr.iv397, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next398, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block278, %middle.block164
  %.lcssa139 = phi float [ %631, %middle.block164 ], [ %739, %vec.epilog.middle.block278 ], [ %818, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %630, %middle.block164 ], [ %738, %vec.epilog.middle.block278 ], [ %819, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %indvars.iv.next118 = add nuw nsw i64 %indvars.iv117, 1
  %exitcond121.not = icmp eq i64 %indvars.iv.next118, %wide.trip.count120
  br i1 %exitcond121.not, label %after_for18, label %iter.check167

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %820 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %820, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %true_block13
  %821 = getelementptr i8, ptr %81, i64 4
  %822 = getelementptr i8, ptr %81, i64 8
  %823 = load ptr, ptr %822, align 8
  %824 = load i32, ptr %821, align 4
  %825 = sext i32 %824 to i64
  %smax = tail call i32 @llvm.smax.i32(i32 %72, i32 1)
  %smax130 = tail call i32 @llvm.smax.i32(i32 %70, i32 1)
  %wide.trip.count131 = zext nneg i32 %smax130 to i64
  %wide.trip.count125 = zext i32 %smax to i64
  %826 = add nsw i64 %wide.trip.count125, -1
  %min.iters.check = icmp slt i32 %72, 4
  %827 = trunc nsw i64 %826 to i32
  %828 = add i32 %68, %827
  %829 = icmp slt i32 %828, %68
  %830 = icmp ugt i64 %826, 4294967295
  %831 = or i1 %829, %830
  %min.iters.check141 = icmp slt i32 %72, 32
  %n.vec = and i64 %wide.trip.count125, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count125
  %n.vec.remaining = and i64 %wide.trip.count125, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec155 = and i64 %wide.trip.count125, 2147483644
  %cmp.n161 = icmp eq i64 %n.vec155, %wide.trip.count125
  %xtraiter = and i64 %wide.trip.count125, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %832 = lshr i64 %wide.trip.count125, 2
  %833 = mul nsw i64 %832, -4
  %834 = zext i32 %68 to i64
  %835 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %indvars.iv127 = phi i64 [ %indvars.iv.next128, %for_loop_test73.after_for72_crit_edge.us ], [ 0, %for_loop_body66.lr.ph.split.us ]
  %.048104.us = phi float [ %.lcssa140, %for_loop_test73.after_for72_crit_edge.us ], [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ]
  %836 = trunc nuw nsw i64 %indvars.iv127 to i32
  %837 = add i32 %64, %836
  %838 = sext i32 %837 to i64
  %839 = mul nsw i64 %825, %838
  %840 = getelementptr float, ptr %823, i64 %839
  %841 = mul nsw i64 %838, %119
  %842 = getelementptr float, ptr %116, i64 %841
  %brmerge391 = select i1 %min.iters.check, i1 true, i1 %831
  br i1 %brmerge391, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %iter.check
  br i1 %min.iters.check141, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %843 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.048104.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv401 = phi i32 [ %lsr.iv.next402, %vector.body ], [ %68, %vector.ph ]
  %lsr.iv399 = phi i64 [ %lsr.iv.next400, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %843, %vector.ph ], [ %861, %vector.body ]
  %vec.phi142 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %862, %vector.body ]
  %vec.phi143 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %863, %vector.body ]
  %vec.phi144 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %864, %vector.body ]
  %844 = sext i32 %lsr.iv401 to i64
  %845 = getelementptr float, ptr %840, i64 %844
  %846 = getelementptr i8, ptr %845, i64 32
  %847 = getelementptr i8, ptr %845, i64 64
  %848 = getelementptr i8, ptr %845, i64 96
  %wide.load = load <8 x float>, ptr %845, align 4
  %wide.load145 = load <8 x float>, ptr %846, align 4
  %wide.load146 = load <8 x float>, ptr %847, align 4
  %wide.load147 = load <8 x float>, ptr %848, align 4
  %849 = getelementptr float, ptr %842, i64 %844
  %850 = getelementptr i8, ptr %849, i64 32
  %851 = getelementptr i8, ptr %849, i64 64
  %852 = getelementptr i8, ptr %849, i64 96
  %wide.load148 = load <8 x float>, ptr %849, align 4
  %wide.load149 = load <8 x float>, ptr %850, align 4
  %wide.load150 = load <8 x float>, ptr %851, align 4
  %wide.load151 = load <8 x float>, ptr %852, align 4
  %853 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load148
  %854 = fsub reassoc ninf nsz <8 x float> %wide.load145, %wide.load149
  %855 = fsub reassoc ninf nsz <8 x float> %wide.load146, %wide.load150
  %856 = fsub reassoc ninf nsz <8 x float> %wide.load147, %wide.load151
  %857 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %853)
  %858 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %854)
  %859 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %855)
  %860 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %856)
  %861 = fadd reassoc ninf nsz <8 x float> %857, %vec.phi
  %862 = fadd reassoc ninf nsz <8 x float> %858, %vec.phi142
  %863 = fadd reassoc ninf nsz <8 x float> %859, %vec.phi143
  %864 = fadd reassoc ninf nsz <8 x float> %860, %vec.phi144
  %lsr.iv.next400 = add nsw i64 %lsr.iv399, -32
  %lsr.iv.next402 = add i32 %lsr.iv401, 32
  %865 = icmp eq i64 %lsr.iv.next400, 0
  br i1 %865, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %862, %861
  %bin.rdx152 = fadd reassoc ninf nsz <8 x float> %863, %bin.rdx
  %bin.rdx153 = fadd reassoc ninf nsz <8 x float> %864, %bin.rdx152
  %866 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx153)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %866, %vec.epilog.iter.check ], [ %.048104.us, %vector.main.loop.iter.check ]
  %867 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %868 = add i64 %833, %vec.epilog.resume.val
  %869 = trunc i64 %vec.epilog.resume.val to i32
  %870 = add i32 %68, %869
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv405 = phi i32 [ %lsr.iv.next406, %vec.epilog.vector.body ], [ %870, %vec.epilog.ph ]
  %lsr.iv403 = phi i64 [ %lsr.iv.next404, %vec.epilog.vector.body ], [ %868, %vec.epilog.ph ]
  %vec.phi157 = phi <4 x float> [ %867, %vec.epilog.ph ], [ %876, %vec.epilog.vector.body ]
  %871 = sext i32 %lsr.iv405 to i64
  %872 = getelementptr float, ptr %840, i64 %871
  %wide.load158 = load <4 x float>, ptr %872, align 4
  %873 = getelementptr float, ptr %842, i64 %871
  %wide.load159 = load <4 x float>, ptr %873, align 4
  %874 = fsub reassoc ninf nsz <4 x float> %wide.load158, %wide.load159
  %875 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %874)
  %876 = fadd reassoc ninf nsz <4 x float> %875, %vec.phi157
  %lsr.iv.next404 = add i64 %lsr.iv403, 4
  %lsr.iv.next406 = add i32 %lsr.iv405, 4
  %877 = icmp eq i64 %lsr.iv.next404, 0
  br i1 %877, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %878 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %876)
  br i1 %cmp.n161, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %iter.check
  %indvars.iv122.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ %n.vec155, %vec.epilog.middle.block ]
  %.1102.us.ph = phi float [ %866, %vec.epilog.iter.check ], [ %.048104.us, %iter.check ], [ %878, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv407 = phi i64 [ %835, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next408, %for_loop_body70.us.prol ]
  %indvars.iv122.prol = phi i64 [ %indvars.iv.next123.prol, %for_loop_body70.us.prol ], [ %indvars.iv122.ph, %for_loop_body70.us.prol.preheader ]
  %.1102.us.prol = phi float [ %887, %for_loop_body70.us.prol ], [ %.1102.us.ph, %for_loop_body70.us.prol.preheader ]
  %879 = add i64 %834, %indvars.iv122.prol
  %tmp = trunc i64 %879 to i32
  %880 = sext i32 %tmp to i64
  %881 = getelementptr float, ptr %840, i64 %880
  %882 = load float, ptr %881, align 4
  %883 = getelementptr float, ptr %842, i64 %880
  %884 = load float, ptr %883, align 4
  %885 = fsub reassoc ninf nsz float %882, %884
  %886 = tail call noundef float @llvm.fabs.f32(float %885)
  %887 = fadd reassoc ninf nsz float %886, %.1102.us.prol
  %indvars.iv.next123.prol = add nuw nsw i64 %indvars.iv122.prol, 1
  %lsr.iv.next408 = add nsw i64 %lsr.iv407, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next408, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa361.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %887, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv122.unr = phi i64 [ %indvars.iv122.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next123.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1102.us.unr = phi float [ %.1102.us.ph, %for_loop_body70.us.preheader ], [ %887, %for_loop_body70.us.prol.loopexit.loopexit ]
  %888 = sub nsw i64 %indvars.iv122.ph, %wide.trip.count125
  %889 = icmp ugt i64 %888, -4
  br i1 %889, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader392

for_loop_body70.us.preheader392:                  ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader392
  %indvars.iv122 = phi i64 [ %indvars.iv.next123.3, %for_loop_body70.us ], [ %indvars.iv122.unr, %for_loop_body70.us.preheader392 ]
  %.1102.us = phi float [ %925, %for_loop_body70.us ], [ %.1102.us.unr, %for_loop_body70.us.preheader392 ]
  %890 = add i64 %834, %indvars.iv122
  %tmp412 = trunc i64 %890 to i32
  %891 = sext i32 %tmp412 to i64
  %892 = getelementptr float, ptr %840, i64 %891
  %893 = load float, ptr %892, align 4
  %894 = getelementptr float, ptr %842, i64 %891
  %895 = load float, ptr %894, align 4
  %896 = fsub reassoc ninf nsz float %893, %895
  %897 = tail call noundef float @llvm.fabs.f32(float %896)
  %898 = fadd reassoc ninf nsz float %897, %.1102.us
  %899 = add i64 %890, 1
  %tmp411 = trunc i64 %899 to i32
  %900 = sext i32 %tmp411 to i64
  %901 = getelementptr float, ptr %840, i64 %900
  %902 = load float, ptr %901, align 4
  %903 = getelementptr float, ptr %842, i64 %900
  %904 = load float, ptr %903, align 4
  %905 = fsub reassoc ninf nsz float %902, %904
  %906 = tail call noundef float @llvm.fabs.f32(float %905)
  %907 = fadd reassoc ninf nsz float %906, %898
  %908 = add i64 %890, 2
  %tmp410 = trunc i64 %908 to i32
  %909 = sext i32 %tmp410 to i64
  %910 = getelementptr float, ptr %840, i64 %909
  %911 = load float, ptr %910, align 4
  %912 = getelementptr float, ptr %842, i64 %909
  %913 = load float, ptr %912, align 4
  %914 = fsub reassoc ninf nsz float %911, %913
  %915 = tail call noundef float @llvm.fabs.f32(float %914)
  %916 = fadd reassoc ninf nsz float %915, %907
  %917 = add i64 %890, 3
  %tmp409 = trunc i64 %917 to i32
  %918 = sext i32 %tmp409 to i64
  %919 = getelementptr float, ptr %840, i64 %918
  %920 = load float, ptr %919, align 4
  %921 = getelementptr float, ptr %842, i64 %918
  %922 = load float, ptr %921, align 4
  %923 = fsub reassoc ninf nsz float %920, %922
  %924 = tail call noundef float @llvm.fabs.f32(float %923)
  %925 = fadd reassoc ninf nsz float %924, %916
  %indvars.iv.next123.3 = add nuw nsw i64 %indvars.iv122, 4
  %exitcond126.not.3 = icmp eq i64 %wide.trip.count125, %indvars.iv.next123.3
  br i1 %exitcond126.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa140 = phi float [ %866, %middle.block ], [ %878, %vec.epilog.middle.block ], [ %.lcssa361.unr, %for_loop_body70.us.prol.loopexit ], [ %925, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %indvars.iv.next128 = add nuw nsw i64 %indvars.iv127, 1
  %exitcond132.not = icmp eq i64 %indvars.iv.next128, %wide.trip.count131
  br i1 %exitcond132.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %926 = fdiv reassoc ninf nsz float %.lcssa139, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.049 = phi float [ %941, %after_for68 ], [ %926, %false_block64 ]
  %927 = getelementptr i8, ptr %81, i64 208
  %928 = load float, ptr %927, align 4
  %929 = getelementptr i8, ptr %81, i64 212
  %930 = load float, ptr %929, align 4
  %931 = fmul reassoc ninf nsz float %930, %168
  %932 = fsub reassoc ninf nsz float %.049, %931
  %933 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %932, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %928
  %934 = fmul reassoc ninf nsz float %933, %neg
  %935 = tail call noundef float @expf(float noundef %934) #9
  %936 = fmul reassoc ninf nsz float %.066, %.067
  %937 = fmul reassoc ninf nsz float %936, %935
  %938 = fcmp reassoc ninf nsz ult float %937, 0x3EB0C6F7A0000000
  br i1 %938, label %after_if3, label %true_block74

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %939 = mul i32 %72, %70
  %940 = sitofp i32 %939 to float
  %941 = fdiv reassoc ninf nsz float %.lcssa140, %940
  br label %after_if65

true_block74:                                     ; preds = %after_if65
  %942 = mul i32 %72, %70
  %943 = icmp sgt i32 %942, 0
  br i1 %943, label %for_loop_body77.lr.ph, label %after_if3

for_loop_body77.lr.ph:                            ; preds = %true_block74
  %944 = load ptr, ptr %0, align 8
  %945 = getelementptr i8, ptr %944, i64 136
  %946 = getelementptr i8, ptr %944, i64 132
  br label %for_loop_body77

for_loop_body77:                                  ; preds = %after_if86, %for_loop_body77.lr.ph
  %.045109 = phi i32 [ 0, %for_loop_body77.lr.ph ], [ %975, %after_if86 ]
  %947 = udiv i32 %.045109, %72
  %.recomposed = urem i32 %.045109, %72
  br i1 %33, label %true_block81, label %after_if83

true_block81:                                     ; preds = %for_loop_body77
  %948 = uitofp nneg i32 %947 to float
  %949 = fmul reassoc ninf nsz float %948, 0x401921FB60000000
  %950 = fdiv reassoc ninf nsz float %949, %36
  %951 = tail call noundef float @cosf(float noundef %950) #9
  %952 = fmul reassoc ninf nsz float %951, 5.000000e-01
  %953 = fsub reassoc ninf nsz float 5.000000e-01, %952
  br label %after_if83

after_if83:                                       ; preds = %true_block81, %for_loop_body77
  %.044 = phi float [ %953, %true_block81 ], [ 1.000000e+00, %for_loop_body77 ]
  br i1 %34, label %true_block84, label %after_if86

true_block84:                                     ; preds = %after_if83
  %954 = uitofp nneg i32 %.recomposed to float
  %955 = fmul reassoc ninf nsz float %954, 0x401921FB60000000
  %956 = fdiv reassoc ninf nsz float %955, %38
  %957 = tail call noundef float @cosf(float noundef %956) #9
  %958 = fmul reassoc ninf nsz float %957, 5.000000e-01
  %959 = fsub reassoc ninf nsz float 5.000000e-01, %958
  br label %after_if86

after_if86:                                       ; preds = %true_block84, %after_if83
  %.0 = phi float [ %959, %true_block84 ], [ 1.000000e+00, %after_if83 ]
  %960 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.044, float 0x3F1A36E2E0000000)
  %961 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0, float 0x3F1A36E2E0000000)
  %962 = fmul reassoc ninf nsz float %960, %937
  %963 = fmul reassoc ninf nsz float %962, %961
  %964 = add i32 %947, %64
  %965 = add i32 %.recomposed, %68
  %966 = load ptr, ptr %945, align 8
  %967 = load i32, ptr %946, align 4
  %968 = sext i32 %967 to i64
  %969 = sext i32 %964 to i64
  %970 = mul nsw i64 %968, %969
  %971 = sext i32 %965 to i64
  %972 = getelementptr float, ptr %966, i64 %970
  %973 = getelementptr float, ptr %972, i64 %971
  %974 = atomicrmw fadd ptr %973, float %963 seq_cst, align 4
  %975 = add nuw nsw i32 %.045109, 1
  %exitcond133.not = icmp eq i32 %942, %975
  br i1 %exitcond133.not, label %after_if3.loopexit, label %for_loop_body77
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

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @cosf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.6, align 8
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
