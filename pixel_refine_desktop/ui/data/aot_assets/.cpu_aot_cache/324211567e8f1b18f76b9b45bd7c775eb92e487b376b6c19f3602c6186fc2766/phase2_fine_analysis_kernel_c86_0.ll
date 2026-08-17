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
  %14 = shl i32 %8, 1
  %15 = sub i32 %2, %14
  %16 = load ptr, ptr %9, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 12
  store i32 %15, ptr %19, align 4
  %20 = load ptr, ptr %context, align 8
  %21 = getelementptr i8, ptr %20, i64 152
  %22 = load i32, ptr %21, align 4
  %23 = getelementptr i8, ptr %20, i64 168
  %24 = load i32, ptr %23, align 4
  %25 = sub i32 %22, %8
  %26 = add i32 %25, 1
  %27 = sdiv i32 %26, 2
  %28 = icmp slt i32 %26, 0
  %29 = shl nsw i32 %27, 1
  %30 = icmp ne i32 %29, %26
  %31 = and i1 %28, %30
  %.neg1 = sext i1 %31 to i32
  %32 = add nsw i32 %27, %.neg1
  %33 = sub i32 %24, %15
  %34 = add i32 %33, 1
  %35 = sdiv i32 %34, 2
  %36 = icmp slt i32 %34, 0
  %37 = shl nsw i32 %35, 1
  %38 = icmp ne i32 %37, %34
  %39 = and i1 %36, %38
  %.neg2 = sext i1 %39 to i32
  %40 = add nsw i32 %35, %.neg2
  %41 = tail call i32 @llvm.smax.i32(i32 %32, i32 0)
  %42 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %43 = load ptr, ptr %9, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  store i32 %42, ptr %46, align 4
  %47 = mul i32 %42, %41
  %48 = load ptr, ptr %9, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 32872
  %50 = load ptr, ptr %49, align 8
  store i32 %47, ptr %50, align 4
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
  %.055112 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %85, %after_if3 ]
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 4
  %43 = load i32, ptr %42, align 4
  %44 = sdiv i32 %.055112, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.055112
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %45, %.055112
  %49 = and i1 %47, %48
  %.neg83 = sext i1 %49 to i32
  %50 = add i32 %44, %.neg83
  %51 = mul i32 %50, %43
  %52 = sub i32 %.055112, %51
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
  %85 = add nsw i32 %.055112, 1
  %exitcond128.not = icmp eq i32 %85, %18
  br i1 %exitcond128.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %86 = getelementptr i8, ptr %81, i64 104
  %87 = load ptr, ptr %86, align 8
  %88 = getelementptr i8, ptr %81, i64 100
  %89 = load i32, ptr %88, align 4
  %90 = mul i32 %89, %80
  %91 = add i32 %90, %77
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %87, i64 %92
  %94 = load float, ptr %93, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.067 = phi float [ %94, %true_block4 ], [ 1.000000e+00, %true_block1 ]
  %95 = getelementptr i8, ptr %81, i64 216
  %96 = load i32, ptr %95, align 4
  %97 = icmp eq i32 %96, 1
  br i1 %97, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %98 = getelementptr i8, ptr %81, i64 120
  %99 = load ptr, ptr %98, align 8
  %100 = getelementptr i8, ptr %81, i64 116
  %101 = load i32, ptr %100, align 4
  %102 = mul i32 %101, %80
  %103 = add i32 %102, %77
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %99, i64 %104
  %106 = load float, ptr %105, align 4
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.066 = phi float [ %106, %true_block7 ], [ 1.000000e+00, %after_if6 ]
  %107 = getelementptr i8, ptr %81, i64 224
  %108 = load float, ptr %107, align 4
  %109 = fcmp reassoc ninf nsz oge float %.067, %108
  %110 = fcmp reassoc ninf nsz oge float %.066, %108
  %.065 = select i1 %109, i1 %110, i1 false
  br i1 %.065, label %true_block13, label %after_if3

true_block13:                                     ; preds = %after_if9
  %111 = getelementptr i8, ptr %81, i64 24
  %112 = load ptr, ptr %111, align 8
  %113 = getelementptr i8, ptr %81, i64 20
  %114 = load i32, ptr %113, align 4
  %115 = mul i32 %114, %79
  %116 = add i32 %115, %76
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %112, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = mul i32 %114, %64
  %121 = add i32 %120, %68
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %112, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = add nsw i32 %72, -1
  %126 = add i32 %125, %68
  %127 = add i32 %120, %126
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %112, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = add nsw i32 %70, -1
  %132 = add i32 %131, %64
  %133 = mul i32 %114, %132
  %134 = add i32 %133, %68
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
  %163 = getelementptr i8, ptr %81, i64 204
  %164 = load float, ptr %163, align 4
  %165 = fmul reassoc ninf nsz float %162, 6.075000e+02
  %166 = fadd reassoc ninf nsz float %165, 2.025000e+02
  %167 = lshr i32 %131, 1
  %168 = add i32 %64, 1
  %169 = add i32 %68, 1
  %170 = fmul reassoc ninf nsz float %164, 0x3FC99999A0000000
  %171 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %170, float 0x3F747AE140000000)
  %172 = fcmp reassoc ninf nsz ogt float %164, 0x3EB0C6F7A0000000
  %.not = icmp samesign ult i32 %70, 3
  %.not113 = icmp samesign ult i32 %72, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not113
  br i1 %or.cond, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %true_block13
  %173 = lshr i32 %125, 1
  %174 = getelementptr i8, ptr %81, i64 84
  %175 = getelementptr i8, ptr %81, i64 88
  %176 = getelementptr i8, ptr %81, i64 68
  %177 = getelementptr i8, ptr %81, i64 72
  %178 = getelementptr i8, ptr %81, i64 52
  %179 = getelementptr i8, ptr %81, i64 56
  %180 = getelementptr i8, ptr %81, i64 36
  %181 = getelementptr i8, ptr %81, i64 40
  %182 = getelementptr i8, ptr %81, i64 4
  %183 = getelementptr i8, ptr %81, i64 8
  %184 = load ptr, ptr %183, align 8
  %185 = load i32, ptr %182, align 4
  %186 = load ptr, ptr %181, align 8
  %187 = load i32, ptr %180, align 4
  %188 = load ptr, ptr %179, align 8
  %189 = load i32, ptr %178, align 4
  %190 = load ptr, ptr %177, align 8
  %191 = load i32, ptr %176, align 4
  %192 = load ptr, ptr %175, align 8
  %193 = load i32, ptr %174, align 4
  %wide.trip.count = zext i32 %173 to i64
  %194 = add nsw i64 %wide.trip.count, -1
  %195 = mul i32 %185, %168
  %196 = add i32 %169, %195
  %197 = shl i32 %185, 1
  %198 = mul i32 %114, %168
  %199 = add i32 %169, %198
  %200 = shl i32 %114, 1
  %201 = mul i32 %187, %168
  %202 = add i32 %169, %201
  %203 = shl i32 %187, 1
  %204 = mul i32 %189, %168
  %205 = add i32 %169, %204
  %206 = shl i32 %189, 1
  %207 = mul i32 %191, %168
  %208 = add i32 %169, %207
  %209 = shl i32 %191, 1
  %210 = mul i32 %193, %168
  %211 = add i32 %169, %210
  %212 = shl i32 %193, 1
  %min.iters.check174 = icmp ult i32 %72, 17
  %213 = trunc nsw i64 %194 to i32
  %mul.result = shl i32 %213, 1
  %invariant.op418 = add i32 %196, %mul.result
  %invariant.op420 = add i32 %199, %mul.result
  %214 = icmp ugt i64 %194, 4294967295
  %invariant.op422 = add i32 %202, %mul.result
  %invariant.op424 = add i32 %205, %mul.result
  %invariant.op426 = add i32 %208, %mul.result
  %invariant.op428 = add i32 %211, %mul.result
  %min.iters.check177 = icmp ult i32 %72, 65
  %n.vec181 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %172, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %215 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert192 = insertelement <8 x i32> poison, i32 %169, i64 0
  %broadcast.splat193 = shufflevector <8 x i32> %broadcast.splatinsert192, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert229 = insertelement <8 x float> poison, float %171, i64 0
  %broadcast.splat230 = shufflevector <8 x float> %broadcast.splatinsert229, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert246 = insertelement <8 x float> poison, float %166, i64 0
  %broadcast.splat247 = shufflevector <8 x float> %broadcast.splatinsert246, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat193
  %invariant.op414 = add <8 x i32> splat (i32 32), %broadcast.splat193
  %invariant.op416 = add <8 x i32> splat (i32 48), %broadcast.splat193
  %cmp.n295 = icmp eq i64 %n.vec181, %wide.trip.count
  %n.vec.remaining303 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check304 = icmp eq i64 %n.vec.remaining303, 0
  %n.vec306 = and i64 %wide.trip.count, 2147483640
  %cmp.n354 = icmp eq i64 %n.vec306, %wide.trip.count
  %216 = zext i32 %125 to i64
  %217 = lshr i64 %216, 4
  %218 = mul nsw i64 %217, -8
  %219 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check176

iter.check176:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %lsr.iv462 = phi i32 [ %lsr.iv.next463, %for_loop_test23.after_for22_crit_edge.us ], [ %196, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv458 = phi i32 [ %lsr.iv.next459, %for_loop_test23.after_for22_crit_edge.us ], [ %199, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv454 = phi i32 [ %lsr.iv.next455, %for_loop_test23.after_for22_crit_edge.us ], [ %202, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv450 = phi i32 [ %lsr.iv.next451, %for_loop_test23.after_for22_crit_edge.us ], [ %205, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv446 = phi i32 [ %lsr.iv.next447, %for_loop_test23.after_for22_crit_edge.us ], [ %208, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv442 = phi i32 [ %lsr.iv.next443, %for_loop_test23.after_for22_crit_edge.us ], [ %211, %for_loop_body16.lr.ph.split.us ]
  %.06098.us = phi i32 [ 0, %for_loop_body16.lr.ph.split.us ], [ %908, %for_loop_test23.after_for22_crit_edge.us ]
  %.06197.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ]
  %.06396.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa133, %for_loop_test23.after_for22_crit_edge.us ]
  %220 = shl nuw i32 %.06098.us, 1
  %221 = add i32 %168, %220
  %222 = mul i32 %185, %221
  %223 = mul i32 %221, %114
  %224 = mul i32 %187, %221
  %225 = mul i32 %189, %221
  %226 = mul i32 %191, %221
  %227 = mul i32 %193, %221
  br i1 %min.iters.check174, label %for_loop_body20.us.preheader, label %vector.scevcheck157

vector.scevcheck157:                              ; preds = %iter.check176
  %228 = mul i32 %212, %.06098.us
  %229 = add i32 %211, %228
  %230 = mul i32 %209, %.06098.us
  %231 = add i32 %208, %230
  %232 = mul i32 %206, %.06098.us
  %233 = add i32 %205, %232
  %234 = mul i32 %203, %.06098.us
  %235 = add i32 %202, %234
  %236 = mul i32 %200, %.06098.us
  %237 = add i32 %199, %236
  %238 = mul i32 %197, %.06098.us
  %239 = add i32 %196, %238
  %.reass419 = add i32 %238, %invariant.op418
  %240 = icmp slt i32 %.reass419, %239
  %.reass421 = add i32 %236, %invariant.op420
  %241 = icmp slt i32 %.reass421, %237
  %242 = or i1 %241, %214
  %.reass423 = add i32 %234, %invariant.op422
  %243 = icmp slt i32 %.reass423, %235
  %.reass425 = add i32 %232, %invariant.op424
  %244 = icmp slt i32 %.reass425, %233
  %.reass427 = add i32 %230, %invariant.op426
  %245 = icmp slt i32 %.reass427, %231
  %.reass429 = add i32 %228, %invariant.op428
  %246 = icmp slt i32 %.reass429, %229
  %247 = or i1 %240, %242
  %248 = or i1 %243, %247
  %249 = or i1 %244, %248
  %250 = or i1 %245, %249
  %251 = or i1 %246, %250
  br i1 %251, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check178

vector.main.loop.iter.check178:                   ; preds = %vector.scevcheck157
  br i1 %min.iters.check177, label %vec.epilog.ph301, label %vector.ph179

vector.ph179:                                     ; preds = %vector.main.loop.iter.check178
  %252 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06197.us, i64 0
  %253 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06396.us, i64 0
  %broadcast.splatinsert194 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat195 = shufflevector <8 x i32> %broadcast.splatinsert194, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert199 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat200 = shufflevector <8 x i32> %broadcast.splatinsert199, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert205 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat206 = shufflevector <8 x i32> %broadcast.splatinsert205, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert211 = insertelement <8 x i32> poison, i32 %225, i64 0
  %broadcast.splat212 = shufflevector <8 x i32> %broadcast.splatinsert211, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert217 = insertelement <8 x i32> poison, i32 %226, i64 0
  %broadcast.splat218 = shufflevector <8 x i32> %broadcast.splatinsert217, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert223 = insertelement <8 x i32> poison, i32 %227, i64 0
  %broadcast.splat224 = shufflevector <8 x i32> %broadcast.splatinsert223, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body182

vector.body182:                                   ; preds = %vector.body182, %vector.ph179
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body182 ], [ %n.vec181, %vector.ph179 ]
  %vec.phi184 = phi <8 x float> [ %252, %vector.ph179 ], [ %692, %vector.body182 ]
  %vec.phi185 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %693, %vector.body182 ]
  %vec.phi186 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %694, %vector.body182 ]
  %vec.phi187 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %695, %vector.body182 ]
  %vec.phi188 = phi <8 x float> [ %253, %vector.ph179 ], [ %688, %vector.body182 ]
  %vec.phi189 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %689, %vector.body182 ]
  %vec.phi190 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %690, %vector.body182 ]
  %vec.phi191 = phi <8 x float> [ zeroinitializer, %vector.ph179 ], [ %691, %vector.body182 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph179 ], [ %vec.ind.next, %vector.body182 ]
  %254 = shl <8 x i32> %vec.ind, splat (i32 1)
  %255 = add <8 x i32> %broadcast.splat193, %254
  %.reass = add <8 x i32> %254, %invariant.op
  %.reass415 = add <8 x i32> %254, %invariant.op414
  %.reass417 = add <8 x i32> %254, %invariant.op416
  %256 = add <8 x i32> %broadcast.splat195, %255
  %257 = add <8 x i32> %broadcast.splat195, %.reass
  %258 = add <8 x i32> %broadcast.splat195, %.reass415
  %259 = add <8 x i32> %broadcast.splat195, %.reass417
  %260 = sext <8 x i32> %256 to <8 x i64>
  %261 = sext <8 x i32> %257 to <8 x i64>
  %262 = sext <8 x i32> %258 to <8 x i64>
  %263 = sext <8 x i32> %259 to <8 x i64>
  %264 = getelementptr float, ptr %184, <8 x i64> %260
  %265 = getelementptr float, ptr %184, <8 x i64> %261
  %266 = getelementptr float, ptr %184, <8 x i64> %262
  %267 = getelementptr float, ptr %184, <8 x i64> %263
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %264, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather196 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %265, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather197 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %266, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather198 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %267, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %268 = add <8 x i32> %255, %broadcast.splat200
  %269 = add <8 x i32> %.reass, %broadcast.splat200
  %270 = add <8 x i32> %.reass415, %broadcast.splat200
  %271 = add <8 x i32> %.reass417, %broadcast.splat200
  %272 = sext <8 x i32> %268 to <8 x i64>
  %273 = sext <8 x i32> %269 to <8 x i64>
  %274 = sext <8 x i32> %270 to <8 x i64>
  %275 = sext <8 x i32> %271 to <8 x i64>
  %276 = getelementptr float, ptr %112, <8 x i64> %272
  %277 = getelementptr float, ptr %112, <8 x i64> %273
  %278 = getelementptr float, ptr %112, <8 x i64> %274
  %279 = getelementptr float, ptr %112, <8 x i64> %275
  %wide.masked.gather201 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %276, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather202 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %277, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %278, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %279, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %280 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather201
  %281 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather196, %wide.masked.gather202
  %282 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather197, %wide.masked.gather203
  %283 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather198, %wide.masked.gather204
  %284 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %280)
  %285 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %281)
  %286 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %282)
  %287 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %283)
  %288 = add <8 x i32> %broadcast.splat206, %255
  %289 = add <8 x i32> %broadcast.splat206, %.reass
  %290 = add <8 x i32> %broadcast.splat206, %.reass415
  %291 = add <8 x i32> %broadcast.splat206, %.reass417
  %292 = sext <8 x i32> %288 to <8 x i64>
  %293 = sext <8 x i32> %289 to <8 x i64>
  %294 = sext <8 x i32> %290 to <8 x i64>
  %295 = sext <8 x i32> %291 to <8 x i64>
  %296 = getelementptr float, ptr %186, <8 x i64> %292
  %297 = getelementptr float, ptr %186, <8 x i64> %293
  %298 = getelementptr float, ptr %186, <8 x i64> %294
  %299 = getelementptr float, ptr %186, <8 x i64> %295
  %wide.masked.gather207 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %296, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather208 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %297, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather209 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %298, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather210 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %299, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %300 = add <8 x i32> %broadcast.splat212, %255
  %301 = add <8 x i32> %broadcast.splat212, %.reass
  %302 = add <8 x i32> %broadcast.splat212, %.reass415
  %303 = add <8 x i32> %broadcast.splat212, %.reass417
  %304 = sext <8 x i32> %300 to <8 x i64>
  %305 = sext <8 x i32> %301 to <8 x i64>
  %306 = sext <8 x i32> %302 to <8 x i64>
  %307 = sext <8 x i32> %303 to <8 x i64>
  %308 = getelementptr float, ptr %188, <8 x i64> %304
  %309 = getelementptr float, ptr %188, <8 x i64> %305
  %310 = getelementptr float, ptr %188, <8 x i64> %306
  %311 = getelementptr float, ptr %188, <8 x i64> %307
  %wide.masked.gather213 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %308, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather214 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %309, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather215 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %310, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather216 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %311, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %312 = add <8 x i32> %broadcast.splat218, %255
  %313 = add <8 x i32> %broadcast.splat218, %.reass
  %314 = add <8 x i32> %broadcast.splat218, %.reass415
  %315 = add <8 x i32> %broadcast.splat218, %.reass417
  %316 = sext <8 x i32> %312 to <8 x i64>
  %317 = sext <8 x i32> %313 to <8 x i64>
  %318 = sext <8 x i32> %314 to <8 x i64>
  %319 = sext <8 x i32> %315 to <8 x i64>
  %320 = getelementptr float, ptr %190, <8 x i64> %316
  %321 = getelementptr float, ptr %190, <8 x i64> %317
  %322 = getelementptr float, ptr %190, <8 x i64> %318
  %323 = getelementptr float, ptr %190, <8 x i64> %319
  %wide.masked.gather219 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %320, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather220 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %321, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather221 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %322, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather222 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %323, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %324 = add <8 x i32> %broadcast.splat224, %255
  %325 = add <8 x i32> %broadcast.splat224, %.reass
  %326 = add <8 x i32> %broadcast.splat224, %.reass415
  %327 = add <8 x i32> %broadcast.splat224, %.reass417
  %328 = sext <8 x i32> %324 to <8 x i64>
  %329 = sext <8 x i32> %325 to <8 x i64>
  %330 = sext <8 x i32> %326 to <8 x i64>
  %331 = sext <8 x i32> %327 to <8 x i64>
  %332 = getelementptr float, ptr %192, <8 x i64> %328
  %333 = getelementptr float, ptr %192, <8 x i64> %329
  %334 = getelementptr float, ptr %192, <8 x i64> %330
  %335 = getelementptr float, ptr %192, <8 x i64> %331
  %wide.masked.gather225 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %332, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather226 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %333, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather227 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %334, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather228 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %335, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %336 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather207, %wide.masked.gather207
  %337 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather208
  %338 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather209
  %339 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather210
  %340 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather213, %wide.masked.gather213
  %341 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather214, %wide.masked.gather214
  %342 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather215, %wide.masked.gather215
  %343 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather216, %wide.masked.gather216
  %344 = fadd reassoc ninf nsz <8 x float> %340, %336
  %345 = fadd reassoc ninf nsz <8 x float> %341, %337
  %346 = fadd reassoc ninf nsz <8 x float> %342, %338
  %347 = fadd reassoc ninf nsz <8 x float> %343, %339
  %348 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather219, %wide.masked.gather219
  %349 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather220
  %350 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather221, %wide.masked.gather221
  %351 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather222, %wide.masked.gather222
  %352 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather225, %wide.masked.gather225
  %353 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather226
  %354 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather227
  %355 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather228
  %356 = fadd reassoc ninf nsz <8 x float> %352, %348
  %357 = fadd reassoc ninf nsz <8 x float> %353, %349
  %358 = fadd reassoc ninf nsz <8 x float> %354, %350
  %359 = fadd reassoc ninf nsz <8 x float> %355, %351
  %360 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %344, <8 x float> %356)
  %361 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %345, <8 x float> %357)
  %362 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %346, <8 x float> %358)
  %363 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %347, <8 x float> %359)
  %364 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather201, splat (float -2.000000e+00)
  %365 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, splat (float -2.000000e+00)
  %366 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, splat (float -2.000000e+00)
  %367 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, splat (float -2.000000e+00)
  %368 = fadd reassoc ninf nsz <8 x float> %364, splat (float 3.000000e+00)
  %369 = fadd reassoc ninf nsz <8 x float> %365, splat (float 3.000000e+00)
  %370 = fadd reassoc ninf nsz <8 x float> %366, splat (float 3.000000e+00)
  %371 = fadd reassoc ninf nsz <8 x float> %367, splat (float 3.000000e+00)
  %372 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %368, <8 x float> splat (float 3.000000e+00))
  %373 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %369, <8 x float> splat (float 3.000000e+00))
  %374 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %370, <8 x float> splat (float 3.000000e+00))
  %375 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %371, <8 x float> splat (float 3.000000e+00))
  %376 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %372, <8 x float> splat (float 1.000000e+00))
  %377 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %373, <8 x float> splat (float 1.000000e+00))
  %378 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %374, <8 x float> splat (float 1.000000e+00))
  %379 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %375, <8 x float> splat (float 1.000000e+00))
  %380 = fmul reassoc ninf nsz <8 x float> %376, %broadcast.splat230
  %381 = fmul reassoc ninf nsz <8 x float> %377, %broadcast.splat230
  %382 = fmul reassoc ninf nsz <8 x float> %378, %broadcast.splat230
  %383 = fmul reassoc ninf nsz <8 x float> %379, %broadcast.splat230
  %384 = fcmp reassoc ninf nsz olt <8 x float> %360, splat (float 1.500000e+02)
  %385 = fcmp reassoc ninf nsz olt <8 x float> %361, splat (float 1.500000e+02)
  %386 = fcmp reassoc ninf nsz olt <8 x float> %362, splat (float 1.500000e+02)
  %387 = fcmp reassoc ninf nsz olt <8 x float> %363, splat (float 1.500000e+02)
  %388 = xor <8 x i1> %384, splat (i1 true)
  %389 = xor <8 x i1> %385, splat (i1 true)
  %390 = xor <8 x i1> %386, splat (i1 true)
  %391 = xor <8 x i1> %387, splat (i1 true)
  %392 = select <8 x i1> %broadcast.splat, <8 x i1> %388, <8 x i1> zeroinitializer
  %393 = select <8 x i1> %broadcast.splat, <8 x i1> %389, <8 x i1> zeroinitializer
  %394 = select <8 x i1> %broadcast.splat, <8 x i1> %390, <8 x i1> zeroinitializer
  %395 = select <8 x i1> %broadcast.splat, <8 x i1> %391, <8 x i1> zeroinitializer
  %396 = fcmp reassoc ninf nsz olt <8 x float> %284, %380
  %397 = fcmp reassoc ninf nsz olt <8 x float> %285, %381
  %398 = fcmp reassoc ninf nsz olt <8 x float> %286, %382
  %399 = fcmp reassoc ninf nsz olt <8 x float> %287, %383
  %400 = xor <8 x i1> %396, splat (i1 true)
  %401 = xor <8 x i1> %397, splat (i1 true)
  %402 = xor <8 x i1> %398, splat (i1 true)
  %403 = xor <8 x i1> %399, splat (i1 true)
  %404 = select <8 x i1> %392, <8 x i1> %400, <8 x i1> zeroinitializer
  %405 = select <8 x i1> %393, <8 x i1> %401, <8 x i1> zeroinitializer
  %406 = select <8 x i1> %394, <8 x i1> %402, <8 x i1> zeroinitializer
  %407 = select <8 x i1> %395, <8 x i1> %403, <8 x i1> zeroinitializer
  %408 = fmul reassoc ninf nsz <8 x float> %380, splat (float 4.000000e+00)
  %409 = fmul reassoc ninf nsz <8 x float> %381, splat (float 4.000000e+00)
  %410 = fmul reassoc ninf nsz <8 x float> %382, splat (float 4.000000e+00)
  %411 = fmul reassoc ninf nsz <8 x float> %383, splat (float 4.000000e+00)
  %412 = fdiv reassoc ninf nsz <8 x float> %284, %408
  %413 = fdiv reassoc ninf nsz <8 x float> %285, %409
  %414 = fdiv reassoc ninf nsz <8 x float> %286, %410
  %415 = fdiv reassoc ninf nsz <8 x float> %287, %411
  %416 = fcmp reassoc ninf nsz ogt <8 x float> %412, splat (float 1.000000e+00)
  %417 = fcmp reassoc ninf nsz ogt <8 x float> %413, splat (float 1.000000e+00)
  %418 = fcmp reassoc ninf nsz ogt <8 x float> %414, splat (float 1.000000e+00)
  %419 = fcmp reassoc ninf nsz ogt <8 x float> %415, splat (float 1.000000e+00)
  %420 = select <8 x i1> %416, <8 x float> splat (float 1.000000e+00), <8 x float> %412
  %421 = select <8 x i1> %417, <8 x float> splat (float 1.000000e+00), <8 x float> %413
  %422 = select <8 x i1> %418, <8 x float> splat (float 1.000000e+00), <8 x float> %414
  %423 = select <8 x i1> %419, <8 x float> splat (float 1.000000e+00), <8 x float> %415
  %424 = fmul reassoc ninf nsz <8 x float> %420, splat (float 0x3FD99999A0000000)
  %425 = fmul reassoc ninf nsz <8 x float> %421, splat (float 0x3FD99999A0000000)
  %426 = fmul reassoc ninf nsz <8 x float> %422, splat (float 0x3FD99999A0000000)
  %427 = fmul reassoc ninf nsz <8 x float> %423, splat (float 0x3FD99999A0000000)
  %428 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %424
  %429 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %425
  %430 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %426
  %431 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %427
  %432 = select <8 x i1> %392, <8 x i1> %396, <8 x i1> zeroinitializer
  %433 = select <8 x i1> %393, <8 x i1> %397, <8 x i1> zeroinitializer
  %434 = select <8 x i1> %394, <8 x i1> %398, <8 x i1> zeroinitializer
  %435 = select <8 x i1> %395, <8 x i1> %399, <8 x i1> zeroinitializer
  %436 = fmul reassoc ninf nsz <8 x float> %284, splat (float 0x3FC3333340000000)
  %437 = fmul reassoc ninf nsz <8 x float> %285, splat (float 0x3FC3333340000000)
  %438 = fmul reassoc ninf nsz <8 x float> %286, splat (float 0x3FC3333340000000)
  %439 = fmul reassoc ninf nsz <8 x float> %287, splat (float 0x3FC3333340000000)
  %440 = fdiv reassoc ninf nsz <8 x float> %436, %380
  %441 = fdiv reassoc ninf nsz <8 x float> %437, %381
  %442 = fdiv reassoc ninf nsz <8 x float> %438, %382
  %443 = fdiv reassoc ninf nsz <8 x float> %439, %383
  %444 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %440
  %445 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %441
  %446 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %442
  %447 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %443
  %448 = select <8 x i1> %broadcast.splat, <8 x i1> %384, <8 x i1> zeroinitializer
  %449 = select <8 x i1> %broadcast.splat, <8 x i1> %385, <8 x i1> zeroinitializer
  %450 = select <8 x i1> %broadcast.splat, <8 x i1> %386, <8 x i1> zeroinitializer
  %451 = select <8 x i1> %broadcast.splat, <8 x i1> %387, <8 x i1> zeroinitializer
  %452 = fmul reassoc ninf nsz <8 x float> %380, splat (float 1.500000e+00)
  %453 = fmul reassoc ninf nsz <8 x float> %381, splat (float 1.500000e+00)
  %454 = fmul reassoc ninf nsz <8 x float> %382, splat (float 1.500000e+00)
  %455 = fmul reassoc ninf nsz <8 x float> %383, splat (float 1.500000e+00)
  %456 = fcmp reassoc ninf nsz uge <8 x float> %284, %452
  %457 = fcmp reassoc ninf nsz uge <8 x float> %285, %453
  %458 = fcmp reassoc ninf nsz uge <8 x float> %286, %454
  %459 = fcmp reassoc ninf nsz uge <8 x float> %287, %455
  %460 = select <8 x i1> %448, <8 x i1> %456, <8 x i1> zeroinitializer
  %461 = select <8 x i1> %449, <8 x i1> %457, <8 x i1> zeroinitializer
  %462 = select <8 x i1> %450, <8 x i1> %458, <8 x i1> zeroinitializer
  %463 = select <8 x i1> %451, <8 x i1> %459, <8 x i1> zeroinitializer
  %464 = fsub reassoc ninf nsz <8 x float> %284, %452
  %465 = fsub reassoc ninf nsz <8 x float> %285, %453
  %466 = fsub reassoc ninf nsz <8 x float> %286, %454
  %467 = fsub reassoc ninf nsz <8 x float> %287, %455
  %468 = fdiv reassoc ninf nsz <8 x float> %464, %452
  %469 = fdiv reassoc ninf nsz <8 x float> %465, %453
  %470 = fdiv reassoc ninf nsz <8 x float> %466, %454
  %471 = fdiv reassoc ninf nsz <8 x float> %467, %455
  %472 = fcmp reassoc ninf nsz ogt <8 x float> %468, splat (float 1.000000e+00)
  %473 = fcmp reassoc ninf nsz ogt <8 x float> %469, splat (float 1.000000e+00)
  %474 = fcmp reassoc ninf nsz ogt <8 x float> %470, splat (float 1.000000e+00)
  %475 = fcmp reassoc ninf nsz ogt <8 x float> %471, splat (float 1.000000e+00)
  %476 = select <8 x i1> %472, <8 x float> splat (float 1.000000e+00), <8 x float> %468
  %477 = select <8 x i1> %473, <8 x float> splat (float 1.000000e+00), <8 x float> %469
  %478 = select <8 x i1> %474, <8 x float> splat (float 1.000000e+00), <8 x float> %470
  %479 = select <8 x i1> %475, <8 x float> splat (float 1.000000e+00), <8 x float> %471
  %480 = fmul reassoc ninf nsz <8 x float> %476, splat (float 0x3FC99999A0000000)
  %481 = fmul reassoc ninf nsz <8 x float> %477, splat (float 0x3FC99999A0000000)
  %482 = fmul reassoc ninf nsz <8 x float> %478, splat (float 0x3FC99999A0000000)
  %483 = fmul reassoc ninf nsz <8 x float> %479, splat (float 0x3FC99999A0000000)
  %484 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %480
  %485 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %481
  %486 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %482
  %487 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %483
  %488 = fmul reassoc ninf nsz <8 x float> %284, splat (float 0x3FEE666660000000)
  %489 = fmul reassoc ninf nsz <8 x float> %285, splat (float 0x3FEE666660000000)
  %490 = fmul reassoc ninf nsz <8 x float> %286, splat (float 0x3FEE666660000000)
  %491 = fmul reassoc ninf nsz <8 x float> %287, splat (float 0x3FEE666660000000)
  %492 = fdiv reassoc ninf nsz <8 x float> %488, %452
  %493 = fdiv reassoc ninf nsz <8 x float> %489, %453
  %494 = fdiv reassoc ninf nsz <8 x float> %490, %454
  %495 = fdiv reassoc ninf nsz <8 x float> %491, %455
  %496 = fadd reassoc ninf nsz <8 x float> %492, splat (float 0x3FA99999A0000000)
  %497 = fadd reassoc ninf nsz <8 x float> %493, splat (float 0x3FA99999A0000000)
  %498 = fadd reassoc ninf nsz <8 x float> %494, splat (float 0x3FA99999A0000000)
  %499 = fadd reassoc ninf nsz <8 x float> %495, splat (float 0x3FA99999A0000000)
  %500 = or <8 x i1> %448, %432
  %501 = or <8 x i1> %449, %433
  %502 = or <8 x i1> %450, %434
  %503 = or <8 x i1> %451, %435
  %504 = or <8 x i1> %500, %404
  %505 = or <8 x i1> %501, %405
  %506 = or <8 x i1> %502, %406
  %507 = or <8 x i1> %503, %407
  %508 = or <8 x i1> %504, %215
  %509 = or <8 x i1> %505, %215
  %510 = or <8 x i1> %506, %215
  %511 = or <8 x i1> %507, %215
  %predphi = select <8 x i1> %460, <8 x float> %484, <8 x float> %496
  %predphi231 = select <8 x i1> %432, <8 x float> %444, <8 x float> %predphi
  %predphi232 = select <8 x i1> %404, <8 x float> %428, <8 x float> %predphi231
  %predphi233 = select <8 x i1> %broadcast.splat, <8 x float> %predphi232, <8 x float> splat (float 1.000000e+00)
  %predphi234 = select <8 x i1> %461, <8 x float> %485, <8 x float> %497
  %predphi235 = select <8 x i1> %433, <8 x float> %445, <8 x float> %predphi234
  %predphi236 = select <8 x i1> %405, <8 x float> %429, <8 x float> %predphi235
  %predphi237 = select <8 x i1> %broadcast.splat, <8 x float> %predphi236, <8 x float> splat (float 1.000000e+00)
  %predphi238 = select <8 x i1> %462, <8 x float> %486, <8 x float> %498
  %predphi239 = select <8 x i1> %434, <8 x float> %446, <8 x float> %predphi238
  %predphi240 = select <8 x i1> %406, <8 x float> %430, <8 x float> %predphi239
  %predphi241 = select <8 x i1> %broadcast.splat, <8 x float> %predphi240, <8 x float> splat (float 1.000000e+00)
  %predphi242 = select <8 x i1> %463, <8 x float> %487, <8 x float> %499
  %predphi243 = select <8 x i1> %435, <8 x float> %447, <8 x float> %predphi242
  %predphi244 = select <8 x i1> %407, <8 x float> %431, <8 x float> %predphi243
  %predphi245 = select <8 x i1> %broadcast.splat, <8 x float> %predphi244, <8 x float> splat (float 1.000000e+00)
  %512 = fcmp reassoc ninf nsz ogt <8 x float> %360, splat (float 0x3EB0C6F7A0000000)
  %513 = fcmp reassoc ninf nsz ogt <8 x float> %361, splat (float 0x3EB0C6F7A0000000)
  %514 = fcmp reassoc ninf nsz ogt <8 x float> %362, splat (float 0x3EB0C6F7A0000000)
  %515 = fcmp reassoc ninf nsz ogt <8 x float> %363, splat (float 0x3EB0C6F7A0000000)
  %516 = select <8 x i1> %508, <8 x i1> %512, <8 x i1> zeroinitializer
  %517 = select <8 x i1> %509, <8 x i1> %513, <8 x i1> zeroinitializer
  %518 = select <8 x i1> %510, <8 x i1> %514, <8 x i1> zeroinitializer
  %519 = select <8 x i1> %511, <8 x i1> %515, <8 x i1> zeroinitializer
  %520 = fcmp reassoc ninf nsz ogt <8 x float> %344, splat (float 0x3EB0C6F7A0000000)
  %521 = fcmp reassoc ninf nsz ogt <8 x float> %345, splat (float 0x3EB0C6F7A0000000)
  %522 = fcmp reassoc ninf nsz ogt <8 x float> %346, splat (float 0x3EB0C6F7A0000000)
  %523 = fcmp reassoc ninf nsz ogt <8 x float> %347, splat (float 0x3EB0C6F7A0000000)
  %524 = fcmp reassoc ninf nsz ogt <8 x float> %356, splat (float 0x3EB0C6F7A0000000)
  %525 = fcmp reassoc ninf nsz ogt <8 x float> %357, splat (float 0x3EB0C6F7A0000000)
  %526 = fcmp reassoc ninf nsz ogt <8 x float> %358, splat (float 0x3EB0C6F7A0000000)
  %527 = fcmp reassoc ninf nsz ogt <8 x float> %359, splat (float 0x3EB0C6F7A0000000)
  %528 = select <8 x i1> %520, <8 x i1> %524, <8 x i1> zeroinitializer
  %529 = select <8 x i1> %521, <8 x i1> %525, <8 x i1> zeroinitializer
  %530 = select <8 x i1> %522, <8 x i1> %526, <8 x i1> zeroinitializer
  %531 = select <8 x i1> %523, <8 x i1> %527, <8 x i1> zeroinitializer
  %532 = select <8 x i1> %516, <8 x i1> %528, <8 x i1> zeroinitializer
  %533 = select <8 x i1> %517, <8 x i1> %529, <8 x i1> zeroinitializer
  %534 = select <8 x i1> %518, <8 x i1> %530, <8 x i1> zeroinitializer
  %535 = select <8 x i1> %519, <8 x i1> %531, <8 x i1> zeroinitializer
  %536 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather219, %wide.masked.gather207
  %537 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather208
  %538 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather221, %wide.masked.gather209
  %539 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather222, %wide.masked.gather210
  %540 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather225, %wide.masked.gather213
  %541 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather214
  %542 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather215
  %543 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather216
  %544 = fadd reassoc ninf nsz <8 x float> %540, %536
  %545 = fadd reassoc ninf nsz <8 x float> %541, %537
  %546 = fadd reassoc ninf nsz <8 x float> %542, %538
  %547 = fadd reassoc ninf nsz <8 x float> %543, %539
  %548 = fmul reassoc ninf nsz <8 x float> %356, %344
  %549 = fmul reassoc ninf nsz <8 x float> %357, %345
  %550 = fmul reassoc ninf nsz <8 x float> %358, %346
  %551 = fmul reassoc ninf nsz <8 x float> %359, %347
  %552 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %548)
  %553 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %549)
  %554 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %550)
  %555 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %551)
  %556 = fdiv reassoc ninf nsz <8 x float> %544, %552
  %557 = fdiv reassoc ninf nsz <8 x float> %545, %553
  %558 = fdiv reassoc ninf nsz <8 x float> %546, %554
  %559 = fdiv reassoc ninf nsz <8 x float> %547, %555
  %560 = fcmp reassoc ninf nsz ule <8 x float> %360, splat (float 1.500000e+02)
  %561 = fcmp reassoc ninf nsz ule <8 x float> %361, splat (float 1.500000e+02)
  %562 = fcmp reassoc ninf nsz ule <8 x float> %362, splat (float 1.500000e+02)
  %563 = fcmp reassoc ninf nsz ule <8 x float> %363, splat (float 1.500000e+02)
  %564 = fcmp reassoc ninf nsz uge <8 x float> %556, splat (float 0x3FC99999A0000000)
  %565 = fcmp reassoc ninf nsz uge <8 x float> %557, splat (float 0x3FC99999A0000000)
  %566 = fcmp reassoc ninf nsz uge <8 x float> %558, splat (float 0x3FC99999A0000000)
  %567 = fcmp reassoc ninf nsz uge <8 x float> %559, splat (float 0x3FC99999A0000000)
  %.not360 = select <8 x i1> %560, <8 x i1> splat (i1 true), <8 x i1> %564
  %.not363 = select <8 x i1> %561, <8 x i1> splat (i1 true), <8 x i1> %565
  %.not366 = select <8 x i1> %562, <8 x i1> splat (i1 true), <8 x i1> %566
  %.not369 = select <8 x i1> %563, <8 x i1> splat (i1 true), <8 x i1> %567
  %568 = select <8 x i1> %532, <8 x i1> %.not360, <8 x i1> zeroinitializer
  %569 = select <8 x i1> %533, <8 x i1> %.not363, <8 x i1> zeroinitializer
  %570 = select <8 x i1> %534, <8 x i1> %.not366, <8 x i1> zeroinitializer
  %571 = select <8 x i1> %535, <8 x i1> %.not369, <8 x i1> zeroinitializer
  %572 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %556, <8 x float> zeroinitializer)
  %573 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %557, <8 x float> zeroinitializer)
  %574 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %558, <8 x float> zeroinitializer)
  %575 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %559, <8 x float> zeroinitializer)
  %576 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %360)
  %577 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %361)
  %578 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %362)
  %579 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %363)
  %580 = fmul reassoc ninf nsz <8 x float> %576, %broadcast.splat247
  %581 = fmul reassoc ninf nsz <8 x float> %577, %broadcast.splat247
  %582 = fmul reassoc ninf nsz <8 x float> %578, %broadcast.splat247
  %583 = fmul reassoc ninf nsz <8 x float> %579, %broadcast.splat247
  %584 = fmul reassoc ninf nsz <8 x float> %580, %572
  %.fr = freeze <8 x float> %584
  %585 = fmul reassoc ninf nsz <8 x float> %581, %573
  %.fr370 = freeze <8 x float> %585
  %586 = fmul reassoc ninf nsz <8 x float> %582, %574
  %.fr371 = freeze <8 x float> %586
  %587 = fmul reassoc ninf nsz <8 x float> %583, %575
  %.fr372 = freeze <8 x float> %587
  %588 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %589 = fcmp reassoc nsz ogt <8 x float> %.fr370, splat (float 3.000000e+00)
  %590 = fcmp reassoc nsz ogt <8 x float> %.fr371, splat (float 3.000000e+00)
  %591 = fcmp reassoc nsz ogt <8 x float> %.fr372, splat (float 3.000000e+00)
  %592 = xor <8 x i1> %588, splat (i1 true)
  %593 = xor <8 x i1> %589, splat (i1 true)
  %594 = xor <8 x i1> %590, splat (i1 true)
  %595 = xor <8 x i1> %591, splat (i1 true)
  %596 = and <8 x i1> %568, %592
  %597 = and <8 x i1> %569, %593
  %598 = and <8 x i1> %570, %594
  %599 = and <8 x i1> %571, %595
  %600 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %601 = fcmp reassoc nsz olt <8 x float> %.fr370, splat (float -3.000000e+00)
  %602 = fcmp reassoc nsz olt <8 x float> %.fr371, splat (float -3.000000e+00)
  %603 = fcmp reassoc nsz olt <8 x float> %.fr372, splat (float -3.000000e+00)
  %604 = xor <8 x i1> %600, splat (i1 true)
  %605 = xor <8 x i1> %601, splat (i1 true)
  %606 = xor <8 x i1> %602, splat (i1 true)
  %607 = xor <8 x i1> %603, splat (i1 true)
  %608 = and <8 x i1> %596, %604
  %609 = and <8 x i1> %597, %605
  %610 = and <8 x i1> %598, %606
  %611 = and <8 x i1> %599, %607
  %612 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %613 = fmul reassoc ninf nsz <8 x float> %.fr370, %.fr370
  %614 = fmul reassoc ninf nsz <8 x float> %.fr371, %.fr371
  %615 = fmul reassoc ninf nsz <8 x float> %.fr372, %.fr372
  %616 = fadd reassoc ninf nsz <8 x float> %612, splat (float 2.700000e+01)
  %617 = fadd reassoc ninf nsz <8 x float> %613, splat (float 2.700000e+01)
  %618 = fadd reassoc ninf nsz <8 x float> %614, splat (float 2.700000e+01)
  %619 = fadd reassoc ninf nsz <8 x float> %615, splat (float 2.700000e+01)
  %620 = fmul reassoc ninf nsz <8 x float> %616, %.fr
  %621 = fmul reassoc ninf nsz <8 x float> %617, %.fr370
  %622 = fmul reassoc ninf nsz <8 x float> %618, %.fr371
  %623 = fmul reassoc ninf nsz <8 x float> %619, %.fr372
  %624 = fmul reassoc ninf nsz <8 x float> %612, splat (float 9.000000e+00)
  %625 = fmul reassoc ninf nsz <8 x float> %613, splat (float 9.000000e+00)
  %626 = fmul reassoc ninf nsz <8 x float> %614, splat (float 9.000000e+00)
  %627 = fmul reassoc ninf nsz <8 x float> %615, splat (float 9.000000e+00)
  %628 = fadd reassoc ninf nsz <8 x float> %624, splat (float 2.700000e+01)
  %629 = fadd reassoc ninf nsz <8 x float> %625, splat (float 2.700000e+01)
  %630 = fadd reassoc ninf nsz <8 x float> %626, splat (float 2.700000e+01)
  %631 = fadd reassoc ninf nsz <8 x float> %627, splat (float 2.700000e+01)
  %632 = fdiv reassoc ninf nsz <8 x float> %620, %628
  %633 = fdiv reassoc ninf nsz <8 x float> %621, %629
  %634 = fdiv reassoc ninf nsz <8 x float> %622, %630
  %635 = fdiv reassoc ninf nsz <8 x float> %623, %631
  %636 = fadd reassoc ninf nsz <8 x float> %632, splat (float 1.000000e+00)
  %637 = fadd reassoc ninf nsz <8 x float> %633, splat (float 1.000000e+00)
  %638 = fadd reassoc ninf nsz <8 x float> %634, splat (float 1.000000e+00)
  %639 = fadd reassoc ninf nsz <8 x float> %635, splat (float 1.000000e+00)
  %640 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %556
  %641 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %557
  %642 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %558
  %643 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %559
  %644 = fmul reassoc ninf nsz <8 x float> %640, %284
  %645 = fmul reassoc ninf nsz <8 x float> %641, %285
  %646 = fmul reassoc ninf nsz <8 x float> %642, %286
  %647 = fmul reassoc ninf nsz <8 x float> %643, %287
  %648 = and <8 x i1> %596, %600
  %649 = and <8 x i1> %597, %601
  %650 = and <8 x i1> %598, %602
  %651 = and <8 x i1> %599, %603
  %652 = and <8 x i1> %568, %588
  %653 = and <8 x i1> %569, %589
  %654 = and <8 x i1> %570, %590
  %655 = and <8 x i1> %571, %591
  %656 = xor <8 x i1> %528, splat (i1 true)
  %657 = xor <8 x i1> %529, splat (i1 true)
  %658 = xor <8 x i1> %530, splat (i1 true)
  %659 = xor <8 x i1> %531, splat (i1 true)
  %660 = select <8 x i1> %516, <8 x i1> %656, <8 x i1> zeroinitializer
  %661 = select <8 x i1> %517, <8 x i1> %657, <8 x i1> zeroinitializer
  %662 = select <8 x i1> %518, <8 x i1> %658, <8 x i1> zeroinitializer
  %663 = select <8 x i1> %519, <8 x i1> %659, <8 x i1> zeroinitializer
  %664 = xor <8 x i1> %512, splat (i1 true)
  %665 = xor <8 x i1> %513, splat (i1 true)
  %666 = xor <8 x i1> %514, splat (i1 true)
  %667 = xor <8 x i1> %515, splat (i1 true)
  %668 = select <8 x i1> %508, <8 x i1> %664, <8 x i1> zeroinitializer
  %669 = select <8 x i1> %509, <8 x i1> %665, <8 x i1> zeroinitializer
  %670 = select <8 x i1> %510, <8 x i1> %666, <8 x i1> zeroinitializer
  %671 = select <8 x i1> %511, <8 x i1> %667, <8 x i1> zeroinitializer
  %672 = select <8 x i1> %568, <8 x i1> splat (i1 true), <8 x i1> %668
  %673 = select <8 x i1> %672, <8 x i1> splat (i1 true), <8 x i1> %660
  %predphi252 = select <8 x i1> %673, <8 x float> %284, <8 x float> %644
  %674 = select <8 x i1> %569, <8 x i1> splat (i1 true), <8 x i1> %669
  %675 = select <8 x i1> %674, <8 x i1> splat (i1 true), <8 x i1> %661
  %predphi257 = select <8 x i1> %675, <8 x float> %285, <8 x float> %645
  %676 = select <8 x i1> %570, <8 x i1> splat (i1 true), <8 x i1> %670
  %677 = select <8 x i1> %676, <8 x i1> splat (i1 true), <8 x i1> %662
  %predphi262 = select <8 x i1> %677, <8 x float> %286, <8 x float> %646
  %678 = select <8 x i1> %571, <8 x i1> splat (i1 true), <8 x i1> %671
  %679 = select <8 x i1> %678, <8 x i1> splat (i1 true), <8 x i1> %663
  %predphi267 = select <8 x i1> %679, <8 x float> %287, <8 x float> %647
  %predphi270 = select <8 x i1> %652, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi271 = select <8 x i1> %608, <8 x float> %636, <8 x float> %predphi270
  %predphi272 = select <8 x i1> %648, <8 x float> zeroinitializer, <8 x float> %predphi271
  %predphi275 = select <8 x i1> %653, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi276 = select <8 x i1> %609, <8 x float> %637, <8 x float> %predphi275
  %predphi277 = select <8 x i1> %649, <8 x float> zeroinitializer, <8 x float> %predphi276
  %predphi280 = select <8 x i1> %654, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi281 = select <8 x i1> %610, <8 x float> %638, <8 x float> %predphi280
  %predphi282 = select <8 x i1> %650, <8 x float> zeroinitializer, <8 x float> %predphi281
  %predphi285 = select <8 x i1> %655, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi286 = select <8 x i1> %611, <8 x float> %639, <8 x float> %predphi285
  %predphi287 = select <8 x i1> %651, <8 x float> zeroinitializer, <8 x float> %predphi286
  %680 = fmul reassoc ninf nsz <8 x float> %predphi272, %predphi233
  %681 = fmul reassoc ninf nsz <8 x float> %predphi277, %predphi237
  %682 = fmul reassoc ninf nsz <8 x float> %predphi282, %predphi241
  %683 = fmul reassoc ninf nsz <8 x float> %predphi287, %predphi245
  %684 = fmul reassoc ninf nsz <8 x float> %680, %predphi252
  %685 = fmul reassoc ninf nsz <8 x float> %681, %predphi257
  %686 = fmul reassoc ninf nsz <8 x float> %682, %predphi262
  %687 = fmul reassoc ninf nsz <8 x float> %683, %predphi267
  %688 = fadd reassoc ninf nsz <8 x float> %684, %vec.phi188
  %689 = fadd reassoc ninf nsz <8 x float> %685, %vec.phi189
  %690 = fadd reassoc ninf nsz <8 x float> %686, %vec.phi190
  %691 = fadd reassoc ninf nsz <8 x float> %687, %vec.phi191
  %692 = fadd reassoc ninf nsz <8 x float> %680, %vec.phi184
  %693 = fadd reassoc ninf nsz <8 x float> %681, %vec.phi185
  %694 = fadd reassoc ninf nsz <8 x float> %682, %vec.phi186
  %695 = fadd reassoc ninf nsz <8 x float> %683, %vec.phi187
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %696 = icmp eq i64 %lsr.iv.next, 0
  br i1 %696, label %middle.block173, label %vector.body182, !llvm.loop !11

middle.block173:                                  ; preds = %vector.body182
  %bin.rdx289 = fadd reassoc ninf nsz <8 x float> %693, %692
  %bin.rdx290 = fadd reassoc ninf nsz <8 x float> %694, %bin.rdx289
  %bin.rdx291 = fadd reassoc ninf nsz <8 x float> %695, %bin.rdx290
  %697 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx291)
  %bin.rdx292 = fadd reassoc ninf nsz <8 x float> %689, %688
  %bin.rdx293 = fadd reassoc ninf nsz <8 x float> %690, %bin.rdx292
  %bin.rdx294 = fadd reassoc ninf nsz <8 x float> %691, %bin.rdx293
  %698 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx294)
  br i1 %cmp.n295, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check302

vec.epilog.iter.check302:                         ; preds = %middle.block173
  br i1 %min.epilog.iters.check304, label %for_loop_body20.us.preheader, label %vec.epilog.ph301

vec.epilog.ph301:                                 ; preds = %vec.epilog.iter.check302, %vector.main.loop.iter.check178
  %bc.resume.val296 = phi i64 [ %n.vec181, %vec.epilog.iter.check302 ], [ 0, %vector.main.loop.iter.check178 ]
  %bc.merge.rdx297 = phi float [ %697, %vec.epilog.iter.check302 ], [ %.06197.us, %vector.main.loop.iter.check178 ]
  %bc.merge.rdx298 = phi float [ %698, %vec.epilog.iter.check302 ], [ %.06396.us, %vector.main.loop.iter.check178 ]
  %699 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx297, i64 0
  %700 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx298, i64 0
  %701 = trunc nuw nsw i64 %bc.resume.val296 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %701, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert317 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat318 = shufflevector <8 x i32> %broadcast.splatinsert317, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert320 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat321 = shufflevector <8 x i32> %broadcast.splatinsert320, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert323 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat324 = shufflevector <8 x i32> %broadcast.splatinsert323, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert326 = insertelement <8 x i32> poison, i32 %225, i64 0
  %broadcast.splat327 = shufflevector <8 x i32> %broadcast.splatinsert326, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert329 = insertelement <8 x i32> poison, i32 %226, i64 0
  %broadcast.splat330 = shufflevector <8 x i32> %broadcast.splatinsert329, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert332 = insertelement <8 x i32> poison, i32 %227, i64 0
  %broadcast.splat333 = shufflevector <8 x i32> %broadcast.splatinsert332, <8 x i32> poison, <8 x i32> zeroinitializer
  %702 = add i64 %218, %bc.resume.val296
  br label %vec.epilog.vector.body309

vec.epilog.vector.body309:                        ; preds = %vec.epilog.vector.body309, %vec.epilog.ph301
  %lsr.iv440 = phi i64 [ %lsr.iv.next441, %vec.epilog.vector.body309 ], [ %702, %vec.epilog.ph301 ]
  %vec.phi311 = phi <8 x float> [ %699, %vec.epilog.ph301 ], [ %814, %vec.epilog.vector.body309 ]
  %vec.phi312 = phi <8 x float> [ %700, %vec.epilog.ph301 ], [ %813, %vec.epilog.vector.body309 ]
  %vec.ind313 = phi <8 x i32> [ %induction, %vec.epilog.ph301 ], [ %vec.ind.next314, %vec.epilog.vector.body309 ]
  %703 = shl <8 x i32> %vec.ind313, splat (i32 1)
  %704 = add <8 x i32> %broadcast.splat193, %703
  %705 = add <8 x i32> %broadcast.splat318, %704
  %706 = sext <8 x i32> %705 to <8 x i64>
  %707 = getelementptr float, ptr %184, <8 x i64> %706
  %wide.masked.gather319 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %707, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %708 = add <8 x i32> %704, %broadcast.splat321
  %709 = sext <8 x i32> %708 to <8 x i64>
  %710 = getelementptr float, ptr %112, <8 x i64> %709
  %wide.masked.gather322 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %710, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %711 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather319, %wide.masked.gather322
  %712 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %711)
  %713 = add <8 x i32> %broadcast.splat324, %704
  %714 = sext <8 x i32> %713 to <8 x i64>
  %715 = getelementptr float, ptr %186, <8 x i64> %714
  %wide.masked.gather325 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %715, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %716 = add <8 x i32> %broadcast.splat327, %704
  %717 = sext <8 x i32> %716 to <8 x i64>
  %718 = getelementptr float, ptr %188, <8 x i64> %717
  %wide.masked.gather328 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %718, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %719 = add <8 x i32> %broadcast.splat330, %704
  %720 = sext <8 x i32> %719 to <8 x i64>
  %721 = getelementptr float, ptr %190, <8 x i64> %720
  %wide.masked.gather331 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %721, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %722 = add <8 x i32> %broadcast.splat333, %704
  %723 = sext <8 x i32> %722 to <8 x i64>
  %724 = getelementptr float, ptr %192, <8 x i64> %723
  %wide.masked.gather334 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %724, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %725 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather325, %wide.masked.gather325
  %726 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather328, %wide.masked.gather328
  %727 = fadd reassoc ninf nsz <8 x float> %726, %725
  %728 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather331, %wide.masked.gather331
  %729 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather334, %wide.masked.gather334
  %730 = fadd reassoc ninf nsz <8 x float> %729, %728
  %731 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %727, <8 x float> %730)
  %732 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather322, splat (float -2.000000e+00)
  %733 = fadd reassoc ninf nsz <8 x float> %732, splat (float 3.000000e+00)
  %734 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %733, <8 x float> splat (float 3.000000e+00))
  %735 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %734, <8 x float> splat (float 1.000000e+00))
  %736 = fmul reassoc ninf nsz <8 x float> %735, %broadcast.splat230
  %737 = fcmp reassoc ninf nsz olt <8 x float> %731, splat (float 1.500000e+02)
  %738 = xor <8 x i1> %737, splat (i1 true)
  %739 = select <8 x i1> %broadcast.splat, <8 x i1> %738, <8 x i1> zeroinitializer
  %740 = fcmp reassoc ninf nsz olt <8 x float> %712, %736
  %741 = xor <8 x i1> %740, splat (i1 true)
  %742 = select <8 x i1> %739, <8 x i1> %741, <8 x i1> zeroinitializer
  %743 = fmul reassoc ninf nsz <8 x float> %736, splat (float 4.000000e+00)
  %744 = fdiv reassoc ninf nsz <8 x float> %712, %743
  %745 = fcmp reassoc ninf nsz ogt <8 x float> %744, splat (float 1.000000e+00)
  %746 = select <8 x i1> %745, <8 x float> splat (float 1.000000e+00), <8 x float> %744
  %747 = fmul reassoc ninf nsz <8 x float> %746, splat (float 0x3FD99999A0000000)
  %748 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %747
  %749 = select <8 x i1> %739, <8 x i1> %740, <8 x i1> zeroinitializer
  %750 = fmul reassoc ninf nsz <8 x float> %712, splat (float 0x3FC3333340000000)
  %751 = fdiv reassoc ninf nsz <8 x float> %750, %736
  %752 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %751
  %753 = select <8 x i1> %broadcast.splat, <8 x i1> %737, <8 x i1> zeroinitializer
  %754 = fmul reassoc ninf nsz <8 x float> %736, splat (float 1.500000e+00)
  %755 = fcmp reassoc ninf nsz uge <8 x float> %712, %754
  %756 = select <8 x i1> %753, <8 x i1> %755, <8 x i1> zeroinitializer
  %757 = fsub reassoc ninf nsz <8 x float> %712, %754
  %758 = fdiv reassoc ninf nsz <8 x float> %757, %754
  %759 = fcmp reassoc ninf nsz ogt <8 x float> %758, splat (float 1.000000e+00)
  %760 = select <8 x i1> %759, <8 x float> splat (float 1.000000e+00), <8 x float> %758
  %761 = fmul reassoc ninf nsz <8 x float> %760, splat (float 0x3FC99999A0000000)
  %762 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %761
  %763 = fmul reassoc ninf nsz <8 x float> %712, splat (float 0x3FEE666660000000)
  %764 = fdiv reassoc ninf nsz <8 x float> %763, %754
  %765 = fadd reassoc ninf nsz <8 x float> %764, splat (float 0x3FA99999A0000000)
  %766 = or <8 x i1> %749, %215
  %767 = or <8 x i1> %766, %753
  %768 = or <8 x i1> %767, %742
  %predphi337 = select <8 x i1> %756, <8 x float> %762, <8 x float> %765
  %predphi338 = select <8 x i1> %749, <8 x float> %752, <8 x float> %predphi337
  %predphi339 = select <8 x i1> %742, <8 x float> %748, <8 x float> %predphi338
  %predphi340 = select <8 x i1> %broadcast.splat, <8 x float> %predphi339, <8 x float> splat (float 1.000000e+00)
  %769 = fcmp reassoc ninf nsz ogt <8 x float> %731, splat (float 0x3EB0C6F7A0000000)
  %770 = select <8 x i1> %768, <8 x i1> %769, <8 x i1> zeroinitializer
  %771 = fcmp reassoc ninf nsz ogt <8 x float> %727, splat (float 0x3EB0C6F7A0000000)
  %772 = fcmp reassoc ninf nsz ogt <8 x float> %730, splat (float 0x3EB0C6F7A0000000)
  %773 = select <8 x i1> %771, <8 x i1> %772, <8 x i1> zeroinitializer
  %774 = select <8 x i1> %770, <8 x i1> %773, <8 x i1> zeroinitializer
  %775 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather331, %wide.masked.gather325
  %776 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather334, %wide.masked.gather328
  %777 = fadd reassoc ninf nsz <8 x float> %776, %775
  %778 = fmul reassoc ninf nsz <8 x float> %730, %727
  %779 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %778)
  %780 = fdiv reassoc ninf nsz <8 x float> %777, %779
  %781 = fcmp reassoc ninf nsz ule <8 x float> %731, splat (float 1.500000e+02)
  %782 = fcmp reassoc ninf nsz uge <8 x float> %780, splat (float 0x3FC99999A0000000)
  %.not375 = select <8 x i1> %781, <8 x i1> splat (i1 true), <8 x i1> %782
  %783 = select <8 x i1> %774, <8 x i1> %.not375, <8 x i1> zeroinitializer
  %784 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %780, <8 x float> zeroinitializer)
  %785 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %731)
  %786 = fmul reassoc ninf nsz <8 x float> %785, %broadcast.splat247
  %787 = fmul reassoc ninf nsz <8 x float> %786, %784
  %.fr376 = freeze <8 x float> %787
  %788 = fcmp reassoc nsz ogt <8 x float> %.fr376, splat (float 3.000000e+00)
  %789 = xor <8 x i1> %788, splat (i1 true)
  %790 = and <8 x i1> %783, %789
  %791 = fcmp reassoc nsz olt <8 x float> %.fr376, splat (float -3.000000e+00)
  %792 = xor <8 x i1> %791, splat (i1 true)
  %793 = and <8 x i1> %790, %792
  %794 = fmul reassoc ninf nsz <8 x float> %.fr376, %.fr376
  %795 = fadd reassoc ninf nsz <8 x float> %794, splat (float 2.700000e+01)
  %796 = fmul reassoc ninf nsz <8 x float> %795, %.fr376
  %797 = fmul reassoc ninf nsz <8 x float> %794, splat (float 9.000000e+00)
  %798 = fadd reassoc ninf nsz <8 x float> %797, splat (float 2.700000e+01)
  %799 = fdiv reassoc ninf nsz <8 x float> %796, %798
  %800 = fadd reassoc ninf nsz <8 x float> %799, splat (float 1.000000e+00)
  %801 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %780
  %802 = fmul reassoc ninf nsz <8 x float> %801, %712
  %803 = and <8 x i1> %790, %791
  %804 = and <8 x i1> %783, %788
  %805 = xor <8 x i1> %773, splat (i1 true)
  %806 = select <8 x i1> %770, <8 x i1> %805, <8 x i1> zeroinitializer
  %807 = xor <8 x i1> %769, splat (i1 true)
  %808 = select <8 x i1> %768, <8 x i1> %807, <8 x i1> zeroinitializer
  %809 = select <8 x i1> %783, <8 x i1> splat (i1 true), <8 x i1> %808
  %810 = select <8 x i1> %809, <8 x i1> splat (i1 true), <8 x i1> %806
  %predphi347 = select <8 x i1> %810, <8 x float> %712, <8 x float> %802
  %predphi350 = select <8 x i1> %804, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi351 = select <8 x i1> %793, <8 x float> %800, <8 x float> %predphi350
  %predphi352 = select <8 x i1> %803, <8 x float> zeroinitializer, <8 x float> %predphi351
  %811 = fmul reassoc ninf nsz <8 x float> %predphi352, %predphi340
  %812 = fmul reassoc ninf nsz <8 x float> %811, %predphi347
  %813 = fadd reassoc ninf nsz <8 x float> %812, %vec.phi312
  %814 = fadd reassoc ninf nsz <8 x float> %811, %vec.phi311
  %vec.ind.next314 = add <8 x i32> %vec.ind313, splat (i32 8)
  %lsr.iv.next441 = add i64 %lsr.iv440, 8
  %815 = icmp eq i64 %lsr.iv.next441, 0
  br i1 %815, label %vec.epilog.middle.block299, label %vec.epilog.vector.body309, !llvm.loop !14

vec.epilog.middle.block299:                       ; preds = %vec.epilog.vector.body309
  %816 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %814)
  %817 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %813)
  br i1 %cmp.n354, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block299, %vec.epilog.iter.check302, %vector.scevcheck157, %iter.check176
  %indvars.iv.ph = phi i64 [ %n.vec181, %vec.epilog.iter.check302 ], [ 0, %iter.check176 ], [ 0, %vector.scevcheck157 ], [ %n.vec306, %vec.epilog.middle.block299 ]
  %.16293.us.ph = phi float [ %697, %vec.epilog.iter.check302 ], [ %.06197.us, %iter.check176 ], [ %.06197.us, %vector.scevcheck157 ], [ %816, %vec.epilog.middle.block299 ]
  %.16492.us.ph = phi float [ %698, %vec.epilog.iter.check302 ], [ %.06396.us, %iter.check176 ], [ %.06396.us, %vector.scevcheck157 ], [ %817, %vec.epilog.middle.block299 ]
  %818 = trunc i64 %indvars.iv.ph to i32
  %819 = shl nuw i32 %818, 1
  %820 = add i64 %219, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv466 = phi i64 [ %820, %for_loop_body20.us.preheader ], [ %lsr.iv.next467, %after_if50.us ]
  %lsr.iv464 = phi i32 [ %lsr.iv462, %for_loop_body20.us.preheader ], [ %lsr.iv.next465, %after_if50.us ]
  %lsr.iv460 = phi i32 [ %lsr.iv458, %for_loop_body20.us.preheader ], [ %lsr.iv.next461, %after_if50.us ]
  %lsr.iv456 = phi i32 [ %lsr.iv454, %for_loop_body20.us.preheader ], [ %lsr.iv.next457, %after_if50.us ]
  %lsr.iv452 = phi i32 [ %lsr.iv450, %for_loop_body20.us.preheader ], [ %lsr.iv.next453, %after_if50.us ]
  %lsr.iv448 = phi i32 [ %lsr.iv446, %for_loop_body20.us.preheader ], [ %lsr.iv.next449, %after_if50.us ]
  %lsr.iv444 = phi i32 [ %lsr.iv442, %for_loop_body20.us.preheader ], [ %lsr.iv.next445, %after_if50.us ]
  %.16293.us = phi float [ %907, %after_if50.us ], [ %.16293.us.ph, %for_loop_body20.us.preheader ]
  %.16492.us = phi float [ %906, %after_if50.us ], [ %.16492.us.ph, %for_loop_body20.us.preheader ]
  %821 = add i32 %819, %lsr.iv464
  %822 = sext i32 %821 to i64
  %823 = getelementptr float, ptr %184, i64 %822
  %824 = load float, ptr %823, align 4
  %825 = add i32 %819, %lsr.iv460
  %826 = sext i32 %825 to i64
  %827 = getelementptr float, ptr %112, i64 %826
  %828 = load float, ptr %827, align 4
  %829 = fsub reassoc ninf nsz float %824, %828
  %830 = tail call noundef float @llvm.fabs.f32(float %829)
  %831 = add i32 %819, %lsr.iv456
  %832 = sext i32 %831 to i64
  %833 = getelementptr float, ptr %186, i64 %832
  %834 = load float, ptr %833, align 4
  %835 = add i32 %819, %lsr.iv452
  %836 = sext i32 %835 to i64
  %837 = getelementptr float, ptr %188, i64 %836
  %838 = load float, ptr %837, align 4
  %839 = add i32 %819, %lsr.iv448
  %840 = sext i32 %839 to i64
  %841 = getelementptr float, ptr %190, i64 %840
  %842 = load float, ptr %841, align 4
  %843 = add i32 %819, %lsr.iv444
  %844 = sext i32 %843 to i64
  %845 = getelementptr float, ptr %192, i64 %844
  %846 = load float, ptr %845, align 4
  %847 = fmul reassoc ninf nsz float %834, %834
  %848 = fmul reassoc ninf nsz float %838, %838
  %849 = fadd reassoc ninf nsz float %848, %847
  %850 = fmul reassoc ninf nsz float %842, %842
  %851 = fmul reassoc ninf nsz float %846, %846
  %852 = fadd reassoc ninf nsz float %851, %850
  %853 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %849, float %852)
  %factor.us = fmul reassoc ninf nsz float %828, -2.000000e+00
  %854 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %855 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %854, float 3.000000e+00)
  %856 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %855, float 1.000000e+00)
  %857 = fmul reassoc ninf nsz float %856, %171
  br i1 %172, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %858 = fcmp reassoc ninf nsz olt float %853, 1.500000e+02
  br i1 %858, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %859 = fcmp reassoc ninf nsz olt float %830, %857
  br i1 %859, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %860 = fmul reassoc ninf nsz float %857, 4.000000e+00
  %861 = fdiv reassoc ninf nsz float %830, %860
  %862 = fcmp reassoc ninf nsz ogt float %861, 1.000000e+00
  %spec.store.select1.us = select i1 %862, float 1.000000e+00, float %861
  %863 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %864 = fsub reassoc ninf nsz float 0x3FE6666680000000, %863
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %865 = fmul reassoc ninf nsz float %830, 0x3FC3333340000000
  %866 = fdiv reassoc ninf nsz float %865, %857
  %867 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %866
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %868 = fmul reassoc ninf nsz float %857, 1.500000e+00
  %869 = fcmp reassoc ninf nsz olt float %830, %868
  br i1 %869, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %870 = fsub reassoc ninf nsz float %830, %868
  %871 = fdiv reassoc ninf nsz float %870, %868
  %872 = fcmp reassoc ninf nsz ogt float %871, 1.000000e+00
  %spec.store.select.us = select i1 %872, float 1.000000e+00, float %871
  %873 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %874 = fsub reassoc ninf nsz float 1.000000e+00, %873
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %875 = fmul reassoc ninf nsz float %830, 0x3FEE666660000000
  %876 = fdiv reassoc ninf nsz float %875, %868
  %877 = fadd reassoc ninf nsz float %876, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.057.us = phi float [ %877, %true_block30.us ], [ %874, %false_block31.us ], [ %867, %true_block36.us ], [ %864, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %878 = fcmp reassoc ninf nsz ogt float %853, 0x3EB0C6F7A0000000
  br i1 %878, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %879 = fcmp reassoc ninf nsz ogt float %849, 0x3EB0C6F7A0000000
  %880 = fcmp reassoc ninf nsz ogt float %852, 0x3EB0C6F7A0000000
  %.052.us = select i1 %879, i1 %880, i1 false
  br i1 %.052.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %881 = fmul reassoc ninf nsz float %842, %834
  %882 = fmul reassoc ninf nsz float %846, %838
  %883 = fadd reassoc ninf nsz float %882, %881
  %884 = fmul reassoc ninf nsz float %852, %849
  %885 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %884)
  %886 = fdiv reassoc ninf nsz float %883, %885
  %887 = fcmp reassoc ninf nsz ogt float %853, 1.500000e+02
  %888 = fcmp reassoc ninf nsz olt float %886, 0x3FC99999A0000000
  %.051.us = select i1 %887, i1 %888, i1 false
  br i1 %.051.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %889 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %886, float 0.000000e+00)
  %890 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %853)
  %891 = fmul reassoc ninf nsz float %890, %166
  %892 = fmul reassoc ninf nsz float %891, %889
  %893 = fcmp reassoc ninf nsz ogt float %892, 3.000000e+00
  br i1 %893, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %894 = fcmp reassoc ninf nsz olt float %892, -3.000000e+00
  br i1 %894, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %895 = fmul reassoc ninf nsz float %892, %892
  %896 = fadd reassoc ninf nsz float %895, 2.700000e+01
  %897 = fmul reassoc ninf nsz float %896, %892
  %898 = fmul reassoc ninf nsz float %895, 9.000000e+00
  %899 = fadd reassoc ninf nsz float %898, 2.700000e+01
  %900 = fdiv reassoc ninf nsz float %897, %899
  %901 = fadd reassoc ninf nsz float %900, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %902 = fsub reassoc ninf nsz float 1.500000e+00, %886
  %903 = fmul reassoc ninf nsz float %902, %830
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.058.us = phi float [ %903, %true_block54.us ], [ %830, %true_block42.us ], [ %830, %after_if26.us ], [ %830, %false_block55.us ], [ %830, %false_block61.us ], [ %830, %false_block58.us ]
  %.054.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %901, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %904 = fmul reassoc ninf nsz float %.054.us, %.057.us
  %905 = fmul reassoc ninf nsz float %904, %.058.us
  %906 = fadd reassoc ninf nsz float %905, %.16492.us
  %907 = fadd reassoc ninf nsz float %904, %.16293.us
  %lsr.iv.next445 = add i32 %lsr.iv444, 2
  %lsr.iv.next449 = add i32 %lsr.iv448, 2
  %lsr.iv.next453 = add i32 %lsr.iv452, 2
  %lsr.iv.next457 = add i32 %lsr.iv456, 2
  %lsr.iv.next461 = add i32 %lsr.iv460, 2
  %lsr.iv.next465 = add i32 %lsr.iv464, 2
  %lsr.iv.next467 = add i64 %lsr.iv466, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next467, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block299, %middle.block173
  %.lcssa133 = phi float [ %698, %middle.block173 ], [ %817, %vec.epilog.middle.block299 ], [ %906, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %697, %middle.block173 ], [ %816, %vec.epilog.middle.block299 ], [ %907, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %908 = add nuw nsw i32 %.06098.us, 1
  %lsr.iv.next443 = add i32 %lsr.iv442, %212
  %lsr.iv.next447 = add i32 %lsr.iv446, %209
  %lsr.iv.next451 = add i32 %lsr.iv450, %206
  %lsr.iv.next455 = add i32 %lsr.iv454, %203
  %lsr.iv.next459 = add i32 %lsr.iv458, %200
  %lsr.iv.next463 = add i32 %lsr.iv462, %197
  %exitcond119.not = icmp eq i32 %908, %167
  br i1 %exitcond119.not, label %after_for18, label %iter.check176

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %909 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %909, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %true_block13
  %910 = getelementptr i8, ptr %81, i64 4
  %911 = getelementptr i8, ptr %81, i64 8
  %912 = load ptr, ptr %911, align 8
  %913 = load i32, ptr %910, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %72, i32 1)
  %smax125 = tail call i32 @llvm.smax.i32(i32 %70, i32 1)
  %wide.trip.count123 = zext i32 %smax to i64
  %914 = add nsw i64 %wide.trip.count123, -1
  %915 = mul i32 %64, %913
  %916 = add i32 %68, %915
  %min.iters.check = icmp slt i32 %72, 4
  %917 = trunc nsw i64 %914 to i32
  %invariant.op436 = add i32 %916, %917
  %invariant.op438 = add i32 %121, %917
  %918 = icmp ugt i64 %914, 4294967295
  %min.iters.check135 = icmp slt i32 %72, 32
  %n.vec = and i64 %wide.trip.count123, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count123
  %n.vec.remaining = and i64 %wide.trip.count123, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec149 = and i64 %wide.trip.count123, 2147483644
  %cmp.n155 = icmp eq i64 %n.vec149, %wide.trip.count123
  %xtraiter = and i64 %wide.trip.count123, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %919 = lshr i64 %wide.trip.count123, 2
  %920 = mul nsw i64 %919, -4
  %921 = zext i32 %121 to i64
  %922 = zext i32 %114 to i64
  %923 = zext i32 %916 to i64
  %924 = zext i32 %913 to i64
  %925 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %lsr.iv486 = phi i64 [ %lsr.iv.next487, %for_loop_test73.after_for72_crit_edge.us ], [ %923, %for_loop_body66.lr.ph.split.us ]
  %lsr.iv484 = phi i64 [ %lsr.iv.next485, %for_loop_test73.after_for72_crit_edge.us ], [ %921, %for_loop_body66.lr.ph.split.us ]
  %.047107.us = phi i32 [ 0, %for_loop_body66.lr.ph.split.us ], [ %1030, %for_loop_test73.after_for72_crit_edge.us ]
  %.048106.us = phi float [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ], [ %.lcssa134, %for_loop_test73.after_for72_crit_edge.us ]
  %lsr501 = trunc i64 %lsr.iv486 to i32
  %lsr499 = trunc i64 %lsr.iv484 to i32
  br i1 %min.iters.check, label %for_loop_body70.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %926 = mul i32 %114, %.047107.us
  %927 = add i32 %121, %926
  %928 = mul i32 %913, %.047107.us
  %929 = add i32 %916, %928
  %.reass437 = add i32 %928, %invariant.op436
  %930 = icmp slt i32 %.reass437, %929
  %.reass439 = add i32 %926, %invariant.op438
  %931 = icmp slt i32 %.reass439, %927
  %932 = or i1 %931, %918
  %933 = or i1 %930, %932
  br i1 %933, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check135, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %934 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.048106.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv476 = phi i32 [ %lsr.iv.next477, %vector.body ], [ %lsr499, %vector.ph ]
  %lsr.iv472 = phi i32 [ %lsr.iv.next473, %vector.body ], [ %lsr501, %vector.ph ]
  %lsr.iv468 = phi i64 [ %lsr.iv.next469, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %934, %vector.ph ], [ %953, %vector.body ]
  %vec.phi136 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %954, %vector.body ]
  %vec.phi137 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %955, %vector.body ]
  %vec.phi138 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %956, %vector.body ]
  %935 = sext i32 %lsr.iv472 to i64
  %936 = getelementptr float, ptr %912, i64 %935
  %937 = getelementptr i8, ptr %936, i64 32
  %938 = getelementptr i8, ptr %936, i64 64
  %939 = getelementptr i8, ptr %936, i64 96
  %wide.load = load <8 x float>, ptr %936, align 4
  %wide.load139 = load <8 x float>, ptr %937, align 4
  %wide.load140 = load <8 x float>, ptr %938, align 4
  %wide.load141 = load <8 x float>, ptr %939, align 4
  %940 = sext i32 %lsr.iv476 to i64
  %941 = getelementptr float, ptr %112, i64 %940
  %942 = getelementptr i8, ptr %941, i64 32
  %943 = getelementptr i8, ptr %941, i64 64
  %944 = getelementptr i8, ptr %941, i64 96
  %wide.load142 = load <8 x float>, ptr %941, align 4
  %wide.load143 = load <8 x float>, ptr %942, align 4
  %wide.load144 = load <8 x float>, ptr %943, align 4
  %wide.load145 = load <8 x float>, ptr %944, align 4
  %945 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load142
  %946 = fsub reassoc ninf nsz <8 x float> %wide.load139, %wide.load143
  %947 = fsub reassoc ninf nsz <8 x float> %wide.load140, %wide.load144
  %948 = fsub reassoc ninf nsz <8 x float> %wide.load141, %wide.load145
  %949 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %945)
  %950 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %946)
  %951 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %947)
  %952 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %948)
  %953 = fadd reassoc ninf nsz <8 x float> %949, %vec.phi
  %954 = fadd reassoc ninf nsz <8 x float> %950, %vec.phi136
  %955 = fadd reassoc ninf nsz <8 x float> %951, %vec.phi137
  %956 = fadd reassoc ninf nsz <8 x float> %952, %vec.phi138
  %lsr.iv.next469 = add nsw i64 %lsr.iv468, -32
  %lsr.iv.next473 = add i32 %lsr.iv472, 32
  %lsr.iv.next477 = add i32 %lsr.iv476, 32
  %957 = icmp eq i64 %lsr.iv.next469, 0
  br i1 %957, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %954, %953
  %bin.rdx146 = fadd reassoc ninf nsz <8 x float> %955, %bin.rdx
  %bin.rdx147 = fadd reassoc ninf nsz <8 x float> %956, %bin.rdx146
  %958 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx147)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %958, %vec.epilog.iter.check ], [ %.048106.us, %vector.main.loop.iter.check ]
  %959 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %960 = add i64 %920, %vec.epilog.resume.val
  %961 = trunc i64 %vec.epilog.resume.val to i32
  %962 = add i32 %lsr501, %961
  %963 = add i32 %lsr499, %961
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv482 = phi i32 [ %lsr.iv.next483, %vec.epilog.vector.body ], [ %963, %vec.epilog.ph ]
  %lsr.iv480 = phi i32 [ %lsr.iv.next481, %vec.epilog.vector.body ], [ %962, %vec.epilog.ph ]
  %lsr.iv478 = phi i64 [ %lsr.iv.next479, %vec.epilog.vector.body ], [ %960, %vec.epilog.ph ]
  %vec.phi151 = phi <4 x float> [ %959, %vec.epilog.ph ], [ %970, %vec.epilog.vector.body ]
  %964 = sext i32 %lsr.iv480 to i64
  %965 = getelementptr float, ptr %912, i64 %964
  %wide.load152 = load <4 x float>, ptr %965, align 4
  %966 = sext i32 %lsr.iv482 to i64
  %967 = getelementptr float, ptr %112, i64 %966
  %wide.load153 = load <4 x float>, ptr %967, align 4
  %968 = fsub reassoc ninf nsz <4 x float> %wide.load152, %wide.load153
  %969 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %968)
  %970 = fadd reassoc ninf nsz <4 x float> %969, %vec.phi151
  %lsr.iv.next479 = add i64 %lsr.iv478, 4
  %lsr.iv.next481 = add i32 %lsr.iv480, 4
  %lsr.iv.next483 = add i32 %lsr.iv482, 4
  %971 = icmp eq i64 %lsr.iv.next479, 0
  br i1 %971, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %972 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %970)
  br i1 %cmp.n155, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv120.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec149, %vec.epilog.middle.block ]
  %.1102.us.ph = phi float [ %958, %vec.epilog.iter.check ], [ %.048106.us, %iter.check ], [ %.048106.us, %vector.scevcheck ], [ %972, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv489 = phi i64 [ %925, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next490, %for_loop_body70.us.prol ]
  %indvars.iv120.prol = phi i64 [ %indvars.iv.next121.prol, %for_loop_body70.us.prol ], [ %indvars.iv120.ph, %for_loop_body70.us.prol.preheader ]
  %.1102.us.prol = phi float [ %983, %for_loop_body70.us.prol ], [ %.1102.us.ph, %for_loop_body70.us.prol.preheader ]
  %973 = add i64 %lsr.iv486, %indvars.iv120.prol
  %tmp488 = trunc i64 %973 to i32
  %974 = sext i32 %tmp488 to i64
  %975 = getelementptr float, ptr %912, i64 %974
  %976 = load float, ptr %975, align 4
  %977 = add i64 %lsr.iv484, %indvars.iv120.prol
  %tmp = trunc i64 %977 to i32
  %978 = sext i32 %tmp to i64
  %979 = getelementptr float, ptr %112, i64 %978
  %980 = load float, ptr %979, align 4
  %981 = fsub reassoc ninf nsz float %976, %980
  %982 = tail call noundef float @llvm.fabs.f32(float %981)
  %983 = fadd reassoc ninf nsz float %982, %.1102.us.prol
  %indvars.iv.next121.prol = add nuw nsw i64 %indvars.iv120.prol, 1
  %lsr.iv.next490 = add nsw i64 %lsr.iv489, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next490, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa394.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %983, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv120.unr = phi i64 [ %indvars.iv120.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next121.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1102.us.unr = phi float [ %.1102.us.ph, %for_loop_body70.us.preheader ], [ %983, %for_loop_body70.us.prol.loopexit.loopexit ]
  %984 = sub nsw i64 %indvars.iv120.ph, %wide.trip.count123
  %985 = icmp ugt i64 %984, -4
  br i1 %985, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader.new

for_loop_body70.us.preheader.new:                 ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader.new
  %indvars.iv120 = phi i64 [ %indvars.iv120.unr, %for_loop_body70.us.preheader.new ], [ %indvars.iv.next121.3, %for_loop_body70.us ]
  %.1102.us = phi float [ %.1102.us.unr, %for_loop_body70.us.preheader.new ], [ %1029, %for_loop_body70.us ]
  %986 = add i64 %lsr.iv486, %indvars.iv120
  %tmp498 = trunc i64 %986 to i32
  %987 = sext i32 %tmp498 to i64
  %988 = getelementptr float, ptr %912, i64 %987
  %989 = load float, ptr %988, align 4
  %990 = add i64 %lsr.iv484, %indvars.iv120
  %tmp497 = trunc i64 %990 to i32
  %991 = sext i32 %tmp497 to i64
  %992 = getelementptr float, ptr %112, i64 %991
  %993 = load float, ptr %992, align 4
  %994 = fsub reassoc ninf nsz float %989, %993
  %995 = tail call noundef float @llvm.fabs.f32(float %994)
  %996 = fadd reassoc ninf nsz float %995, %.1102.us
  %997 = add i64 %986, 1
  %tmp496 = trunc i64 %997 to i32
  %998 = sext i32 %tmp496 to i64
  %999 = getelementptr float, ptr %912, i64 %998
  %1000 = load float, ptr %999, align 4
  %1001 = add i64 %990, 1
  %tmp495 = trunc i64 %1001 to i32
  %1002 = sext i32 %tmp495 to i64
  %1003 = getelementptr float, ptr %112, i64 %1002
  %1004 = load float, ptr %1003, align 4
  %1005 = fsub reassoc ninf nsz float %1000, %1004
  %1006 = tail call noundef float @llvm.fabs.f32(float %1005)
  %1007 = fadd reassoc ninf nsz float %1006, %996
  %1008 = add i64 %986, 2
  %tmp494 = trunc i64 %1008 to i32
  %1009 = sext i32 %tmp494 to i64
  %1010 = getelementptr float, ptr %912, i64 %1009
  %1011 = load float, ptr %1010, align 4
  %1012 = add i64 %990, 2
  %tmp493 = trunc i64 %1012 to i32
  %1013 = sext i32 %tmp493 to i64
  %1014 = getelementptr float, ptr %112, i64 %1013
  %1015 = load float, ptr %1014, align 4
  %1016 = fsub reassoc ninf nsz float %1011, %1015
  %1017 = tail call noundef float @llvm.fabs.f32(float %1016)
  %1018 = fadd reassoc ninf nsz float %1017, %1007
  %1019 = add i64 %986, 3
  %tmp492 = trunc i64 %1019 to i32
  %1020 = sext i32 %tmp492 to i64
  %1021 = getelementptr float, ptr %912, i64 %1020
  %1022 = load float, ptr %1021, align 4
  %1023 = add i64 %990, 3
  %tmp491 = trunc i64 %1023 to i32
  %1024 = sext i32 %tmp491 to i64
  %1025 = getelementptr float, ptr %112, i64 %1024
  %1026 = load float, ptr %1025, align 4
  %1027 = fsub reassoc ninf nsz float %1022, %1026
  %1028 = tail call noundef float @llvm.fabs.f32(float %1027)
  %1029 = fadd reassoc ninf nsz float %1028, %1018
  %indvars.iv.next121.3 = add nuw nsw i64 %indvars.iv120, 4
  %exitcond124.not.3 = icmp eq i64 %wide.trip.count123, %indvars.iv.next121.3
  br i1 %exitcond124.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa134 = phi float [ %958, %middle.block ], [ %972, %vec.epilog.middle.block ], [ %.lcssa394.unr, %for_loop_body70.us.prol.loopexit ], [ %1029, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %1030 = add nuw nsw i32 %.047107.us, 1
  %lsr.iv.next487 = add i64 %lsr.iv486, %924
  %lsr.iv.next485 = add i64 %lsr.iv484, %922
  %exitcond126.not = icmp eq i32 %1030, %smax125
  br i1 %exitcond126.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %1031 = fdiv reassoc ninf nsz float %.lcssa133, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.049 = phi float [ %1046, %after_for68 ], [ %1031, %false_block64 ]
  %1032 = getelementptr i8, ptr %81, i64 208
  %1033 = load float, ptr %1032, align 4
  %1034 = getelementptr i8, ptr %81, i64 212
  %1035 = load float, ptr %1034, align 4
  %1036 = fmul reassoc ninf nsz float %1035, %164
  %1037 = fsub reassoc ninf nsz float %.049, %1036
  %1038 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1037, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %1033
  %1039 = fmul reassoc ninf nsz float %1038, %neg
  %1040 = tail call noundef float @expf(float noundef %1039) #9
  %1041 = fmul reassoc ninf nsz float %.066, %.067
  %1042 = fmul reassoc ninf nsz float %1041, %1040
  %1043 = fcmp reassoc ninf nsz ult float %1042, 0x3EB0C6F7A0000000
  br i1 %1043, label %after_if3, label %true_block74

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %1044 = mul i32 %72, %70
  %1045 = sitofp i32 %1044 to float
  %1046 = fdiv reassoc ninf nsz float %.lcssa134, %1045
  br label %after_if65

true_block74:                                     ; preds = %after_if65
  %1047 = mul i32 %72, %70
  %1048 = icmp sgt i32 %1047, 0
  br i1 %1048, label %for_loop_body77.lr.ph, label %after_if3

for_loop_body77.lr.ph:                            ; preds = %true_block74
  %1049 = load ptr, ptr %0, align 8
  %1050 = getelementptr i8, ptr %1049, i64 136
  %1051 = getelementptr i8, ptr %1049, i64 132
  br label %for_loop_body77

for_loop_body77:                                  ; preds = %after_if86, %for_loop_body77.lr.ph
  %.045111 = phi i32 [ 0, %for_loop_body77.lr.ph ], [ %1078, %after_if86 ]
  %1052 = udiv i32 %.045111, %72
  %.recomposed = urem i32 %.045111, %72
  br i1 %33, label %true_block81, label %after_if83

true_block81:                                     ; preds = %for_loop_body77
  %1053 = uitofp nneg i32 %1052 to float
  %1054 = fmul reassoc ninf nsz float %1053, 0x401921FB60000000
  %1055 = fdiv reassoc ninf nsz float %1054, %36
  %1056 = tail call noundef float @cosf(float noundef %1055) #9
  %1057 = fmul reassoc ninf nsz float %1056, 5.000000e-01
  %1058 = fsub reassoc ninf nsz float 5.000000e-01, %1057
  br label %after_if83

after_if83:                                       ; preds = %true_block81, %for_loop_body77
  %.044 = phi float [ %1058, %true_block81 ], [ 1.000000e+00, %for_loop_body77 ]
  br i1 %34, label %true_block84, label %after_if86

true_block84:                                     ; preds = %after_if83
  %1059 = uitofp nneg i32 %.recomposed to float
  %1060 = fmul reassoc ninf nsz float %1059, 0x401921FB60000000
  %1061 = fdiv reassoc ninf nsz float %1060, %38
  %1062 = tail call noundef float @cosf(float noundef %1061) #9
  %1063 = fmul reassoc ninf nsz float %1062, 5.000000e-01
  %1064 = fsub reassoc ninf nsz float 5.000000e-01, %1063
  br label %after_if86

after_if86:                                       ; preds = %true_block84, %after_if83
  %.0 = phi float [ %1064, %true_block84 ], [ 1.000000e+00, %after_if83 ]
  %1065 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.044, float 0x3F1A36E2E0000000)
  %1066 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0, float 0x3F1A36E2E0000000)
  %1067 = fmul reassoc ninf nsz float %1065, %1042
  %1068 = fmul reassoc ninf nsz float %1067, %1066
  %1069 = add i32 %1052, %64
  %1070 = add i32 %.recomposed, %68
  %1071 = load ptr, ptr %1050, align 8
  %1072 = load i32, ptr %1051, align 4
  %1073 = mul i32 %1072, %1069
  %1074 = add i32 %1070, %1073
  %1075 = sext i32 %1074 to i64
  %1076 = getelementptr float, ptr %1071, i64 %1075
  %1077 = atomicrmw fadd ptr %1076, float %1068 seq_cst, align 4
  %1078 = add nuw nsw i32 %.045111, 1
  %exitcond127.not = icmp eq i32 %1047, %1078
  br i1 %exitcond127.not, label %after_if3.loopexit, label %for_loop_body77
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
