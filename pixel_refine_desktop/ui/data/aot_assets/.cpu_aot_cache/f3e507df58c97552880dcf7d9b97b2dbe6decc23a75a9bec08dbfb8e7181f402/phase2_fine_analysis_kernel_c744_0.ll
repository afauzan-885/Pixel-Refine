; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.10 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase2_fine_analysis_kernel_c744_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %20 = getelementptr i8, ptr %19, i64 188
  %21 = load i32, ptr %20, align 4
  %22 = load ptr, ptr %9, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 16
  store i32 %21, ptr %25, align 4
  %26 = icmp sgt i32 %21, 1
  %27 = load ptr, ptr %9, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 24
  store i1 %26, ptr %30, align 1
  %31 = add nsw i32 %21, -1
  %32 = sitofp i32 %31 to float
  %33 = fdiv reassoc ninf nsz float 1.000000e+00, %32
  %.02 = select i1 %26, float %33, float 0.000000e+00
  %34 = load ptr, ptr %9, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 28
  store float %.02, ptr %37, align 4
  %38 = load ptr, ptr %context, align 8
  %39 = getelementptr i8, ptr %38, i64 192
  %40 = load i32, ptr %39, align 4
  %41 = load ptr, ptr %9, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 20
  store i32 %40, ptr %44, align 4
  %45 = icmp sgt i32 %40, 1
  %46 = load ptr, ptr %9, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 32
  store i1 %45, ptr %49, align 1
  %50 = add nsw i32 %40, -1
  %51 = sitofp i32 %50 to float
  %52 = fdiv reassoc ninf nsz float 1.000000e+00, %51
  %.0 = select i1 %45, float %52, float 0.000000e+00
  %53 = load ptr, ptr %9, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 32872
  %55 = load ptr, ptr %54, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 36
  store float %.0, ptr %56, align 4
  %57 = load ptr, ptr %context, align 8
  %58 = getelementptr i8, ptr %57, i64 152
  %59 = load i32, ptr %58, align 4
  %60 = getelementptr i8, ptr %57, i64 168
  %61 = load i32, ptr %60, align 4
  %62 = sub i32 %59, %8
  %63 = add i32 %62, 1
  %64 = sdiv i32 %63, 2
  %65 = icmp slt i32 %63, 0
  %66 = shl nsw i32 %64, 1
  %67 = icmp ne i32 %66, %63
  %68 = and i1 %65, %67
  %.neg3 = sext i1 %68 to i32
  %69 = add nsw i32 %64, %.neg3
  %70 = sub i32 %61, %14
  %71 = add i32 %70, 1
  %72 = sdiv i32 %71, 2
  %73 = icmp slt i32 %71, 0
  %74 = shl nsw i32 %72, 1
  %75 = icmp ne i32 %74, %71
  %76 = and i1 %73, %75
  %.neg4 = sext i1 %76 to i32
  %77 = add nsw i32 %72, %.neg4
  %78 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %79 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %80 = load ptr, ptr %9, align 8
  %81 = getelementptr inbounds nuw i8, ptr %80, i64 32872
  %82 = load ptr, ptr %81, align 8
  %83 = getelementptr inbounds nuw i8, ptr %82, i64 4
  store i32 %79, ptr %83, align 4
  %84 = mul i32 %79, %78
  %85 = load ptr, ptr %9, align 8
  %86 = getelementptr inbounds nuw i8, ptr %85, i64 32872
  %87 = load ptr, ptr %86, align 8
  store i32 %84, ptr %87, align 4
  ret void
}

define void @phase2_fine_analysis_kernel_c744_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 196
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 200
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 160
  %26 = getelementptr i8, ptr %19, i64 176
  %27 = add i32 %23, -1
  %28 = add i32 %21, -1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.055112 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %79, %after_if3 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.055112, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.055112
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %35, %.055112
  %39 = and i1 %37, %38
  %.neg83 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg83
  %41 = mul i32 %40, %33
  %42 = sub i32 %.055112, %41
  %43 = shl i32 %40, 1
  %44 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %45 = load i32, ptr %44, align 4
  %46 = add i32 %43, %45
  %47 = shl i32 %42, 1
  %48 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %49 = load i32, ptr %48, align 4
  %50 = add i32 %47, %49
  %51 = load ptr, ptr %25, align 8
  %52 = sext i32 %46 to i64
  %53 = getelementptr i32, ptr %51, i64 %52
  %54 = load i32, ptr %53, align 4
  %55 = load ptr, ptr %26, align 8
  %56 = sext i32 %50 to i64
  %57 = getelementptr i32, ptr %55, i64 %56
  %58 = load i32, ptr %57, align 4
  %59 = sub i32 %21, %54
  %60 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %61 = load i32, ptr %60, align 4
  %62 = tail call i32 @llvm.smin.i32(i32 %61, i32 %59)
  %63 = sub i32 %23, %58
  %64 = getelementptr inbounds nuw i8, ptr %31, i64 20
  %65 = load i32, ptr %64, align 4
  %66 = tail call i32 @llvm.smin.i32(i32 %65, i32 %63)
  %67 = icmp sgt i32 %62, 0
  %68 = icmp sgt i32 %66, 0
  %spec.select = select i1 %67, i1 %68, i1 false
  br i1 %spec.select, label %true_block1, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %69 = lshr i32 %66, 1
  %70 = add i32 %69, %58
  %71 = tail call i32 @llvm.smin.i32(i32 %70, i32 %27)
  %72 = lshr i32 %62, 1
  %73 = add i32 %72, %54
  %74 = tail call i32 @llvm.smin.i32(i32 %73, i32 %28)
  %75 = load ptr, ptr %0, align 8
  %76 = getelementptr i8, ptr %75, i64 220
  %77 = load i32, ptr %76, align 4
  %78 = icmp eq i32 %77, 1
  br i1 %78, label %true_block4, label %after_if6

after_if3.loopexit:                               ; preds = %after_if86
  br label %after_if3

after_if3:                                        ; preds = %true_block74, %after_if65, %after_if9, %after_if3.loopexit, %for_loop_body
  %79 = add nsw i32 %.055112, 1
  %exitcond128.not = icmp eq i32 %79, %18
  br i1 %exitcond128.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %80 = getelementptr i8, ptr %75, i64 104
  %81 = load ptr, ptr %80, align 8
  %82 = getelementptr i8, ptr %75, i64 100
  %83 = load i32, ptr %82, align 4
  %84 = mul i32 %83, %74
  %85 = add i32 %84, %71
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %81, i64 %86
  %88 = load float, ptr %87, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.067 = phi float [ %88, %true_block4 ], [ 1.000000e+00, %true_block1 ]
  %89 = getelementptr i8, ptr %75, i64 216
  %90 = load i32, ptr %89, align 4
  %91 = icmp eq i32 %90, 1
  br i1 %91, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %92 = getelementptr i8, ptr %75, i64 120
  %93 = load ptr, ptr %92, align 8
  %94 = getelementptr i8, ptr %75, i64 116
  %95 = load i32, ptr %94, align 4
  %96 = mul i32 %95, %74
  %97 = add i32 %96, %71
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %93, i64 %98
  %100 = load float, ptr %99, align 4
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.066 = phi float [ %100, %true_block7 ], [ 1.000000e+00, %after_if6 ]
  %101 = getelementptr i8, ptr %75, i64 224
  %102 = load float, ptr %101, align 4
  %103 = fcmp reassoc ninf nsz oge float %.067, %102
  %104 = fcmp reassoc ninf nsz oge float %.066, %102
  %.065 = select i1 %103, i1 %104, i1 false
  br i1 %.065, label %true_block13, label %after_if3

true_block13:                                     ; preds = %after_if9
  %105 = getelementptr i8, ptr %75, i64 24
  %106 = load ptr, ptr %105, align 8
  %107 = getelementptr i8, ptr %75, i64 20
  %108 = load i32, ptr %107, align 4
  %109 = mul i32 %108, %73
  %110 = add i32 %109, %70
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %106, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = mul i32 %108, %54
  %115 = add i32 %114, %58
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %106, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = add nsw i32 %66, -1
  %120 = add i32 %119, %58
  %121 = add i32 %114, %120
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %106, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = add nsw i32 %62, -1
  %126 = add i32 %125, %54
  %127 = mul i32 %108, %126
  %128 = add i32 %127, %58
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %106, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = add i32 %127, %120
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %106, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float %135)
  %137 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float %136)
  %138 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %118, float %137)
  %139 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %113, float %138)
  %140 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float %135)
  %141 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %124, float %140)
  %142 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float %141)
  %143 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %113, float %142)
  %144 = fadd reassoc ninf nsz float %118, %113
  %145 = fadd reassoc ninf nsz float %144, %124
  %146 = fadd reassoc ninf nsz float %145, %131
  %147 = fadd reassoc ninf nsz float %146, %135
  %148 = fmul reassoc ninf nsz float %147, 0x3FC99999A0000000
  %149 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %148, float 0x3FA99999A0000000)
  %150 = fmul reassoc ninf nsz float %149, 0x3FBEB851E0000000
  %151 = fmul reassoc ninf nsz float %149, 0x3FB47AE140000000
  %152 = fsub reassoc ninf nsz float %139, %143
  %153 = fadd reassoc ninf nsz float %152, %150
  %154 = fdiv reassoc ninf nsz float %153, %151
  %155 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %154, float 1.000000e+00)
  %156 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %155, float 0.000000e+00)
  %157 = getelementptr i8, ptr %75, i64 204
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %156, 6.075000e+02
  %160 = fadd reassoc ninf nsz float %159, 2.025000e+02
  %161 = fmul reassoc ninf nsz float %158, 0x3FC99999A0000000
  %162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0x3F747AE140000000)
  %163 = fcmp reassoc ninf nsz ogt float %158, 0x3EB0C6F7A0000000
  %164 = lshr i32 %125, 1
  %165 = add i32 %54, 1
  %166 = add i32 %58, 1
  %.not = icmp samesign ult i32 %62, 3
  %.not113 = icmp samesign ult i32 %66, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not113
  br i1 %or.cond, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %true_block13
  %167 = lshr i32 %119, 1
  %168 = getelementptr i8, ptr %75, i64 84
  %169 = getelementptr i8, ptr %75, i64 88
  %170 = getelementptr i8, ptr %75, i64 68
  %171 = getelementptr i8, ptr %75, i64 72
  %172 = getelementptr i8, ptr %75, i64 52
  %173 = getelementptr i8, ptr %75, i64 56
  %174 = getelementptr i8, ptr %75, i64 36
  %175 = getelementptr i8, ptr %75, i64 40
  %176 = getelementptr i8, ptr %75, i64 4
  %177 = getelementptr i8, ptr %75, i64 8
  %178 = load ptr, ptr %177, align 8
  %179 = load i32, ptr %176, align 4
  %180 = load ptr, ptr %175, align 8
  %181 = load i32, ptr %174, align 4
  %182 = load ptr, ptr %173, align 8
  %183 = load i32, ptr %172, align 4
  %184 = load ptr, ptr %171, align 8
  %185 = load i32, ptr %170, align 4
  %186 = load ptr, ptr %169, align 8
  %187 = load i32, ptr %168, align 4
  %wide.trip.count = zext i32 %167 to i64
  %188 = add nsw i64 %wide.trip.count, -1
  %189 = mul i32 %179, %165
  %190 = add i32 %166, %189
  %191 = shl i32 %179, 1
  %192 = mul i32 %108, %165
  %193 = add i32 %166, %192
  %194 = shl i32 %108, 1
  %195 = mul i32 %181, %165
  %196 = add i32 %166, %195
  %197 = shl i32 %181, 1
  %198 = mul i32 %183, %165
  %199 = add i32 %166, %198
  %200 = shl i32 %183, 1
  %201 = mul i32 %185, %165
  %202 = add i32 %166, %201
  %203 = shl i32 %185, 1
  %204 = mul i32 %187, %165
  %205 = add i32 %166, %204
  %206 = shl i32 %187, 1
  %min.iters.check175 = icmp ult i32 %66, 17
  %207 = trunc nsw i64 %188 to i32
  %mul.result = shl i32 %207, 1
  %invariant.op419 = add i32 %190, %mul.result
  %invariant.op421 = add i32 %193, %mul.result
  %208 = icmp ugt i64 %188, 4294967295
  %invariant.op423 = add i32 %196, %mul.result
  %invariant.op425 = add i32 %199, %mul.result
  %invariant.op427 = add i32 %202, %mul.result
  %invariant.op429 = add i32 %205, %mul.result
  %min.iters.check178 = icmp ult i32 %66, 65
  %n.vec182 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %163, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %209 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert193 = insertelement <8 x i32> poison, i32 %166, i64 0
  %broadcast.splat194 = shufflevector <8 x i32> %broadcast.splatinsert193, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert230 = insertelement <8 x float> poison, float %162, i64 0
  %broadcast.splat231 = shufflevector <8 x float> %broadcast.splatinsert230, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert247 = insertelement <8 x float> poison, float %160, i64 0
  %broadcast.splat248 = shufflevector <8 x float> %broadcast.splatinsert247, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat194
  %invariant.op415 = add <8 x i32> splat (i32 32), %broadcast.splat194
  %invariant.op417 = add <8 x i32> splat (i32 48), %broadcast.splat194
  %cmp.n296 = icmp eq i64 %n.vec182, %wide.trip.count
  %n.vec.remaining304 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check305 = icmp eq i64 %n.vec.remaining304, 0
  %n.vec307 = and i64 %wide.trip.count, 2147483640
  %cmp.n355 = icmp eq i64 %n.vec307, %wide.trip.count
  %210 = zext i32 %119 to i64
  %211 = lshr i64 %210, 4
  %212 = mul nsw i64 %211, -8
  %213 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check177

iter.check177:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %lsr.iv463 = phi i32 [ %lsr.iv.next464, %for_loop_test23.after_for22_crit_edge.us ], [ %190, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv459 = phi i32 [ %lsr.iv.next460, %for_loop_test23.after_for22_crit_edge.us ], [ %193, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv455 = phi i32 [ %lsr.iv.next456, %for_loop_test23.after_for22_crit_edge.us ], [ %196, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv451 = phi i32 [ %lsr.iv.next452, %for_loop_test23.after_for22_crit_edge.us ], [ %199, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv447 = phi i32 [ %lsr.iv.next448, %for_loop_test23.after_for22_crit_edge.us ], [ %202, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv443 = phi i32 [ %lsr.iv.next444, %for_loop_test23.after_for22_crit_edge.us ], [ %205, %for_loop_body16.lr.ph.split.us ]
  %.06098.us = phi i32 [ 0, %for_loop_body16.lr.ph.split.us ], [ %902, %for_loop_test23.after_for22_crit_edge.us ]
  %.06197.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ]
  %.06396.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa134, %for_loop_test23.after_for22_crit_edge.us ]
  %214 = shl nuw i32 %.06098.us, 1
  %215 = add i32 %165, %214
  %216 = mul i32 %179, %215
  %217 = mul i32 %215, %108
  %218 = mul i32 %181, %215
  %219 = mul i32 %183, %215
  %220 = mul i32 %185, %215
  %221 = mul i32 %187, %215
  br i1 %min.iters.check175, label %for_loop_body20.us.preheader, label %vector.scevcheck158

vector.scevcheck158:                              ; preds = %iter.check177
  %222 = mul i32 %206, %.06098.us
  %223 = add i32 %205, %222
  %224 = mul i32 %203, %.06098.us
  %225 = add i32 %202, %224
  %226 = mul i32 %200, %.06098.us
  %227 = add i32 %199, %226
  %228 = mul i32 %197, %.06098.us
  %229 = add i32 %196, %228
  %230 = mul i32 %194, %.06098.us
  %231 = add i32 %193, %230
  %232 = mul i32 %191, %.06098.us
  %233 = add i32 %190, %232
  %.reass420 = add i32 %232, %invariant.op419
  %234 = icmp slt i32 %.reass420, %233
  %.reass422 = add i32 %230, %invariant.op421
  %235 = icmp slt i32 %.reass422, %231
  %236 = or i1 %235, %208
  %.reass424 = add i32 %228, %invariant.op423
  %237 = icmp slt i32 %.reass424, %229
  %.reass426 = add i32 %226, %invariant.op425
  %238 = icmp slt i32 %.reass426, %227
  %.reass428 = add i32 %224, %invariant.op427
  %239 = icmp slt i32 %.reass428, %225
  %.reass430 = add i32 %222, %invariant.op429
  %240 = icmp slt i32 %.reass430, %223
  %241 = or i1 %234, %236
  %242 = or i1 %237, %241
  %243 = or i1 %238, %242
  %244 = or i1 %239, %243
  %245 = or i1 %240, %244
  br i1 %245, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check179

vector.main.loop.iter.check179:                   ; preds = %vector.scevcheck158
  br i1 %min.iters.check178, label %vec.epilog.ph302, label %vector.ph180

vector.ph180:                                     ; preds = %vector.main.loop.iter.check179
  %246 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06197.us, i64 0
  %247 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06396.us, i64 0
  %broadcast.splatinsert195 = insertelement <8 x i32> poison, i32 %216, i64 0
  %broadcast.splat196 = shufflevector <8 x i32> %broadcast.splatinsert195, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert200 = insertelement <8 x i32> poison, i32 %217, i64 0
  %broadcast.splat201 = shufflevector <8 x i32> %broadcast.splatinsert200, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert206 = insertelement <8 x i32> poison, i32 %218, i64 0
  %broadcast.splat207 = shufflevector <8 x i32> %broadcast.splatinsert206, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert212 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat213 = shufflevector <8 x i32> %broadcast.splatinsert212, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert218 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat219 = shufflevector <8 x i32> %broadcast.splatinsert218, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert224 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat225 = shufflevector <8 x i32> %broadcast.splatinsert224, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body183

vector.body183:                                   ; preds = %vector.body183, %vector.ph180
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body183 ], [ %n.vec182, %vector.ph180 ]
  %vec.phi185 = phi <8 x float> [ %246, %vector.ph180 ], [ %686, %vector.body183 ]
  %vec.phi186 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %687, %vector.body183 ]
  %vec.phi187 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %688, %vector.body183 ]
  %vec.phi188 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %689, %vector.body183 ]
  %vec.phi189 = phi <8 x float> [ %247, %vector.ph180 ], [ %682, %vector.body183 ]
  %vec.phi190 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %683, %vector.body183 ]
  %vec.phi191 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %684, %vector.body183 ]
  %vec.phi192 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %685, %vector.body183 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph180 ], [ %vec.ind.next, %vector.body183 ]
  %248 = shl <8 x i32> %vec.ind, splat (i32 1)
  %249 = add <8 x i32> %broadcast.splat194, %248
  %.reass = add <8 x i32> %248, %invariant.op
  %.reass416 = add <8 x i32> %248, %invariant.op415
  %.reass418 = add <8 x i32> %248, %invariant.op417
  %250 = add <8 x i32> %broadcast.splat196, %249
  %251 = add <8 x i32> %broadcast.splat196, %.reass
  %252 = add <8 x i32> %broadcast.splat196, %.reass416
  %253 = add <8 x i32> %broadcast.splat196, %.reass418
  %254 = sext <8 x i32> %250 to <8 x i64>
  %255 = sext <8 x i32> %251 to <8 x i64>
  %256 = sext <8 x i32> %252 to <8 x i64>
  %257 = sext <8 x i32> %253 to <8 x i64>
  %258 = getelementptr float, ptr %178, <8 x i64> %254
  %259 = getelementptr float, ptr %178, <8 x i64> %255
  %260 = getelementptr float, ptr %178, <8 x i64> %256
  %261 = getelementptr float, ptr %178, <8 x i64> %257
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %258, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather197 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %259, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather198 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %260, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather199 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %261, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %262 = add <8 x i32> %249, %broadcast.splat201
  %263 = add <8 x i32> %.reass, %broadcast.splat201
  %264 = add <8 x i32> %.reass416, %broadcast.splat201
  %265 = add <8 x i32> %.reass418, %broadcast.splat201
  %266 = sext <8 x i32> %262 to <8 x i64>
  %267 = sext <8 x i32> %263 to <8 x i64>
  %268 = sext <8 x i32> %264 to <8 x i64>
  %269 = sext <8 x i32> %265 to <8 x i64>
  %270 = getelementptr float, ptr %106, <8 x i64> %266
  %271 = getelementptr float, ptr %106, <8 x i64> %267
  %272 = getelementptr float, ptr %106, <8 x i64> %268
  %273 = getelementptr float, ptr %106, <8 x i64> %269
  %wide.masked.gather202 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %270, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %271, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %272, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather205 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %273, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %274 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather202
  %275 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather197, %wide.masked.gather203
  %276 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather198, %wide.masked.gather204
  %277 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather199, %wide.masked.gather205
  %278 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %274)
  %279 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %275)
  %280 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %276)
  %281 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %277)
  %282 = add <8 x i32> %broadcast.splat207, %249
  %283 = add <8 x i32> %broadcast.splat207, %.reass
  %284 = add <8 x i32> %broadcast.splat207, %.reass416
  %285 = add <8 x i32> %broadcast.splat207, %.reass418
  %286 = sext <8 x i32> %282 to <8 x i64>
  %287 = sext <8 x i32> %283 to <8 x i64>
  %288 = sext <8 x i32> %284 to <8 x i64>
  %289 = sext <8 x i32> %285 to <8 x i64>
  %290 = getelementptr float, ptr %180, <8 x i64> %286
  %291 = getelementptr float, ptr %180, <8 x i64> %287
  %292 = getelementptr float, ptr %180, <8 x i64> %288
  %293 = getelementptr float, ptr %180, <8 x i64> %289
  %wide.masked.gather208 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %290, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather209 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %291, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather210 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %292, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather211 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %293, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %294 = add <8 x i32> %broadcast.splat213, %249
  %295 = add <8 x i32> %broadcast.splat213, %.reass
  %296 = add <8 x i32> %broadcast.splat213, %.reass416
  %297 = add <8 x i32> %broadcast.splat213, %.reass418
  %298 = sext <8 x i32> %294 to <8 x i64>
  %299 = sext <8 x i32> %295 to <8 x i64>
  %300 = sext <8 x i32> %296 to <8 x i64>
  %301 = sext <8 x i32> %297 to <8 x i64>
  %302 = getelementptr float, ptr %182, <8 x i64> %298
  %303 = getelementptr float, ptr %182, <8 x i64> %299
  %304 = getelementptr float, ptr %182, <8 x i64> %300
  %305 = getelementptr float, ptr %182, <8 x i64> %301
  %wide.masked.gather214 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %302, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather215 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %303, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather216 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %304, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather217 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %305, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %306 = add <8 x i32> %broadcast.splat219, %249
  %307 = add <8 x i32> %broadcast.splat219, %.reass
  %308 = add <8 x i32> %broadcast.splat219, %.reass416
  %309 = add <8 x i32> %broadcast.splat219, %.reass418
  %310 = sext <8 x i32> %306 to <8 x i64>
  %311 = sext <8 x i32> %307 to <8 x i64>
  %312 = sext <8 x i32> %308 to <8 x i64>
  %313 = sext <8 x i32> %309 to <8 x i64>
  %314 = getelementptr float, ptr %184, <8 x i64> %310
  %315 = getelementptr float, ptr %184, <8 x i64> %311
  %316 = getelementptr float, ptr %184, <8 x i64> %312
  %317 = getelementptr float, ptr %184, <8 x i64> %313
  %wide.masked.gather220 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %314, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather221 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %315, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather222 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %316, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather223 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %317, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %318 = add <8 x i32> %broadcast.splat225, %249
  %319 = add <8 x i32> %broadcast.splat225, %.reass
  %320 = add <8 x i32> %broadcast.splat225, %.reass416
  %321 = add <8 x i32> %broadcast.splat225, %.reass418
  %322 = sext <8 x i32> %318 to <8 x i64>
  %323 = sext <8 x i32> %319 to <8 x i64>
  %324 = sext <8 x i32> %320 to <8 x i64>
  %325 = sext <8 x i32> %321 to <8 x i64>
  %326 = getelementptr float, ptr %186, <8 x i64> %322
  %327 = getelementptr float, ptr %186, <8 x i64> %323
  %328 = getelementptr float, ptr %186, <8 x i64> %324
  %329 = getelementptr float, ptr %186, <8 x i64> %325
  %wide.masked.gather226 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %326, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather227 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %327, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather228 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %328, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather229 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %329, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %330 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather208
  %331 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather209
  %332 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather210
  %333 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, %wide.masked.gather211
  %334 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather214, %wide.masked.gather214
  %335 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather215, %wide.masked.gather215
  %336 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather216, %wide.masked.gather216
  %337 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather217, %wide.masked.gather217
  %338 = fadd reassoc ninf nsz <8 x float> %334, %330
  %339 = fadd reassoc ninf nsz <8 x float> %335, %331
  %340 = fadd reassoc ninf nsz <8 x float> %336, %332
  %341 = fadd reassoc ninf nsz <8 x float> %337, %333
  %342 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather220
  %343 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather221, %wide.masked.gather221
  %344 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather222, %wide.masked.gather222
  %345 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather223, %wide.masked.gather223
  %346 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather226
  %347 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather227
  %348 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather228
  %349 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather229, %wide.masked.gather229
  %350 = fadd reassoc ninf nsz <8 x float> %346, %342
  %351 = fadd reassoc ninf nsz <8 x float> %347, %343
  %352 = fadd reassoc ninf nsz <8 x float> %348, %344
  %353 = fadd reassoc ninf nsz <8 x float> %349, %345
  %354 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %338, <8 x float> %350)
  %355 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %339, <8 x float> %351)
  %356 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %340, <8 x float> %352)
  %357 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %341, <8 x float> %353)
  %358 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, splat (float -2.000000e+00)
  %359 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, splat (float -2.000000e+00)
  %360 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, splat (float -2.000000e+00)
  %361 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, splat (float -2.000000e+00)
  %362 = fadd reassoc ninf nsz <8 x float> %358, splat (float 3.000000e+00)
  %363 = fadd reassoc ninf nsz <8 x float> %359, splat (float 3.000000e+00)
  %364 = fadd reassoc ninf nsz <8 x float> %360, splat (float 3.000000e+00)
  %365 = fadd reassoc ninf nsz <8 x float> %361, splat (float 3.000000e+00)
  %366 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %362, <8 x float> splat (float 3.000000e+00))
  %367 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %363, <8 x float> splat (float 3.000000e+00))
  %368 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %364, <8 x float> splat (float 3.000000e+00))
  %369 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %365, <8 x float> splat (float 3.000000e+00))
  %370 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %366, <8 x float> splat (float 1.000000e+00))
  %371 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %367, <8 x float> splat (float 1.000000e+00))
  %372 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %368, <8 x float> splat (float 1.000000e+00))
  %373 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %369, <8 x float> splat (float 1.000000e+00))
  %374 = fmul reassoc ninf nsz <8 x float> %370, %broadcast.splat231
  %375 = fmul reassoc ninf nsz <8 x float> %371, %broadcast.splat231
  %376 = fmul reassoc ninf nsz <8 x float> %372, %broadcast.splat231
  %377 = fmul reassoc ninf nsz <8 x float> %373, %broadcast.splat231
  %378 = fcmp reassoc ninf nsz olt <8 x float> %354, splat (float 1.500000e+02)
  %379 = fcmp reassoc ninf nsz olt <8 x float> %355, splat (float 1.500000e+02)
  %380 = fcmp reassoc ninf nsz olt <8 x float> %356, splat (float 1.500000e+02)
  %381 = fcmp reassoc ninf nsz olt <8 x float> %357, splat (float 1.500000e+02)
  %382 = xor <8 x i1> %378, splat (i1 true)
  %383 = xor <8 x i1> %379, splat (i1 true)
  %384 = xor <8 x i1> %380, splat (i1 true)
  %385 = xor <8 x i1> %381, splat (i1 true)
  %386 = select <8 x i1> %broadcast.splat, <8 x i1> %382, <8 x i1> zeroinitializer
  %387 = select <8 x i1> %broadcast.splat, <8 x i1> %383, <8 x i1> zeroinitializer
  %388 = select <8 x i1> %broadcast.splat, <8 x i1> %384, <8 x i1> zeroinitializer
  %389 = select <8 x i1> %broadcast.splat, <8 x i1> %385, <8 x i1> zeroinitializer
  %390 = fcmp reassoc ninf nsz olt <8 x float> %278, %374
  %391 = fcmp reassoc ninf nsz olt <8 x float> %279, %375
  %392 = fcmp reassoc ninf nsz olt <8 x float> %280, %376
  %393 = fcmp reassoc ninf nsz olt <8 x float> %281, %377
  %394 = xor <8 x i1> %390, splat (i1 true)
  %395 = xor <8 x i1> %391, splat (i1 true)
  %396 = xor <8 x i1> %392, splat (i1 true)
  %397 = xor <8 x i1> %393, splat (i1 true)
  %398 = select <8 x i1> %386, <8 x i1> %394, <8 x i1> zeroinitializer
  %399 = select <8 x i1> %387, <8 x i1> %395, <8 x i1> zeroinitializer
  %400 = select <8 x i1> %388, <8 x i1> %396, <8 x i1> zeroinitializer
  %401 = select <8 x i1> %389, <8 x i1> %397, <8 x i1> zeroinitializer
  %402 = fmul reassoc ninf nsz <8 x float> %374, splat (float 4.000000e+00)
  %403 = fmul reassoc ninf nsz <8 x float> %375, splat (float 4.000000e+00)
  %404 = fmul reassoc ninf nsz <8 x float> %376, splat (float 4.000000e+00)
  %405 = fmul reassoc ninf nsz <8 x float> %377, splat (float 4.000000e+00)
  %406 = fdiv reassoc ninf nsz <8 x float> %278, %402
  %407 = fdiv reassoc ninf nsz <8 x float> %279, %403
  %408 = fdiv reassoc ninf nsz <8 x float> %280, %404
  %409 = fdiv reassoc ninf nsz <8 x float> %281, %405
  %410 = fcmp reassoc ninf nsz ogt <8 x float> %406, splat (float 1.000000e+00)
  %411 = fcmp reassoc ninf nsz ogt <8 x float> %407, splat (float 1.000000e+00)
  %412 = fcmp reassoc ninf nsz ogt <8 x float> %408, splat (float 1.000000e+00)
  %413 = fcmp reassoc ninf nsz ogt <8 x float> %409, splat (float 1.000000e+00)
  %414 = select <8 x i1> %410, <8 x float> splat (float 1.000000e+00), <8 x float> %406
  %415 = select <8 x i1> %411, <8 x float> splat (float 1.000000e+00), <8 x float> %407
  %416 = select <8 x i1> %412, <8 x float> splat (float 1.000000e+00), <8 x float> %408
  %417 = select <8 x i1> %413, <8 x float> splat (float 1.000000e+00), <8 x float> %409
  %418 = fmul reassoc ninf nsz <8 x float> %414, splat (float 0x3FD99999A0000000)
  %419 = fmul reassoc ninf nsz <8 x float> %415, splat (float 0x3FD99999A0000000)
  %420 = fmul reassoc ninf nsz <8 x float> %416, splat (float 0x3FD99999A0000000)
  %421 = fmul reassoc ninf nsz <8 x float> %417, splat (float 0x3FD99999A0000000)
  %422 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %418
  %423 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %419
  %424 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %420
  %425 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %421
  %426 = select <8 x i1> %386, <8 x i1> %390, <8 x i1> zeroinitializer
  %427 = select <8 x i1> %387, <8 x i1> %391, <8 x i1> zeroinitializer
  %428 = select <8 x i1> %388, <8 x i1> %392, <8 x i1> zeroinitializer
  %429 = select <8 x i1> %389, <8 x i1> %393, <8 x i1> zeroinitializer
  %430 = fmul reassoc ninf nsz <8 x float> %278, splat (float 0x3FC3333340000000)
  %431 = fmul reassoc ninf nsz <8 x float> %279, splat (float 0x3FC3333340000000)
  %432 = fmul reassoc ninf nsz <8 x float> %280, splat (float 0x3FC3333340000000)
  %433 = fmul reassoc ninf nsz <8 x float> %281, splat (float 0x3FC3333340000000)
  %434 = fdiv reassoc ninf nsz <8 x float> %430, %374
  %435 = fdiv reassoc ninf nsz <8 x float> %431, %375
  %436 = fdiv reassoc ninf nsz <8 x float> %432, %376
  %437 = fdiv reassoc ninf nsz <8 x float> %433, %377
  %438 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %434
  %439 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %435
  %440 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %436
  %441 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %437
  %442 = select <8 x i1> %broadcast.splat, <8 x i1> %378, <8 x i1> zeroinitializer
  %443 = select <8 x i1> %broadcast.splat, <8 x i1> %379, <8 x i1> zeroinitializer
  %444 = select <8 x i1> %broadcast.splat, <8 x i1> %380, <8 x i1> zeroinitializer
  %445 = select <8 x i1> %broadcast.splat, <8 x i1> %381, <8 x i1> zeroinitializer
  %446 = fmul reassoc ninf nsz <8 x float> %374, splat (float 1.500000e+00)
  %447 = fmul reassoc ninf nsz <8 x float> %375, splat (float 1.500000e+00)
  %448 = fmul reassoc ninf nsz <8 x float> %376, splat (float 1.500000e+00)
  %449 = fmul reassoc ninf nsz <8 x float> %377, splat (float 1.500000e+00)
  %450 = fcmp reassoc ninf nsz uge <8 x float> %278, %446
  %451 = fcmp reassoc ninf nsz uge <8 x float> %279, %447
  %452 = fcmp reassoc ninf nsz uge <8 x float> %280, %448
  %453 = fcmp reassoc ninf nsz uge <8 x float> %281, %449
  %454 = select <8 x i1> %442, <8 x i1> %450, <8 x i1> zeroinitializer
  %455 = select <8 x i1> %443, <8 x i1> %451, <8 x i1> zeroinitializer
  %456 = select <8 x i1> %444, <8 x i1> %452, <8 x i1> zeroinitializer
  %457 = select <8 x i1> %445, <8 x i1> %453, <8 x i1> zeroinitializer
  %458 = fsub reassoc ninf nsz <8 x float> %278, %446
  %459 = fsub reassoc ninf nsz <8 x float> %279, %447
  %460 = fsub reassoc ninf nsz <8 x float> %280, %448
  %461 = fsub reassoc ninf nsz <8 x float> %281, %449
  %462 = fdiv reassoc ninf nsz <8 x float> %458, %446
  %463 = fdiv reassoc ninf nsz <8 x float> %459, %447
  %464 = fdiv reassoc ninf nsz <8 x float> %460, %448
  %465 = fdiv reassoc ninf nsz <8 x float> %461, %449
  %466 = fcmp reassoc ninf nsz ogt <8 x float> %462, splat (float 1.000000e+00)
  %467 = fcmp reassoc ninf nsz ogt <8 x float> %463, splat (float 1.000000e+00)
  %468 = fcmp reassoc ninf nsz ogt <8 x float> %464, splat (float 1.000000e+00)
  %469 = fcmp reassoc ninf nsz ogt <8 x float> %465, splat (float 1.000000e+00)
  %470 = select <8 x i1> %466, <8 x float> splat (float 1.000000e+00), <8 x float> %462
  %471 = select <8 x i1> %467, <8 x float> splat (float 1.000000e+00), <8 x float> %463
  %472 = select <8 x i1> %468, <8 x float> splat (float 1.000000e+00), <8 x float> %464
  %473 = select <8 x i1> %469, <8 x float> splat (float 1.000000e+00), <8 x float> %465
  %474 = fmul reassoc ninf nsz <8 x float> %470, splat (float 0x3FC99999A0000000)
  %475 = fmul reassoc ninf nsz <8 x float> %471, splat (float 0x3FC99999A0000000)
  %476 = fmul reassoc ninf nsz <8 x float> %472, splat (float 0x3FC99999A0000000)
  %477 = fmul reassoc ninf nsz <8 x float> %473, splat (float 0x3FC99999A0000000)
  %478 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %474
  %479 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %475
  %480 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %476
  %481 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %477
  %482 = fmul reassoc ninf nsz <8 x float> %278, splat (float 0x3FEE666660000000)
  %483 = fmul reassoc ninf nsz <8 x float> %279, splat (float 0x3FEE666660000000)
  %484 = fmul reassoc ninf nsz <8 x float> %280, splat (float 0x3FEE666660000000)
  %485 = fmul reassoc ninf nsz <8 x float> %281, splat (float 0x3FEE666660000000)
  %486 = fdiv reassoc ninf nsz <8 x float> %482, %446
  %487 = fdiv reassoc ninf nsz <8 x float> %483, %447
  %488 = fdiv reassoc ninf nsz <8 x float> %484, %448
  %489 = fdiv reassoc ninf nsz <8 x float> %485, %449
  %490 = fadd reassoc ninf nsz <8 x float> %486, splat (float 0x3FA99999A0000000)
  %491 = fadd reassoc ninf nsz <8 x float> %487, splat (float 0x3FA99999A0000000)
  %492 = fadd reassoc ninf nsz <8 x float> %488, splat (float 0x3FA99999A0000000)
  %493 = fadd reassoc ninf nsz <8 x float> %489, splat (float 0x3FA99999A0000000)
  %494 = or <8 x i1> %442, %426
  %495 = or <8 x i1> %443, %427
  %496 = or <8 x i1> %444, %428
  %497 = or <8 x i1> %445, %429
  %498 = or <8 x i1> %494, %398
  %499 = or <8 x i1> %495, %399
  %500 = or <8 x i1> %496, %400
  %501 = or <8 x i1> %497, %401
  %502 = or <8 x i1> %498, %209
  %503 = or <8 x i1> %499, %209
  %504 = or <8 x i1> %500, %209
  %505 = or <8 x i1> %501, %209
  %predphi = select <8 x i1> %454, <8 x float> %478, <8 x float> %490
  %predphi232 = select <8 x i1> %426, <8 x float> %438, <8 x float> %predphi
  %predphi233 = select <8 x i1> %398, <8 x float> %422, <8 x float> %predphi232
  %predphi234 = select <8 x i1> %broadcast.splat, <8 x float> %predphi233, <8 x float> splat (float 1.000000e+00)
  %predphi235 = select <8 x i1> %455, <8 x float> %479, <8 x float> %491
  %predphi236 = select <8 x i1> %427, <8 x float> %439, <8 x float> %predphi235
  %predphi237 = select <8 x i1> %399, <8 x float> %423, <8 x float> %predphi236
  %predphi238 = select <8 x i1> %broadcast.splat, <8 x float> %predphi237, <8 x float> splat (float 1.000000e+00)
  %predphi239 = select <8 x i1> %456, <8 x float> %480, <8 x float> %492
  %predphi240 = select <8 x i1> %428, <8 x float> %440, <8 x float> %predphi239
  %predphi241 = select <8 x i1> %400, <8 x float> %424, <8 x float> %predphi240
  %predphi242 = select <8 x i1> %broadcast.splat, <8 x float> %predphi241, <8 x float> splat (float 1.000000e+00)
  %predphi243 = select <8 x i1> %457, <8 x float> %481, <8 x float> %493
  %predphi244 = select <8 x i1> %429, <8 x float> %441, <8 x float> %predphi243
  %predphi245 = select <8 x i1> %401, <8 x float> %425, <8 x float> %predphi244
  %predphi246 = select <8 x i1> %broadcast.splat, <8 x float> %predphi245, <8 x float> splat (float 1.000000e+00)
  %506 = fcmp reassoc ninf nsz ogt <8 x float> %354, splat (float 0x3EB0C6F7A0000000)
  %507 = fcmp reassoc ninf nsz ogt <8 x float> %355, splat (float 0x3EB0C6F7A0000000)
  %508 = fcmp reassoc ninf nsz ogt <8 x float> %356, splat (float 0x3EB0C6F7A0000000)
  %509 = fcmp reassoc ninf nsz ogt <8 x float> %357, splat (float 0x3EB0C6F7A0000000)
  %510 = select <8 x i1> %502, <8 x i1> %506, <8 x i1> zeroinitializer
  %511 = select <8 x i1> %503, <8 x i1> %507, <8 x i1> zeroinitializer
  %512 = select <8 x i1> %504, <8 x i1> %508, <8 x i1> zeroinitializer
  %513 = select <8 x i1> %505, <8 x i1> %509, <8 x i1> zeroinitializer
  %514 = fcmp reassoc ninf nsz ogt <8 x float> %338, splat (float 0x3EB0C6F7A0000000)
  %515 = fcmp reassoc ninf nsz ogt <8 x float> %339, splat (float 0x3EB0C6F7A0000000)
  %516 = fcmp reassoc ninf nsz ogt <8 x float> %340, splat (float 0x3EB0C6F7A0000000)
  %517 = fcmp reassoc ninf nsz ogt <8 x float> %341, splat (float 0x3EB0C6F7A0000000)
  %518 = fcmp reassoc ninf nsz ogt <8 x float> %350, splat (float 0x3EB0C6F7A0000000)
  %519 = fcmp reassoc ninf nsz ogt <8 x float> %351, splat (float 0x3EB0C6F7A0000000)
  %520 = fcmp reassoc ninf nsz ogt <8 x float> %352, splat (float 0x3EB0C6F7A0000000)
  %521 = fcmp reassoc ninf nsz ogt <8 x float> %353, splat (float 0x3EB0C6F7A0000000)
  %522 = select <8 x i1> %514, <8 x i1> %518, <8 x i1> zeroinitializer
  %523 = select <8 x i1> %515, <8 x i1> %519, <8 x i1> zeroinitializer
  %524 = select <8 x i1> %516, <8 x i1> %520, <8 x i1> zeroinitializer
  %525 = select <8 x i1> %517, <8 x i1> %521, <8 x i1> zeroinitializer
  %526 = select <8 x i1> %510, <8 x i1> %522, <8 x i1> zeroinitializer
  %527 = select <8 x i1> %511, <8 x i1> %523, <8 x i1> zeroinitializer
  %528 = select <8 x i1> %512, <8 x i1> %524, <8 x i1> zeroinitializer
  %529 = select <8 x i1> %513, <8 x i1> %525, <8 x i1> zeroinitializer
  %530 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather208
  %531 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather221, %wide.masked.gather209
  %532 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather222, %wide.masked.gather210
  %533 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather223, %wide.masked.gather211
  %534 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather214
  %535 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather215
  %536 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather216
  %537 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather229, %wide.masked.gather217
  %538 = fadd reassoc ninf nsz <8 x float> %534, %530
  %539 = fadd reassoc ninf nsz <8 x float> %535, %531
  %540 = fadd reassoc ninf nsz <8 x float> %536, %532
  %541 = fadd reassoc ninf nsz <8 x float> %537, %533
  %542 = fmul reassoc ninf nsz <8 x float> %350, %338
  %543 = fmul reassoc ninf nsz <8 x float> %351, %339
  %544 = fmul reassoc ninf nsz <8 x float> %352, %340
  %545 = fmul reassoc ninf nsz <8 x float> %353, %341
  %546 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %542)
  %547 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %543)
  %548 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %544)
  %549 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %545)
  %550 = fdiv reassoc ninf nsz <8 x float> %538, %546
  %551 = fdiv reassoc ninf nsz <8 x float> %539, %547
  %552 = fdiv reassoc ninf nsz <8 x float> %540, %548
  %553 = fdiv reassoc ninf nsz <8 x float> %541, %549
  %554 = fcmp reassoc ninf nsz ule <8 x float> %354, splat (float 1.500000e+02)
  %555 = fcmp reassoc ninf nsz ule <8 x float> %355, splat (float 1.500000e+02)
  %556 = fcmp reassoc ninf nsz ule <8 x float> %356, splat (float 1.500000e+02)
  %557 = fcmp reassoc ninf nsz ule <8 x float> %357, splat (float 1.500000e+02)
  %558 = fcmp reassoc ninf nsz uge <8 x float> %550, splat (float 0x3FC99999A0000000)
  %559 = fcmp reassoc ninf nsz uge <8 x float> %551, splat (float 0x3FC99999A0000000)
  %560 = fcmp reassoc ninf nsz uge <8 x float> %552, splat (float 0x3FC99999A0000000)
  %561 = fcmp reassoc ninf nsz uge <8 x float> %553, splat (float 0x3FC99999A0000000)
  %.not361 = select <8 x i1> %554, <8 x i1> splat (i1 true), <8 x i1> %558
  %.not364 = select <8 x i1> %555, <8 x i1> splat (i1 true), <8 x i1> %559
  %.not367 = select <8 x i1> %556, <8 x i1> splat (i1 true), <8 x i1> %560
  %.not370 = select <8 x i1> %557, <8 x i1> splat (i1 true), <8 x i1> %561
  %562 = select <8 x i1> %526, <8 x i1> %.not361, <8 x i1> zeroinitializer
  %563 = select <8 x i1> %527, <8 x i1> %.not364, <8 x i1> zeroinitializer
  %564 = select <8 x i1> %528, <8 x i1> %.not367, <8 x i1> zeroinitializer
  %565 = select <8 x i1> %529, <8 x i1> %.not370, <8 x i1> zeroinitializer
  %566 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %550, <8 x float> zeroinitializer)
  %567 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %551, <8 x float> zeroinitializer)
  %568 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %552, <8 x float> zeroinitializer)
  %569 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %553, <8 x float> zeroinitializer)
  %570 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %354)
  %571 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %355)
  %572 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %356)
  %573 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %357)
  %574 = fmul reassoc ninf nsz <8 x float> %570, %broadcast.splat248
  %575 = fmul reassoc ninf nsz <8 x float> %571, %broadcast.splat248
  %576 = fmul reassoc ninf nsz <8 x float> %572, %broadcast.splat248
  %577 = fmul reassoc ninf nsz <8 x float> %573, %broadcast.splat248
  %578 = fmul reassoc ninf nsz <8 x float> %574, %566
  %.fr = freeze <8 x float> %578
  %579 = fmul reassoc ninf nsz <8 x float> %575, %567
  %.fr371 = freeze <8 x float> %579
  %580 = fmul reassoc ninf nsz <8 x float> %576, %568
  %.fr372 = freeze <8 x float> %580
  %581 = fmul reassoc ninf nsz <8 x float> %577, %569
  %.fr373 = freeze <8 x float> %581
  %582 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %583 = fcmp reassoc nsz ogt <8 x float> %.fr371, splat (float 3.000000e+00)
  %584 = fcmp reassoc nsz ogt <8 x float> %.fr372, splat (float 3.000000e+00)
  %585 = fcmp reassoc nsz ogt <8 x float> %.fr373, splat (float 3.000000e+00)
  %586 = xor <8 x i1> %582, splat (i1 true)
  %587 = xor <8 x i1> %583, splat (i1 true)
  %588 = xor <8 x i1> %584, splat (i1 true)
  %589 = xor <8 x i1> %585, splat (i1 true)
  %590 = and <8 x i1> %562, %586
  %591 = and <8 x i1> %563, %587
  %592 = and <8 x i1> %564, %588
  %593 = and <8 x i1> %565, %589
  %594 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %595 = fcmp reassoc nsz olt <8 x float> %.fr371, splat (float -3.000000e+00)
  %596 = fcmp reassoc nsz olt <8 x float> %.fr372, splat (float -3.000000e+00)
  %597 = fcmp reassoc nsz olt <8 x float> %.fr373, splat (float -3.000000e+00)
  %598 = xor <8 x i1> %594, splat (i1 true)
  %599 = xor <8 x i1> %595, splat (i1 true)
  %600 = xor <8 x i1> %596, splat (i1 true)
  %601 = xor <8 x i1> %597, splat (i1 true)
  %602 = and <8 x i1> %590, %598
  %603 = and <8 x i1> %591, %599
  %604 = and <8 x i1> %592, %600
  %605 = and <8 x i1> %593, %601
  %606 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %607 = fmul reassoc ninf nsz <8 x float> %.fr371, %.fr371
  %608 = fmul reassoc ninf nsz <8 x float> %.fr372, %.fr372
  %609 = fmul reassoc ninf nsz <8 x float> %.fr373, %.fr373
  %610 = fadd reassoc ninf nsz <8 x float> %606, splat (float 2.700000e+01)
  %611 = fadd reassoc ninf nsz <8 x float> %607, splat (float 2.700000e+01)
  %612 = fadd reassoc ninf nsz <8 x float> %608, splat (float 2.700000e+01)
  %613 = fadd reassoc ninf nsz <8 x float> %609, splat (float 2.700000e+01)
  %614 = fmul reassoc ninf nsz <8 x float> %610, %.fr
  %615 = fmul reassoc ninf nsz <8 x float> %611, %.fr371
  %616 = fmul reassoc ninf nsz <8 x float> %612, %.fr372
  %617 = fmul reassoc ninf nsz <8 x float> %613, %.fr373
  %618 = fmul reassoc ninf nsz <8 x float> %606, splat (float 9.000000e+00)
  %619 = fmul reassoc ninf nsz <8 x float> %607, splat (float 9.000000e+00)
  %620 = fmul reassoc ninf nsz <8 x float> %608, splat (float 9.000000e+00)
  %621 = fmul reassoc ninf nsz <8 x float> %609, splat (float 9.000000e+00)
  %622 = fadd reassoc ninf nsz <8 x float> %618, splat (float 2.700000e+01)
  %623 = fadd reassoc ninf nsz <8 x float> %619, splat (float 2.700000e+01)
  %624 = fadd reassoc ninf nsz <8 x float> %620, splat (float 2.700000e+01)
  %625 = fadd reassoc ninf nsz <8 x float> %621, splat (float 2.700000e+01)
  %626 = fdiv reassoc ninf nsz <8 x float> %614, %622
  %627 = fdiv reassoc ninf nsz <8 x float> %615, %623
  %628 = fdiv reassoc ninf nsz <8 x float> %616, %624
  %629 = fdiv reassoc ninf nsz <8 x float> %617, %625
  %630 = fadd reassoc ninf nsz <8 x float> %626, splat (float 1.000000e+00)
  %631 = fadd reassoc ninf nsz <8 x float> %627, splat (float 1.000000e+00)
  %632 = fadd reassoc ninf nsz <8 x float> %628, splat (float 1.000000e+00)
  %633 = fadd reassoc ninf nsz <8 x float> %629, splat (float 1.000000e+00)
  %634 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %550
  %635 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %551
  %636 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %552
  %637 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %553
  %638 = fmul reassoc ninf nsz <8 x float> %634, %278
  %639 = fmul reassoc ninf nsz <8 x float> %635, %279
  %640 = fmul reassoc ninf nsz <8 x float> %636, %280
  %641 = fmul reassoc ninf nsz <8 x float> %637, %281
  %642 = and <8 x i1> %590, %594
  %643 = and <8 x i1> %591, %595
  %644 = and <8 x i1> %592, %596
  %645 = and <8 x i1> %593, %597
  %646 = and <8 x i1> %562, %582
  %647 = and <8 x i1> %563, %583
  %648 = and <8 x i1> %564, %584
  %649 = and <8 x i1> %565, %585
  %650 = xor <8 x i1> %522, splat (i1 true)
  %651 = xor <8 x i1> %523, splat (i1 true)
  %652 = xor <8 x i1> %524, splat (i1 true)
  %653 = xor <8 x i1> %525, splat (i1 true)
  %654 = select <8 x i1> %510, <8 x i1> %650, <8 x i1> zeroinitializer
  %655 = select <8 x i1> %511, <8 x i1> %651, <8 x i1> zeroinitializer
  %656 = select <8 x i1> %512, <8 x i1> %652, <8 x i1> zeroinitializer
  %657 = select <8 x i1> %513, <8 x i1> %653, <8 x i1> zeroinitializer
  %658 = xor <8 x i1> %506, splat (i1 true)
  %659 = xor <8 x i1> %507, splat (i1 true)
  %660 = xor <8 x i1> %508, splat (i1 true)
  %661 = xor <8 x i1> %509, splat (i1 true)
  %662 = select <8 x i1> %502, <8 x i1> %658, <8 x i1> zeroinitializer
  %663 = select <8 x i1> %503, <8 x i1> %659, <8 x i1> zeroinitializer
  %664 = select <8 x i1> %504, <8 x i1> %660, <8 x i1> zeroinitializer
  %665 = select <8 x i1> %505, <8 x i1> %661, <8 x i1> zeroinitializer
  %666 = select <8 x i1> %562, <8 x i1> splat (i1 true), <8 x i1> %662
  %667 = select <8 x i1> %666, <8 x i1> splat (i1 true), <8 x i1> %654
  %predphi253 = select <8 x i1> %667, <8 x float> %278, <8 x float> %638
  %668 = select <8 x i1> %563, <8 x i1> splat (i1 true), <8 x i1> %663
  %669 = select <8 x i1> %668, <8 x i1> splat (i1 true), <8 x i1> %655
  %predphi258 = select <8 x i1> %669, <8 x float> %279, <8 x float> %639
  %670 = select <8 x i1> %564, <8 x i1> splat (i1 true), <8 x i1> %664
  %671 = select <8 x i1> %670, <8 x i1> splat (i1 true), <8 x i1> %656
  %predphi263 = select <8 x i1> %671, <8 x float> %280, <8 x float> %640
  %672 = select <8 x i1> %565, <8 x i1> splat (i1 true), <8 x i1> %665
  %673 = select <8 x i1> %672, <8 x i1> splat (i1 true), <8 x i1> %657
  %predphi268 = select <8 x i1> %673, <8 x float> %281, <8 x float> %641
  %predphi271 = select <8 x i1> %646, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi272 = select <8 x i1> %602, <8 x float> %630, <8 x float> %predphi271
  %predphi273 = select <8 x i1> %642, <8 x float> zeroinitializer, <8 x float> %predphi272
  %predphi276 = select <8 x i1> %647, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi277 = select <8 x i1> %603, <8 x float> %631, <8 x float> %predphi276
  %predphi278 = select <8 x i1> %643, <8 x float> zeroinitializer, <8 x float> %predphi277
  %predphi281 = select <8 x i1> %648, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi282 = select <8 x i1> %604, <8 x float> %632, <8 x float> %predphi281
  %predphi283 = select <8 x i1> %644, <8 x float> zeroinitializer, <8 x float> %predphi282
  %predphi286 = select <8 x i1> %649, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi287 = select <8 x i1> %605, <8 x float> %633, <8 x float> %predphi286
  %predphi288 = select <8 x i1> %645, <8 x float> zeroinitializer, <8 x float> %predphi287
  %674 = fmul reassoc ninf nsz <8 x float> %predphi273, %predphi234
  %675 = fmul reassoc ninf nsz <8 x float> %predphi278, %predphi238
  %676 = fmul reassoc ninf nsz <8 x float> %predphi283, %predphi242
  %677 = fmul reassoc ninf nsz <8 x float> %predphi288, %predphi246
  %678 = fmul reassoc ninf nsz <8 x float> %674, %predphi253
  %679 = fmul reassoc ninf nsz <8 x float> %675, %predphi258
  %680 = fmul reassoc ninf nsz <8 x float> %676, %predphi263
  %681 = fmul reassoc ninf nsz <8 x float> %677, %predphi268
  %682 = fadd reassoc ninf nsz <8 x float> %678, %vec.phi189
  %683 = fadd reassoc ninf nsz <8 x float> %679, %vec.phi190
  %684 = fadd reassoc ninf nsz <8 x float> %680, %vec.phi191
  %685 = fadd reassoc ninf nsz <8 x float> %681, %vec.phi192
  %686 = fadd reassoc ninf nsz <8 x float> %674, %vec.phi185
  %687 = fadd reassoc ninf nsz <8 x float> %675, %vec.phi186
  %688 = fadd reassoc ninf nsz <8 x float> %676, %vec.phi187
  %689 = fadd reassoc ninf nsz <8 x float> %677, %vec.phi188
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %690 = icmp eq i64 %lsr.iv.next, 0
  br i1 %690, label %middle.block174, label %vector.body183, !llvm.loop !11

middle.block174:                                  ; preds = %vector.body183
  %bin.rdx290 = fadd reassoc ninf nsz <8 x float> %687, %686
  %bin.rdx291 = fadd reassoc ninf nsz <8 x float> %688, %bin.rdx290
  %bin.rdx292 = fadd reassoc ninf nsz <8 x float> %689, %bin.rdx291
  %691 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx292)
  %bin.rdx293 = fadd reassoc ninf nsz <8 x float> %683, %682
  %bin.rdx294 = fadd reassoc ninf nsz <8 x float> %684, %bin.rdx293
  %bin.rdx295 = fadd reassoc ninf nsz <8 x float> %685, %bin.rdx294
  %692 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx295)
  br i1 %cmp.n296, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check303

vec.epilog.iter.check303:                         ; preds = %middle.block174
  br i1 %min.epilog.iters.check305, label %for_loop_body20.us.preheader, label %vec.epilog.ph302

vec.epilog.ph302:                                 ; preds = %vec.epilog.iter.check303, %vector.main.loop.iter.check179
  %bc.resume.val297 = phi i64 [ %n.vec182, %vec.epilog.iter.check303 ], [ 0, %vector.main.loop.iter.check179 ]
  %bc.merge.rdx298 = phi float [ %691, %vec.epilog.iter.check303 ], [ %.06197.us, %vector.main.loop.iter.check179 ]
  %bc.merge.rdx299 = phi float [ %692, %vec.epilog.iter.check303 ], [ %.06396.us, %vector.main.loop.iter.check179 ]
  %693 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx298, i64 0
  %694 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx299, i64 0
  %695 = trunc nuw nsw i64 %bc.resume.val297 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %695, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert318 = insertelement <8 x i32> poison, i32 %216, i64 0
  %broadcast.splat319 = shufflevector <8 x i32> %broadcast.splatinsert318, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert321 = insertelement <8 x i32> poison, i32 %217, i64 0
  %broadcast.splat322 = shufflevector <8 x i32> %broadcast.splatinsert321, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert324 = insertelement <8 x i32> poison, i32 %218, i64 0
  %broadcast.splat325 = shufflevector <8 x i32> %broadcast.splatinsert324, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert327 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat328 = shufflevector <8 x i32> %broadcast.splatinsert327, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert330 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat331 = shufflevector <8 x i32> %broadcast.splatinsert330, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert333 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat334 = shufflevector <8 x i32> %broadcast.splatinsert333, <8 x i32> poison, <8 x i32> zeroinitializer
  %696 = add i64 %212, %bc.resume.val297
  br label %vec.epilog.vector.body310

vec.epilog.vector.body310:                        ; preds = %vec.epilog.vector.body310, %vec.epilog.ph302
  %lsr.iv441 = phi i64 [ %lsr.iv.next442, %vec.epilog.vector.body310 ], [ %696, %vec.epilog.ph302 ]
  %vec.phi312 = phi <8 x float> [ %693, %vec.epilog.ph302 ], [ %808, %vec.epilog.vector.body310 ]
  %vec.phi313 = phi <8 x float> [ %694, %vec.epilog.ph302 ], [ %807, %vec.epilog.vector.body310 ]
  %vec.ind314 = phi <8 x i32> [ %induction, %vec.epilog.ph302 ], [ %vec.ind.next315, %vec.epilog.vector.body310 ]
  %697 = shl <8 x i32> %vec.ind314, splat (i32 1)
  %698 = add <8 x i32> %broadcast.splat194, %697
  %699 = add <8 x i32> %broadcast.splat319, %698
  %700 = sext <8 x i32> %699 to <8 x i64>
  %701 = getelementptr float, ptr %178, <8 x i64> %700
  %wide.masked.gather320 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %701, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %702 = add <8 x i32> %698, %broadcast.splat322
  %703 = sext <8 x i32> %702 to <8 x i64>
  %704 = getelementptr float, ptr %106, <8 x i64> %703
  %wide.masked.gather323 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %704, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %705 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather320, %wide.masked.gather323
  %706 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %705)
  %707 = add <8 x i32> %broadcast.splat325, %698
  %708 = sext <8 x i32> %707 to <8 x i64>
  %709 = getelementptr float, ptr %180, <8 x i64> %708
  %wide.masked.gather326 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %709, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %710 = add <8 x i32> %broadcast.splat328, %698
  %711 = sext <8 x i32> %710 to <8 x i64>
  %712 = getelementptr float, ptr %182, <8 x i64> %711
  %wide.masked.gather329 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %712, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %713 = add <8 x i32> %broadcast.splat331, %698
  %714 = sext <8 x i32> %713 to <8 x i64>
  %715 = getelementptr float, ptr %184, <8 x i64> %714
  %wide.masked.gather332 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %715, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %716 = add <8 x i32> %broadcast.splat334, %698
  %717 = sext <8 x i32> %716 to <8 x i64>
  %718 = getelementptr float, ptr %186, <8 x i64> %717
  %wide.masked.gather335 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %718, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %719 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather326, %wide.masked.gather326
  %720 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather329, %wide.masked.gather329
  %721 = fadd reassoc ninf nsz <8 x float> %720, %719
  %722 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather332, %wide.masked.gather332
  %723 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather335, %wide.masked.gather335
  %724 = fadd reassoc ninf nsz <8 x float> %723, %722
  %725 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %721, <8 x float> %724)
  %726 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather323, splat (float -2.000000e+00)
  %727 = fadd reassoc ninf nsz <8 x float> %726, splat (float 3.000000e+00)
  %728 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %727, <8 x float> splat (float 3.000000e+00))
  %729 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %728, <8 x float> splat (float 1.000000e+00))
  %730 = fmul reassoc ninf nsz <8 x float> %729, %broadcast.splat231
  %731 = fcmp reassoc ninf nsz olt <8 x float> %725, splat (float 1.500000e+02)
  %732 = xor <8 x i1> %731, splat (i1 true)
  %733 = select <8 x i1> %broadcast.splat, <8 x i1> %732, <8 x i1> zeroinitializer
  %734 = fcmp reassoc ninf nsz olt <8 x float> %706, %730
  %735 = xor <8 x i1> %734, splat (i1 true)
  %736 = select <8 x i1> %733, <8 x i1> %735, <8 x i1> zeroinitializer
  %737 = fmul reassoc ninf nsz <8 x float> %730, splat (float 4.000000e+00)
  %738 = fdiv reassoc ninf nsz <8 x float> %706, %737
  %739 = fcmp reassoc ninf nsz ogt <8 x float> %738, splat (float 1.000000e+00)
  %740 = select <8 x i1> %739, <8 x float> splat (float 1.000000e+00), <8 x float> %738
  %741 = fmul reassoc ninf nsz <8 x float> %740, splat (float 0x3FD99999A0000000)
  %742 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %741
  %743 = select <8 x i1> %733, <8 x i1> %734, <8 x i1> zeroinitializer
  %744 = fmul reassoc ninf nsz <8 x float> %706, splat (float 0x3FC3333340000000)
  %745 = fdiv reassoc ninf nsz <8 x float> %744, %730
  %746 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %745
  %747 = select <8 x i1> %broadcast.splat, <8 x i1> %731, <8 x i1> zeroinitializer
  %748 = fmul reassoc ninf nsz <8 x float> %730, splat (float 1.500000e+00)
  %749 = fcmp reassoc ninf nsz uge <8 x float> %706, %748
  %750 = select <8 x i1> %747, <8 x i1> %749, <8 x i1> zeroinitializer
  %751 = fsub reassoc ninf nsz <8 x float> %706, %748
  %752 = fdiv reassoc ninf nsz <8 x float> %751, %748
  %753 = fcmp reassoc ninf nsz ogt <8 x float> %752, splat (float 1.000000e+00)
  %754 = select <8 x i1> %753, <8 x float> splat (float 1.000000e+00), <8 x float> %752
  %755 = fmul reassoc ninf nsz <8 x float> %754, splat (float 0x3FC99999A0000000)
  %756 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %755
  %757 = fmul reassoc ninf nsz <8 x float> %706, splat (float 0x3FEE666660000000)
  %758 = fdiv reassoc ninf nsz <8 x float> %757, %748
  %759 = fadd reassoc ninf nsz <8 x float> %758, splat (float 0x3FA99999A0000000)
  %760 = or <8 x i1> %743, %209
  %761 = or <8 x i1> %760, %747
  %762 = or <8 x i1> %761, %736
  %predphi338 = select <8 x i1> %750, <8 x float> %756, <8 x float> %759
  %predphi339 = select <8 x i1> %743, <8 x float> %746, <8 x float> %predphi338
  %predphi340 = select <8 x i1> %736, <8 x float> %742, <8 x float> %predphi339
  %predphi341 = select <8 x i1> %broadcast.splat, <8 x float> %predphi340, <8 x float> splat (float 1.000000e+00)
  %763 = fcmp reassoc ninf nsz ogt <8 x float> %725, splat (float 0x3EB0C6F7A0000000)
  %764 = select <8 x i1> %762, <8 x i1> %763, <8 x i1> zeroinitializer
  %765 = fcmp reassoc ninf nsz ogt <8 x float> %721, splat (float 0x3EB0C6F7A0000000)
  %766 = fcmp reassoc ninf nsz ogt <8 x float> %724, splat (float 0x3EB0C6F7A0000000)
  %767 = select <8 x i1> %765, <8 x i1> %766, <8 x i1> zeroinitializer
  %768 = select <8 x i1> %764, <8 x i1> %767, <8 x i1> zeroinitializer
  %769 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather332, %wide.masked.gather326
  %770 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather335, %wide.masked.gather329
  %771 = fadd reassoc ninf nsz <8 x float> %770, %769
  %772 = fmul reassoc ninf nsz <8 x float> %724, %721
  %773 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %772)
  %774 = fdiv reassoc ninf nsz <8 x float> %771, %773
  %775 = fcmp reassoc ninf nsz ule <8 x float> %725, splat (float 1.500000e+02)
  %776 = fcmp reassoc ninf nsz uge <8 x float> %774, splat (float 0x3FC99999A0000000)
  %.not376 = select <8 x i1> %775, <8 x i1> splat (i1 true), <8 x i1> %776
  %777 = select <8 x i1> %768, <8 x i1> %.not376, <8 x i1> zeroinitializer
  %778 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %774, <8 x float> zeroinitializer)
  %779 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %725)
  %780 = fmul reassoc ninf nsz <8 x float> %779, %broadcast.splat248
  %781 = fmul reassoc ninf nsz <8 x float> %780, %778
  %.fr377 = freeze <8 x float> %781
  %782 = fcmp reassoc nsz ogt <8 x float> %.fr377, splat (float 3.000000e+00)
  %783 = xor <8 x i1> %782, splat (i1 true)
  %784 = and <8 x i1> %777, %783
  %785 = fcmp reassoc nsz olt <8 x float> %.fr377, splat (float -3.000000e+00)
  %786 = xor <8 x i1> %785, splat (i1 true)
  %787 = and <8 x i1> %784, %786
  %788 = fmul reassoc ninf nsz <8 x float> %.fr377, %.fr377
  %789 = fadd reassoc ninf nsz <8 x float> %788, splat (float 2.700000e+01)
  %790 = fmul reassoc ninf nsz <8 x float> %789, %.fr377
  %791 = fmul reassoc ninf nsz <8 x float> %788, splat (float 9.000000e+00)
  %792 = fadd reassoc ninf nsz <8 x float> %791, splat (float 2.700000e+01)
  %793 = fdiv reassoc ninf nsz <8 x float> %790, %792
  %794 = fadd reassoc ninf nsz <8 x float> %793, splat (float 1.000000e+00)
  %795 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %774
  %796 = fmul reassoc ninf nsz <8 x float> %795, %706
  %797 = and <8 x i1> %784, %785
  %798 = and <8 x i1> %777, %782
  %799 = xor <8 x i1> %767, splat (i1 true)
  %800 = select <8 x i1> %764, <8 x i1> %799, <8 x i1> zeroinitializer
  %801 = xor <8 x i1> %763, splat (i1 true)
  %802 = select <8 x i1> %762, <8 x i1> %801, <8 x i1> zeroinitializer
  %803 = select <8 x i1> %777, <8 x i1> splat (i1 true), <8 x i1> %802
  %804 = select <8 x i1> %803, <8 x i1> splat (i1 true), <8 x i1> %800
  %predphi348 = select <8 x i1> %804, <8 x float> %706, <8 x float> %796
  %predphi351 = select <8 x i1> %798, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi352 = select <8 x i1> %787, <8 x float> %794, <8 x float> %predphi351
  %predphi353 = select <8 x i1> %797, <8 x float> zeroinitializer, <8 x float> %predphi352
  %805 = fmul reassoc ninf nsz <8 x float> %predphi353, %predphi341
  %806 = fmul reassoc ninf nsz <8 x float> %805, %predphi348
  %807 = fadd reassoc ninf nsz <8 x float> %806, %vec.phi313
  %808 = fadd reassoc ninf nsz <8 x float> %805, %vec.phi312
  %vec.ind.next315 = add <8 x i32> %vec.ind314, splat (i32 8)
  %lsr.iv.next442 = add i64 %lsr.iv441, 8
  %809 = icmp eq i64 %lsr.iv.next442, 0
  br i1 %809, label %vec.epilog.middle.block300, label %vec.epilog.vector.body310, !llvm.loop !14

vec.epilog.middle.block300:                       ; preds = %vec.epilog.vector.body310
  %810 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %808)
  %811 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %807)
  br i1 %cmp.n355, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block300, %vec.epilog.iter.check303, %vector.scevcheck158, %iter.check177
  %indvars.iv.ph = phi i64 [ %n.vec182, %vec.epilog.iter.check303 ], [ 0, %iter.check177 ], [ 0, %vector.scevcheck158 ], [ %n.vec307, %vec.epilog.middle.block300 ]
  %.16293.us.ph = phi float [ %691, %vec.epilog.iter.check303 ], [ %.06197.us, %iter.check177 ], [ %.06197.us, %vector.scevcheck158 ], [ %810, %vec.epilog.middle.block300 ]
  %.16492.us.ph = phi float [ %692, %vec.epilog.iter.check303 ], [ %.06396.us, %iter.check177 ], [ %.06396.us, %vector.scevcheck158 ], [ %811, %vec.epilog.middle.block300 ]
  %812 = trunc i64 %indvars.iv.ph to i32
  %813 = shl nuw i32 %812, 1
  %814 = add i64 %213, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv467 = phi i64 [ %814, %for_loop_body20.us.preheader ], [ %lsr.iv.next468, %after_if50.us ]
  %lsr.iv465 = phi i32 [ %lsr.iv463, %for_loop_body20.us.preheader ], [ %lsr.iv.next466, %after_if50.us ]
  %lsr.iv461 = phi i32 [ %lsr.iv459, %for_loop_body20.us.preheader ], [ %lsr.iv.next462, %after_if50.us ]
  %lsr.iv457 = phi i32 [ %lsr.iv455, %for_loop_body20.us.preheader ], [ %lsr.iv.next458, %after_if50.us ]
  %lsr.iv453 = phi i32 [ %lsr.iv451, %for_loop_body20.us.preheader ], [ %lsr.iv.next454, %after_if50.us ]
  %lsr.iv449 = phi i32 [ %lsr.iv447, %for_loop_body20.us.preheader ], [ %lsr.iv.next450, %after_if50.us ]
  %lsr.iv445 = phi i32 [ %lsr.iv443, %for_loop_body20.us.preheader ], [ %lsr.iv.next446, %after_if50.us ]
  %.16293.us = phi float [ %901, %after_if50.us ], [ %.16293.us.ph, %for_loop_body20.us.preheader ]
  %.16492.us = phi float [ %900, %after_if50.us ], [ %.16492.us.ph, %for_loop_body20.us.preheader ]
  %815 = add i32 %813, %lsr.iv465
  %816 = sext i32 %815 to i64
  %817 = getelementptr float, ptr %178, i64 %816
  %818 = load float, ptr %817, align 4
  %819 = add i32 %813, %lsr.iv461
  %820 = sext i32 %819 to i64
  %821 = getelementptr float, ptr %106, i64 %820
  %822 = load float, ptr %821, align 4
  %823 = fsub reassoc ninf nsz float %818, %822
  %824 = tail call noundef float @llvm.fabs.f32(float %823)
  %825 = add i32 %813, %lsr.iv457
  %826 = sext i32 %825 to i64
  %827 = getelementptr float, ptr %180, i64 %826
  %828 = load float, ptr %827, align 4
  %829 = add i32 %813, %lsr.iv453
  %830 = sext i32 %829 to i64
  %831 = getelementptr float, ptr %182, i64 %830
  %832 = load float, ptr %831, align 4
  %833 = add i32 %813, %lsr.iv449
  %834 = sext i32 %833 to i64
  %835 = getelementptr float, ptr %184, i64 %834
  %836 = load float, ptr %835, align 4
  %837 = add i32 %813, %lsr.iv445
  %838 = sext i32 %837 to i64
  %839 = getelementptr float, ptr %186, i64 %838
  %840 = load float, ptr %839, align 4
  %841 = fmul reassoc ninf nsz float %828, %828
  %842 = fmul reassoc ninf nsz float %832, %832
  %843 = fadd reassoc ninf nsz float %842, %841
  %844 = fmul reassoc ninf nsz float %836, %836
  %845 = fmul reassoc ninf nsz float %840, %840
  %846 = fadd reassoc ninf nsz float %845, %844
  %847 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %843, float %846)
  %factor.us = fmul reassoc ninf nsz float %822, -2.000000e+00
  %848 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %849 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %848, float 3.000000e+00)
  %850 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %849, float 1.000000e+00)
  %851 = fmul reassoc ninf nsz float %850, %162
  br i1 %163, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %852 = fcmp reassoc ninf nsz olt float %847, 1.500000e+02
  br i1 %852, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %853 = fcmp reassoc ninf nsz olt float %824, %851
  br i1 %853, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %854 = fmul reassoc ninf nsz float %851, 4.000000e+00
  %855 = fdiv reassoc ninf nsz float %824, %854
  %856 = fcmp reassoc ninf nsz ogt float %855, 1.000000e+00
  %spec.store.select1.us = select i1 %856, float 1.000000e+00, float %855
  %857 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %858 = fsub reassoc ninf nsz float 0x3FE6666680000000, %857
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %859 = fmul reassoc ninf nsz float %824, 0x3FC3333340000000
  %860 = fdiv reassoc ninf nsz float %859, %851
  %861 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %860
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %862 = fmul reassoc ninf nsz float %851, 1.500000e+00
  %863 = fcmp reassoc ninf nsz olt float %824, %862
  br i1 %863, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %864 = fsub reassoc ninf nsz float %824, %862
  %865 = fdiv reassoc ninf nsz float %864, %862
  %866 = fcmp reassoc ninf nsz ogt float %865, 1.000000e+00
  %spec.store.select.us = select i1 %866, float 1.000000e+00, float %865
  %867 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %868 = fsub reassoc ninf nsz float 1.000000e+00, %867
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %869 = fmul reassoc ninf nsz float %824, 0x3FEE666660000000
  %870 = fdiv reassoc ninf nsz float %869, %862
  %871 = fadd reassoc ninf nsz float %870, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.057.us = phi float [ %871, %true_block30.us ], [ %868, %false_block31.us ], [ %861, %true_block36.us ], [ %858, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %872 = fcmp reassoc ninf nsz ogt float %847, 0x3EB0C6F7A0000000
  br i1 %872, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %873 = fcmp reassoc ninf nsz ogt float %843, 0x3EB0C6F7A0000000
  %874 = fcmp reassoc ninf nsz ogt float %846, 0x3EB0C6F7A0000000
  %.052.us = select i1 %873, i1 %874, i1 false
  br i1 %.052.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %875 = fmul reassoc ninf nsz float %836, %828
  %876 = fmul reassoc ninf nsz float %840, %832
  %877 = fadd reassoc ninf nsz float %876, %875
  %878 = fmul reassoc ninf nsz float %846, %843
  %879 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %878)
  %880 = fdiv reassoc ninf nsz float %877, %879
  %881 = fcmp reassoc ninf nsz ogt float %847, 1.500000e+02
  %882 = fcmp reassoc ninf nsz olt float %880, 0x3FC99999A0000000
  %.051.us = select i1 %881, i1 %882, i1 false
  br i1 %.051.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %883 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %880, float 0.000000e+00)
  %884 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %847)
  %885 = fmul reassoc ninf nsz float %884, %160
  %886 = fmul reassoc ninf nsz float %885, %883
  %887 = fcmp reassoc ninf nsz ogt float %886, 3.000000e+00
  br i1 %887, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %888 = fcmp reassoc ninf nsz olt float %886, -3.000000e+00
  br i1 %888, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %889 = fmul reassoc ninf nsz float %886, %886
  %890 = fadd reassoc ninf nsz float %889, 2.700000e+01
  %891 = fmul reassoc ninf nsz float %890, %886
  %892 = fmul reassoc ninf nsz float %889, 9.000000e+00
  %893 = fadd reassoc ninf nsz float %892, 2.700000e+01
  %894 = fdiv reassoc ninf nsz float %891, %893
  %895 = fadd reassoc ninf nsz float %894, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %896 = fsub reassoc ninf nsz float 1.500000e+00, %880
  %897 = fmul reassoc ninf nsz float %896, %824
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.058.us = phi float [ %897, %true_block54.us ], [ %824, %true_block42.us ], [ %824, %after_if26.us ], [ %824, %false_block55.us ], [ %824, %false_block61.us ], [ %824, %false_block58.us ]
  %.054.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %895, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %898 = fmul reassoc ninf nsz float %.054.us, %.057.us
  %899 = fmul reassoc ninf nsz float %898, %.058.us
  %900 = fadd reassoc ninf nsz float %899, %.16492.us
  %901 = fadd reassoc ninf nsz float %898, %.16293.us
  %lsr.iv.next446 = add i32 %lsr.iv445, 2
  %lsr.iv.next450 = add i32 %lsr.iv449, 2
  %lsr.iv.next454 = add i32 %lsr.iv453, 2
  %lsr.iv.next458 = add i32 %lsr.iv457, 2
  %lsr.iv.next462 = add i32 %lsr.iv461, 2
  %lsr.iv.next466 = add i32 %lsr.iv465, 2
  %lsr.iv.next468 = add i64 %lsr.iv467, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next468, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block300, %middle.block174
  %.lcssa134 = phi float [ %692, %middle.block174 ], [ %811, %vec.epilog.middle.block300 ], [ %900, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %691, %middle.block174 ], [ %810, %vec.epilog.middle.block300 ], [ %901, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %902 = add nuw nsw i32 %.06098.us, 1
  %lsr.iv.next444 = add i32 %lsr.iv443, %206
  %lsr.iv.next448 = add i32 %lsr.iv447, %203
  %lsr.iv.next452 = add i32 %lsr.iv451, %200
  %lsr.iv.next456 = add i32 %lsr.iv455, %197
  %lsr.iv.next460 = add i32 %lsr.iv459, %194
  %lsr.iv.next464 = add i32 %lsr.iv463, %191
  %exitcond119.not = icmp eq i32 %902, %164
  br i1 %exitcond119.not, label %after_for18, label %iter.check177

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %903 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %903, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %true_block13
  %904 = getelementptr i8, ptr %75, i64 4
  %905 = getelementptr i8, ptr %75, i64 8
  %906 = load ptr, ptr %905, align 8
  %907 = load i32, ptr %904, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %66, i32 1)
  %smax125 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  %wide.trip.count123 = zext i32 %smax to i64
  %908 = add nsw i64 %wide.trip.count123, -1
  %909 = mul i32 %54, %907
  %910 = add i32 %58, %909
  %min.iters.check = icmp slt i32 %66, 4
  %911 = trunc nsw i64 %908 to i32
  %invariant.op437 = add i32 %910, %911
  %invariant.op439 = add i32 %115, %911
  %912 = icmp ugt i64 %908, 4294967295
  %min.iters.check136 = icmp slt i32 %66, 32
  %n.vec = and i64 %wide.trip.count123, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count123
  %n.vec.remaining = and i64 %wide.trip.count123, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec150 = and i64 %wide.trip.count123, 2147483644
  %cmp.n156 = icmp eq i64 %n.vec150, %wide.trip.count123
  %xtraiter = and i64 %wide.trip.count123, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %913 = lshr i64 %wide.trip.count123, 2
  %914 = mul nsw i64 %913, -4
  %915 = zext i32 %115 to i64
  %916 = zext i32 %108 to i64
  %917 = zext i32 %910 to i64
  %918 = zext i32 %907 to i64
  %919 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %lsr.iv487 = phi i64 [ %lsr.iv.next488, %for_loop_test73.after_for72_crit_edge.us ], [ %917, %for_loop_body66.lr.ph.split.us ]
  %lsr.iv485 = phi i64 [ %lsr.iv.next486, %for_loop_test73.after_for72_crit_edge.us ], [ %915, %for_loop_body66.lr.ph.split.us ]
  %.047107.us = phi i32 [ 0, %for_loop_body66.lr.ph.split.us ], [ %1024, %for_loop_test73.after_for72_crit_edge.us ]
  %.048106.us = phi float [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ], [ %.lcssa135, %for_loop_test73.after_for72_crit_edge.us ]
  %lsr502 = trunc i64 %lsr.iv487 to i32
  %lsr500 = trunc i64 %lsr.iv485 to i32
  br i1 %min.iters.check, label %for_loop_body70.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %920 = mul i32 %108, %.047107.us
  %921 = add i32 %115, %920
  %922 = mul i32 %907, %.047107.us
  %923 = add i32 %910, %922
  %.reass438 = add i32 %922, %invariant.op437
  %924 = icmp slt i32 %.reass438, %923
  %.reass440 = add i32 %920, %invariant.op439
  %925 = icmp slt i32 %.reass440, %921
  %926 = or i1 %925, %912
  %927 = or i1 %924, %926
  br i1 %927, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check136, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %928 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.048106.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv477 = phi i32 [ %lsr.iv.next478, %vector.body ], [ %lsr500, %vector.ph ]
  %lsr.iv473 = phi i32 [ %lsr.iv.next474, %vector.body ], [ %lsr502, %vector.ph ]
  %lsr.iv469 = phi i64 [ %lsr.iv.next470, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %928, %vector.ph ], [ %947, %vector.body ]
  %vec.phi137 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %948, %vector.body ]
  %vec.phi138 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %949, %vector.body ]
  %vec.phi139 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %950, %vector.body ]
  %929 = sext i32 %lsr.iv473 to i64
  %930 = getelementptr float, ptr %906, i64 %929
  %931 = getelementptr i8, ptr %930, i64 32
  %932 = getelementptr i8, ptr %930, i64 64
  %933 = getelementptr i8, ptr %930, i64 96
  %wide.load = load <8 x float>, ptr %930, align 4
  %wide.load140 = load <8 x float>, ptr %931, align 4
  %wide.load141 = load <8 x float>, ptr %932, align 4
  %wide.load142 = load <8 x float>, ptr %933, align 4
  %934 = sext i32 %lsr.iv477 to i64
  %935 = getelementptr float, ptr %106, i64 %934
  %936 = getelementptr i8, ptr %935, i64 32
  %937 = getelementptr i8, ptr %935, i64 64
  %938 = getelementptr i8, ptr %935, i64 96
  %wide.load143 = load <8 x float>, ptr %935, align 4
  %wide.load144 = load <8 x float>, ptr %936, align 4
  %wide.load145 = load <8 x float>, ptr %937, align 4
  %wide.load146 = load <8 x float>, ptr %938, align 4
  %939 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load143
  %940 = fsub reassoc ninf nsz <8 x float> %wide.load140, %wide.load144
  %941 = fsub reassoc ninf nsz <8 x float> %wide.load141, %wide.load145
  %942 = fsub reassoc ninf nsz <8 x float> %wide.load142, %wide.load146
  %943 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %939)
  %944 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %940)
  %945 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %941)
  %946 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %942)
  %947 = fadd reassoc ninf nsz <8 x float> %943, %vec.phi
  %948 = fadd reassoc ninf nsz <8 x float> %944, %vec.phi137
  %949 = fadd reassoc ninf nsz <8 x float> %945, %vec.phi138
  %950 = fadd reassoc ninf nsz <8 x float> %946, %vec.phi139
  %lsr.iv.next470 = add nsw i64 %lsr.iv469, -32
  %lsr.iv.next474 = add i32 %lsr.iv473, 32
  %lsr.iv.next478 = add i32 %lsr.iv477, 32
  %951 = icmp eq i64 %lsr.iv.next470, 0
  br i1 %951, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %948, %947
  %bin.rdx147 = fadd reassoc ninf nsz <8 x float> %949, %bin.rdx
  %bin.rdx148 = fadd reassoc ninf nsz <8 x float> %950, %bin.rdx147
  %952 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx148)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %952, %vec.epilog.iter.check ], [ %.048106.us, %vector.main.loop.iter.check ]
  %953 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %954 = add i64 %914, %vec.epilog.resume.val
  %955 = trunc i64 %vec.epilog.resume.val to i32
  %956 = add i32 %lsr502, %955
  %957 = add i32 %lsr500, %955
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv483 = phi i32 [ %lsr.iv.next484, %vec.epilog.vector.body ], [ %957, %vec.epilog.ph ]
  %lsr.iv481 = phi i32 [ %lsr.iv.next482, %vec.epilog.vector.body ], [ %956, %vec.epilog.ph ]
  %lsr.iv479 = phi i64 [ %lsr.iv.next480, %vec.epilog.vector.body ], [ %954, %vec.epilog.ph ]
  %vec.phi152 = phi <4 x float> [ %953, %vec.epilog.ph ], [ %964, %vec.epilog.vector.body ]
  %958 = sext i32 %lsr.iv481 to i64
  %959 = getelementptr float, ptr %906, i64 %958
  %wide.load153 = load <4 x float>, ptr %959, align 4
  %960 = sext i32 %lsr.iv483 to i64
  %961 = getelementptr float, ptr %106, i64 %960
  %wide.load154 = load <4 x float>, ptr %961, align 4
  %962 = fsub reassoc ninf nsz <4 x float> %wide.load153, %wide.load154
  %963 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %962)
  %964 = fadd reassoc ninf nsz <4 x float> %963, %vec.phi152
  %lsr.iv.next480 = add i64 %lsr.iv479, 4
  %lsr.iv.next482 = add i32 %lsr.iv481, 4
  %lsr.iv.next484 = add i32 %lsr.iv483, 4
  %965 = icmp eq i64 %lsr.iv.next480, 0
  br i1 %965, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %966 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %964)
  br i1 %cmp.n156, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv120.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec150, %vec.epilog.middle.block ]
  %.1102.us.ph = phi float [ %952, %vec.epilog.iter.check ], [ %.048106.us, %iter.check ], [ %.048106.us, %vector.scevcheck ], [ %966, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv490 = phi i64 [ %919, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next491, %for_loop_body70.us.prol ]
  %indvars.iv120.prol = phi i64 [ %indvars.iv.next121.prol, %for_loop_body70.us.prol ], [ %indvars.iv120.ph, %for_loop_body70.us.prol.preheader ]
  %.1102.us.prol = phi float [ %977, %for_loop_body70.us.prol ], [ %.1102.us.ph, %for_loop_body70.us.prol.preheader ]
  %967 = add i64 %lsr.iv487, %indvars.iv120.prol
  %tmp489 = trunc i64 %967 to i32
  %968 = sext i32 %tmp489 to i64
  %969 = getelementptr float, ptr %906, i64 %968
  %970 = load float, ptr %969, align 4
  %971 = add i64 %lsr.iv485, %indvars.iv120.prol
  %tmp = trunc i64 %971 to i32
  %972 = sext i32 %tmp to i64
  %973 = getelementptr float, ptr %106, i64 %972
  %974 = load float, ptr %973, align 4
  %975 = fsub reassoc ninf nsz float %970, %974
  %976 = tail call noundef float @llvm.fabs.f32(float %975)
  %977 = fadd reassoc ninf nsz float %976, %.1102.us.prol
  %indvars.iv.next121.prol = add nuw nsw i64 %indvars.iv120.prol, 1
  %lsr.iv.next491 = add nsw i64 %lsr.iv490, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next491, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa395.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %977, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv120.unr = phi i64 [ %indvars.iv120.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next121.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1102.us.unr = phi float [ %.1102.us.ph, %for_loop_body70.us.preheader ], [ %977, %for_loop_body70.us.prol.loopexit.loopexit ]
  %978 = sub nsw i64 %indvars.iv120.ph, %wide.trip.count123
  %979 = icmp ugt i64 %978, -4
  br i1 %979, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader.new

for_loop_body70.us.preheader.new:                 ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader.new
  %indvars.iv120 = phi i64 [ %indvars.iv120.unr, %for_loop_body70.us.preheader.new ], [ %indvars.iv.next121.3, %for_loop_body70.us ]
  %.1102.us = phi float [ %.1102.us.unr, %for_loop_body70.us.preheader.new ], [ %1023, %for_loop_body70.us ]
  %980 = add i64 %lsr.iv487, %indvars.iv120
  %tmp499 = trunc i64 %980 to i32
  %981 = sext i32 %tmp499 to i64
  %982 = getelementptr float, ptr %906, i64 %981
  %983 = load float, ptr %982, align 4
  %984 = add i64 %lsr.iv485, %indvars.iv120
  %tmp498 = trunc i64 %984 to i32
  %985 = sext i32 %tmp498 to i64
  %986 = getelementptr float, ptr %106, i64 %985
  %987 = load float, ptr %986, align 4
  %988 = fsub reassoc ninf nsz float %983, %987
  %989 = tail call noundef float @llvm.fabs.f32(float %988)
  %990 = fadd reassoc ninf nsz float %989, %.1102.us
  %991 = add i64 %980, 1
  %tmp497 = trunc i64 %991 to i32
  %992 = sext i32 %tmp497 to i64
  %993 = getelementptr float, ptr %906, i64 %992
  %994 = load float, ptr %993, align 4
  %995 = add i64 %984, 1
  %tmp496 = trunc i64 %995 to i32
  %996 = sext i32 %tmp496 to i64
  %997 = getelementptr float, ptr %106, i64 %996
  %998 = load float, ptr %997, align 4
  %999 = fsub reassoc ninf nsz float %994, %998
  %1000 = tail call noundef float @llvm.fabs.f32(float %999)
  %1001 = fadd reassoc ninf nsz float %1000, %990
  %1002 = add i64 %980, 2
  %tmp495 = trunc i64 %1002 to i32
  %1003 = sext i32 %tmp495 to i64
  %1004 = getelementptr float, ptr %906, i64 %1003
  %1005 = load float, ptr %1004, align 4
  %1006 = add i64 %984, 2
  %tmp494 = trunc i64 %1006 to i32
  %1007 = sext i32 %tmp494 to i64
  %1008 = getelementptr float, ptr %106, i64 %1007
  %1009 = load float, ptr %1008, align 4
  %1010 = fsub reassoc ninf nsz float %1005, %1009
  %1011 = tail call noundef float @llvm.fabs.f32(float %1010)
  %1012 = fadd reassoc ninf nsz float %1011, %1001
  %1013 = add i64 %980, 3
  %tmp493 = trunc i64 %1013 to i32
  %1014 = sext i32 %tmp493 to i64
  %1015 = getelementptr float, ptr %906, i64 %1014
  %1016 = load float, ptr %1015, align 4
  %1017 = add i64 %984, 3
  %tmp492 = trunc i64 %1017 to i32
  %1018 = sext i32 %tmp492 to i64
  %1019 = getelementptr float, ptr %106, i64 %1018
  %1020 = load float, ptr %1019, align 4
  %1021 = fsub reassoc ninf nsz float %1016, %1020
  %1022 = tail call noundef float @llvm.fabs.f32(float %1021)
  %1023 = fadd reassoc ninf nsz float %1022, %1012
  %indvars.iv.next121.3 = add nuw nsw i64 %indvars.iv120, 4
  %exitcond124.not.3 = icmp eq i64 %wide.trip.count123, %indvars.iv.next121.3
  br i1 %exitcond124.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa135 = phi float [ %952, %middle.block ], [ %966, %vec.epilog.middle.block ], [ %.lcssa395.unr, %for_loop_body70.us.prol.loopexit ], [ %1023, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %1024 = add nuw nsw i32 %.047107.us, 1
  %lsr.iv.next488 = add i64 %lsr.iv487, %918
  %lsr.iv.next486 = add i64 %lsr.iv485, %916
  %exitcond126.not = icmp eq i32 %1024, %smax125
  br i1 %exitcond126.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %1025 = fdiv reassoc ninf nsz float %.lcssa134, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.049 = phi float [ %1040, %after_for68 ], [ %1025, %false_block64 ]
  %1026 = getelementptr i8, ptr %75, i64 208
  %1027 = load float, ptr %1026, align 4
  %1028 = getelementptr i8, ptr %75, i64 212
  %1029 = load float, ptr %1028, align 4
  %1030 = fmul reassoc ninf nsz float %1029, %158
  %1031 = fsub reassoc ninf nsz float %.049, %1030
  %1032 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1031, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %1027
  %1033 = fmul reassoc ninf nsz float %1032, %neg
  %1034 = tail call noundef float @expf(float noundef %1033) #9
  %1035 = fmul reassoc ninf nsz float %.066, %.067
  %1036 = fmul reassoc ninf nsz float %1035, %1034
  %1037 = fcmp reassoc ninf nsz ult float %1036, 0x3EB0C6F7A0000000
  br i1 %1037, label %after_if3, label %true_block74

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %1038 = mul i32 %66, %62
  %1039 = sitofp i32 %1038 to float
  %1040 = fdiv reassoc ninf nsz float %.lcssa135, %1039
  br label %after_if65

true_block74:                                     ; preds = %after_if65
  %1041 = mul i32 %66, %62
  %1042 = icmp sgt i32 %1041, 0
  br i1 %1042, label %for_loop_body77.lr.ph, label %after_if3

for_loop_body77.lr.ph:                            ; preds = %true_block74
  %1043 = load ptr, ptr %0, align 8
  %1044 = getelementptr i8, ptr %1043, i64 136
  %1045 = getelementptr i8, ptr %1043, i64 132
  br label %for_loop_body77

for_loop_body77:                                  ; preds = %after_if86, %for_loop_body77.lr.ph
  %.045111 = phi i32 [ 0, %for_loop_body77.lr.ph ], [ %1084, %after_if86 ]
  %1046 = udiv i32 %.045111, %66
  %.recomposed = urem i32 %.045111, %66
  %1047 = load ptr, ptr %3, align 8
  %1048 = getelementptr inbounds nuw i8, ptr %1047, i64 32872
  %1049 = load ptr, ptr %1048, align 8
  %1050 = getelementptr inbounds nuw i8, ptr %1049, i64 24
  %1051 = load i1, ptr %1050, align 1
  br i1 %1051, label %true_block81, label %after_if83

true_block81:                                     ; preds = %for_loop_body77
  %1052 = uitofp nneg i32 %1046 to float
  %1053 = fmul reassoc ninf nsz float %1052, 0x401921FB60000000
  %1054 = getelementptr inbounds nuw i8, ptr %1049, i64 28
  %1055 = load float, ptr %1054, align 4
  %1056 = fmul reassoc ninf nsz float %1053, %1055
  %1057 = tail call noundef float @cosf(float noundef %1056) #9
  %1058 = fmul reassoc ninf nsz float %1057, 5.000000e-01
  %1059 = fsub reassoc ninf nsz float 5.000000e-01, %1058
  %.pre = load ptr, ptr %3, align 8
  %.phi.trans.insert = getelementptr inbounds nuw i8, ptr %.pre, i64 32872
  %.pre129 = load ptr, ptr %.phi.trans.insert, align 8
  br label %after_if83

after_if83:                                       ; preds = %true_block81, %for_loop_body77
  %1060 = phi ptr [ %.pre129, %true_block81 ], [ %1049, %for_loop_body77 ]
  %.044 = phi float [ %1059, %true_block81 ], [ 1.000000e+00, %for_loop_body77 ]
  %1061 = getelementptr inbounds nuw i8, ptr %1060, i64 32
  %1062 = load i1, ptr %1061, align 1
  br i1 %1062, label %true_block84, label %after_if86

true_block84:                                     ; preds = %after_if83
  %1063 = uitofp nneg i32 %.recomposed to float
  %1064 = fmul reassoc ninf nsz float %1063, 0x401921FB60000000
  %1065 = getelementptr inbounds nuw i8, ptr %1060, i64 36
  %1066 = load float, ptr %1065, align 4
  %1067 = fmul reassoc ninf nsz float %1064, %1066
  %1068 = tail call noundef float @cosf(float noundef %1067) #9
  %1069 = fmul reassoc ninf nsz float %1068, 5.000000e-01
  %1070 = fsub reassoc ninf nsz float 5.000000e-01, %1069
  br label %after_if86

after_if86:                                       ; preds = %true_block84, %after_if83
  %.0 = phi float [ %1070, %true_block84 ], [ 1.000000e+00, %after_if83 ]
  %1071 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.044, float 0x3F1A36E2E0000000)
  %1072 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0, float 0x3F1A36E2E0000000)
  %1073 = fmul reassoc ninf nsz float %1071, %1036
  %1074 = fmul reassoc ninf nsz float %1073, %1072
  %1075 = add i32 %1046, %54
  %1076 = add i32 %.recomposed, %58
  %1077 = load ptr, ptr %1044, align 8
  %1078 = load i32, ptr %1045, align 4
  %1079 = mul i32 %1078, %1075
  %1080 = add i32 %1076, %1079
  %1081 = sext i32 %1080 to i64
  %1082 = getelementptr float, ptr %1077, i64 %1081
  %1083 = atomicrmw fadd ptr %1082, float %1074 seq_cst, align 4
  %1084 = add nuw nsw i32 %.045111, 1
  %exitcond127.not = icmp eq i32 %1041, %1084
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
  %4 = alloca %struct.RuntimeContext.10, align 8
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
