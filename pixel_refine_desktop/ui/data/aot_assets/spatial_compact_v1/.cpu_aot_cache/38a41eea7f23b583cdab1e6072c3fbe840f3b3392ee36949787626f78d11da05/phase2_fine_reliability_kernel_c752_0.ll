; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.66 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase2_fine_reliability_kernel_c752_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 200
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
  %20 = getelementptr i8, ptr %19, i64 204
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
  %39 = getelementptr i8, ptr %38, i64 208
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
  %58 = getelementptr i8, ptr %57, i64 168
  %59 = load i32, ptr %58, align 4
  %60 = getelementptr i8, ptr %57, i64 184
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
  %78 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %69, i32 range(i32 -1073741825, 1073741824) 0)
  %79 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %77, i32 range(i32 -1073741825, 1073741824) 0)
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

define void @phase2_fine_reliability_kernel_c752_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 212
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 216
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 176
  %26 = getelementptr i8, ptr %19, i64 192
  %27 = add i32 %23, -1
  %28 = add i32 %21, -1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.059126 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %79, %after_if3 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.059126, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.059126
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %35, %.059126
  %39 = and i1 %37, %38
  %.neg87 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg87
  %41 = mul i32 %40, %33
  %42 = sub i32 %.059126, %41
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
  %76 = getelementptr i8, ptr %75, i64 236
  %77 = load i32, ptr %76, align 4
  %78 = icmp eq i32 %77, 1
  br i1 %78, label %true_block4, label %after_if6

after_if3.loopexit:                               ; preds = %after_for86
  br label %after_if3

after_if3:                                        ; preds = %after_if65, %after_if9, %after_if3.loopexit, %for_loop_body
  %79 = add nsw i32 %.059126, 1
  %exitcond145.not = icmp eq i32 %79, %18
  br i1 %exitcond145.not, label %after_for.loopexit, label %for_loop_body

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
  %.071 = phi float [ %88, %true_block4 ], [ 1.000000e+00, %true_block1 ]
  %89 = getelementptr i8, ptr %75, i64 232
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
  %.070 = phi float [ %100, %true_block7 ], [ 1.000000e+00, %after_if6 ]
  %101 = getelementptr i8, ptr %75, i64 240
  %102 = load float, ptr %101, align 4
  %103 = fcmp reassoc ninf nsz oge float %.071, %102
  %104 = fcmp reassoc ninf nsz oge float %.070, %102
  %.069 = select i1 %103, i1 %104, i1 false
  br i1 %.069, label %true_block13, label %after_if3

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
  %157 = getelementptr i8, ptr %75, i64 220
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %156, 6.075000e+02
  %160 = fadd reassoc ninf nsz float %159, 2.025000e+02
  %161 = fmul reassoc ninf nsz float %158, 0x3FC99999A0000000
  %162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0x3F747AE140000000)
  %163 = fcmp reassoc ninf nsz ogt float %158, 0x3EB0C6F7A0000000
  %164 = lshr i32 %125, 1
  %165 = add i32 %54, 1
  %166 = lshr i32 %119, 1
  %167 = add i32 %58, 1
  %.not = icmp samesign ult i32 %62, 3
  br i1 %.not, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph

for_loop_body16.lr.ph:                            ; preds = %true_block13
  %168 = fadd reassoc ninf nsz float %156, 1.000000e+00
  %169 = fmul reassoc ninf nsz float %158, %158
  %170 = fmul reassoc ninf nsz float %169, 4.000000e+00
  %171 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %170, float 0x3F62E62140000000)
  %.not127 = icmp samesign ult i32 %66, 3
  %172 = fmul reassoc ninf nsz float %168, %171
  br i1 %.not127, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %for_loop_body16.lr.ph
  %173 = getelementptr i8, ptr %75, i64 4
  %174 = getelementptr i8, ptr %75, i64 8
  %175 = load ptr, ptr %174, align 8
  %176 = load i32, ptr %173, align 4
  %wide.trip.count = zext i32 %166 to i64
  %177 = add nsw i64 %wide.trip.count, -1
  %178 = mul i32 %176, %165
  %179 = add i32 %167, %178
  %180 = shl i32 %176, 1
  %181 = mul i32 %108, %165
  %182 = add i32 %167, %181
  %183 = shl i32 %108, 1
  %184 = add i32 %58, 2
  %185 = add i32 %184, %178
  %186 = add i32 %58, %178
  %187 = mul i32 %54, %176
  %188 = add i32 %184, %187
  %189 = add i32 %58, %187
  %190 = add i32 %54, 2
  %191 = mul i32 %176, %190
  %192 = add i32 %184, %191
  %193 = add i32 %58, %191
  %194 = add i32 %167, %191
  %195 = add i32 %167, %187
  %196 = add i32 %184, %181
  %197 = add i32 %58, %181
  %198 = add i32 %184, %114
  %199 = mul i32 %108, %190
  %200 = add i32 %184, %199
  %201 = add i32 %58, %199
  %202 = add i32 %167, %199
  %203 = add i32 %167, %114
  %min.iters.check227 = icmp ult i32 %66, 17
  %204 = trunc nsw i64 %177 to i32
  %mul.result = shl i32 %204, 1
  %invariant.op545 = add i32 %179, %mul.result
  %invariant.op547 = add i32 %182, %mul.result
  %205 = icmp ugt i64 %177, 4294967295
  %invariant.op549 = add i32 %185, %mul.result
  %invariant.op551 = add i32 %186, %mul.result
  %invariant.op553 = add i32 %188, %mul.result
  %invariant.op555 = add i32 %189, %mul.result
  %invariant.op557 = add i32 %192, %mul.result
  %invariant.op559 = add i32 %193, %mul.result
  %invariant.op561 = add i32 %194, %mul.result
  %invariant.op563 = add i32 %195, %mul.result
  %invariant.op565 = add i32 %196, %mul.result
  %invariant.op567 = add i32 %197, %mul.result
  %invariant.op569 = add i32 %198, %mul.result
  %invariant.op571 = add i32 %115, %mul.result
  %invariant.op573 = add i32 %200, %mul.result
  %invariant.op575 = add i32 %201, %mul.result
  %invariant.op577 = add i32 %202, %mul.result
  %invariant.op579 = add i32 %203, %mul.result
  %min.iters.check230 = icmp ult i32 %66, 65
  %n.vec234 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %163, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %206 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert245 = insertelement <8 x i32> poison, i32 %167, i64 0
  %broadcast.splat246 = shufflevector <8 x i32> %broadcast.splatinsert245, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert262 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat263 = shufflevector <8 x i32> %broadcast.splatinsert262, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert332 = insertelement <8 x float> poison, float %162, i64 0
  %broadcast.splat333 = shufflevector <8 x float> %broadcast.splatinsert332, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert334 = insertelement <8 x float> poison, float %172, i64 0
  %broadcast.splat335 = shufflevector <8 x float> %broadcast.splatinsert334, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert351 = insertelement <8 x float> poison, float %160, i64 0
  %broadcast.splat352 = shufflevector <8 x float> %broadcast.splatinsert351, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat246
  %invariant.op535 = add <8 x i32> splat (i32 32), %broadcast.splat246
  %invariant.op537 = add <8 x i32> splat (i32 48), %broadcast.splat246
  %invariant.op539 = add <8 x i32> splat (i32 16), %broadcast.splat263
  %invariant.op541 = add <8 x i32> splat (i32 32), %broadcast.splat263
  %invariant.op543 = add <8 x i32> splat (i32 48), %broadcast.splat263
  %cmp.n400 = icmp eq i64 %n.vec234, %wide.trip.count
  %n.vec.remaining408 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check409 = icmp eq i64 %n.vec.remaining408, 0
  %n.vec411 = and i64 %wide.trip.count, 2147483640
  %cmp.n475 = icmp eq i64 %n.vec411, %wide.trip.count
  %207 = zext i32 %119 to i64
  %208 = lshr i64 %207, 4
  %209 = mul nsw i64 %208, -8
  %210 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check229

iter.check229:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %lsr.iv613 = phi i32 [ %lsr.iv.next614, %for_loop_test23.after_for22_crit_edge.us ], [ %186, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv609 = phi i32 [ %lsr.iv.next610, %for_loop_test23.after_for22_crit_edge.us ], [ %197, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv605 = phi i32 [ %lsr.iv.next606, %for_loop_test23.after_for22_crit_edge.us ], [ %193, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv601 = phi i32 [ %lsr.iv.next602, %for_loop_test23.after_for22_crit_edge.us ], [ %189, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv597 = phi i32 [ %lsr.iv.next598, %for_loop_test23.after_for22_crit_edge.us ], [ %201, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv593 = phi i32 [ %lsr.iv.next594, %for_loop_test23.after_for22_crit_edge.us ], [ %115, %for_loop_body16.lr.ph.split.us ]
  %.064111.us = phi i32 [ 0, %for_loop_body16.lr.ph.split.us ], [ %1326, %for_loop_test23.after_for22_crit_edge.us ]
  %.065110.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ]
  %.067109.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa150, %for_loop_test23.after_for22_crit_edge.us ]
  %211 = shl nuw i32 %.064111.us, 1
  %212 = add i32 %165, %211
  %213 = add i32 %211, %54
  %214 = add i32 %212, 1
  %215 = mul i32 %176, %212
  %216 = mul i32 %212, %108
  %217 = mul i32 %176, %213
  %218 = mul i32 %176, %214
  %219 = mul i32 %213, %108
  %220 = mul i32 %214, %108
  br i1 %min.iters.check227, label %for_loop_body20.us.preheader, label %vector.scevcheck174

vector.scevcheck174:                              ; preds = %iter.check229
  %221 = mul i32 %183, %.064111.us
  %222 = add i32 %203, %221
  %223 = add i32 %202, %221
  %224 = add i32 %201, %221
  %225 = add i32 %200, %221
  %226 = add i32 %115, %221
  %227 = add i32 %198, %221
  %228 = add i32 %197, %221
  %229 = add i32 %196, %221
  %230 = mul i32 %180, %.064111.us
  %231 = add i32 %195, %230
  %232 = add i32 %194, %230
  %233 = add i32 %193, %230
  %234 = add i32 %192, %230
  %235 = add i32 %189, %230
  %236 = add i32 %188, %230
  %237 = add i32 %186, %230
  %238 = add i32 %185, %230
  %239 = add i32 %182, %221
  %240 = add i32 %179, %230
  %.reass546 = add i32 %230, %invariant.op545
  %241 = icmp slt i32 %.reass546, %240
  %.reass548 = add i32 %221, %invariant.op547
  %242 = icmp slt i32 %.reass548, %239
  %243 = or i1 %242, %205
  %.reass550 = add i32 %230, %invariant.op549
  %244 = icmp slt i32 %.reass550, %238
  %.reass552 = add i32 %230, %invariant.op551
  %245 = icmp slt i32 %.reass552, %237
  %.reass554 = add i32 %230, %invariant.op553
  %246 = icmp slt i32 %.reass554, %236
  %.reass556 = add i32 %230, %invariant.op555
  %247 = icmp slt i32 %.reass556, %235
  %.reass558 = add i32 %230, %invariant.op557
  %248 = icmp slt i32 %.reass558, %234
  %.reass560 = add i32 %230, %invariant.op559
  %249 = icmp slt i32 %.reass560, %233
  %.reass562 = add i32 %230, %invariant.op561
  %250 = icmp slt i32 %.reass562, %232
  %.reass564 = add i32 %230, %invariant.op563
  %251 = icmp slt i32 %.reass564, %231
  %252 = or i1 %251, %205
  %.reass566 = add i32 %221, %invariant.op565
  %253 = icmp slt i32 %.reass566, %229
  %.reass568 = add i32 %221, %invariant.op567
  %254 = icmp slt i32 %.reass568, %228
  %.reass570 = add i32 %221, %invariant.op569
  %255 = icmp slt i32 %.reass570, %227
  %.reass572 = add i32 %221, %invariant.op571
  %256 = icmp slt i32 %.reass572, %226
  %.reass574 = add i32 %221, %invariant.op573
  %257 = icmp slt i32 %.reass574, %225
  %.reass576 = add i32 %221, %invariant.op575
  %258 = icmp slt i32 %.reass576, %224
  %.reass578 = add i32 %221, %invariant.op577
  %259 = icmp slt i32 %.reass578, %223
  %.reass580 = add i32 %221, %invariant.op579
  %260 = icmp slt i32 %.reass580, %222
  %261 = or i1 %260, %205
  %262 = or i1 %241, %243
  %263 = or i1 %244, %262
  %264 = or i1 %245, %263
  %265 = or i1 %246, %264
  %266 = or i1 %247, %265
  %267 = or i1 %248, %266
  %268 = or i1 %249, %267
  %269 = or i1 %250, %268
  %270 = or i1 %269, %252
  %271 = or i1 %253, %270
  %272 = or i1 %254, %271
  %273 = or i1 %255, %272
  %274 = or i1 %256, %273
  %275 = or i1 %257, %274
  %276 = or i1 %258, %275
  %277 = or i1 %259, %276
  %278 = or i1 %277, %261
  br i1 %278, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check231

vector.main.loop.iter.check231:                   ; preds = %vector.scevcheck174
  br i1 %min.iters.check230, label %vec.epilog.ph406, label %vector.ph232

vector.ph232:                                     ; preds = %vector.main.loop.iter.check231
  %279 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.065110.us, i64 0
  %280 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.067109.us, i64 0
  %broadcast.splatinsert247 = insertelement <8 x i32> poison, i32 %215, i64 0
  %broadcast.splat248 = shufflevector <8 x i32> %broadcast.splatinsert247, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert252 = insertelement <8 x i32> poison, i32 %216, i64 0
  %broadcast.splat253 = shufflevector <8 x i32> %broadcast.splatinsert252, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert268 = insertelement <8 x i32> poison, i32 %217, i64 0
  %broadcast.splat269 = shufflevector <8 x i32> %broadcast.splatinsert268, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert278 = insertelement <8 x i32> poison, i32 %218, i64 0
  %broadcast.splat279 = shufflevector <8 x i32> %broadcast.splatinsert278, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert304 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat305 = shufflevector <8 x i32> %broadcast.splatinsert304, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert314 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat315 = shufflevector <8 x i32> %broadcast.splatinsert314, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body235

vector.body235:                                   ; preds = %vector.body235, %vector.ph232
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body235 ], [ %n.vec234, %vector.ph232 ]
  %vec.phi237 = phi <8 x float> [ %279, %vector.ph232 ], [ %972, %vector.body235 ]
  %vec.phi238 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %973, %vector.body235 ]
  %vec.phi239 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %974, %vector.body235 ]
  %vec.phi240 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %975, %vector.body235 ]
  %vec.phi241 = phi <8 x float> [ %280, %vector.ph232 ], [ %968, %vector.body235 ]
  %vec.phi242 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %969, %vector.body235 ]
  %vec.phi243 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %970, %vector.body235 ]
  %vec.phi244 = phi <8 x float> [ zeroinitializer, %vector.ph232 ], [ %971, %vector.body235 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph232 ], [ %vec.ind.next, %vector.body235 ]
  %281 = shl <8 x i32> %vec.ind, splat (i32 1)
  %282 = add <8 x i32> %broadcast.splat246, %281
  %.reass = add <8 x i32> %281, %invariant.op
  %.reass536 = add <8 x i32> %281, %invariant.op535
  %.reass538 = add <8 x i32> %281, %invariant.op537
  %283 = add <8 x i32> %broadcast.splat248, %282
  %284 = add <8 x i32> %broadcast.splat248, %.reass
  %285 = add <8 x i32> %broadcast.splat248, %.reass536
  %286 = add <8 x i32> %broadcast.splat248, %.reass538
  %287 = sext <8 x i32> %283 to <8 x i64>
  %288 = sext <8 x i32> %284 to <8 x i64>
  %289 = sext <8 x i32> %285 to <8 x i64>
  %290 = sext <8 x i32> %286 to <8 x i64>
  %291 = getelementptr float, ptr %175, <8 x i64> %287
  %292 = getelementptr float, ptr %175, <8 x i64> %288
  %293 = getelementptr float, ptr %175, <8 x i64> %289
  %294 = getelementptr float, ptr %175, <8 x i64> %290
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %291, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather249 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %292, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather250 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %293, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather251 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %294, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %295 = add <8 x i32> %282, %broadcast.splat253
  %296 = add <8 x i32> %.reass, %broadcast.splat253
  %297 = add <8 x i32> %.reass536, %broadcast.splat253
  %298 = add <8 x i32> %.reass538, %broadcast.splat253
  %299 = sext <8 x i32> %295 to <8 x i64>
  %300 = sext <8 x i32> %296 to <8 x i64>
  %301 = sext <8 x i32> %297 to <8 x i64>
  %302 = sext <8 x i32> %298 to <8 x i64>
  %303 = getelementptr float, ptr %106, <8 x i64> %299
  %304 = getelementptr float, ptr %106, <8 x i64> %300
  %305 = getelementptr float, ptr %106, <8 x i64> %301
  %306 = getelementptr float, ptr %106, <8 x i64> %302
  %wide.masked.gather254 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %303, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather255 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %304, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather256 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %305, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather257 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %306, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %307 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather254
  %308 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather249, %wide.masked.gather255
  %309 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather250, %wide.masked.gather256
  %310 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather251, %wide.masked.gather257
  %311 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %307)
  %312 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %308)
  %313 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %309)
  %314 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %310)
  %315 = add <8 x i32> %282, splat (i32 1)
  %316 = add <8 x i32> %.reass, splat (i32 1)
  %317 = add <8 x i32> %.reass536, splat (i32 1)
  %318 = add <8 x i32> %.reass538, splat (i32 1)
  %319 = add <8 x i32> %broadcast.splat248, %315
  %320 = add <8 x i32> %broadcast.splat248, %316
  %321 = add <8 x i32> %broadcast.splat248, %317
  %322 = add <8 x i32> %broadcast.splat248, %318
  %323 = sext <8 x i32> %319 to <8 x i64>
  %324 = sext <8 x i32> %320 to <8 x i64>
  %325 = sext <8 x i32> %321 to <8 x i64>
  %326 = sext <8 x i32> %322 to <8 x i64>
  %327 = getelementptr float, ptr %175, <8 x i64> %323
  %328 = getelementptr float, ptr %175, <8 x i64> %324
  %329 = getelementptr float, ptr %175, <8 x i64> %325
  %330 = getelementptr float, ptr %175, <8 x i64> %326
  %wide.masked.gather258 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %327, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather259 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %328, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather260 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %329, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather261 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %330, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %331 = add <8 x i32> %281, %broadcast.splat263
  %.reass540 = add <8 x i32> %281, %invariant.op539
  %.reass542 = add <8 x i32> %281, %invariant.op541
  %.reass544 = add <8 x i32> %281, %invariant.op543
  %332 = add <8 x i32> %broadcast.splat248, %331
  %333 = add <8 x i32> %broadcast.splat248, %.reass540
  %334 = add <8 x i32> %broadcast.splat248, %.reass542
  %335 = add <8 x i32> %broadcast.splat248, %.reass544
  %336 = sext <8 x i32> %332 to <8 x i64>
  %337 = sext <8 x i32> %333 to <8 x i64>
  %338 = sext <8 x i32> %334 to <8 x i64>
  %339 = sext <8 x i32> %335 to <8 x i64>
  %340 = getelementptr float, ptr %175, <8 x i64> %336
  %341 = getelementptr float, ptr %175, <8 x i64> %337
  %342 = getelementptr float, ptr %175, <8 x i64> %338
  %343 = getelementptr float, ptr %175, <8 x i64> %339
  %wide.masked.gather264 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %340, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather265 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %341, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather266 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %342, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather267 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %343, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %344 = add <8 x i32> %broadcast.splat269, %315
  %345 = add <8 x i32> %broadcast.splat269, %316
  %346 = add <8 x i32> %broadcast.splat269, %317
  %347 = add <8 x i32> %broadcast.splat269, %318
  %348 = sext <8 x i32> %344 to <8 x i64>
  %349 = sext <8 x i32> %345 to <8 x i64>
  %350 = sext <8 x i32> %346 to <8 x i64>
  %351 = sext <8 x i32> %347 to <8 x i64>
  %352 = getelementptr float, ptr %175, <8 x i64> %348
  %353 = getelementptr float, ptr %175, <8 x i64> %349
  %354 = getelementptr float, ptr %175, <8 x i64> %350
  %355 = getelementptr float, ptr %175, <8 x i64> %351
  %wide.masked.gather270 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %352, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather271 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %353, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather272 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %354, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather273 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %355, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %356 = add <8 x i32> %broadcast.splat269, %331
  %357 = add <8 x i32> %broadcast.splat269, %.reass540
  %358 = add <8 x i32> %broadcast.splat269, %.reass542
  %359 = add <8 x i32> %broadcast.splat269, %.reass544
  %360 = sext <8 x i32> %356 to <8 x i64>
  %361 = sext <8 x i32> %357 to <8 x i64>
  %362 = sext <8 x i32> %358 to <8 x i64>
  %363 = sext <8 x i32> %359 to <8 x i64>
  %364 = getelementptr float, ptr %175, <8 x i64> %360
  %365 = getelementptr float, ptr %175, <8 x i64> %361
  %366 = getelementptr float, ptr %175, <8 x i64> %362
  %367 = getelementptr float, ptr %175, <8 x i64> %363
  %wide.masked.gather274 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %364, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather275 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %365, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather276 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %366, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather277 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %367, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %368 = add <8 x i32> %broadcast.splat279, %315
  %369 = add <8 x i32> %broadcast.splat279, %316
  %370 = add <8 x i32> %broadcast.splat279, %317
  %371 = add <8 x i32> %broadcast.splat279, %318
  %372 = sext <8 x i32> %368 to <8 x i64>
  %373 = sext <8 x i32> %369 to <8 x i64>
  %374 = sext <8 x i32> %370 to <8 x i64>
  %375 = sext <8 x i32> %371 to <8 x i64>
  %376 = getelementptr float, ptr %175, <8 x i64> %372
  %377 = getelementptr float, ptr %175, <8 x i64> %373
  %378 = getelementptr float, ptr %175, <8 x i64> %374
  %379 = getelementptr float, ptr %175, <8 x i64> %375
  %wide.masked.gather280 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %376, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather281 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %377, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather282 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %378, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather283 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %379, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %380 = add <8 x i32> %broadcast.splat279, %331
  %381 = add <8 x i32> %broadcast.splat279, %.reass540
  %382 = add <8 x i32> %broadcast.splat279, %.reass542
  %383 = add <8 x i32> %broadcast.splat279, %.reass544
  %384 = sext <8 x i32> %380 to <8 x i64>
  %385 = sext <8 x i32> %381 to <8 x i64>
  %386 = sext <8 x i32> %382 to <8 x i64>
  %387 = sext <8 x i32> %383 to <8 x i64>
  %388 = getelementptr float, ptr %175, <8 x i64> %384
  %389 = getelementptr float, ptr %175, <8 x i64> %385
  %390 = getelementptr float, ptr %175, <8 x i64> %386
  %391 = getelementptr float, ptr %175, <8 x i64> %387
  %wide.masked.gather284 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %388, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather285 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %389, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather286 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %390, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather287 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %391, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %392 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather258, %wide.masked.gather270
  %393 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather259, %wide.masked.gather271
  %394 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather260, %wide.masked.gather272
  %395 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather261, %wide.masked.gather273
  %396 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather264, %wide.masked.gather274
  %397 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather265, %wide.masked.gather275
  %398 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather266, %wide.masked.gather276
  %399 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather267, %wide.masked.gather277
  %400 = fadd reassoc ninf nsz <8 x float> %392, %wide.masked.gather280
  %401 = fadd reassoc ninf nsz <8 x float> %393, %wide.masked.gather281
  %402 = fadd reassoc ninf nsz <8 x float> %394, %wide.masked.gather282
  %403 = fadd reassoc ninf nsz <8 x float> %395, %wide.masked.gather283
  %404 = fadd reassoc ninf nsz <8 x float> %396, %wide.masked.gather284
  %405 = fadd reassoc ninf nsz <8 x float> %397, %wide.masked.gather285
  %406 = fadd reassoc ninf nsz <8 x float> %398, %wide.masked.gather286
  %407 = fadd reassoc ninf nsz <8 x float> %399, %wide.masked.gather287
  %408 = fsub reassoc ninf nsz <8 x float> %400, %404
  %409 = fsub reassoc ninf nsz <8 x float> %401, %405
  %410 = fsub reassoc ninf nsz <8 x float> %402, %406
  %411 = fsub reassoc ninf nsz <8 x float> %403, %407
  %412 = fmul reassoc ninf nsz <8 x float> %408, splat (float 0x3FD5555560000000)
  %413 = fmul reassoc ninf nsz <8 x float> %409, splat (float 0x3FD5555560000000)
  %414 = fmul reassoc ninf nsz <8 x float> %410, splat (float 0x3FD5555560000000)
  %415 = fmul reassoc ninf nsz <8 x float> %411, splat (float 0x3FD5555560000000)
  %416 = add <8 x i32> %broadcast.splat279, %282
  %417 = add <8 x i32> %broadcast.splat279, %.reass
  %418 = add <8 x i32> %broadcast.splat279, %.reass536
  %419 = add <8 x i32> %broadcast.splat279, %.reass538
  %420 = sext <8 x i32> %416 to <8 x i64>
  %421 = sext <8 x i32> %417 to <8 x i64>
  %422 = sext <8 x i32> %418 to <8 x i64>
  %423 = sext <8 x i32> %419 to <8 x i64>
  %424 = getelementptr float, ptr %175, <8 x i64> %420
  %425 = getelementptr float, ptr %175, <8 x i64> %421
  %426 = getelementptr float, ptr %175, <8 x i64> %422
  %427 = getelementptr float, ptr %175, <8 x i64> %423
  %wide.masked.gather288 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %424, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather289 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %425, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather290 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %426, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather291 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %427, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %428 = add <8 x i32> %broadcast.splat269, %282
  %429 = add <8 x i32> %broadcast.splat269, %.reass
  %430 = add <8 x i32> %broadcast.splat269, %.reass536
  %431 = add <8 x i32> %broadcast.splat269, %.reass538
  %432 = sext <8 x i32> %428 to <8 x i64>
  %433 = sext <8 x i32> %429 to <8 x i64>
  %434 = sext <8 x i32> %430 to <8 x i64>
  %435 = sext <8 x i32> %431 to <8 x i64>
  %436 = getelementptr float, ptr %175, <8 x i64> %432
  %437 = getelementptr float, ptr %175, <8 x i64> %433
  %438 = getelementptr float, ptr %175, <8 x i64> %434
  %439 = getelementptr float, ptr %175, <8 x i64> %435
  %wide.masked.gather292 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %436, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather293 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %437, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather294 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %438, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather295 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %439, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %440 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather270, %wide.masked.gather274
  %441 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather271, %wide.masked.gather275
  %442 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather272, %wide.masked.gather276
  %443 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather273, %wide.masked.gather277
  %444 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather280, %440
  %445 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather281, %441
  %446 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather282, %442
  %447 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather283, %443
  %448 = fadd reassoc ninf nsz <8 x float> %444, %wide.masked.gather284
  %449 = fadd reassoc ninf nsz <8 x float> %445, %wide.masked.gather285
  %450 = fadd reassoc ninf nsz <8 x float> %446, %wide.masked.gather286
  %451 = fadd reassoc ninf nsz <8 x float> %447, %wide.masked.gather287
  %452 = fadd reassoc ninf nsz <8 x float> %448, %wide.masked.gather288
  %453 = fadd reassoc ninf nsz <8 x float> %449, %wide.masked.gather289
  %454 = fadd reassoc ninf nsz <8 x float> %450, %wide.masked.gather290
  %455 = fadd reassoc ninf nsz <8 x float> %451, %wide.masked.gather291
  %456 = fsub reassoc ninf nsz <8 x float> %452, %wide.masked.gather292
  %457 = fsub reassoc ninf nsz <8 x float> %453, %wide.masked.gather293
  %458 = fsub reassoc ninf nsz <8 x float> %454, %wide.masked.gather294
  %459 = fsub reassoc ninf nsz <8 x float> %455, %wide.masked.gather295
  %460 = fmul reassoc ninf nsz <8 x float> %456, splat (float 0x3FD5555560000000)
  %461 = fmul reassoc ninf nsz <8 x float> %457, splat (float 0x3FD5555560000000)
  %462 = fmul reassoc ninf nsz <8 x float> %458, splat (float 0x3FD5555560000000)
  %463 = fmul reassoc ninf nsz <8 x float> %459, splat (float 0x3FD5555560000000)
  %464 = add <8 x i32> %315, %broadcast.splat253
  %465 = add <8 x i32> %316, %broadcast.splat253
  %466 = add <8 x i32> %317, %broadcast.splat253
  %467 = add <8 x i32> %318, %broadcast.splat253
  %468 = sext <8 x i32> %464 to <8 x i64>
  %469 = sext <8 x i32> %465 to <8 x i64>
  %470 = sext <8 x i32> %466 to <8 x i64>
  %471 = sext <8 x i32> %467 to <8 x i64>
  %472 = getelementptr float, ptr %106, <8 x i64> %468
  %473 = getelementptr float, ptr %106, <8 x i64> %469
  %474 = getelementptr float, ptr %106, <8 x i64> %470
  %475 = getelementptr float, ptr %106, <8 x i64> %471
  %wide.masked.gather296 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %472, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather297 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %473, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather298 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %474, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather299 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %475, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %476 = add <8 x i32> %331, %broadcast.splat253
  %477 = add <8 x i32> %.reass540, %broadcast.splat253
  %478 = add <8 x i32> %.reass542, %broadcast.splat253
  %479 = add <8 x i32> %.reass544, %broadcast.splat253
  %480 = sext <8 x i32> %476 to <8 x i64>
  %481 = sext <8 x i32> %477 to <8 x i64>
  %482 = sext <8 x i32> %478 to <8 x i64>
  %483 = sext <8 x i32> %479 to <8 x i64>
  %484 = getelementptr float, ptr %106, <8 x i64> %480
  %485 = getelementptr float, ptr %106, <8 x i64> %481
  %486 = getelementptr float, ptr %106, <8 x i64> %482
  %487 = getelementptr float, ptr %106, <8 x i64> %483
  %wide.masked.gather300 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %484, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather301 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %485, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather302 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %486, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather303 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %487, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %488 = add <8 x i32> %315, %broadcast.splat305
  %489 = add <8 x i32> %316, %broadcast.splat305
  %490 = add <8 x i32> %317, %broadcast.splat305
  %491 = add <8 x i32> %318, %broadcast.splat305
  %492 = sext <8 x i32> %488 to <8 x i64>
  %493 = sext <8 x i32> %489 to <8 x i64>
  %494 = sext <8 x i32> %490 to <8 x i64>
  %495 = sext <8 x i32> %491 to <8 x i64>
  %496 = getelementptr float, ptr %106, <8 x i64> %492
  %497 = getelementptr float, ptr %106, <8 x i64> %493
  %498 = getelementptr float, ptr %106, <8 x i64> %494
  %499 = getelementptr float, ptr %106, <8 x i64> %495
  %wide.masked.gather306 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %496, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather307 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %497, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather308 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %498, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather309 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %499, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %500 = add <8 x i32> %331, %broadcast.splat305
  %501 = add <8 x i32> %.reass540, %broadcast.splat305
  %502 = add <8 x i32> %.reass542, %broadcast.splat305
  %503 = add <8 x i32> %.reass544, %broadcast.splat305
  %504 = sext <8 x i32> %500 to <8 x i64>
  %505 = sext <8 x i32> %501 to <8 x i64>
  %506 = sext <8 x i32> %502 to <8 x i64>
  %507 = sext <8 x i32> %503 to <8 x i64>
  %508 = getelementptr float, ptr %106, <8 x i64> %504
  %509 = getelementptr float, ptr %106, <8 x i64> %505
  %510 = getelementptr float, ptr %106, <8 x i64> %506
  %511 = getelementptr float, ptr %106, <8 x i64> %507
  %wide.masked.gather310 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %508, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather311 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %509, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather312 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %510, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather313 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %511, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %512 = add <8 x i32> %315, %broadcast.splat315
  %513 = add <8 x i32> %316, %broadcast.splat315
  %514 = add <8 x i32> %317, %broadcast.splat315
  %515 = add <8 x i32> %318, %broadcast.splat315
  %516 = sext <8 x i32> %512 to <8 x i64>
  %517 = sext <8 x i32> %513 to <8 x i64>
  %518 = sext <8 x i32> %514 to <8 x i64>
  %519 = sext <8 x i32> %515 to <8 x i64>
  %520 = getelementptr float, ptr %106, <8 x i64> %516
  %521 = getelementptr float, ptr %106, <8 x i64> %517
  %522 = getelementptr float, ptr %106, <8 x i64> %518
  %523 = getelementptr float, ptr %106, <8 x i64> %519
  %wide.masked.gather316 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %520, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather317 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %521, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather318 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %522, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather319 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %523, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %524 = add <8 x i32> %331, %broadcast.splat315
  %525 = add <8 x i32> %.reass540, %broadcast.splat315
  %526 = add <8 x i32> %.reass542, %broadcast.splat315
  %527 = add <8 x i32> %.reass544, %broadcast.splat315
  %528 = sext <8 x i32> %524 to <8 x i64>
  %529 = sext <8 x i32> %525 to <8 x i64>
  %530 = sext <8 x i32> %526 to <8 x i64>
  %531 = sext <8 x i32> %527 to <8 x i64>
  %532 = getelementptr float, ptr %106, <8 x i64> %528
  %533 = getelementptr float, ptr %106, <8 x i64> %529
  %534 = getelementptr float, ptr %106, <8 x i64> %530
  %535 = getelementptr float, ptr %106, <8 x i64> %531
  %wide.masked.gather320 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %532, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather321 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %533, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather322 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %534, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather323 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %535, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %536 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather296, %wide.masked.gather306
  %537 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather297, %wide.masked.gather307
  %538 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather298, %wide.masked.gather308
  %539 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather299, %wide.masked.gather309
  %540 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather300, %wide.masked.gather310
  %541 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather301, %wide.masked.gather311
  %542 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather302, %wide.masked.gather312
  %543 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather303, %wide.masked.gather313
  %544 = fadd reassoc ninf nsz <8 x float> %536, %wide.masked.gather316
  %545 = fadd reassoc ninf nsz <8 x float> %537, %wide.masked.gather317
  %546 = fadd reassoc ninf nsz <8 x float> %538, %wide.masked.gather318
  %547 = fadd reassoc ninf nsz <8 x float> %539, %wide.masked.gather319
  %548 = fadd reassoc ninf nsz <8 x float> %540, %wide.masked.gather320
  %549 = fadd reassoc ninf nsz <8 x float> %541, %wide.masked.gather321
  %550 = fadd reassoc ninf nsz <8 x float> %542, %wide.masked.gather322
  %551 = fadd reassoc ninf nsz <8 x float> %543, %wide.masked.gather323
  %552 = fsub reassoc ninf nsz <8 x float> %544, %548
  %553 = fsub reassoc ninf nsz <8 x float> %545, %549
  %554 = fsub reassoc ninf nsz <8 x float> %546, %550
  %555 = fsub reassoc ninf nsz <8 x float> %547, %551
  %556 = fmul reassoc ninf nsz <8 x float> %552, splat (float 0x3FD5555560000000)
  %557 = fmul reassoc ninf nsz <8 x float> %553, splat (float 0x3FD5555560000000)
  %558 = fmul reassoc ninf nsz <8 x float> %554, splat (float 0x3FD5555560000000)
  %559 = fmul reassoc ninf nsz <8 x float> %555, splat (float 0x3FD5555560000000)
  %560 = add <8 x i32> %282, %broadcast.splat315
  %561 = add <8 x i32> %.reass, %broadcast.splat315
  %562 = add <8 x i32> %.reass536, %broadcast.splat315
  %563 = add <8 x i32> %.reass538, %broadcast.splat315
  %564 = sext <8 x i32> %560 to <8 x i64>
  %565 = sext <8 x i32> %561 to <8 x i64>
  %566 = sext <8 x i32> %562 to <8 x i64>
  %567 = sext <8 x i32> %563 to <8 x i64>
  %568 = getelementptr float, ptr %106, <8 x i64> %564
  %569 = getelementptr float, ptr %106, <8 x i64> %565
  %570 = getelementptr float, ptr %106, <8 x i64> %566
  %571 = getelementptr float, ptr %106, <8 x i64> %567
  %wide.masked.gather324 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %568, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather325 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %569, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather326 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %570, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather327 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %571, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %572 = add <8 x i32> %282, %broadcast.splat305
  %573 = add <8 x i32> %.reass, %broadcast.splat305
  %574 = add <8 x i32> %.reass536, %broadcast.splat305
  %575 = add <8 x i32> %.reass538, %broadcast.splat305
  %576 = sext <8 x i32> %572 to <8 x i64>
  %577 = sext <8 x i32> %573 to <8 x i64>
  %578 = sext <8 x i32> %574 to <8 x i64>
  %579 = sext <8 x i32> %575 to <8 x i64>
  %580 = getelementptr float, ptr %106, <8 x i64> %576
  %581 = getelementptr float, ptr %106, <8 x i64> %577
  %582 = getelementptr float, ptr %106, <8 x i64> %578
  %583 = getelementptr float, ptr %106, <8 x i64> %579
  %wide.masked.gather328 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %580, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather329 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %581, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather330 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %582, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather331 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %583, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %584 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather306, %wide.masked.gather310
  %585 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather307, %wide.masked.gather311
  %586 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather308, %wide.masked.gather312
  %587 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather309, %wide.masked.gather313
  %588 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather316, %584
  %589 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather317, %585
  %590 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather318, %586
  %591 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather319, %587
  %592 = fadd reassoc ninf nsz <8 x float> %588, %wide.masked.gather320
  %593 = fadd reassoc ninf nsz <8 x float> %589, %wide.masked.gather321
  %594 = fadd reassoc ninf nsz <8 x float> %590, %wide.masked.gather322
  %595 = fadd reassoc ninf nsz <8 x float> %591, %wide.masked.gather323
  %596 = fadd reassoc ninf nsz <8 x float> %592, %wide.masked.gather324
  %597 = fadd reassoc ninf nsz <8 x float> %593, %wide.masked.gather325
  %598 = fadd reassoc ninf nsz <8 x float> %594, %wide.masked.gather326
  %599 = fadd reassoc ninf nsz <8 x float> %595, %wide.masked.gather327
  %600 = fsub reassoc ninf nsz <8 x float> %596, %wide.masked.gather328
  %601 = fsub reassoc ninf nsz <8 x float> %597, %wide.masked.gather329
  %602 = fsub reassoc ninf nsz <8 x float> %598, %wide.masked.gather330
  %603 = fsub reassoc ninf nsz <8 x float> %599, %wide.masked.gather331
  %604 = fmul reassoc ninf nsz <8 x float> %600, splat (float 0x3FD5555560000000)
  %605 = fmul reassoc ninf nsz <8 x float> %601, splat (float 0x3FD5555560000000)
  %606 = fmul reassoc ninf nsz <8 x float> %602, splat (float 0x3FD5555560000000)
  %607 = fmul reassoc ninf nsz <8 x float> %603, splat (float 0x3FD5555560000000)
  %608 = fmul reassoc ninf nsz <8 x float> %412, %412
  %609 = fmul reassoc ninf nsz <8 x float> %413, %413
  %610 = fmul reassoc ninf nsz <8 x float> %414, %414
  %611 = fmul reassoc ninf nsz <8 x float> %415, %415
  %612 = fmul reassoc ninf nsz <8 x float> %460, %460
  %613 = fmul reassoc ninf nsz <8 x float> %461, %461
  %614 = fmul reassoc ninf nsz <8 x float> %462, %462
  %615 = fmul reassoc ninf nsz <8 x float> %463, %463
  %616 = fadd reassoc ninf nsz <8 x float> %612, %608
  %617 = fadd reassoc ninf nsz <8 x float> %613, %609
  %618 = fadd reassoc ninf nsz <8 x float> %614, %610
  %619 = fadd reassoc ninf nsz <8 x float> %615, %611
  %620 = fmul reassoc ninf nsz <8 x float> %556, %556
  %621 = fmul reassoc ninf nsz <8 x float> %557, %557
  %622 = fmul reassoc ninf nsz <8 x float> %558, %558
  %623 = fmul reassoc ninf nsz <8 x float> %559, %559
  %624 = fmul reassoc ninf nsz <8 x float> %604, %604
  %625 = fmul reassoc ninf nsz <8 x float> %605, %605
  %626 = fmul reassoc ninf nsz <8 x float> %606, %606
  %627 = fmul reassoc ninf nsz <8 x float> %607, %607
  %628 = fadd reassoc ninf nsz <8 x float> %624, %620
  %629 = fadd reassoc ninf nsz <8 x float> %625, %621
  %630 = fadd reassoc ninf nsz <8 x float> %626, %622
  %631 = fadd reassoc ninf nsz <8 x float> %627, %623
  %632 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %616, <8 x float> %628)
  %633 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %617, <8 x float> %629)
  %634 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %618, <8 x float> %630)
  %635 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %619, <8 x float> %631)
  %636 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather254, splat (float -2.000000e+00)
  %637 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather255, splat (float -2.000000e+00)
  %638 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather256, splat (float -2.000000e+00)
  %639 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather257, splat (float -2.000000e+00)
  %640 = fadd reassoc ninf nsz <8 x float> %636, splat (float 3.000000e+00)
  %641 = fadd reassoc ninf nsz <8 x float> %637, splat (float 3.000000e+00)
  %642 = fadd reassoc ninf nsz <8 x float> %638, splat (float 3.000000e+00)
  %643 = fadd reassoc ninf nsz <8 x float> %639, splat (float 3.000000e+00)
  %644 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %640, <8 x float> splat (float 3.000000e+00))
  %645 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %641, <8 x float> splat (float 3.000000e+00))
  %646 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %642, <8 x float> splat (float 3.000000e+00))
  %647 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %643, <8 x float> splat (float 3.000000e+00))
  %648 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %644, <8 x float> splat (float 1.000000e+00))
  %649 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %645, <8 x float> splat (float 1.000000e+00))
  %650 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %646, <8 x float> splat (float 1.000000e+00))
  %651 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %647, <8 x float> splat (float 1.000000e+00))
  %652 = fmul reassoc ninf nsz <8 x float> %648, %broadcast.splat333
  %653 = fmul reassoc ninf nsz <8 x float> %649, %broadcast.splat333
  %654 = fmul reassoc ninf nsz <8 x float> %650, %broadcast.splat333
  %655 = fmul reassoc ninf nsz <8 x float> %651, %broadcast.splat333
  %656 = fmul reassoc ninf nsz <8 x float> %648, %648
  %657 = fmul reassoc ninf nsz <8 x float> %649, %649
  %658 = fmul reassoc ninf nsz <8 x float> %650, %650
  %659 = fmul reassoc ninf nsz <8 x float> %651, %651
  %660 = fmul reassoc ninf nsz <8 x float> %656, %broadcast.splat335
  %661 = fmul reassoc ninf nsz <8 x float> %657, %broadcast.splat335
  %662 = fmul reassoc ninf nsz <8 x float> %658, %broadcast.splat335
  %663 = fmul reassoc ninf nsz <8 x float> %659, %broadcast.splat335
  %664 = fcmp reassoc ninf nsz olt <8 x float> %632, %660
  %665 = fcmp reassoc ninf nsz olt <8 x float> %633, %661
  %666 = fcmp reassoc ninf nsz olt <8 x float> %634, %662
  %667 = fcmp reassoc ninf nsz olt <8 x float> %635, %663
  %668 = xor <8 x i1> %664, splat (i1 true)
  %669 = xor <8 x i1> %665, splat (i1 true)
  %670 = xor <8 x i1> %666, splat (i1 true)
  %671 = xor <8 x i1> %667, splat (i1 true)
  %672 = select <8 x i1> %broadcast.splat, <8 x i1> %668, <8 x i1> zeroinitializer
  %673 = select <8 x i1> %broadcast.splat, <8 x i1> %669, <8 x i1> zeroinitializer
  %674 = select <8 x i1> %broadcast.splat, <8 x i1> %670, <8 x i1> zeroinitializer
  %675 = select <8 x i1> %broadcast.splat, <8 x i1> %671, <8 x i1> zeroinitializer
  %676 = fcmp reassoc ninf nsz olt <8 x float> %311, %652
  %677 = fcmp reassoc ninf nsz olt <8 x float> %312, %653
  %678 = fcmp reassoc ninf nsz olt <8 x float> %313, %654
  %679 = fcmp reassoc ninf nsz olt <8 x float> %314, %655
  %680 = xor <8 x i1> %676, splat (i1 true)
  %681 = xor <8 x i1> %677, splat (i1 true)
  %682 = xor <8 x i1> %678, splat (i1 true)
  %683 = xor <8 x i1> %679, splat (i1 true)
  %684 = select <8 x i1> %672, <8 x i1> %680, <8 x i1> zeroinitializer
  %685 = select <8 x i1> %673, <8 x i1> %681, <8 x i1> zeroinitializer
  %686 = select <8 x i1> %674, <8 x i1> %682, <8 x i1> zeroinitializer
  %687 = select <8 x i1> %675, <8 x i1> %683, <8 x i1> zeroinitializer
  %688 = fmul reassoc ninf nsz <8 x float> %652, splat (float 4.000000e+00)
  %689 = fmul reassoc ninf nsz <8 x float> %653, splat (float 4.000000e+00)
  %690 = fmul reassoc ninf nsz <8 x float> %654, splat (float 4.000000e+00)
  %691 = fmul reassoc ninf nsz <8 x float> %655, splat (float 4.000000e+00)
  %692 = fdiv reassoc ninf nsz <8 x float> %311, %688
  %693 = fdiv reassoc ninf nsz <8 x float> %312, %689
  %694 = fdiv reassoc ninf nsz <8 x float> %313, %690
  %695 = fdiv reassoc ninf nsz <8 x float> %314, %691
  %696 = fcmp reassoc ninf nsz ogt <8 x float> %692, splat (float 1.000000e+00)
  %697 = fcmp reassoc ninf nsz ogt <8 x float> %693, splat (float 1.000000e+00)
  %698 = fcmp reassoc ninf nsz ogt <8 x float> %694, splat (float 1.000000e+00)
  %699 = fcmp reassoc ninf nsz ogt <8 x float> %695, splat (float 1.000000e+00)
  %700 = select <8 x i1> %696, <8 x float> splat (float 1.000000e+00), <8 x float> %692
  %701 = select <8 x i1> %697, <8 x float> splat (float 1.000000e+00), <8 x float> %693
  %702 = select <8 x i1> %698, <8 x float> splat (float 1.000000e+00), <8 x float> %694
  %703 = select <8 x i1> %699, <8 x float> splat (float 1.000000e+00), <8 x float> %695
  %704 = fmul reassoc ninf nsz <8 x float> %700, splat (float 0x3FD99999A0000000)
  %705 = fmul reassoc ninf nsz <8 x float> %701, splat (float 0x3FD99999A0000000)
  %706 = fmul reassoc ninf nsz <8 x float> %702, splat (float 0x3FD99999A0000000)
  %707 = fmul reassoc ninf nsz <8 x float> %703, splat (float 0x3FD99999A0000000)
  %708 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %704
  %709 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %705
  %710 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %706
  %711 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %707
  %712 = select <8 x i1> %672, <8 x i1> %676, <8 x i1> zeroinitializer
  %713 = select <8 x i1> %673, <8 x i1> %677, <8 x i1> zeroinitializer
  %714 = select <8 x i1> %674, <8 x i1> %678, <8 x i1> zeroinitializer
  %715 = select <8 x i1> %675, <8 x i1> %679, <8 x i1> zeroinitializer
  %716 = fmul reassoc ninf nsz <8 x float> %311, splat (float 0x3FC3333340000000)
  %717 = fmul reassoc ninf nsz <8 x float> %312, splat (float 0x3FC3333340000000)
  %718 = fmul reassoc ninf nsz <8 x float> %313, splat (float 0x3FC3333340000000)
  %719 = fmul reassoc ninf nsz <8 x float> %314, splat (float 0x3FC3333340000000)
  %720 = fdiv reassoc ninf nsz <8 x float> %716, %652
  %721 = fdiv reassoc ninf nsz <8 x float> %717, %653
  %722 = fdiv reassoc ninf nsz <8 x float> %718, %654
  %723 = fdiv reassoc ninf nsz <8 x float> %719, %655
  %724 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %720
  %725 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %721
  %726 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %722
  %727 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %723
  %728 = select <8 x i1> %broadcast.splat, <8 x i1> %664, <8 x i1> zeroinitializer
  %729 = select <8 x i1> %broadcast.splat, <8 x i1> %665, <8 x i1> zeroinitializer
  %730 = select <8 x i1> %broadcast.splat, <8 x i1> %666, <8 x i1> zeroinitializer
  %731 = select <8 x i1> %broadcast.splat, <8 x i1> %667, <8 x i1> zeroinitializer
  %732 = fmul reassoc ninf nsz <8 x float> %652, splat (float 1.500000e+00)
  %733 = fmul reassoc ninf nsz <8 x float> %653, splat (float 1.500000e+00)
  %734 = fmul reassoc ninf nsz <8 x float> %654, splat (float 1.500000e+00)
  %735 = fmul reassoc ninf nsz <8 x float> %655, splat (float 1.500000e+00)
  %736 = fcmp reassoc ninf nsz uge <8 x float> %311, %732
  %737 = fcmp reassoc ninf nsz uge <8 x float> %312, %733
  %738 = fcmp reassoc ninf nsz uge <8 x float> %313, %734
  %739 = fcmp reassoc ninf nsz uge <8 x float> %314, %735
  %740 = select <8 x i1> %728, <8 x i1> %736, <8 x i1> zeroinitializer
  %741 = select <8 x i1> %729, <8 x i1> %737, <8 x i1> zeroinitializer
  %742 = select <8 x i1> %730, <8 x i1> %738, <8 x i1> zeroinitializer
  %743 = select <8 x i1> %731, <8 x i1> %739, <8 x i1> zeroinitializer
  %744 = fsub reassoc ninf nsz <8 x float> %311, %732
  %745 = fsub reassoc ninf nsz <8 x float> %312, %733
  %746 = fsub reassoc ninf nsz <8 x float> %313, %734
  %747 = fsub reassoc ninf nsz <8 x float> %314, %735
  %748 = fdiv reassoc ninf nsz <8 x float> %744, %732
  %749 = fdiv reassoc ninf nsz <8 x float> %745, %733
  %750 = fdiv reassoc ninf nsz <8 x float> %746, %734
  %751 = fdiv reassoc ninf nsz <8 x float> %747, %735
  %752 = fcmp reassoc ninf nsz ogt <8 x float> %748, splat (float 1.000000e+00)
  %753 = fcmp reassoc ninf nsz ogt <8 x float> %749, splat (float 1.000000e+00)
  %754 = fcmp reassoc ninf nsz ogt <8 x float> %750, splat (float 1.000000e+00)
  %755 = fcmp reassoc ninf nsz ogt <8 x float> %751, splat (float 1.000000e+00)
  %756 = select <8 x i1> %752, <8 x float> splat (float 1.000000e+00), <8 x float> %748
  %757 = select <8 x i1> %753, <8 x float> splat (float 1.000000e+00), <8 x float> %749
  %758 = select <8 x i1> %754, <8 x float> splat (float 1.000000e+00), <8 x float> %750
  %759 = select <8 x i1> %755, <8 x float> splat (float 1.000000e+00), <8 x float> %751
  %760 = fmul reassoc ninf nsz <8 x float> %756, splat (float 0x3FC99999A0000000)
  %761 = fmul reassoc ninf nsz <8 x float> %757, splat (float 0x3FC99999A0000000)
  %762 = fmul reassoc ninf nsz <8 x float> %758, splat (float 0x3FC99999A0000000)
  %763 = fmul reassoc ninf nsz <8 x float> %759, splat (float 0x3FC99999A0000000)
  %764 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %760
  %765 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %761
  %766 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %762
  %767 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %763
  %768 = fmul reassoc ninf nsz <8 x float> %311, splat (float 0x3FEE666660000000)
  %769 = fmul reassoc ninf nsz <8 x float> %312, splat (float 0x3FEE666660000000)
  %770 = fmul reassoc ninf nsz <8 x float> %313, splat (float 0x3FEE666660000000)
  %771 = fmul reassoc ninf nsz <8 x float> %314, splat (float 0x3FEE666660000000)
  %772 = fdiv reassoc ninf nsz <8 x float> %768, %732
  %773 = fdiv reassoc ninf nsz <8 x float> %769, %733
  %774 = fdiv reassoc ninf nsz <8 x float> %770, %734
  %775 = fdiv reassoc ninf nsz <8 x float> %771, %735
  %776 = fadd reassoc ninf nsz <8 x float> %772, splat (float 0x3FA99999A0000000)
  %777 = fadd reassoc ninf nsz <8 x float> %773, splat (float 0x3FA99999A0000000)
  %778 = fadd reassoc ninf nsz <8 x float> %774, splat (float 0x3FA99999A0000000)
  %779 = fadd reassoc ninf nsz <8 x float> %775, splat (float 0x3FA99999A0000000)
  %780 = or <8 x i1> %728, %712
  %781 = or <8 x i1> %729, %713
  %782 = or <8 x i1> %730, %714
  %783 = or <8 x i1> %731, %715
  %784 = or <8 x i1> %780, %684
  %785 = or <8 x i1> %781, %685
  %786 = or <8 x i1> %782, %686
  %787 = or <8 x i1> %783, %687
  %788 = or <8 x i1> %784, %206
  %789 = or <8 x i1> %785, %206
  %790 = or <8 x i1> %786, %206
  %791 = or <8 x i1> %787, %206
  %predphi = select <8 x i1> %740, <8 x float> %764, <8 x float> %776
  %predphi336 = select <8 x i1> %712, <8 x float> %724, <8 x float> %predphi
  %predphi337 = select <8 x i1> %684, <8 x float> %708, <8 x float> %predphi336
  %predphi338 = select <8 x i1> %broadcast.splat, <8 x float> %predphi337, <8 x float> splat (float 1.000000e+00)
  %predphi339 = select <8 x i1> %741, <8 x float> %765, <8 x float> %777
  %predphi340 = select <8 x i1> %713, <8 x float> %725, <8 x float> %predphi339
  %predphi341 = select <8 x i1> %685, <8 x float> %709, <8 x float> %predphi340
  %predphi342 = select <8 x i1> %broadcast.splat, <8 x float> %predphi341, <8 x float> splat (float 1.000000e+00)
  %predphi343 = select <8 x i1> %742, <8 x float> %766, <8 x float> %778
  %predphi344 = select <8 x i1> %714, <8 x float> %726, <8 x float> %predphi343
  %predphi345 = select <8 x i1> %686, <8 x float> %710, <8 x float> %predphi344
  %predphi346 = select <8 x i1> %broadcast.splat, <8 x float> %predphi345, <8 x float> splat (float 1.000000e+00)
  %predphi347 = select <8 x i1> %743, <8 x float> %767, <8 x float> %779
  %predphi348 = select <8 x i1> %715, <8 x float> %727, <8 x float> %predphi347
  %predphi349 = select <8 x i1> %687, <8 x float> %711, <8 x float> %predphi348
  %predphi350 = select <8 x i1> %broadcast.splat, <8 x float> %predphi349, <8 x float> splat (float 1.000000e+00)
  %792 = fcmp reassoc ninf nsz ogt <8 x float> %632, splat (float 0x3EB0C6F7A0000000)
  %793 = fcmp reassoc ninf nsz ogt <8 x float> %633, splat (float 0x3EB0C6F7A0000000)
  %794 = fcmp reassoc ninf nsz ogt <8 x float> %634, splat (float 0x3EB0C6F7A0000000)
  %795 = fcmp reassoc ninf nsz ogt <8 x float> %635, splat (float 0x3EB0C6F7A0000000)
  %796 = select <8 x i1> %788, <8 x i1> %792, <8 x i1> zeroinitializer
  %797 = select <8 x i1> %789, <8 x i1> %793, <8 x i1> zeroinitializer
  %798 = select <8 x i1> %790, <8 x i1> %794, <8 x i1> zeroinitializer
  %799 = select <8 x i1> %791, <8 x i1> %795, <8 x i1> zeroinitializer
  %800 = fcmp reassoc ninf nsz ogt <8 x float> %616, splat (float 0x3EB0C6F7A0000000)
  %801 = fcmp reassoc ninf nsz ogt <8 x float> %617, splat (float 0x3EB0C6F7A0000000)
  %802 = fcmp reassoc ninf nsz ogt <8 x float> %618, splat (float 0x3EB0C6F7A0000000)
  %803 = fcmp reassoc ninf nsz ogt <8 x float> %619, splat (float 0x3EB0C6F7A0000000)
  %804 = fcmp reassoc ninf nsz ogt <8 x float> %628, splat (float 0x3EB0C6F7A0000000)
  %805 = fcmp reassoc ninf nsz ogt <8 x float> %629, splat (float 0x3EB0C6F7A0000000)
  %806 = fcmp reassoc ninf nsz ogt <8 x float> %630, splat (float 0x3EB0C6F7A0000000)
  %807 = fcmp reassoc ninf nsz ogt <8 x float> %631, splat (float 0x3EB0C6F7A0000000)
  %808 = select <8 x i1> %800, <8 x i1> %804, <8 x i1> zeroinitializer
  %809 = select <8 x i1> %801, <8 x i1> %805, <8 x i1> zeroinitializer
  %810 = select <8 x i1> %802, <8 x i1> %806, <8 x i1> zeroinitializer
  %811 = select <8 x i1> %803, <8 x i1> %807, <8 x i1> zeroinitializer
  %812 = select <8 x i1> %796, <8 x i1> %808, <8 x i1> zeroinitializer
  %813 = select <8 x i1> %797, <8 x i1> %809, <8 x i1> zeroinitializer
  %814 = select <8 x i1> %798, <8 x i1> %810, <8 x i1> zeroinitializer
  %815 = select <8 x i1> %799, <8 x i1> %811, <8 x i1> zeroinitializer
  %816 = fmul reassoc ninf nsz <8 x float> %556, %412
  %817 = fmul reassoc ninf nsz <8 x float> %557, %413
  %818 = fmul reassoc ninf nsz <8 x float> %558, %414
  %819 = fmul reassoc ninf nsz <8 x float> %559, %415
  %820 = fmul reassoc ninf nsz <8 x float> %604, %460
  %821 = fmul reassoc ninf nsz <8 x float> %605, %461
  %822 = fmul reassoc ninf nsz <8 x float> %606, %462
  %823 = fmul reassoc ninf nsz <8 x float> %607, %463
  %824 = fadd reassoc ninf nsz <8 x float> %820, %816
  %825 = fadd reassoc ninf nsz <8 x float> %821, %817
  %826 = fadd reassoc ninf nsz <8 x float> %822, %818
  %827 = fadd reassoc ninf nsz <8 x float> %823, %819
  %828 = fmul reassoc ninf nsz <8 x float> %628, %616
  %829 = fmul reassoc ninf nsz <8 x float> %629, %617
  %830 = fmul reassoc ninf nsz <8 x float> %630, %618
  %831 = fmul reassoc ninf nsz <8 x float> %631, %619
  %832 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %828)
  %833 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %829)
  %834 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %830)
  %835 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %831)
  %836 = fdiv reassoc ninf nsz <8 x float> %824, %832
  %837 = fdiv reassoc ninf nsz <8 x float> %825, %833
  %838 = fdiv reassoc ninf nsz <8 x float> %826, %834
  %839 = fdiv reassoc ninf nsz <8 x float> %827, %835
  %840 = fcmp reassoc ninf nsz ule <8 x float> %632, %660
  %841 = fcmp reassoc ninf nsz ule <8 x float> %633, %661
  %842 = fcmp reassoc ninf nsz ule <8 x float> %634, %662
  %843 = fcmp reassoc ninf nsz ule <8 x float> %635, %663
  %844 = fcmp reassoc ninf nsz uge <8 x float> %836, splat (float 0x3FC99999A0000000)
  %845 = fcmp reassoc ninf nsz uge <8 x float> %837, splat (float 0x3FC99999A0000000)
  %846 = fcmp reassoc ninf nsz uge <8 x float> %838, splat (float 0x3FC99999A0000000)
  %847 = fcmp reassoc ninf nsz uge <8 x float> %839, splat (float 0x3FC99999A0000000)
  %.not481 = select <8 x i1> %840, <8 x i1> splat (i1 true), <8 x i1> %844
  %.not484 = select <8 x i1> %841, <8 x i1> splat (i1 true), <8 x i1> %845
  %.not487 = select <8 x i1> %842, <8 x i1> splat (i1 true), <8 x i1> %846
  %.not490 = select <8 x i1> %843, <8 x i1> splat (i1 true), <8 x i1> %847
  %848 = select <8 x i1> %812, <8 x i1> %.not481, <8 x i1> zeroinitializer
  %849 = select <8 x i1> %813, <8 x i1> %.not484, <8 x i1> zeroinitializer
  %850 = select <8 x i1> %814, <8 x i1> %.not487, <8 x i1> zeroinitializer
  %851 = select <8 x i1> %815, <8 x i1> %.not490, <8 x i1> zeroinitializer
  %852 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %836, <8 x float> zeroinitializer)
  %853 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %837, <8 x float> zeroinitializer)
  %854 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %838, <8 x float> zeroinitializer)
  %855 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %839, <8 x float> zeroinitializer)
  %856 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %632)
  %857 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %633)
  %858 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %634)
  %859 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %635)
  %860 = fmul reassoc ninf nsz <8 x float> %856, %broadcast.splat352
  %861 = fmul reassoc ninf nsz <8 x float> %857, %broadcast.splat352
  %862 = fmul reassoc ninf nsz <8 x float> %858, %broadcast.splat352
  %863 = fmul reassoc ninf nsz <8 x float> %859, %broadcast.splat352
  %864 = fmul reassoc ninf nsz <8 x float> %860, %852
  %.fr = freeze <8 x float> %864
  %865 = fmul reassoc ninf nsz <8 x float> %861, %853
  %.fr491 = freeze <8 x float> %865
  %866 = fmul reassoc ninf nsz <8 x float> %862, %854
  %.fr492 = freeze <8 x float> %866
  %867 = fmul reassoc ninf nsz <8 x float> %863, %855
  %.fr493 = freeze <8 x float> %867
  %868 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %869 = fcmp reassoc nsz ogt <8 x float> %.fr491, splat (float 3.000000e+00)
  %870 = fcmp reassoc nsz ogt <8 x float> %.fr492, splat (float 3.000000e+00)
  %871 = fcmp reassoc nsz ogt <8 x float> %.fr493, splat (float 3.000000e+00)
  %872 = xor <8 x i1> %868, splat (i1 true)
  %873 = xor <8 x i1> %869, splat (i1 true)
  %874 = xor <8 x i1> %870, splat (i1 true)
  %875 = xor <8 x i1> %871, splat (i1 true)
  %876 = and <8 x i1> %848, %872
  %877 = and <8 x i1> %849, %873
  %878 = and <8 x i1> %850, %874
  %879 = and <8 x i1> %851, %875
  %880 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %881 = fcmp reassoc nsz olt <8 x float> %.fr491, splat (float -3.000000e+00)
  %882 = fcmp reassoc nsz olt <8 x float> %.fr492, splat (float -3.000000e+00)
  %883 = fcmp reassoc nsz olt <8 x float> %.fr493, splat (float -3.000000e+00)
  %884 = xor <8 x i1> %880, splat (i1 true)
  %885 = xor <8 x i1> %881, splat (i1 true)
  %886 = xor <8 x i1> %882, splat (i1 true)
  %887 = xor <8 x i1> %883, splat (i1 true)
  %888 = and <8 x i1> %876, %884
  %889 = and <8 x i1> %877, %885
  %890 = and <8 x i1> %878, %886
  %891 = and <8 x i1> %879, %887
  %892 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %893 = fmul reassoc ninf nsz <8 x float> %.fr491, %.fr491
  %894 = fmul reassoc ninf nsz <8 x float> %.fr492, %.fr492
  %895 = fmul reassoc ninf nsz <8 x float> %.fr493, %.fr493
  %896 = fadd reassoc ninf nsz <8 x float> %892, splat (float 2.700000e+01)
  %897 = fadd reassoc ninf nsz <8 x float> %893, splat (float 2.700000e+01)
  %898 = fadd reassoc ninf nsz <8 x float> %894, splat (float 2.700000e+01)
  %899 = fadd reassoc ninf nsz <8 x float> %895, splat (float 2.700000e+01)
  %900 = fmul reassoc ninf nsz <8 x float> %896, %.fr
  %901 = fmul reassoc ninf nsz <8 x float> %897, %.fr491
  %902 = fmul reassoc ninf nsz <8 x float> %898, %.fr492
  %903 = fmul reassoc ninf nsz <8 x float> %899, %.fr493
  %904 = fmul reassoc ninf nsz <8 x float> %892, splat (float 9.000000e+00)
  %905 = fmul reassoc ninf nsz <8 x float> %893, splat (float 9.000000e+00)
  %906 = fmul reassoc ninf nsz <8 x float> %894, splat (float 9.000000e+00)
  %907 = fmul reassoc ninf nsz <8 x float> %895, splat (float 9.000000e+00)
  %908 = fadd reassoc ninf nsz <8 x float> %904, splat (float 2.700000e+01)
  %909 = fadd reassoc ninf nsz <8 x float> %905, splat (float 2.700000e+01)
  %910 = fadd reassoc ninf nsz <8 x float> %906, splat (float 2.700000e+01)
  %911 = fadd reassoc ninf nsz <8 x float> %907, splat (float 2.700000e+01)
  %912 = fdiv reassoc ninf nsz <8 x float> %900, %908
  %913 = fdiv reassoc ninf nsz <8 x float> %901, %909
  %914 = fdiv reassoc ninf nsz <8 x float> %902, %910
  %915 = fdiv reassoc ninf nsz <8 x float> %903, %911
  %916 = fadd reassoc ninf nsz <8 x float> %912, splat (float 1.000000e+00)
  %917 = fadd reassoc ninf nsz <8 x float> %913, splat (float 1.000000e+00)
  %918 = fadd reassoc ninf nsz <8 x float> %914, splat (float 1.000000e+00)
  %919 = fadd reassoc ninf nsz <8 x float> %915, splat (float 1.000000e+00)
  %920 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %836
  %921 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %837
  %922 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %838
  %923 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %839
  %924 = fmul reassoc ninf nsz <8 x float> %920, %311
  %925 = fmul reassoc ninf nsz <8 x float> %921, %312
  %926 = fmul reassoc ninf nsz <8 x float> %922, %313
  %927 = fmul reassoc ninf nsz <8 x float> %923, %314
  %928 = and <8 x i1> %876, %880
  %929 = and <8 x i1> %877, %881
  %930 = and <8 x i1> %878, %882
  %931 = and <8 x i1> %879, %883
  %932 = and <8 x i1> %848, %868
  %933 = and <8 x i1> %849, %869
  %934 = and <8 x i1> %850, %870
  %935 = and <8 x i1> %851, %871
  %936 = xor <8 x i1> %808, splat (i1 true)
  %937 = xor <8 x i1> %809, splat (i1 true)
  %938 = xor <8 x i1> %810, splat (i1 true)
  %939 = xor <8 x i1> %811, splat (i1 true)
  %940 = select <8 x i1> %796, <8 x i1> %936, <8 x i1> zeroinitializer
  %941 = select <8 x i1> %797, <8 x i1> %937, <8 x i1> zeroinitializer
  %942 = select <8 x i1> %798, <8 x i1> %938, <8 x i1> zeroinitializer
  %943 = select <8 x i1> %799, <8 x i1> %939, <8 x i1> zeroinitializer
  %944 = xor <8 x i1> %792, splat (i1 true)
  %945 = xor <8 x i1> %793, splat (i1 true)
  %946 = xor <8 x i1> %794, splat (i1 true)
  %947 = xor <8 x i1> %795, splat (i1 true)
  %948 = select <8 x i1> %788, <8 x i1> %944, <8 x i1> zeroinitializer
  %949 = select <8 x i1> %789, <8 x i1> %945, <8 x i1> zeroinitializer
  %950 = select <8 x i1> %790, <8 x i1> %946, <8 x i1> zeroinitializer
  %951 = select <8 x i1> %791, <8 x i1> %947, <8 x i1> zeroinitializer
  %952 = select <8 x i1> %848, <8 x i1> splat (i1 true), <8 x i1> %948
  %953 = select <8 x i1> %952, <8 x i1> splat (i1 true), <8 x i1> %940
  %predphi357 = select <8 x i1> %953, <8 x float> %311, <8 x float> %924
  %954 = select <8 x i1> %849, <8 x i1> splat (i1 true), <8 x i1> %949
  %955 = select <8 x i1> %954, <8 x i1> splat (i1 true), <8 x i1> %941
  %predphi362 = select <8 x i1> %955, <8 x float> %312, <8 x float> %925
  %956 = select <8 x i1> %850, <8 x i1> splat (i1 true), <8 x i1> %950
  %957 = select <8 x i1> %956, <8 x i1> splat (i1 true), <8 x i1> %942
  %predphi367 = select <8 x i1> %957, <8 x float> %313, <8 x float> %926
  %958 = select <8 x i1> %851, <8 x i1> splat (i1 true), <8 x i1> %951
  %959 = select <8 x i1> %958, <8 x i1> splat (i1 true), <8 x i1> %943
  %predphi372 = select <8 x i1> %959, <8 x float> %314, <8 x float> %927
  %predphi375 = select <8 x i1> %932, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi376 = select <8 x i1> %888, <8 x float> %916, <8 x float> %predphi375
  %predphi377 = select <8 x i1> %928, <8 x float> zeroinitializer, <8 x float> %predphi376
  %predphi380 = select <8 x i1> %933, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi381 = select <8 x i1> %889, <8 x float> %917, <8 x float> %predphi380
  %predphi382 = select <8 x i1> %929, <8 x float> zeroinitializer, <8 x float> %predphi381
  %predphi385 = select <8 x i1> %934, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi386 = select <8 x i1> %890, <8 x float> %918, <8 x float> %predphi385
  %predphi387 = select <8 x i1> %930, <8 x float> zeroinitializer, <8 x float> %predphi386
  %predphi390 = select <8 x i1> %935, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi391 = select <8 x i1> %891, <8 x float> %919, <8 x float> %predphi390
  %predphi392 = select <8 x i1> %931, <8 x float> zeroinitializer, <8 x float> %predphi391
  %960 = fmul reassoc ninf nsz <8 x float> %predphi377, %predphi338
  %961 = fmul reassoc ninf nsz <8 x float> %predphi382, %predphi342
  %962 = fmul reassoc ninf nsz <8 x float> %predphi387, %predphi346
  %963 = fmul reassoc ninf nsz <8 x float> %predphi392, %predphi350
  %964 = fmul reassoc ninf nsz <8 x float> %960, %predphi357
  %965 = fmul reassoc ninf nsz <8 x float> %961, %predphi362
  %966 = fmul reassoc ninf nsz <8 x float> %962, %predphi367
  %967 = fmul reassoc ninf nsz <8 x float> %963, %predphi372
  %968 = fadd reassoc ninf nsz <8 x float> %964, %vec.phi241
  %969 = fadd reassoc ninf nsz <8 x float> %965, %vec.phi242
  %970 = fadd reassoc ninf nsz <8 x float> %966, %vec.phi243
  %971 = fadd reassoc ninf nsz <8 x float> %967, %vec.phi244
  %972 = fadd reassoc ninf nsz <8 x float> %960, %vec.phi237
  %973 = fadd reassoc ninf nsz <8 x float> %961, %vec.phi238
  %974 = fadd reassoc ninf nsz <8 x float> %962, %vec.phi239
  %975 = fadd reassoc ninf nsz <8 x float> %963, %vec.phi240
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %976 = icmp eq i64 %lsr.iv.next, 0
  br i1 %976, label %middle.block226, label %vector.body235, !llvm.loop !11

middle.block226:                                  ; preds = %vector.body235
  %bin.rdx394 = fadd reassoc ninf nsz <8 x float> %973, %972
  %bin.rdx395 = fadd reassoc ninf nsz <8 x float> %974, %bin.rdx394
  %bin.rdx396 = fadd reassoc ninf nsz <8 x float> %975, %bin.rdx395
  %977 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx396)
  %bin.rdx397 = fadd reassoc ninf nsz <8 x float> %969, %968
  %bin.rdx398 = fadd reassoc ninf nsz <8 x float> %970, %bin.rdx397
  %bin.rdx399 = fadd reassoc ninf nsz <8 x float> %971, %bin.rdx398
  %978 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx399)
  br i1 %cmp.n400, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check407

vec.epilog.iter.check407:                         ; preds = %middle.block226
  br i1 %min.epilog.iters.check409, label %for_loop_body20.us.preheader, label %vec.epilog.ph406

vec.epilog.ph406:                                 ; preds = %vec.epilog.iter.check407, %vector.main.loop.iter.check231
  %bc.resume.val401 = phi i64 [ %n.vec234, %vec.epilog.iter.check407 ], [ 0, %vector.main.loop.iter.check231 ]
  %bc.merge.rdx402 = phi float [ %977, %vec.epilog.iter.check407 ], [ %.065110.us, %vector.main.loop.iter.check231 ]
  %bc.merge.rdx403 = phi float [ %978, %vec.epilog.iter.check407 ], [ %.067109.us, %vector.main.loop.iter.check231 ]
  %979 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx402, i64 0
  %980 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx403, i64 0
  %981 = trunc nuw nsw i64 %bc.resume.val401 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %981, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert422 = insertelement <8 x i32> poison, i32 %215, i64 0
  %broadcast.splat423 = shufflevector <8 x i32> %broadcast.splatinsert422, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert425 = insertelement <8 x i32> poison, i32 %216, i64 0
  %broadcast.splat426 = shufflevector <8 x i32> %broadcast.splatinsert425, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert432 = insertelement <8 x i32> poison, i32 %217, i64 0
  %broadcast.splat433 = shufflevector <8 x i32> %broadcast.splatinsert432, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert436 = insertelement <8 x i32> poison, i32 %218, i64 0
  %broadcast.splat437 = shufflevector <8 x i32> %broadcast.splatinsert436, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert444 = insertelement <8 x i32> poison, i32 %219, i64 0
  %broadcast.splat445 = shufflevector <8 x i32> %broadcast.splatinsert444, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert448 = insertelement <8 x i32> poison, i32 %220, i64 0
  %broadcast.splat449 = shufflevector <8 x i32> %broadcast.splatinsert448, <8 x i32> poison, <8 x i32> zeroinitializer
  %982 = add i64 %209, %bc.resume.val401
  br label %vec.epilog.vector.body414

vec.epilog.vector.body414:                        ; preds = %vec.epilog.vector.body414, %vec.epilog.ph406
  %lsr.iv591 = phi i64 [ %lsr.iv.next592, %vec.epilog.vector.body414 ], [ %982, %vec.epilog.ph406 ]
  %vec.phi416 = phi <8 x float> [ %979, %vec.epilog.ph406 ], [ %1158, %vec.epilog.vector.body414 ]
  %vec.phi417 = phi <8 x float> [ %980, %vec.epilog.ph406 ], [ %1157, %vec.epilog.vector.body414 ]
  %vec.ind418 = phi <8 x i32> [ %induction, %vec.epilog.ph406 ], [ %vec.ind.next419, %vec.epilog.vector.body414 ]
  %983 = shl <8 x i32> %vec.ind418, splat (i32 1)
  %984 = add <8 x i32> %broadcast.splat246, %983
  %985 = add <8 x i32> %broadcast.splat423, %984
  %986 = sext <8 x i32> %985 to <8 x i64>
  %987 = getelementptr float, ptr %175, <8 x i64> %986
  %wide.masked.gather424 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %987, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %988 = add <8 x i32> %984, %broadcast.splat426
  %989 = sext <8 x i32> %988 to <8 x i64>
  %990 = getelementptr float, ptr %106, <8 x i64> %989
  %wide.masked.gather427 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %990, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %991 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather424, %wide.masked.gather427
  %992 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %991)
  %993 = add <8 x i32> %984, splat (i32 1)
  %994 = add <8 x i32> %broadcast.splat423, %993
  %995 = sext <8 x i32> %994 to <8 x i64>
  %996 = getelementptr float, ptr %175, <8 x i64> %995
  %wide.masked.gather428 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %996, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %997 = add <8 x i32> %983, %broadcast.splat263
  %998 = add <8 x i32> %broadcast.splat423, %997
  %999 = sext <8 x i32> %998 to <8 x i64>
  %1000 = getelementptr float, ptr %175, <8 x i64> %999
  %wide.masked.gather431 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1000, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1001 = add <8 x i32> %broadcast.splat433, %993
  %1002 = sext <8 x i32> %1001 to <8 x i64>
  %1003 = getelementptr float, ptr %175, <8 x i64> %1002
  %wide.masked.gather434 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1003, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1004 = add <8 x i32> %broadcast.splat433, %997
  %1005 = sext <8 x i32> %1004 to <8 x i64>
  %1006 = getelementptr float, ptr %175, <8 x i64> %1005
  %wide.masked.gather435 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1006, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1007 = add <8 x i32> %broadcast.splat437, %993
  %1008 = sext <8 x i32> %1007 to <8 x i64>
  %1009 = getelementptr float, ptr %175, <8 x i64> %1008
  %wide.masked.gather438 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1009, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1010 = add <8 x i32> %broadcast.splat437, %997
  %1011 = sext <8 x i32> %1010 to <8 x i64>
  %1012 = getelementptr float, ptr %175, <8 x i64> %1011
  %wide.masked.gather439 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1012, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1013 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather428, %wide.masked.gather434
  %1014 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather431, %wide.masked.gather435
  %1015 = fadd reassoc ninf nsz <8 x float> %1013, %wide.masked.gather438
  %1016 = fadd reassoc ninf nsz <8 x float> %1014, %wide.masked.gather439
  %1017 = fsub reassoc ninf nsz <8 x float> %1015, %1016
  %1018 = fmul reassoc ninf nsz <8 x float> %1017, splat (float 0x3FD5555560000000)
  %1019 = add <8 x i32> %broadcast.splat437, %984
  %1020 = sext <8 x i32> %1019 to <8 x i64>
  %1021 = getelementptr float, ptr %175, <8 x i64> %1020
  %wide.masked.gather440 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1021, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1022 = add <8 x i32> %broadcast.splat433, %984
  %1023 = sext <8 x i32> %1022 to <8 x i64>
  %1024 = getelementptr float, ptr %175, <8 x i64> %1023
  %wide.masked.gather441 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1024, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1025 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather434, %wide.masked.gather435
  %1026 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather438, %1025
  %1027 = fadd reassoc ninf nsz <8 x float> %1026, %wide.masked.gather439
  %1028 = fadd reassoc ninf nsz <8 x float> %1027, %wide.masked.gather440
  %1029 = fsub reassoc ninf nsz <8 x float> %1028, %wide.masked.gather441
  %1030 = fmul reassoc ninf nsz <8 x float> %1029, splat (float 0x3FD5555560000000)
  %1031 = add <8 x i32> %993, %broadcast.splat426
  %1032 = sext <8 x i32> %1031 to <8 x i64>
  %1033 = getelementptr float, ptr %106, <8 x i64> %1032
  %wide.masked.gather442 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1033, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1034 = add <8 x i32> %997, %broadcast.splat426
  %1035 = sext <8 x i32> %1034 to <8 x i64>
  %1036 = getelementptr float, ptr %106, <8 x i64> %1035
  %wide.masked.gather443 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1036, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1037 = add <8 x i32> %993, %broadcast.splat445
  %1038 = sext <8 x i32> %1037 to <8 x i64>
  %1039 = getelementptr float, ptr %106, <8 x i64> %1038
  %wide.masked.gather446 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1039, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1040 = add <8 x i32> %997, %broadcast.splat445
  %1041 = sext <8 x i32> %1040 to <8 x i64>
  %1042 = getelementptr float, ptr %106, <8 x i64> %1041
  %wide.masked.gather447 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1042, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1043 = add <8 x i32> %993, %broadcast.splat449
  %1044 = sext <8 x i32> %1043 to <8 x i64>
  %1045 = getelementptr float, ptr %106, <8 x i64> %1044
  %wide.masked.gather450 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1045, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1046 = add <8 x i32> %997, %broadcast.splat449
  %1047 = sext <8 x i32> %1046 to <8 x i64>
  %1048 = getelementptr float, ptr %106, <8 x i64> %1047
  %wide.masked.gather451 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1048, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1049 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather442, %wide.masked.gather446
  %1050 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather443, %wide.masked.gather447
  %1051 = fadd reassoc ninf nsz <8 x float> %1049, %wide.masked.gather450
  %1052 = fadd reassoc ninf nsz <8 x float> %1050, %wide.masked.gather451
  %1053 = fsub reassoc ninf nsz <8 x float> %1051, %1052
  %1054 = fmul reassoc ninf nsz <8 x float> %1053, splat (float 0x3FD5555560000000)
  %1055 = add <8 x i32> %984, %broadcast.splat449
  %1056 = sext <8 x i32> %1055 to <8 x i64>
  %1057 = getelementptr float, ptr %106, <8 x i64> %1056
  %wide.masked.gather452 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1057, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1058 = add <8 x i32> %984, %broadcast.splat445
  %1059 = sext <8 x i32> %1058 to <8 x i64>
  %1060 = getelementptr float, ptr %106, <8 x i64> %1059
  %wide.masked.gather453 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %1060, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %1061 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather446, %wide.masked.gather447
  %1062 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather450, %1061
  %1063 = fadd reassoc ninf nsz <8 x float> %1062, %wide.masked.gather451
  %1064 = fadd reassoc ninf nsz <8 x float> %1063, %wide.masked.gather452
  %1065 = fsub reassoc ninf nsz <8 x float> %1064, %wide.masked.gather453
  %1066 = fmul reassoc ninf nsz <8 x float> %1065, splat (float 0x3FD5555560000000)
  %1067 = fmul reassoc ninf nsz <8 x float> %1018, %1018
  %1068 = fmul reassoc ninf nsz <8 x float> %1030, %1030
  %1069 = fadd reassoc ninf nsz <8 x float> %1068, %1067
  %1070 = fmul reassoc ninf nsz <8 x float> %1054, %1054
  %1071 = fmul reassoc ninf nsz <8 x float> %1066, %1066
  %1072 = fadd reassoc ninf nsz <8 x float> %1071, %1070
  %1073 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %1069, <8 x float> %1072)
  %1074 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather427, splat (float -2.000000e+00)
  %1075 = fadd reassoc ninf nsz <8 x float> %1074, splat (float 3.000000e+00)
  %1076 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %1075, <8 x float> splat (float 3.000000e+00))
  %1077 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %1076, <8 x float> splat (float 1.000000e+00))
  %1078 = fmul reassoc ninf nsz <8 x float> %1077, %broadcast.splat333
  %1079 = fmul reassoc ninf nsz <8 x float> %1077, %1077
  %1080 = fmul reassoc ninf nsz <8 x float> %1079, %broadcast.splat335
  %1081 = fcmp reassoc ninf nsz olt <8 x float> %1073, %1080
  %1082 = xor <8 x i1> %1081, splat (i1 true)
  %1083 = select <8 x i1> %broadcast.splat, <8 x i1> %1082, <8 x i1> zeroinitializer
  %1084 = fcmp reassoc ninf nsz olt <8 x float> %992, %1078
  %1085 = xor <8 x i1> %1084, splat (i1 true)
  %1086 = select <8 x i1> %1083, <8 x i1> %1085, <8 x i1> zeroinitializer
  %1087 = fmul reassoc ninf nsz <8 x float> %1078, splat (float 4.000000e+00)
  %1088 = fdiv reassoc ninf nsz <8 x float> %992, %1087
  %1089 = fcmp reassoc ninf nsz ogt <8 x float> %1088, splat (float 1.000000e+00)
  %1090 = select <8 x i1> %1089, <8 x float> splat (float 1.000000e+00), <8 x float> %1088
  %1091 = fmul reassoc ninf nsz <8 x float> %1090, splat (float 0x3FD99999A0000000)
  %1092 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %1091
  %1093 = select <8 x i1> %1083, <8 x i1> %1084, <8 x i1> zeroinitializer
  %1094 = fmul reassoc ninf nsz <8 x float> %992, splat (float 0x3FC3333340000000)
  %1095 = fdiv reassoc ninf nsz <8 x float> %1094, %1078
  %1096 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %1095
  %1097 = select <8 x i1> %broadcast.splat, <8 x i1> %1081, <8 x i1> zeroinitializer
  %1098 = fmul reassoc ninf nsz <8 x float> %1078, splat (float 1.500000e+00)
  %1099 = fcmp reassoc ninf nsz uge <8 x float> %992, %1098
  %1100 = select <8 x i1> %1097, <8 x i1> %1099, <8 x i1> zeroinitializer
  %1101 = fsub reassoc ninf nsz <8 x float> %992, %1098
  %1102 = fdiv reassoc ninf nsz <8 x float> %1101, %1098
  %1103 = fcmp reassoc ninf nsz ogt <8 x float> %1102, splat (float 1.000000e+00)
  %1104 = select <8 x i1> %1103, <8 x float> splat (float 1.000000e+00), <8 x float> %1102
  %1105 = fmul reassoc ninf nsz <8 x float> %1104, splat (float 0x3FC99999A0000000)
  %1106 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %1105
  %1107 = fmul reassoc ninf nsz <8 x float> %992, splat (float 0x3FEE666660000000)
  %1108 = fdiv reassoc ninf nsz <8 x float> %1107, %1098
  %1109 = fadd reassoc ninf nsz <8 x float> %1108, splat (float 0x3FA99999A0000000)
  %1110 = or <8 x i1> %1093, %206
  %1111 = or <8 x i1> %1110, %1097
  %1112 = or <8 x i1> %1111, %1086
  %predphi458 = select <8 x i1> %1100, <8 x float> %1106, <8 x float> %1109
  %predphi459 = select <8 x i1> %1093, <8 x float> %1096, <8 x float> %predphi458
  %predphi460 = select <8 x i1> %1086, <8 x float> %1092, <8 x float> %predphi459
  %predphi461 = select <8 x i1> %broadcast.splat, <8 x float> %predphi460, <8 x float> splat (float 1.000000e+00)
  %1113 = fcmp reassoc ninf nsz ogt <8 x float> %1073, splat (float 0x3EB0C6F7A0000000)
  %1114 = select <8 x i1> %1112, <8 x i1> %1113, <8 x i1> zeroinitializer
  %1115 = fcmp reassoc ninf nsz ogt <8 x float> %1069, splat (float 0x3EB0C6F7A0000000)
  %1116 = fcmp reassoc ninf nsz ogt <8 x float> %1072, splat (float 0x3EB0C6F7A0000000)
  %1117 = select <8 x i1> %1115, <8 x i1> %1116, <8 x i1> zeroinitializer
  %1118 = select <8 x i1> %1114, <8 x i1> %1117, <8 x i1> zeroinitializer
  %1119 = fmul reassoc ninf nsz <8 x float> %1054, %1018
  %1120 = fmul reassoc ninf nsz <8 x float> %1066, %1030
  %1121 = fadd reassoc ninf nsz <8 x float> %1120, %1119
  %1122 = fmul reassoc ninf nsz <8 x float> %1072, %1069
  %1123 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %1122)
  %1124 = fdiv reassoc ninf nsz <8 x float> %1121, %1123
  %1125 = fcmp reassoc ninf nsz ule <8 x float> %1073, %1080
  %1126 = fcmp reassoc ninf nsz uge <8 x float> %1124, splat (float 0x3FC99999A0000000)
  %.not496 = select <8 x i1> %1125, <8 x i1> splat (i1 true), <8 x i1> %1126
  %1127 = select <8 x i1> %1118, <8 x i1> %.not496, <8 x i1> zeroinitializer
  %1128 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %1124, <8 x float> zeroinitializer)
  %1129 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %1073)
  %1130 = fmul reassoc ninf nsz <8 x float> %1129, %broadcast.splat352
  %1131 = fmul reassoc ninf nsz <8 x float> %1130, %1128
  %.fr497 = freeze <8 x float> %1131
  %1132 = fcmp reassoc nsz ogt <8 x float> %.fr497, splat (float 3.000000e+00)
  %1133 = xor <8 x i1> %1132, splat (i1 true)
  %1134 = and <8 x i1> %1127, %1133
  %1135 = fcmp reassoc nsz olt <8 x float> %.fr497, splat (float -3.000000e+00)
  %1136 = xor <8 x i1> %1135, splat (i1 true)
  %1137 = and <8 x i1> %1134, %1136
  %1138 = fmul reassoc ninf nsz <8 x float> %.fr497, %.fr497
  %1139 = fadd reassoc ninf nsz <8 x float> %1138, splat (float 2.700000e+01)
  %1140 = fmul reassoc ninf nsz <8 x float> %1139, %.fr497
  %1141 = fmul reassoc ninf nsz <8 x float> %1138, splat (float 9.000000e+00)
  %1142 = fadd reassoc ninf nsz <8 x float> %1141, splat (float 2.700000e+01)
  %1143 = fdiv reassoc ninf nsz <8 x float> %1140, %1142
  %1144 = fadd reassoc ninf nsz <8 x float> %1143, splat (float 1.000000e+00)
  %1145 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %1124
  %1146 = fmul reassoc ninf nsz <8 x float> %1145, %992
  %1147 = and <8 x i1> %1134, %1135
  %1148 = and <8 x i1> %1127, %1132
  %1149 = xor <8 x i1> %1117, splat (i1 true)
  %1150 = select <8 x i1> %1114, <8 x i1> %1149, <8 x i1> zeroinitializer
  %1151 = xor <8 x i1> %1113, splat (i1 true)
  %1152 = select <8 x i1> %1112, <8 x i1> %1151, <8 x i1> zeroinitializer
  %1153 = select <8 x i1> %1127, <8 x i1> splat (i1 true), <8 x i1> %1152
  %1154 = select <8 x i1> %1153, <8 x i1> splat (i1 true), <8 x i1> %1150
  %predphi468 = select <8 x i1> %1154, <8 x float> %992, <8 x float> %1146
  %predphi471 = select <8 x i1> %1148, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi472 = select <8 x i1> %1137, <8 x float> %1144, <8 x float> %predphi471
  %predphi473 = select <8 x i1> %1147, <8 x float> zeroinitializer, <8 x float> %predphi472
  %1155 = fmul reassoc ninf nsz <8 x float> %predphi473, %predphi461
  %1156 = fmul reassoc ninf nsz <8 x float> %1155, %predphi468
  %1157 = fadd reassoc ninf nsz <8 x float> %1156, %vec.phi417
  %1158 = fadd reassoc ninf nsz <8 x float> %1155, %vec.phi416
  %vec.ind.next419 = add <8 x i32> %vec.ind418, splat (i32 8)
  %lsr.iv.next592 = add i64 %lsr.iv591, 8
  %1159 = icmp eq i64 %lsr.iv.next592, 0
  br i1 %1159, label %vec.epilog.middle.block404, label %vec.epilog.vector.body414, !llvm.loop !14

vec.epilog.middle.block404:                       ; preds = %vec.epilog.vector.body414
  %1160 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1158)
  %1161 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1157)
  br i1 %cmp.n475, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block404, %vec.epilog.iter.check407, %vector.scevcheck174, %iter.check229
  %indvars.iv.ph = phi i64 [ %n.vec234, %vec.epilog.iter.check407 ], [ 0, %iter.check229 ], [ 0, %vector.scevcheck174 ], [ %n.vec411, %vec.epilog.middle.block404 ]
  %.166106.us.ph = phi float [ %977, %vec.epilog.iter.check407 ], [ %.065110.us, %iter.check229 ], [ %.065110.us, %vector.scevcheck174 ], [ %1160, %vec.epilog.middle.block404 ]
  %.168105.us.ph = phi float [ %978, %vec.epilog.iter.check407 ], [ %.067109.us, %iter.check229 ], [ %.067109.us, %vector.scevcheck174 ], [ %1161, %vec.epilog.middle.block404 ]
  %1162 = trunc i64 %indvars.iv.ph to i32
  %1163 = shl nuw i32 %1162, 1
  %1164 = add i64 %210, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv617 = phi i64 [ %1164, %for_loop_body20.us.preheader ], [ %lsr.iv.next618, %after_if50.us ]
  %lsr.iv615 = phi i32 [ %lsr.iv613, %for_loop_body20.us.preheader ], [ %lsr.iv.next616, %after_if50.us ]
  %lsr.iv611 = phi i32 [ %lsr.iv609, %for_loop_body20.us.preheader ], [ %lsr.iv.next612, %after_if50.us ]
  %lsr.iv607 = phi i32 [ %lsr.iv605, %for_loop_body20.us.preheader ], [ %lsr.iv.next608, %after_if50.us ]
  %lsr.iv603 = phi i32 [ %lsr.iv601, %for_loop_body20.us.preheader ], [ %lsr.iv.next604, %after_if50.us ]
  %lsr.iv599 = phi i32 [ %lsr.iv597, %for_loop_body20.us.preheader ], [ %lsr.iv.next600, %after_if50.us ]
  %lsr.iv595 = phi i32 [ %lsr.iv593, %for_loop_body20.us.preheader ], [ %lsr.iv.next596, %after_if50.us ]
  %.166106.us = phi float [ %1325, %after_if50.us ], [ %.166106.us.ph, %for_loop_body20.us.preheader ]
  %.168105.us = phi float [ %1324, %after_if50.us ], [ %.168105.us.ph, %for_loop_body20.us.preheader ]
  %1165 = add i32 %1163, %lsr.iv615
  %1166 = add i32 %1165, 1
  %1167 = sext i32 %1166 to i64
  %1168 = getelementptr float, ptr %175, i64 %1167
  %1169 = load float, ptr %1168, align 4
  %1170 = add i32 %1163, %lsr.iv611
  %1171 = add i32 %1170, 1
  %1172 = sext i32 %1171 to i64
  %1173 = getelementptr float, ptr %106, i64 %1172
  %1174 = load float, ptr %1173, align 4
  %1175 = fsub reassoc ninf nsz float %1169, %1174
  %1176 = tail call noundef float @llvm.fabs.f32(float %1175)
  %1177 = add i32 %1165, 2
  %1178 = sext i32 %1177 to i64
  %1179 = getelementptr float, ptr %175, i64 %1178
  %1180 = load float, ptr %1179, align 4
  %1181 = sext i32 %1165 to i64
  %1182 = getelementptr float, ptr %175, i64 %1181
  %1183 = load float, ptr %1182, align 4
  %1184 = add i32 %1163, %lsr.iv603
  %1185 = add i32 %1184, 2
  %1186 = sext i32 %1185 to i64
  %1187 = getelementptr float, ptr %175, i64 %1186
  %1188 = load float, ptr %1187, align 4
  %1189 = sext i32 %1184 to i64
  %1190 = getelementptr float, ptr %175, i64 %1189
  %1191 = load float, ptr %1190, align 4
  %1192 = add i32 %1163, %lsr.iv607
  %1193 = add i32 %1192, 2
  %1194 = sext i32 %1193 to i64
  %1195 = getelementptr float, ptr %175, i64 %1194
  %1196 = load float, ptr %1195, align 4
  %1197 = sext i32 %1192 to i64
  %1198 = getelementptr float, ptr %175, i64 %1197
  %1199 = load float, ptr %1198, align 4
  %1200 = fadd reassoc ninf nsz float %1180, %1188
  %1201 = fadd reassoc ninf nsz float %1183, %1191
  %1202 = fadd reassoc ninf nsz float %1200, %1196
  %1203 = fadd reassoc ninf nsz float %1201, %1199
  %1204 = fsub reassoc ninf nsz float %1202, %1203
  %1205 = fmul reassoc ninf nsz float %1204, 0x3FD5555560000000
  %1206 = add i32 %1192, 1
  %1207 = sext i32 %1206 to i64
  %1208 = getelementptr float, ptr %175, i64 %1207
  %1209 = load float, ptr %1208, align 4
  %1210 = add i32 %1184, 1
  %1211 = sext i32 %1210 to i64
  %1212 = getelementptr float, ptr %175, i64 %1211
  %1213 = load float, ptr %1212, align 4
  %1214 = fadd reassoc ninf nsz float %1188, %1191
  %1215 = fsub reassoc ninf nsz float %1196, %1214
  %1216 = fadd reassoc ninf nsz float %1215, %1199
  %1217 = fadd reassoc ninf nsz float %1216, %1209
  %1218 = fsub reassoc ninf nsz float %1217, %1213
  %1219 = fmul reassoc ninf nsz float %1218, 0x3FD5555560000000
  %1220 = add i32 %1170, 2
  %1221 = sext i32 %1220 to i64
  %1222 = getelementptr float, ptr %106, i64 %1221
  %1223 = load float, ptr %1222, align 4
  %1224 = sext i32 %1170 to i64
  %1225 = getelementptr float, ptr %106, i64 %1224
  %1226 = load float, ptr %1225, align 4
  %1227 = add i32 %1163, %lsr.iv595
  %1228 = add i32 %1227, 2
  %1229 = sext i32 %1228 to i64
  %1230 = getelementptr float, ptr %106, i64 %1229
  %1231 = load float, ptr %1230, align 4
  %1232 = sext i32 %1227 to i64
  %1233 = getelementptr float, ptr %106, i64 %1232
  %1234 = load float, ptr %1233, align 4
  %1235 = add i32 %1163, %lsr.iv599
  %1236 = add i32 %1235, 2
  %1237 = sext i32 %1236 to i64
  %1238 = getelementptr float, ptr %106, i64 %1237
  %1239 = load float, ptr %1238, align 4
  %1240 = sext i32 %1235 to i64
  %1241 = getelementptr float, ptr %106, i64 %1240
  %1242 = load float, ptr %1241, align 4
  %1243 = fadd reassoc ninf nsz float %1223, %1231
  %1244 = fadd reassoc ninf nsz float %1226, %1234
  %1245 = fadd reassoc ninf nsz float %1243, %1239
  %1246 = fadd reassoc ninf nsz float %1244, %1242
  %1247 = fsub reassoc ninf nsz float %1245, %1246
  %1248 = fmul reassoc ninf nsz float %1247, 0x3FD5555560000000
  %1249 = add i32 %1235, 1
  %1250 = sext i32 %1249 to i64
  %1251 = getelementptr float, ptr %106, i64 %1250
  %1252 = load float, ptr %1251, align 4
  %1253 = add i32 %1227, 1
  %1254 = sext i32 %1253 to i64
  %1255 = getelementptr float, ptr %106, i64 %1254
  %1256 = load float, ptr %1255, align 4
  %1257 = fadd reassoc ninf nsz float %1231, %1234
  %1258 = fsub reassoc ninf nsz float %1239, %1257
  %1259 = fadd reassoc ninf nsz float %1258, %1242
  %1260 = fadd reassoc ninf nsz float %1259, %1252
  %1261 = fsub reassoc ninf nsz float %1260, %1256
  %1262 = fmul reassoc ninf nsz float %1261, 0x3FD5555560000000
  %1263 = fmul reassoc ninf nsz float %1205, %1205
  %1264 = fmul reassoc ninf nsz float %1219, %1219
  %1265 = fadd reassoc ninf nsz float %1264, %1263
  %1266 = fmul reassoc ninf nsz float %1248, %1248
  %1267 = fmul reassoc ninf nsz float %1262, %1262
  %1268 = fadd reassoc ninf nsz float %1267, %1266
  %1269 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1265, float %1268)
  %factor.us = fmul reassoc ninf nsz float %1174, -2.000000e+00
  %1270 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %1271 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1270, float 3.000000e+00)
  %1272 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1271, float 1.000000e+00)
  %1273 = fmul reassoc ninf nsz float %1272, %162
  %1274 = fmul reassoc ninf nsz float %1272, %1272
  %1275 = fmul reassoc ninf nsz float %1274, %172
  br i1 %163, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %1276 = fcmp reassoc ninf nsz olt float %1269, %1275
  br i1 %1276, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %1277 = fcmp reassoc ninf nsz olt float %1176, %1273
  br i1 %1277, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %1278 = fmul reassoc ninf nsz float %1273, 4.000000e+00
  %1279 = fdiv reassoc ninf nsz float %1176, %1278
  %1280 = fcmp reassoc ninf nsz ogt float %1279, 1.000000e+00
  %spec.store.select1.us = select i1 %1280, float 1.000000e+00, float %1279
  %1281 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %1282 = fsub reassoc ninf nsz float 0x3FE6666680000000, %1281
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %1283 = fmul reassoc ninf nsz float %1176, 0x3FC3333340000000
  %1284 = fdiv reassoc ninf nsz float %1283, %1273
  %1285 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %1284
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %1286 = fmul reassoc ninf nsz float %1273, 1.500000e+00
  %1287 = fcmp reassoc ninf nsz olt float %1176, %1286
  br i1 %1287, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %1288 = fsub reassoc ninf nsz float %1176, %1286
  %1289 = fdiv reassoc ninf nsz float %1288, %1286
  %1290 = fcmp reassoc ninf nsz ogt float %1289, 1.000000e+00
  %spec.store.select.us = select i1 %1290, float 1.000000e+00, float %1289
  %1291 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %1292 = fsub reassoc ninf nsz float 1.000000e+00, %1291
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %1293 = fmul reassoc ninf nsz float %1176, 0x3FEE666660000000
  %1294 = fdiv reassoc ninf nsz float %1293, %1286
  %1295 = fadd reassoc ninf nsz float %1294, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.061.us = phi float [ %1295, %true_block30.us ], [ %1292, %false_block31.us ], [ %1285, %true_block36.us ], [ %1282, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %1296 = fcmp reassoc ninf nsz ogt float %1269, 0x3EB0C6F7A0000000
  br i1 %1296, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %1297 = fcmp reassoc ninf nsz ogt float %1265, 0x3EB0C6F7A0000000
  %1298 = fcmp reassoc ninf nsz ogt float %1268, 0x3EB0C6F7A0000000
  %.056.us = select i1 %1297, i1 %1298, i1 false
  br i1 %.056.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %1299 = fmul reassoc ninf nsz float %1248, %1205
  %1300 = fmul reassoc ninf nsz float %1262, %1219
  %1301 = fadd reassoc ninf nsz float %1300, %1299
  %1302 = fmul reassoc ninf nsz float %1268, %1265
  %1303 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1302)
  %1304 = fdiv reassoc ninf nsz float %1301, %1303
  %1305 = fcmp reassoc ninf nsz ogt float %1269, %1275
  %1306 = fcmp reassoc ninf nsz olt float %1304, 0x3FC99999A0000000
  %.055.us = select i1 %1305, i1 %1306, i1 false
  br i1 %.055.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %1307 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1304, float 0.000000e+00)
  %1308 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1269)
  %1309 = fmul reassoc ninf nsz float %1308, %160
  %1310 = fmul reassoc ninf nsz float %1309, %1307
  %1311 = fcmp reassoc ninf nsz ogt float %1310, 3.000000e+00
  br i1 %1311, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %1312 = fcmp reassoc ninf nsz olt float %1310, -3.000000e+00
  br i1 %1312, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %1313 = fmul reassoc ninf nsz float %1310, %1310
  %1314 = fadd reassoc ninf nsz float %1313, 2.700000e+01
  %1315 = fmul reassoc ninf nsz float %1314, %1310
  %1316 = fmul reassoc ninf nsz float %1313, 9.000000e+00
  %1317 = fadd reassoc ninf nsz float %1316, 2.700000e+01
  %1318 = fdiv reassoc ninf nsz float %1315, %1317
  %1319 = fadd reassoc ninf nsz float %1318, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %1320 = fsub reassoc ninf nsz float 1.500000e+00, %1304
  %1321 = fmul reassoc ninf nsz float %1320, %1176
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.062.us = phi float [ %1321, %true_block54.us ], [ %1176, %true_block42.us ], [ %1176, %after_if26.us ], [ %1176, %false_block55.us ], [ %1176, %false_block61.us ], [ %1176, %false_block58.us ]
  %.058.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %1319, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %1322 = fmul reassoc ninf nsz float %.058.us, %.061.us
  %1323 = fmul reassoc ninf nsz float %1322, %.062.us
  %1324 = fadd reassoc ninf nsz float %1323, %.168105.us
  %1325 = fadd reassoc ninf nsz float %1322, %.166106.us
  %lsr.iv.next596 = add i32 %lsr.iv595, 2
  %lsr.iv.next600 = add i32 %lsr.iv599, 2
  %lsr.iv.next604 = add i32 %lsr.iv603, 2
  %lsr.iv.next608 = add i32 %lsr.iv607, 2
  %lsr.iv.next612 = add i32 %lsr.iv611, 2
  %lsr.iv.next616 = add i32 %lsr.iv615, 2
  %lsr.iv.next618 = add i64 %lsr.iv617, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next618, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block404, %middle.block226
  %.lcssa150 = phi float [ %978, %middle.block226 ], [ %1161, %vec.epilog.middle.block404 ], [ %1324, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %977, %middle.block226 ], [ %1160, %vec.epilog.middle.block404 ], [ %1325, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %1326 = add nuw nsw i32 %.064111.us, 1
  %lsr.iv.next594 = add i32 %lsr.iv593, %183
  %lsr.iv.next598 = add i32 %lsr.iv597, %183
  %lsr.iv.next602 = add i32 %lsr.iv601, %180
  %lsr.iv.next606 = add i32 %lsr.iv605, %180
  %lsr.iv.next610 = add i32 %lsr.iv609, %183
  %lsr.iv.next614 = add i32 %lsr.iv613, %180
  %exitcond133.not = icmp eq i32 %1326, %164
  br i1 %exitcond133.not, label %after_for18, label %iter.check229

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %1327 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %1327, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %for_loop_body16.lr.ph, %true_block13
  %1328 = getelementptr i8, ptr %75, i64 4
  %1329 = getelementptr i8, ptr %75, i64 8
  %1330 = load ptr, ptr %1329, align 8
  %1331 = load i32, ptr %1328, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %66, i32 1)
  %smax139 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  %wide.trip.count137 = zext i32 %smax to i64
  %1332 = add nsw i64 %wide.trip.count137, -1
  %1333 = mul i32 %54, %1331
  %1334 = add i32 %58, %1333
  %min.iters.check = icmp slt i32 %66, 4
  %1335 = trunc nsw i64 %1332 to i32
  %invariant.op587 = add i32 %1334, %1335
  %invariant.op589 = add i32 %115, %1335
  %1336 = icmp ugt i64 %1332, 4294967295
  %min.iters.check152 = icmp slt i32 %66, 32
  %n.vec = and i64 %wide.trip.count137, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count137
  %n.vec.remaining = and i64 %wide.trip.count137, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec166 = and i64 %wide.trip.count137, 2147483644
  %cmp.n172 = icmp eq i64 %n.vec166, %wide.trip.count137
  %xtraiter = and i64 %wide.trip.count137, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %1337 = lshr i64 %wide.trip.count137, 2
  %1338 = mul nsw i64 %1337, -4
  %1339 = zext i32 %115 to i64
  %1340 = zext i32 %108 to i64
  %1341 = zext i32 %1334 to i64
  %1342 = zext i32 %1331 to i64
  %1343 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %lsr.iv637 = phi i64 [ %lsr.iv.next638, %for_loop_test73.after_for72_crit_edge.us ], [ %1341, %for_loop_body66.lr.ph.split.us ]
  %lsr.iv635 = phi i64 [ %lsr.iv.next636, %for_loop_test73.after_for72_crit_edge.us ], [ %1339, %for_loop_body66.lr.ph.split.us ]
  %.051120.us = phi i32 [ 0, %for_loop_body66.lr.ph.split.us ], [ %1448, %for_loop_test73.after_for72_crit_edge.us ]
  %.052119.us = phi float [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ], [ %.lcssa151, %for_loop_test73.after_for72_crit_edge.us ]
  %lsr652 = trunc i64 %lsr.iv637 to i32
  %lsr650 = trunc i64 %lsr.iv635 to i32
  br i1 %min.iters.check, label %for_loop_body70.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %1344 = mul i32 %108, %.051120.us
  %1345 = add i32 %115, %1344
  %1346 = mul i32 %1331, %.051120.us
  %1347 = add i32 %1334, %1346
  %.reass588 = add i32 %1346, %invariant.op587
  %1348 = icmp slt i32 %.reass588, %1347
  %.reass590 = add i32 %1344, %invariant.op589
  %1349 = icmp slt i32 %.reass590, %1345
  %1350 = or i1 %1349, %1336
  %1351 = or i1 %1348, %1350
  br i1 %1351, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check152, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %1352 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.052119.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv627 = phi i32 [ %lsr.iv.next628, %vector.body ], [ %lsr650, %vector.ph ]
  %lsr.iv623 = phi i32 [ %lsr.iv.next624, %vector.body ], [ %lsr652, %vector.ph ]
  %lsr.iv619 = phi i64 [ %lsr.iv.next620, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %1352, %vector.ph ], [ %1371, %vector.body ]
  %vec.phi153 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1372, %vector.body ]
  %vec.phi154 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1373, %vector.body ]
  %vec.phi155 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1374, %vector.body ]
  %1353 = sext i32 %lsr.iv623 to i64
  %1354 = getelementptr float, ptr %1330, i64 %1353
  %1355 = getelementptr i8, ptr %1354, i64 32
  %1356 = getelementptr i8, ptr %1354, i64 64
  %1357 = getelementptr i8, ptr %1354, i64 96
  %wide.load = load <8 x float>, ptr %1354, align 4
  %wide.load156 = load <8 x float>, ptr %1355, align 4
  %wide.load157 = load <8 x float>, ptr %1356, align 4
  %wide.load158 = load <8 x float>, ptr %1357, align 4
  %1358 = sext i32 %lsr.iv627 to i64
  %1359 = getelementptr float, ptr %106, i64 %1358
  %1360 = getelementptr i8, ptr %1359, i64 32
  %1361 = getelementptr i8, ptr %1359, i64 64
  %1362 = getelementptr i8, ptr %1359, i64 96
  %wide.load159 = load <8 x float>, ptr %1359, align 4
  %wide.load160 = load <8 x float>, ptr %1360, align 4
  %wide.load161 = load <8 x float>, ptr %1361, align 4
  %wide.load162 = load <8 x float>, ptr %1362, align 4
  %1363 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load159
  %1364 = fsub reassoc ninf nsz <8 x float> %wide.load156, %wide.load160
  %1365 = fsub reassoc ninf nsz <8 x float> %wide.load157, %wide.load161
  %1366 = fsub reassoc ninf nsz <8 x float> %wide.load158, %wide.load162
  %1367 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1363)
  %1368 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1364)
  %1369 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1365)
  %1370 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1366)
  %1371 = fadd reassoc ninf nsz <8 x float> %1367, %vec.phi
  %1372 = fadd reassoc ninf nsz <8 x float> %1368, %vec.phi153
  %1373 = fadd reassoc ninf nsz <8 x float> %1369, %vec.phi154
  %1374 = fadd reassoc ninf nsz <8 x float> %1370, %vec.phi155
  %lsr.iv.next620 = add nsw i64 %lsr.iv619, -32
  %lsr.iv.next624 = add i32 %lsr.iv623, 32
  %lsr.iv.next628 = add i32 %lsr.iv627, 32
  %1375 = icmp eq i64 %lsr.iv.next620, 0
  br i1 %1375, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %1372, %1371
  %bin.rdx163 = fadd reassoc ninf nsz <8 x float> %1373, %bin.rdx
  %bin.rdx164 = fadd reassoc ninf nsz <8 x float> %1374, %bin.rdx163
  %1376 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx164)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %1376, %vec.epilog.iter.check ], [ %.052119.us, %vector.main.loop.iter.check ]
  %1377 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %1378 = add i64 %1338, %vec.epilog.resume.val
  %1379 = trunc i64 %vec.epilog.resume.val to i32
  %1380 = add i32 %lsr652, %1379
  %1381 = add i32 %lsr650, %1379
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv633 = phi i32 [ %lsr.iv.next634, %vec.epilog.vector.body ], [ %1381, %vec.epilog.ph ]
  %lsr.iv631 = phi i32 [ %lsr.iv.next632, %vec.epilog.vector.body ], [ %1380, %vec.epilog.ph ]
  %lsr.iv629 = phi i64 [ %lsr.iv.next630, %vec.epilog.vector.body ], [ %1378, %vec.epilog.ph ]
  %vec.phi168 = phi <4 x float> [ %1377, %vec.epilog.ph ], [ %1388, %vec.epilog.vector.body ]
  %1382 = sext i32 %lsr.iv631 to i64
  %1383 = getelementptr float, ptr %1330, i64 %1382
  %wide.load169 = load <4 x float>, ptr %1383, align 4
  %1384 = sext i32 %lsr.iv633 to i64
  %1385 = getelementptr float, ptr %106, i64 %1384
  %wide.load170 = load <4 x float>, ptr %1385, align 4
  %1386 = fsub reassoc ninf nsz <4 x float> %wide.load169, %wide.load170
  %1387 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %1386)
  %1388 = fadd reassoc ninf nsz <4 x float> %1387, %vec.phi168
  %lsr.iv.next630 = add i64 %lsr.iv629, 4
  %lsr.iv.next632 = add i32 %lsr.iv631, 4
  %lsr.iv.next634 = add i32 %lsr.iv633, 4
  %1389 = icmp eq i64 %lsr.iv.next630, 0
  br i1 %1389, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %1390 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %1388)
  br i1 %cmp.n172, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv134.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec166, %vec.epilog.middle.block ]
  %.1115.us.ph = phi float [ %1376, %vec.epilog.iter.check ], [ %.052119.us, %iter.check ], [ %.052119.us, %vector.scevcheck ], [ %1390, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv640 = phi i64 [ %1343, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next641, %for_loop_body70.us.prol ]
  %indvars.iv134.prol = phi i64 [ %indvars.iv.next135.prol, %for_loop_body70.us.prol ], [ %indvars.iv134.ph, %for_loop_body70.us.prol.preheader ]
  %.1115.us.prol = phi float [ %1401, %for_loop_body70.us.prol ], [ %.1115.us.ph, %for_loop_body70.us.prol.preheader ]
  %1391 = add i64 %lsr.iv637, %indvars.iv134.prol
  %tmp639 = trunc i64 %1391 to i32
  %1392 = sext i32 %tmp639 to i64
  %1393 = getelementptr float, ptr %1330, i64 %1392
  %1394 = load float, ptr %1393, align 4
  %1395 = add i64 %lsr.iv635, %indvars.iv134.prol
  %tmp = trunc i64 %1395 to i32
  %1396 = sext i32 %tmp to i64
  %1397 = getelementptr float, ptr %106, i64 %1396
  %1398 = load float, ptr %1397, align 4
  %1399 = fsub reassoc ninf nsz float %1394, %1398
  %1400 = tail call noundef float @llvm.fabs.f32(float %1399)
  %1401 = fadd reassoc ninf nsz float %1400, %.1115.us.prol
  %indvars.iv.next135.prol = add nuw nsw i64 %indvars.iv134.prol, 1
  %lsr.iv.next641 = add nsw i64 %lsr.iv640, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next641, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa515.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %1401, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv134.unr = phi i64 [ %indvars.iv134.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next135.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1115.us.unr = phi float [ %.1115.us.ph, %for_loop_body70.us.preheader ], [ %1401, %for_loop_body70.us.prol.loopexit.loopexit ]
  %1402 = sub nsw i64 %indvars.iv134.ph, %wide.trip.count137
  %1403 = icmp ugt i64 %1402, -4
  br i1 %1403, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader.new

for_loop_body70.us.preheader.new:                 ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader.new
  %indvars.iv134 = phi i64 [ %indvars.iv134.unr, %for_loop_body70.us.preheader.new ], [ %indvars.iv.next135.3, %for_loop_body70.us ]
  %.1115.us = phi float [ %.1115.us.unr, %for_loop_body70.us.preheader.new ], [ %1447, %for_loop_body70.us ]
  %1404 = add i64 %lsr.iv637, %indvars.iv134
  %tmp649 = trunc i64 %1404 to i32
  %1405 = sext i32 %tmp649 to i64
  %1406 = getelementptr float, ptr %1330, i64 %1405
  %1407 = load float, ptr %1406, align 4
  %1408 = add i64 %lsr.iv635, %indvars.iv134
  %tmp648 = trunc i64 %1408 to i32
  %1409 = sext i32 %tmp648 to i64
  %1410 = getelementptr float, ptr %106, i64 %1409
  %1411 = load float, ptr %1410, align 4
  %1412 = fsub reassoc ninf nsz float %1407, %1411
  %1413 = tail call noundef float @llvm.fabs.f32(float %1412)
  %1414 = fadd reassoc ninf nsz float %1413, %.1115.us
  %1415 = add i64 %1404, 1
  %tmp647 = trunc i64 %1415 to i32
  %1416 = sext i32 %tmp647 to i64
  %1417 = getelementptr float, ptr %1330, i64 %1416
  %1418 = load float, ptr %1417, align 4
  %1419 = add i64 %1408, 1
  %tmp646 = trunc i64 %1419 to i32
  %1420 = sext i32 %tmp646 to i64
  %1421 = getelementptr float, ptr %106, i64 %1420
  %1422 = load float, ptr %1421, align 4
  %1423 = fsub reassoc ninf nsz float %1418, %1422
  %1424 = tail call noundef float @llvm.fabs.f32(float %1423)
  %1425 = fadd reassoc ninf nsz float %1424, %1414
  %1426 = add i64 %1404, 2
  %tmp645 = trunc i64 %1426 to i32
  %1427 = sext i32 %tmp645 to i64
  %1428 = getelementptr float, ptr %1330, i64 %1427
  %1429 = load float, ptr %1428, align 4
  %1430 = add i64 %1408, 2
  %tmp644 = trunc i64 %1430 to i32
  %1431 = sext i32 %tmp644 to i64
  %1432 = getelementptr float, ptr %106, i64 %1431
  %1433 = load float, ptr %1432, align 4
  %1434 = fsub reassoc ninf nsz float %1429, %1433
  %1435 = tail call noundef float @llvm.fabs.f32(float %1434)
  %1436 = fadd reassoc ninf nsz float %1435, %1425
  %1437 = add i64 %1404, 3
  %tmp643 = trunc i64 %1437 to i32
  %1438 = sext i32 %tmp643 to i64
  %1439 = getelementptr float, ptr %1330, i64 %1438
  %1440 = load float, ptr %1439, align 4
  %1441 = add i64 %1408, 3
  %tmp642 = trunc i64 %1441 to i32
  %1442 = sext i32 %tmp642 to i64
  %1443 = getelementptr float, ptr %106, i64 %1442
  %1444 = load float, ptr %1443, align 4
  %1445 = fsub reassoc ninf nsz float %1440, %1444
  %1446 = tail call noundef float @llvm.fabs.f32(float %1445)
  %1447 = fadd reassoc ninf nsz float %1446, %1436
  %indvars.iv.next135.3 = add nuw nsw i64 %indvars.iv134, 4
  %exitcond138.not.3 = icmp eq i64 %wide.trip.count137, %indvars.iv.next135.3
  br i1 %exitcond138.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa151 = phi float [ %1376, %middle.block ], [ %1390, %vec.epilog.middle.block ], [ %.lcssa515.unr, %for_loop_body70.us.prol.loopexit ], [ %1447, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %1448 = add nuw nsw i32 %.051120.us, 1
  %lsr.iv.next638 = add i64 %lsr.iv637, %1342
  %lsr.iv.next636 = add i64 %lsr.iv635, %1340
  %exitcond140.not = icmp eq i32 %1448, %smax139
  br i1 %exitcond140.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %1449 = fdiv reassoc ninf nsz float %.lcssa150, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.053 = phi float [ %1464, %after_for68 ], [ %1449, %false_block64 ]
  %1450 = getelementptr i8, ptr %75, i64 224
  %1451 = load float, ptr %1450, align 4
  %1452 = getelementptr i8, ptr %75, i64 228
  %1453 = load float, ptr %1452, align 4
  %1454 = fmul reassoc ninf nsz float %1453, %158
  %1455 = fsub reassoc ninf nsz float %.053, %1454
  %1456 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1455, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %1451
  %1457 = fmul reassoc ninf nsz float %1456, %neg
  %1458 = tail call noundef float @expf(float noundef %1457) #9
  %1459 = fmul reassoc ninf nsz float %.070, %.071
  %1460 = fmul reassoc ninf nsz float %1459, %1458
  %1461 = fcmp reassoc ninf nsz ult float %1460, 0x3EB0C6F7A0000000
  br i1 %1461, label %after_if3, label %for_loop_body77.lr.ph

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %1462 = mul i32 %66, %62
  %1463 = sitofp i32 %1462 to float
  %1464 = fdiv reassoc ninf nsz float %.lcssa151, %1463
  br label %after_if65

for_loop_body77.lr.ph:                            ; preds = %after_if65
  %1465 = load ptr, ptr %0, align 8
  %1466 = getelementptr i8, ptr %1465, i64 136
  %1467 = getelementptr i8, ptr %1465, i64 132
  %1468 = getelementptr i8, ptr %1465, i64 152
  %1469 = getelementptr i8, ptr %1465, i64 148
  %smax141 = tail call i32 @llvm.smax.i32(i32 %66, i32 1)
  %smax143 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  br label %for_loop_body77

for_loop_body77:                                  ; preds = %after_for86, %for_loop_body77.lr.ph
  %lsr.iv653 = phi i32 [ %54, %for_loop_body77.lr.ph ], [ %lsr.iv.next654, %after_for86 ]
  %.049125 = phi i32 [ 0, %for_loop_body77.lr.ph ], [ %1490, %after_for86 ]
  %1470 = load ptr, ptr %3, align 8
  %1471 = getelementptr inbounds nuw i8, ptr %1470, i64 32872
  %1472 = load ptr, ptr %1471, align 8
  %1473 = getelementptr inbounds nuw i8, ptr %1472, i64 24
  %1474 = load i1, ptr %1473, align 1
  br i1 %1474, label %true_block81, label %for_loop_body84.preheader

true_block81:                                     ; preds = %for_loop_body77
  %1475 = uitofp nneg i32 %.049125 to float
  %1476 = fmul reassoc ninf nsz float %1475, 0x401921FB60000000
  %1477 = getelementptr inbounds nuw i8, ptr %1472, i64 28
  %1478 = load float, ptr %1477, align 4
  %1479 = fmul reassoc ninf nsz float %1476, %1478
  %1480 = tail call noundef float @cosf(float noundef %1479) #9
  %1481 = fmul reassoc ninf nsz float %1480, 5.000000e-01
  %1482 = fsub reassoc ninf nsz float 5.000000e-01, %1481
  br label %for_loop_body84.preheader

for_loop_body84.preheader:                        ; preds = %true_block81, %for_loop_body77
  %.048 = phi float [ %1482, %true_block81 ], [ 1.000000e+00, %for_loop_body77 ]
  %1483 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.048, float 0x3F1A36E2E0000000)
  %1484 = fmul reassoc ninf nsz float %1483, %1460
  br label %for_loop_body84

for_loop_body84:                                  ; preds = %after_if90, %for_loop_body84.preheader
  %.047124 = phi i32 [ %1517, %after_if90 ], [ 0, %for_loop_body84.preheader ]
  %1485 = load ptr, ptr %3, align 8
  %1486 = getelementptr inbounds nuw i8, ptr %1485, i64 32872
  %1487 = load ptr, ptr %1486, align 8
  %1488 = getelementptr inbounds nuw i8, ptr %1487, i64 32
  %1489 = load i1, ptr %1488, align 1
  br i1 %1489, label %true_block88, label %after_if90

after_for86:                                      ; preds = %after_if90
  %1490 = add nuw nsw i32 %.049125, 1
  %lsr.iv.next654 = add i32 %lsr.iv653, 1
  %exitcond144.not = icmp eq i32 %1490, %smax143
  br i1 %exitcond144.not, label %after_if3.loopexit, label %for_loop_body77

true_block88:                                     ; preds = %for_loop_body84
  %1491 = uitofp nneg i32 %.047124 to float
  %1492 = fmul reassoc ninf nsz float %1491, 0x401921FB60000000
  %1493 = getelementptr inbounds nuw i8, ptr %1487, i64 36
  %1494 = load float, ptr %1493, align 4
  %1495 = fmul reassoc ninf nsz float %1492, %1494
  %1496 = tail call noundef float @cosf(float noundef %1495) #9
  %1497 = fmul reassoc ninf nsz float %1496, 5.000000e-01
  %1498 = fsub reassoc ninf nsz float 5.000000e-01, %1497
  br label %after_if90

after_if90:                                       ; preds = %true_block88, %for_loop_body84
  %.0 = phi float [ %1498, %true_block88 ], [ 1.000000e+00, %for_loop_body84 ]
  %1499 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0, float 0x3F1A36E2E0000000)
  %1500 = fmul reassoc ninf nsz float %1484, %1499
  %1501 = load ptr, ptr %1466, align 8
  %1502 = load i32, ptr %1467, align 4
  %1503 = mul i32 %lsr.iv653, %1502
  %1504 = add i32 %58, %.047124
  %1505 = add i32 %1504, %1503
  %1506 = sext i32 %1505 to i64
  %1507 = getelementptr float, ptr %1501, i64 %1506
  %1508 = atomicrmw fadd ptr %1507, float %1500 seq_cst, align 4
  %1509 = fmul reassoc ninf nsz float %1499, %1483
  %1510 = load ptr, ptr %1468, align 8
  %1511 = load i32, ptr %1469, align 4
  %1512 = mul i32 %lsr.iv653, %1511
  %1513 = add i32 %1504, %1512
  %1514 = sext i32 %1513 to i64
  %1515 = getelementptr float, ptr %1510, i64 %1514
  %1516 = atomicrmw fadd ptr %1515, float %1509 seq_cst, align 4
  %1517 = add nuw nsw i32 %.047124, 1
  %exitcond142.not = icmp eq i32 %smax141, %1517
  br i1 %exitcond142.not, label %after_for86, label %for_loop_body84
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
  %4 = alloca %struct.RuntimeContext.66, align 8
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
