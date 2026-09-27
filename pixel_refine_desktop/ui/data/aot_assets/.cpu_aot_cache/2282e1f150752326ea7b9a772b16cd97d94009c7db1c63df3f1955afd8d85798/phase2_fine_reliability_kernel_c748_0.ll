; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.62 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase2_fine_reliability_kernel_c748_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @phase2_fine_reliability_kernel_c748_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.059116 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %79, %after_if3 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.059116, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.059116
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %35, %.059116
  %39 = and i1 %37, %38
  %.neg87 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg87
  %41 = mul i32 %40, %33
  %42 = sub i32 %.059116, %41
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
  %79 = add nsw i32 %.059116, 1
  %exitcond135.not = icmp eq i32 %79, %18
  br i1 %exitcond135.not, label %after_for.loopexit, label %for_loop_body

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
  %.not117 = icmp samesign ult i32 %66, 3
  %172 = fmul reassoc ninf nsz float %168, %171
  br i1 %.not117, label %for_loop_body66.lr.ph.split.us, label %for_loop_body16.lr.ph.split.us

for_loop_body16.lr.ph.split.us:                   ; preds = %for_loop_body16.lr.ph
  %173 = getelementptr i8, ptr %75, i64 84
  %174 = getelementptr i8, ptr %75, i64 88
  %175 = getelementptr i8, ptr %75, i64 68
  %176 = getelementptr i8, ptr %75, i64 72
  %177 = getelementptr i8, ptr %75, i64 52
  %178 = getelementptr i8, ptr %75, i64 56
  %179 = getelementptr i8, ptr %75, i64 36
  %180 = getelementptr i8, ptr %75, i64 40
  %181 = getelementptr i8, ptr %75, i64 4
  %182 = getelementptr i8, ptr %75, i64 8
  %183 = load ptr, ptr %182, align 8
  %184 = load i32, ptr %181, align 4
  %185 = load ptr, ptr %180, align 8
  %186 = load i32, ptr %179, align 4
  %187 = load ptr, ptr %178, align 8
  %188 = load i32, ptr %177, align 4
  %189 = load ptr, ptr %176, align 8
  %190 = load i32, ptr %175, align 4
  %191 = load ptr, ptr %174, align 8
  %192 = load i32, ptr %173, align 4
  %wide.trip.count = zext i32 %166 to i64
  %193 = add nsw i64 %wide.trip.count, -1
  %194 = mul i32 %184, %165
  %195 = add i32 %167, %194
  %196 = shl i32 %184, 1
  %197 = mul i32 %108, %165
  %198 = add i32 %167, %197
  %199 = shl i32 %108, 1
  %200 = mul i32 %186, %165
  %201 = add i32 %167, %200
  %202 = shl i32 %186, 1
  %203 = mul i32 %188, %165
  %204 = add i32 %167, %203
  %205 = shl i32 %188, 1
  %206 = mul i32 %190, %165
  %207 = add i32 %167, %206
  %208 = shl i32 %190, 1
  %209 = mul i32 %192, %165
  %210 = add i32 %167, %209
  %211 = shl i32 %192, 1
  %min.iters.check181 = icmp ult i32 %66, 17
  %212 = trunc nsw i64 %193 to i32
  %mul.result = shl i32 %212, 1
  %invariant.op429 = add i32 %195, %mul.result
  %invariant.op431 = add i32 %198, %mul.result
  %213 = icmp ugt i64 %193, 4294967295
  %invariant.op433 = add i32 %201, %mul.result
  %invariant.op435 = add i32 %204, %mul.result
  %invariant.op437 = add i32 %207, %mul.result
  %invariant.op439 = add i32 %210, %mul.result
  %min.iters.check184 = icmp ult i32 %66, 65
  %n.vec188 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %163, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %214 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert199 = insertelement <8 x i32> poison, i32 %167, i64 0
  %broadcast.splat200 = shufflevector <8 x i32> %broadcast.splatinsert199, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert236 = insertelement <8 x float> poison, float %162, i64 0
  %broadcast.splat237 = shufflevector <8 x float> %broadcast.splatinsert236, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert238 = insertelement <8 x float> poison, float %172, i64 0
  %broadcast.splat239 = shufflevector <8 x float> %broadcast.splatinsert238, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert255 = insertelement <8 x float> poison, float %160, i64 0
  %broadcast.splat256 = shufflevector <8 x float> %broadcast.splatinsert255, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat200
  %invariant.op425 = add <8 x i32> splat (i32 32), %broadcast.splat200
  %invariant.op427 = add <8 x i32> splat (i32 48), %broadcast.splat200
  %cmp.n304 = icmp eq i64 %n.vec188, %wide.trip.count
  %n.vec.remaining312 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check313 = icmp eq i64 %n.vec.remaining312, 0
  %n.vec315 = and i64 %wide.trip.count, 2147483640
  %cmp.n365 = icmp eq i64 %n.vec315, %wide.trip.count
  %215 = zext i32 %119 to i64
  %216 = lshr i64 %215, 4
  %217 = mul nsw i64 %216, -8
  %218 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check183

iter.check183:                                    ; preds = %for_loop_test23.after_for22_crit_edge.us, %for_loop_body16.lr.ph.split.us
  %lsr.iv473 = phi i32 [ %lsr.iv.next474, %for_loop_test23.after_for22_crit_edge.us ], [ %195, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv469 = phi i32 [ %lsr.iv.next470, %for_loop_test23.after_for22_crit_edge.us ], [ %198, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv465 = phi i32 [ %lsr.iv.next466, %for_loop_test23.after_for22_crit_edge.us ], [ %201, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv461 = phi i32 [ %lsr.iv.next462, %for_loop_test23.after_for22_crit_edge.us ], [ %204, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv457 = phi i32 [ %lsr.iv.next458, %for_loop_test23.after_for22_crit_edge.us ], [ %207, %for_loop_body16.lr.ph.split.us ]
  %lsr.iv453 = phi i32 [ %lsr.iv.next454, %for_loop_test23.after_for22_crit_edge.us ], [ %210, %for_loop_body16.lr.ph.split.us ]
  %.064101.us = phi i32 [ 0, %for_loop_body16.lr.ph.split.us ], [ %919, %for_loop_test23.after_for22_crit_edge.us ]
  %.065100.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa, %for_loop_test23.after_for22_crit_edge.us ]
  %.06799.us = phi float [ 0.000000e+00, %for_loop_body16.lr.ph.split.us ], [ %.lcssa140, %for_loop_test23.after_for22_crit_edge.us ]
  %219 = shl nuw i32 %.064101.us, 1
  %220 = add i32 %165, %219
  %221 = mul i32 %184, %220
  %222 = mul i32 %220, %108
  %223 = mul i32 %186, %220
  %224 = mul i32 %188, %220
  %225 = mul i32 %190, %220
  %226 = mul i32 %192, %220
  br i1 %min.iters.check181, label %for_loop_body20.us.preheader, label %vector.scevcheck164

vector.scevcheck164:                              ; preds = %iter.check183
  %227 = mul i32 %211, %.064101.us
  %228 = add i32 %210, %227
  %229 = mul i32 %208, %.064101.us
  %230 = add i32 %207, %229
  %231 = mul i32 %205, %.064101.us
  %232 = add i32 %204, %231
  %233 = mul i32 %202, %.064101.us
  %234 = add i32 %201, %233
  %235 = mul i32 %199, %.064101.us
  %236 = add i32 %198, %235
  %237 = mul i32 %196, %.064101.us
  %238 = add i32 %195, %237
  %.reass430 = add i32 %237, %invariant.op429
  %239 = icmp slt i32 %.reass430, %238
  %.reass432 = add i32 %235, %invariant.op431
  %240 = icmp slt i32 %.reass432, %236
  %241 = or i1 %240, %213
  %.reass434 = add i32 %233, %invariant.op433
  %242 = icmp slt i32 %.reass434, %234
  %.reass436 = add i32 %231, %invariant.op435
  %243 = icmp slt i32 %.reass436, %232
  %.reass438 = add i32 %229, %invariant.op437
  %244 = icmp slt i32 %.reass438, %230
  %.reass440 = add i32 %227, %invariant.op439
  %245 = icmp slt i32 %.reass440, %228
  %246 = or i1 %239, %241
  %247 = or i1 %242, %246
  %248 = or i1 %243, %247
  %249 = or i1 %244, %248
  %250 = or i1 %245, %249
  br i1 %250, label %for_loop_body20.us.preheader, label %vector.main.loop.iter.check185

vector.main.loop.iter.check185:                   ; preds = %vector.scevcheck164
  br i1 %min.iters.check184, label %vec.epilog.ph310, label %vector.ph186

vector.ph186:                                     ; preds = %vector.main.loop.iter.check185
  %251 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.065100.us, i64 0
  %252 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06799.us, i64 0
  %broadcast.splatinsert201 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat202 = shufflevector <8 x i32> %broadcast.splatinsert201, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert206 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat207 = shufflevector <8 x i32> %broadcast.splatinsert206, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert212 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat213 = shufflevector <8 x i32> %broadcast.splatinsert212, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert218 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat219 = shufflevector <8 x i32> %broadcast.splatinsert218, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert224 = insertelement <8 x i32> poison, i32 %225, i64 0
  %broadcast.splat225 = shufflevector <8 x i32> %broadcast.splatinsert224, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert230 = insertelement <8 x i32> poison, i32 %226, i64 0
  %broadcast.splat231 = shufflevector <8 x i32> %broadcast.splatinsert230, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body189

vector.body189:                                   ; preds = %vector.body189, %vector.ph186
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body189 ], [ %n.vec188, %vector.ph186 ]
  %vec.phi191 = phi <8 x float> [ %251, %vector.ph186 ], [ %699, %vector.body189 ]
  %vec.phi192 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %700, %vector.body189 ]
  %vec.phi193 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %701, %vector.body189 ]
  %vec.phi194 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %702, %vector.body189 ]
  %vec.phi195 = phi <8 x float> [ %252, %vector.ph186 ], [ %695, %vector.body189 ]
  %vec.phi196 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %696, %vector.body189 ]
  %vec.phi197 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %697, %vector.body189 ]
  %vec.phi198 = phi <8 x float> [ zeroinitializer, %vector.ph186 ], [ %698, %vector.body189 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph186 ], [ %vec.ind.next, %vector.body189 ]
  %253 = shl <8 x i32> %vec.ind, splat (i32 1)
  %254 = add <8 x i32> %broadcast.splat200, %253
  %.reass = add <8 x i32> %253, %invariant.op
  %.reass426 = add <8 x i32> %253, %invariant.op425
  %.reass428 = add <8 x i32> %253, %invariant.op427
  %255 = add <8 x i32> %broadcast.splat202, %254
  %256 = add <8 x i32> %broadcast.splat202, %.reass
  %257 = add <8 x i32> %broadcast.splat202, %.reass426
  %258 = add <8 x i32> %broadcast.splat202, %.reass428
  %259 = sext <8 x i32> %255 to <8 x i64>
  %260 = sext <8 x i32> %256 to <8 x i64>
  %261 = sext <8 x i32> %257 to <8 x i64>
  %262 = sext <8 x i32> %258 to <8 x i64>
  %263 = getelementptr float, ptr %183, <8 x i64> %259
  %264 = getelementptr float, ptr %183, <8 x i64> %260
  %265 = getelementptr float, ptr %183, <8 x i64> %261
  %266 = getelementptr float, ptr %183, <8 x i64> %262
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %263, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %264, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %265, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather205 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %266, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %267 = add <8 x i32> %254, %broadcast.splat207
  %268 = add <8 x i32> %.reass, %broadcast.splat207
  %269 = add <8 x i32> %.reass426, %broadcast.splat207
  %270 = add <8 x i32> %.reass428, %broadcast.splat207
  %271 = sext <8 x i32> %267 to <8 x i64>
  %272 = sext <8 x i32> %268 to <8 x i64>
  %273 = sext <8 x i32> %269 to <8 x i64>
  %274 = sext <8 x i32> %270 to <8 x i64>
  %275 = getelementptr float, ptr %106, <8 x i64> %271
  %276 = getelementptr float, ptr %106, <8 x i64> %272
  %277 = getelementptr float, ptr %106, <8 x i64> %273
  %278 = getelementptr float, ptr %106, <8 x i64> %274
  %wide.masked.gather208 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %275, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather209 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %276, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather210 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %277, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather211 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %278, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %279 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather208
  %280 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather209
  %281 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather210
  %282 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather211
  %283 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %279)
  %284 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %280)
  %285 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %281)
  %286 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %282)
  %287 = add <8 x i32> %broadcast.splat213, %254
  %288 = add <8 x i32> %broadcast.splat213, %.reass
  %289 = add <8 x i32> %broadcast.splat213, %.reass426
  %290 = add <8 x i32> %broadcast.splat213, %.reass428
  %291 = sext <8 x i32> %287 to <8 x i64>
  %292 = sext <8 x i32> %288 to <8 x i64>
  %293 = sext <8 x i32> %289 to <8 x i64>
  %294 = sext <8 x i32> %290 to <8 x i64>
  %295 = getelementptr float, ptr %185, <8 x i64> %291
  %296 = getelementptr float, ptr %185, <8 x i64> %292
  %297 = getelementptr float, ptr %185, <8 x i64> %293
  %298 = getelementptr float, ptr %185, <8 x i64> %294
  %wide.masked.gather214 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %295, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather215 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %296, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather216 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %297, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather217 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %298, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %299 = add <8 x i32> %broadcast.splat219, %254
  %300 = add <8 x i32> %broadcast.splat219, %.reass
  %301 = add <8 x i32> %broadcast.splat219, %.reass426
  %302 = add <8 x i32> %broadcast.splat219, %.reass428
  %303 = sext <8 x i32> %299 to <8 x i64>
  %304 = sext <8 x i32> %300 to <8 x i64>
  %305 = sext <8 x i32> %301 to <8 x i64>
  %306 = sext <8 x i32> %302 to <8 x i64>
  %307 = getelementptr float, ptr %187, <8 x i64> %303
  %308 = getelementptr float, ptr %187, <8 x i64> %304
  %309 = getelementptr float, ptr %187, <8 x i64> %305
  %310 = getelementptr float, ptr %187, <8 x i64> %306
  %wide.masked.gather220 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %307, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather221 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %308, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather222 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %309, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather223 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %310, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %311 = add <8 x i32> %broadcast.splat225, %254
  %312 = add <8 x i32> %broadcast.splat225, %.reass
  %313 = add <8 x i32> %broadcast.splat225, %.reass426
  %314 = add <8 x i32> %broadcast.splat225, %.reass428
  %315 = sext <8 x i32> %311 to <8 x i64>
  %316 = sext <8 x i32> %312 to <8 x i64>
  %317 = sext <8 x i32> %313 to <8 x i64>
  %318 = sext <8 x i32> %314 to <8 x i64>
  %319 = getelementptr float, ptr %189, <8 x i64> %315
  %320 = getelementptr float, ptr %189, <8 x i64> %316
  %321 = getelementptr float, ptr %189, <8 x i64> %317
  %322 = getelementptr float, ptr %189, <8 x i64> %318
  %wide.masked.gather226 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %319, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather227 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %320, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather228 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %321, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather229 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %322, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %323 = add <8 x i32> %broadcast.splat231, %254
  %324 = add <8 x i32> %broadcast.splat231, %.reass
  %325 = add <8 x i32> %broadcast.splat231, %.reass426
  %326 = add <8 x i32> %broadcast.splat231, %.reass428
  %327 = sext <8 x i32> %323 to <8 x i64>
  %328 = sext <8 x i32> %324 to <8 x i64>
  %329 = sext <8 x i32> %325 to <8 x i64>
  %330 = sext <8 x i32> %326 to <8 x i64>
  %331 = getelementptr float, ptr %191, <8 x i64> %327
  %332 = getelementptr float, ptr %191, <8 x i64> %328
  %333 = getelementptr float, ptr %191, <8 x i64> %329
  %334 = getelementptr float, ptr %191, <8 x i64> %330
  %wide.masked.gather232 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %331, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather233 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %332, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather234 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %333, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather235 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %334, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %335 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather214, %wide.masked.gather214
  %336 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather215, %wide.masked.gather215
  %337 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather216, %wide.masked.gather216
  %338 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather217, %wide.masked.gather217
  %339 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather220
  %340 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather221, %wide.masked.gather221
  %341 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather222, %wide.masked.gather222
  %342 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather223, %wide.masked.gather223
  %343 = fadd reassoc ninf nsz <8 x float> %339, %335
  %344 = fadd reassoc ninf nsz <8 x float> %340, %336
  %345 = fadd reassoc ninf nsz <8 x float> %341, %337
  %346 = fadd reassoc ninf nsz <8 x float> %342, %338
  %347 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather226
  %348 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather227
  %349 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather228
  %350 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather229, %wide.masked.gather229
  %351 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather232, %wide.masked.gather232
  %352 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather233, %wide.masked.gather233
  %353 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather234, %wide.masked.gather234
  %354 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather235, %wide.masked.gather235
  %355 = fadd reassoc ninf nsz <8 x float> %351, %347
  %356 = fadd reassoc ninf nsz <8 x float> %352, %348
  %357 = fadd reassoc ninf nsz <8 x float> %353, %349
  %358 = fadd reassoc ninf nsz <8 x float> %354, %350
  %359 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %343, <8 x float> %355)
  %360 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %344, <8 x float> %356)
  %361 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %345, <8 x float> %357)
  %362 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %346, <8 x float> %358)
  %363 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, splat (float -2.000000e+00)
  %364 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, splat (float -2.000000e+00)
  %365 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, splat (float -2.000000e+00)
  %366 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, splat (float -2.000000e+00)
  %367 = fadd reassoc ninf nsz <8 x float> %363, splat (float 3.000000e+00)
  %368 = fadd reassoc ninf nsz <8 x float> %364, splat (float 3.000000e+00)
  %369 = fadd reassoc ninf nsz <8 x float> %365, splat (float 3.000000e+00)
  %370 = fadd reassoc ninf nsz <8 x float> %366, splat (float 3.000000e+00)
  %371 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %367, <8 x float> splat (float 3.000000e+00))
  %372 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %368, <8 x float> splat (float 3.000000e+00))
  %373 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %369, <8 x float> splat (float 3.000000e+00))
  %374 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %370, <8 x float> splat (float 3.000000e+00))
  %375 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %371, <8 x float> splat (float 1.000000e+00))
  %376 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %372, <8 x float> splat (float 1.000000e+00))
  %377 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %373, <8 x float> splat (float 1.000000e+00))
  %378 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %374, <8 x float> splat (float 1.000000e+00))
  %379 = fmul reassoc ninf nsz <8 x float> %375, %broadcast.splat237
  %380 = fmul reassoc ninf nsz <8 x float> %376, %broadcast.splat237
  %381 = fmul reassoc ninf nsz <8 x float> %377, %broadcast.splat237
  %382 = fmul reassoc ninf nsz <8 x float> %378, %broadcast.splat237
  %383 = fmul reassoc ninf nsz <8 x float> %375, %375
  %384 = fmul reassoc ninf nsz <8 x float> %376, %376
  %385 = fmul reassoc ninf nsz <8 x float> %377, %377
  %386 = fmul reassoc ninf nsz <8 x float> %378, %378
  %387 = fmul reassoc ninf nsz <8 x float> %383, %broadcast.splat239
  %388 = fmul reassoc ninf nsz <8 x float> %384, %broadcast.splat239
  %389 = fmul reassoc ninf nsz <8 x float> %385, %broadcast.splat239
  %390 = fmul reassoc ninf nsz <8 x float> %386, %broadcast.splat239
  %391 = fcmp reassoc ninf nsz olt <8 x float> %359, %387
  %392 = fcmp reassoc ninf nsz olt <8 x float> %360, %388
  %393 = fcmp reassoc ninf nsz olt <8 x float> %361, %389
  %394 = fcmp reassoc ninf nsz olt <8 x float> %362, %390
  %395 = xor <8 x i1> %391, splat (i1 true)
  %396 = xor <8 x i1> %392, splat (i1 true)
  %397 = xor <8 x i1> %393, splat (i1 true)
  %398 = xor <8 x i1> %394, splat (i1 true)
  %399 = select <8 x i1> %broadcast.splat, <8 x i1> %395, <8 x i1> zeroinitializer
  %400 = select <8 x i1> %broadcast.splat, <8 x i1> %396, <8 x i1> zeroinitializer
  %401 = select <8 x i1> %broadcast.splat, <8 x i1> %397, <8 x i1> zeroinitializer
  %402 = select <8 x i1> %broadcast.splat, <8 x i1> %398, <8 x i1> zeroinitializer
  %403 = fcmp reassoc ninf nsz olt <8 x float> %283, %379
  %404 = fcmp reassoc ninf nsz olt <8 x float> %284, %380
  %405 = fcmp reassoc ninf nsz olt <8 x float> %285, %381
  %406 = fcmp reassoc ninf nsz olt <8 x float> %286, %382
  %407 = xor <8 x i1> %403, splat (i1 true)
  %408 = xor <8 x i1> %404, splat (i1 true)
  %409 = xor <8 x i1> %405, splat (i1 true)
  %410 = xor <8 x i1> %406, splat (i1 true)
  %411 = select <8 x i1> %399, <8 x i1> %407, <8 x i1> zeroinitializer
  %412 = select <8 x i1> %400, <8 x i1> %408, <8 x i1> zeroinitializer
  %413 = select <8 x i1> %401, <8 x i1> %409, <8 x i1> zeroinitializer
  %414 = select <8 x i1> %402, <8 x i1> %410, <8 x i1> zeroinitializer
  %415 = fmul reassoc ninf nsz <8 x float> %379, splat (float 4.000000e+00)
  %416 = fmul reassoc ninf nsz <8 x float> %380, splat (float 4.000000e+00)
  %417 = fmul reassoc ninf nsz <8 x float> %381, splat (float 4.000000e+00)
  %418 = fmul reassoc ninf nsz <8 x float> %382, splat (float 4.000000e+00)
  %419 = fdiv reassoc ninf nsz <8 x float> %283, %415
  %420 = fdiv reassoc ninf nsz <8 x float> %284, %416
  %421 = fdiv reassoc ninf nsz <8 x float> %285, %417
  %422 = fdiv reassoc ninf nsz <8 x float> %286, %418
  %423 = fcmp reassoc ninf nsz ogt <8 x float> %419, splat (float 1.000000e+00)
  %424 = fcmp reassoc ninf nsz ogt <8 x float> %420, splat (float 1.000000e+00)
  %425 = fcmp reassoc ninf nsz ogt <8 x float> %421, splat (float 1.000000e+00)
  %426 = fcmp reassoc ninf nsz ogt <8 x float> %422, splat (float 1.000000e+00)
  %427 = select <8 x i1> %423, <8 x float> splat (float 1.000000e+00), <8 x float> %419
  %428 = select <8 x i1> %424, <8 x float> splat (float 1.000000e+00), <8 x float> %420
  %429 = select <8 x i1> %425, <8 x float> splat (float 1.000000e+00), <8 x float> %421
  %430 = select <8 x i1> %426, <8 x float> splat (float 1.000000e+00), <8 x float> %422
  %431 = fmul reassoc ninf nsz <8 x float> %427, splat (float 0x3FD99999A0000000)
  %432 = fmul reassoc ninf nsz <8 x float> %428, splat (float 0x3FD99999A0000000)
  %433 = fmul reassoc ninf nsz <8 x float> %429, splat (float 0x3FD99999A0000000)
  %434 = fmul reassoc ninf nsz <8 x float> %430, splat (float 0x3FD99999A0000000)
  %435 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %431
  %436 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %432
  %437 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %433
  %438 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %434
  %439 = select <8 x i1> %399, <8 x i1> %403, <8 x i1> zeroinitializer
  %440 = select <8 x i1> %400, <8 x i1> %404, <8 x i1> zeroinitializer
  %441 = select <8 x i1> %401, <8 x i1> %405, <8 x i1> zeroinitializer
  %442 = select <8 x i1> %402, <8 x i1> %406, <8 x i1> zeroinitializer
  %443 = fmul reassoc ninf nsz <8 x float> %283, splat (float 0x3FC3333340000000)
  %444 = fmul reassoc ninf nsz <8 x float> %284, splat (float 0x3FC3333340000000)
  %445 = fmul reassoc ninf nsz <8 x float> %285, splat (float 0x3FC3333340000000)
  %446 = fmul reassoc ninf nsz <8 x float> %286, splat (float 0x3FC3333340000000)
  %447 = fdiv reassoc ninf nsz <8 x float> %443, %379
  %448 = fdiv reassoc ninf nsz <8 x float> %444, %380
  %449 = fdiv reassoc ninf nsz <8 x float> %445, %381
  %450 = fdiv reassoc ninf nsz <8 x float> %446, %382
  %451 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %447
  %452 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %448
  %453 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %449
  %454 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %450
  %455 = select <8 x i1> %broadcast.splat, <8 x i1> %391, <8 x i1> zeroinitializer
  %456 = select <8 x i1> %broadcast.splat, <8 x i1> %392, <8 x i1> zeroinitializer
  %457 = select <8 x i1> %broadcast.splat, <8 x i1> %393, <8 x i1> zeroinitializer
  %458 = select <8 x i1> %broadcast.splat, <8 x i1> %394, <8 x i1> zeroinitializer
  %459 = fmul reassoc ninf nsz <8 x float> %379, splat (float 1.500000e+00)
  %460 = fmul reassoc ninf nsz <8 x float> %380, splat (float 1.500000e+00)
  %461 = fmul reassoc ninf nsz <8 x float> %381, splat (float 1.500000e+00)
  %462 = fmul reassoc ninf nsz <8 x float> %382, splat (float 1.500000e+00)
  %463 = fcmp reassoc ninf nsz uge <8 x float> %283, %459
  %464 = fcmp reassoc ninf nsz uge <8 x float> %284, %460
  %465 = fcmp reassoc ninf nsz uge <8 x float> %285, %461
  %466 = fcmp reassoc ninf nsz uge <8 x float> %286, %462
  %467 = select <8 x i1> %455, <8 x i1> %463, <8 x i1> zeroinitializer
  %468 = select <8 x i1> %456, <8 x i1> %464, <8 x i1> zeroinitializer
  %469 = select <8 x i1> %457, <8 x i1> %465, <8 x i1> zeroinitializer
  %470 = select <8 x i1> %458, <8 x i1> %466, <8 x i1> zeroinitializer
  %471 = fsub reassoc ninf nsz <8 x float> %283, %459
  %472 = fsub reassoc ninf nsz <8 x float> %284, %460
  %473 = fsub reassoc ninf nsz <8 x float> %285, %461
  %474 = fsub reassoc ninf nsz <8 x float> %286, %462
  %475 = fdiv reassoc ninf nsz <8 x float> %471, %459
  %476 = fdiv reassoc ninf nsz <8 x float> %472, %460
  %477 = fdiv reassoc ninf nsz <8 x float> %473, %461
  %478 = fdiv reassoc ninf nsz <8 x float> %474, %462
  %479 = fcmp reassoc ninf nsz ogt <8 x float> %475, splat (float 1.000000e+00)
  %480 = fcmp reassoc ninf nsz ogt <8 x float> %476, splat (float 1.000000e+00)
  %481 = fcmp reassoc ninf nsz ogt <8 x float> %477, splat (float 1.000000e+00)
  %482 = fcmp reassoc ninf nsz ogt <8 x float> %478, splat (float 1.000000e+00)
  %483 = select <8 x i1> %479, <8 x float> splat (float 1.000000e+00), <8 x float> %475
  %484 = select <8 x i1> %480, <8 x float> splat (float 1.000000e+00), <8 x float> %476
  %485 = select <8 x i1> %481, <8 x float> splat (float 1.000000e+00), <8 x float> %477
  %486 = select <8 x i1> %482, <8 x float> splat (float 1.000000e+00), <8 x float> %478
  %487 = fmul reassoc ninf nsz <8 x float> %483, splat (float 0x3FC99999A0000000)
  %488 = fmul reassoc ninf nsz <8 x float> %484, splat (float 0x3FC99999A0000000)
  %489 = fmul reassoc ninf nsz <8 x float> %485, splat (float 0x3FC99999A0000000)
  %490 = fmul reassoc ninf nsz <8 x float> %486, splat (float 0x3FC99999A0000000)
  %491 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %487
  %492 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %488
  %493 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %489
  %494 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %490
  %495 = fmul reassoc ninf nsz <8 x float> %283, splat (float 0x3FEE666660000000)
  %496 = fmul reassoc ninf nsz <8 x float> %284, splat (float 0x3FEE666660000000)
  %497 = fmul reassoc ninf nsz <8 x float> %285, splat (float 0x3FEE666660000000)
  %498 = fmul reassoc ninf nsz <8 x float> %286, splat (float 0x3FEE666660000000)
  %499 = fdiv reassoc ninf nsz <8 x float> %495, %459
  %500 = fdiv reassoc ninf nsz <8 x float> %496, %460
  %501 = fdiv reassoc ninf nsz <8 x float> %497, %461
  %502 = fdiv reassoc ninf nsz <8 x float> %498, %462
  %503 = fadd reassoc ninf nsz <8 x float> %499, splat (float 0x3FA99999A0000000)
  %504 = fadd reassoc ninf nsz <8 x float> %500, splat (float 0x3FA99999A0000000)
  %505 = fadd reassoc ninf nsz <8 x float> %501, splat (float 0x3FA99999A0000000)
  %506 = fadd reassoc ninf nsz <8 x float> %502, splat (float 0x3FA99999A0000000)
  %507 = or <8 x i1> %455, %439
  %508 = or <8 x i1> %456, %440
  %509 = or <8 x i1> %457, %441
  %510 = or <8 x i1> %458, %442
  %511 = or <8 x i1> %507, %411
  %512 = or <8 x i1> %508, %412
  %513 = or <8 x i1> %509, %413
  %514 = or <8 x i1> %510, %414
  %515 = or <8 x i1> %511, %214
  %516 = or <8 x i1> %512, %214
  %517 = or <8 x i1> %513, %214
  %518 = or <8 x i1> %514, %214
  %predphi = select <8 x i1> %467, <8 x float> %491, <8 x float> %503
  %predphi240 = select <8 x i1> %439, <8 x float> %451, <8 x float> %predphi
  %predphi241 = select <8 x i1> %411, <8 x float> %435, <8 x float> %predphi240
  %predphi242 = select <8 x i1> %broadcast.splat, <8 x float> %predphi241, <8 x float> splat (float 1.000000e+00)
  %predphi243 = select <8 x i1> %468, <8 x float> %492, <8 x float> %504
  %predphi244 = select <8 x i1> %440, <8 x float> %452, <8 x float> %predphi243
  %predphi245 = select <8 x i1> %412, <8 x float> %436, <8 x float> %predphi244
  %predphi246 = select <8 x i1> %broadcast.splat, <8 x float> %predphi245, <8 x float> splat (float 1.000000e+00)
  %predphi247 = select <8 x i1> %469, <8 x float> %493, <8 x float> %505
  %predphi248 = select <8 x i1> %441, <8 x float> %453, <8 x float> %predphi247
  %predphi249 = select <8 x i1> %413, <8 x float> %437, <8 x float> %predphi248
  %predphi250 = select <8 x i1> %broadcast.splat, <8 x float> %predphi249, <8 x float> splat (float 1.000000e+00)
  %predphi251 = select <8 x i1> %470, <8 x float> %494, <8 x float> %506
  %predphi252 = select <8 x i1> %442, <8 x float> %454, <8 x float> %predphi251
  %predphi253 = select <8 x i1> %414, <8 x float> %438, <8 x float> %predphi252
  %predphi254 = select <8 x i1> %broadcast.splat, <8 x float> %predphi253, <8 x float> splat (float 1.000000e+00)
  %519 = fcmp reassoc ninf nsz ogt <8 x float> %359, splat (float 0x3EB0C6F7A0000000)
  %520 = fcmp reassoc ninf nsz ogt <8 x float> %360, splat (float 0x3EB0C6F7A0000000)
  %521 = fcmp reassoc ninf nsz ogt <8 x float> %361, splat (float 0x3EB0C6F7A0000000)
  %522 = fcmp reassoc ninf nsz ogt <8 x float> %362, splat (float 0x3EB0C6F7A0000000)
  %523 = select <8 x i1> %515, <8 x i1> %519, <8 x i1> zeroinitializer
  %524 = select <8 x i1> %516, <8 x i1> %520, <8 x i1> zeroinitializer
  %525 = select <8 x i1> %517, <8 x i1> %521, <8 x i1> zeroinitializer
  %526 = select <8 x i1> %518, <8 x i1> %522, <8 x i1> zeroinitializer
  %527 = fcmp reassoc ninf nsz ogt <8 x float> %343, splat (float 0x3EB0C6F7A0000000)
  %528 = fcmp reassoc ninf nsz ogt <8 x float> %344, splat (float 0x3EB0C6F7A0000000)
  %529 = fcmp reassoc ninf nsz ogt <8 x float> %345, splat (float 0x3EB0C6F7A0000000)
  %530 = fcmp reassoc ninf nsz ogt <8 x float> %346, splat (float 0x3EB0C6F7A0000000)
  %531 = fcmp reassoc ninf nsz ogt <8 x float> %355, splat (float 0x3EB0C6F7A0000000)
  %532 = fcmp reassoc ninf nsz ogt <8 x float> %356, splat (float 0x3EB0C6F7A0000000)
  %533 = fcmp reassoc ninf nsz ogt <8 x float> %357, splat (float 0x3EB0C6F7A0000000)
  %534 = fcmp reassoc ninf nsz ogt <8 x float> %358, splat (float 0x3EB0C6F7A0000000)
  %535 = select <8 x i1> %527, <8 x i1> %531, <8 x i1> zeroinitializer
  %536 = select <8 x i1> %528, <8 x i1> %532, <8 x i1> zeroinitializer
  %537 = select <8 x i1> %529, <8 x i1> %533, <8 x i1> zeroinitializer
  %538 = select <8 x i1> %530, <8 x i1> %534, <8 x i1> zeroinitializer
  %539 = select <8 x i1> %523, <8 x i1> %535, <8 x i1> zeroinitializer
  %540 = select <8 x i1> %524, <8 x i1> %536, <8 x i1> zeroinitializer
  %541 = select <8 x i1> %525, <8 x i1> %537, <8 x i1> zeroinitializer
  %542 = select <8 x i1> %526, <8 x i1> %538, <8 x i1> zeroinitializer
  %543 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather214
  %544 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather215
  %545 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather216
  %546 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather229, %wide.masked.gather217
  %547 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather232, %wide.masked.gather220
  %548 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather233, %wide.masked.gather221
  %549 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather234, %wide.masked.gather222
  %550 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather235, %wide.masked.gather223
  %551 = fadd reassoc ninf nsz <8 x float> %547, %543
  %552 = fadd reassoc ninf nsz <8 x float> %548, %544
  %553 = fadd reassoc ninf nsz <8 x float> %549, %545
  %554 = fadd reassoc ninf nsz <8 x float> %550, %546
  %555 = fmul reassoc ninf nsz <8 x float> %355, %343
  %556 = fmul reassoc ninf nsz <8 x float> %356, %344
  %557 = fmul reassoc ninf nsz <8 x float> %357, %345
  %558 = fmul reassoc ninf nsz <8 x float> %358, %346
  %559 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %555)
  %560 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %556)
  %561 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %557)
  %562 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %558)
  %563 = fdiv reassoc ninf nsz <8 x float> %551, %559
  %564 = fdiv reassoc ninf nsz <8 x float> %552, %560
  %565 = fdiv reassoc ninf nsz <8 x float> %553, %561
  %566 = fdiv reassoc ninf nsz <8 x float> %554, %562
  %567 = fcmp reassoc ninf nsz ule <8 x float> %359, %387
  %568 = fcmp reassoc ninf nsz ule <8 x float> %360, %388
  %569 = fcmp reassoc ninf nsz ule <8 x float> %361, %389
  %570 = fcmp reassoc ninf nsz ule <8 x float> %362, %390
  %571 = fcmp reassoc ninf nsz uge <8 x float> %563, splat (float 0x3FC99999A0000000)
  %572 = fcmp reassoc ninf nsz uge <8 x float> %564, splat (float 0x3FC99999A0000000)
  %573 = fcmp reassoc ninf nsz uge <8 x float> %565, splat (float 0x3FC99999A0000000)
  %574 = fcmp reassoc ninf nsz uge <8 x float> %566, splat (float 0x3FC99999A0000000)
  %.not371 = select <8 x i1> %567, <8 x i1> splat (i1 true), <8 x i1> %571
  %.not374 = select <8 x i1> %568, <8 x i1> splat (i1 true), <8 x i1> %572
  %.not377 = select <8 x i1> %569, <8 x i1> splat (i1 true), <8 x i1> %573
  %.not380 = select <8 x i1> %570, <8 x i1> splat (i1 true), <8 x i1> %574
  %575 = select <8 x i1> %539, <8 x i1> %.not371, <8 x i1> zeroinitializer
  %576 = select <8 x i1> %540, <8 x i1> %.not374, <8 x i1> zeroinitializer
  %577 = select <8 x i1> %541, <8 x i1> %.not377, <8 x i1> zeroinitializer
  %578 = select <8 x i1> %542, <8 x i1> %.not380, <8 x i1> zeroinitializer
  %579 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %563, <8 x float> zeroinitializer)
  %580 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %564, <8 x float> zeroinitializer)
  %581 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %565, <8 x float> zeroinitializer)
  %582 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %566, <8 x float> zeroinitializer)
  %583 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %359)
  %584 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %360)
  %585 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %361)
  %586 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %362)
  %587 = fmul reassoc ninf nsz <8 x float> %583, %broadcast.splat256
  %588 = fmul reassoc ninf nsz <8 x float> %584, %broadcast.splat256
  %589 = fmul reassoc ninf nsz <8 x float> %585, %broadcast.splat256
  %590 = fmul reassoc ninf nsz <8 x float> %586, %broadcast.splat256
  %591 = fmul reassoc ninf nsz <8 x float> %587, %579
  %.fr = freeze <8 x float> %591
  %592 = fmul reassoc ninf nsz <8 x float> %588, %580
  %.fr381 = freeze <8 x float> %592
  %593 = fmul reassoc ninf nsz <8 x float> %589, %581
  %.fr382 = freeze <8 x float> %593
  %594 = fmul reassoc ninf nsz <8 x float> %590, %582
  %.fr383 = freeze <8 x float> %594
  %595 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %596 = fcmp reassoc nsz ogt <8 x float> %.fr381, splat (float 3.000000e+00)
  %597 = fcmp reassoc nsz ogt <8 x float> %.fr382, splat (float 3.000000e+00)
  %598 = fcmp reassoc nsz ogt <8 x float> %.fr383, splat (float 3.000000e+00)
  %599 = xor <8 x i1> %595, splat (i1 true)
  %600 = xor <8 x i1> %596, splat (i1 true)
  %601 = xor <8 x i1> %597, splat (i1 true)
  %602 = xor <8 x i1> %598, splat (i1 true)
  %603 = and <8 x i1> %575, %599
  %604 = and <8 x i1> %576, %600
  %605 = and <8 x i1> %577, %601
  %606 = and <8 x i1> %578, %602
  %607 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %608 = fcmp reassoc nsz olt <8 x float> %.fr381, splat (float -3.000000e+00)
  %609 = fcmp reassoc nsz olt <8 x float> %.fr382, splat (float -3.000000e+00)
  %610 = fcmp reassoc nsz olt <8 x float> %.fr383, splat (float -3.000000e+00)
  %611 = xor <8 x i1> %607, splat (i1 true)
  %612 = xor <8 x i1> %608, splat (i1 true)
  %613 = xor <8 x i1> %609, splat (i1 true)
  %614 = xor <8 x i1> %610, splat (i1 true)
  %615 = and <8 x i1> %603, %611
  %616 = and <8 x i1> %604, %612
  %617 = and <8 x i1> %605, %613
  %618 = and <8 x i1> %606, %614
  %619 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %620 = fmul reassoc ninf nsz <8 x float> %.fr381, %.fr381
  %621 = fmul reassoc ninf nsz <8 x float> %.fr382, %.fr382
  %622 = fmul reassoc ninf nsz <8 x float> %.fr383, %.fr383
  %623 = fadd reassoc ninf nsz <8 x float> %619, splat (float 2.700000e+01)
  %624 = fadd reassoc ninf nsz <8 x float> %620, splat (float 2.700000e+01)
  %625 = fadd reassoc ninf nsz <8 x float> %621, splat (float 2.700000e+01)
  %626 = fadd reassoc ninf nsz <8 x float> %622, splat (float 2.700000e+01)
  %627 = fmul reassoc ninf nsz <8 x float> %623, %.fr
  %628 = fmul reassoc ninf nsz <8 x float> %624, %.fr381
  %629 = fmul reassoc ninf nsz <8 x float> %625, %.fr382
  %630 = fmul reassoc ninf nsz <8 x float> %626, %.fr383
  %631 = fmul reassoc ninf nsz <8 x float> %619, splat (float 9.000000e+00)
  %632 = fmul reassoc ninf nsz <8 x float> %620, splat (float 9.000000e+00)
  %633 = fmul reassoc ninf nsz <8 x float> %621, splat (float 9.000000e+00)
  %634 = fmul reassoc ninf nsz <8 x float> %622, splat (float 9.000000e+00)
  %635 = fadd reassoc ninf nsz <8 x float> %631, splat (float 2.700000e+01)
  %636 = fadd reassoc ninf nsz <8 x float> %632, splat (float 2.700000e+01)
  %637 = fadd reassoc ninf nsz <8 x float> %633, splat (float 2.700000e+01)
  %638 = fadd reassoc ninf nsz <8 x float> %634, splat (float 2.700000e+01)
  %639 = fdiv reassoc ninf nsz <8 x float> %627, %635
  %640 = fdiv reassoc ninf nsz <8 x float> %628, %636
  %641 = fdiv reassoc ninf nsz <8 x float> %629, %637
  %642 = fdiv reassoc ninf nsz <8 x float> %630, %638
  %643 = fadd reassoc ninf nsz <8 x float> %639, splat (float 1.000000e+00)
  %644 = fadd reassoc ninf nsz <8 x float> %640, splat (float 1.000000e+00)
  %645 = fadd reassoc ninf nsz <8 x float> %641, splat (float 1.000000e+00)
  %646 = fadd reassoc ninf nsz <8 x float> %642, splat (float 1.000000e+00)
  %647 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %563
  %648 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %564
  %649 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %565
  %650 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %566
  %651 = fmul reassoc ninf nsz <8 x float> %647, %283
  %652 = fmul reassoc ninf nsz <8 x float> %648, %284
  %653 = fmul reassoc ninf nsz <8 x float> %649, %285
  %654 = fmul reassoc ninf nsz <8 x float> %650, %286
  %655 = and <8 x i1> %603, %607
  %656 = and <8 x i1> %604, %608
  %657 = and <8 x i1> %605, %609
  %658 = and <8 x i1> %606, %610
  %659 = and <8 x i1> %575, %595
  %660 = and <8 x i1> %576, %596
  %661 = and <8 x i1> %577, %597
  %662 = and <8 x i1> %578, %598
  %663 = xor <8 x i1> %535, splat (i1 true)
  %664 = xor <8 x i1> %536, splat (i1 true)
  %665 = xor <8 x i1> %537, splat (i1 true)
  %666 = xor <8 x i1> %538, splat (i1 true)
  %667 = select <8 x i1> %523, <8 x i1> %663, <8 x i1> zeroinitializer
  %668 = select <8 x i1> %524, <8 x i1> %664, <8 x i1> zeroinitializer
  %669 = select <8 x i1> %525, <8 x i1> %665, <8 x i1> zeroinitializer
  %670 = select <8 x i1> %526, <8 x i1> %666, <8 x i1> zeroinitializer
  %671 = xor <8 x i1> %519, splat (i1 true)
  %672 = xor <8 x i1> %520, splat (i1 true)
  %673 = xor <8 x i1> %521, splat (i1 true)
  %674 = xor <8 x i1> %522, splat (i1 true)
  %675 = select <8 x i1> %515, <8 x i1> %671, <8 x i1> zeroinitializer
  %676 = select <8 x i1> %516, <8 x i1> %672, <8 x i1> zeroinitializer
  %677 = select <8 x i1> %517, <8 x i1> %673, <8 x i1> zeroinitializer
  %678 = select <8 x i1> %518, <8 x i1> %674, <8 x i1> zeroinitializer
  %679 = select <8 x i1> %575, <8 x i1> splat (i1 true), <8 x i1> %675
  %680 = select <8 x i1> %679, <8 x i1> splat (i1 true), <8 x i1> %667
  %predphi261 = select <8 x i1> %680, <8 x float> %283, <8 x float> %651
  %681 = select <8 x i1> %576, <8 x i1> splat (i1 true), <8 x i1> %676
  %682 = select <8 x i1> %681, <8 x i1> splat (i1 true), <8 x i1> %668
  %predphi266 = select <8 x i1> %682, <8 x float> %284, <8 x float> %652
  %683 = select <8 x i1> %577, <8 x i1> splat (i1 true), <8 x i1> %677
  %684 = select <8 x i1> %683, <8 x i1> splat (i1 true), <8 x i1> %669
  %predphi271 = select <8 x i1> %684, <8 x float> %285, <8 x float> %653
  %685 = select <8 x i1> %578, <8 x i1> splat (i1 true), <8 x i1> %678
  %686 = select <8 x i1> %685, <8 x i1> splat (i1 true), <8 x i1> %670
  %predphi276 = select <8 x i1> %686, <8 x float> %286, <8 x float> %654
  %predphi279 = select <8 x i1> %659, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi280 = select <8 x i1> %615, <8 x float> %643, <8 x float> %predphi279
  %predphi281 = select <8 x i1> %655, <8 x float> zeroinitializer, <8 x float> %predphi280
  %predphi284 = select <8 x i1> %660, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi285 = select <8 x i1> %616, <8 x float> %644, <8 x float> %predphi284
  %predphi286 = select <8 x i1> %656, <8 x float> zeroinitializer, <8 x float> %predphi285
  %predphi289 = select <8 x i1> %661, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi290 = select <8 x i1> %617, <8 x float> %645, <8 x float> %predphi289
  %predphi291 = select <8 x i1> %657, <8 x float> zeroinitializer, <8 x float> %predphi290
  %predphi294 = select <8 x i1> %662, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi295 = select <8 x i1> %618, <8 x float> %646, <8 x float> %predphi294
  %predphi296 = select <8 x i1> %658, <8 x float> zeroinitializer, <8 x float> %predphi295
  %687 = fmul reassoc ninf nsz <8 x float> %predphi281, %predphi242
  %688 = fmul reassoc ninf nsz <8 x float> %predphi286, %predphi246
  %689 = fmul reassoc ninf nsz <8 x float> %predphi291, %predphi250
  %690 = fmul reassoc ninf nsz <8 x float> %predphi296, %predphi254
  %691 = fmul reassoc ninf nsz <8 x float> %687, %predphi261
  %692 = fmul reassoc ninf nsz <8 x float> %688, %predphi266
  %693 = fmul reassoc ninf nsz <8 x float> %689, %predphi271
  %694 = fmul reassoc ninf nsz <8 x float> %690, %predphi276
  %695 = fadd reassoc ninf nsz <8 x float> %691, %vec.phi195
  %696 = fadd reassoc ninf nsz <8 x float> %692, %vec.phi196
  %697 = fadd reassoc ninf nsz <8 x float> %693, %vec.phi197
  %698 = fadd reassoc ninf nsz <8 x float> %694, %vec.phi198
  %699 = fadd reassoc ninf nsz <8 x float> %687, %vec.phi191
  %700 = fadd reassoc ninf nsz <8 x float> %688, %vec.phi192
  %701 = fadd reassoc ninf nsz <8 x float> %689, %vec.phi193
  %702 = fadd reassoc ninf nsz <8 x float> %690, %vec.phi194
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %703 = icmp eq i64 %lsr.iv.next, 0
  br i1 %703, label %middle.block180, label %vector.body189, !llvm.loop !11

middle.block180:                                  ; preds = %vector.body189
  %bin.rdx298 = fadd reassoc ninf nsz <8 x float> %700, %699
  %bin.rdx299 = fadd reassoc ninf nsz <8 x float> %701, %bin.rdx298
  %bin.rdx300 = fadd reassoc ninf nsz <8 x float> %702, %bin.rdx299
  %704 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx300)
  %bin.rdx301 = fadd reassoc ninf nsz <8 x float> %696, %695
  %bin.rdx302 = fadd reassoc ninf nsz <8 x float> %697, %bin.rdx301
  %bin.rdx303 = fadd reassoc ninf nsz <8 x float> %698, %bin.rdx302
  %705 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx303)
  br i1 %cmp.n304, label %for_loop_test23.after_for22_crit_edge.us, label %vec.epilog.iter.check311

vec.epilog.iter.check311:                         ; preds = %middle.block180
  br i1 %min.epilog.iters.check313, label %for_loop_body20.us.preheader, label %vec.epilog.ph310

vec.epilog.ph310:                                 ; preds = %vec.epilog.iter.check311, %vector.main.loop.iter.check185
  %bc.resume.val305 = phi i64 [ %n.vec188, %vec.epilog.iter.check311 ], [ 0, %vector.main.loop.iter.check185 ]
  %bc.merge.rdx306 = phi float [ %704, %vec.epilog.iter.check311 ], [ %.065100.us, %vector.main.loop.iter.check185 ]
  %bc.merge.rdx307 = phi float [ %705, %vec.epilog.iter.check311 ], [ %.06799.us, %vector.main.loop.iter.check185 ]
  %706 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx306, i64 0
  %707 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx307, i64 0
  %708 = trunc nuw nsw i64 %bc.resume.val305 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %708, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert326 = insertelement <8 x i32> poison, i32 %221, i64 0
  %broadcast.splat327 = shufflevector <8 x i32> %broadcast.splatinsert326, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert329 = insertelement <8 x i32> poison, i32 %222, i64 0
  %broadcast.splat330 = shufflevector <8 x i32> %broadcast.splatinsert329, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert332 = insertelement <8 x i32> poison, i32 %223, i64 0
  %broadcast.splat333 = shufflevector <8 x i32> %broadcast.splatinsert332, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert335 = insertelement <8 x i32> poison, i32 %224, i64 0
  %broadcast.splat336 = shufflevector <8 x i32> %broadcast.splatinsert335, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert338 = insertelement <8 x i32> poison, i32 %225, i64 0
  %broadcast.splat339 = shufflevector <8 x i32> %broadcast.splatinsert338, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert341 = insertelement <8 x i32> poison, i32 %226, i64 0
  %broadcast.splat342 = shufflevector <8 x i32> %broadcast.splatinsert341, <8 x i32> poison, <8 x i32> zeroinitializer
  %709 = add i64 %217, %bc.resume.val305
  br label %vec.epilog.vector.body318

vec.epilog.vector.body318:                        ; preds = %vec.epilog.vector.body318, %vec.epilog.ph310
  %lsr.iv451 = phi i64 [ %lsr.iv.next452, %vec.epilog.vector.body318 ], [ %709, %vec.epilog.ph310 ]
  %vec.phi320 = phi <8 x float> [ %706, %vec.epilog.ph310 ], [ %823, %vec.epilog.vector.body318 ]
  %vec.phi321 = phi <8 x float> [ %707, %vec.epilog.ph310 ], [ %822, %vec.epilog.vector.body318 ]
  %vec.ind322 = phi <8 x i32> [ %induction, %vec.epilog.ph310 ], [ %vec.ind.next323, %vec.epilog.vector.body318 ]
  %710 = shl <8 x i32> %vec.ind322, splat (i32 1)
  %711 = add <8 x i32> %broadcast.splat200, %710
  %712 = add <8 x i32> %broadcast.splat327, %711
  %713 = sext <8 x i32> %712 to <8 x i64>
  %714 = getelementptr float, ptr %183, <8 x i64> %713
  %wide.masked.gather328 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %714, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %715 = add <8 x i32> %711, %broadcast.splat330
  %716 = sext <8 x i32> %715 to <8 x i64>
  %717 = getelementptr float, ptr %106, <8 x i64> %716
  %wide.masked.gather331 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %717, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %718 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather328, %wide.masked.gather331
  %719 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %718)
  %720 = add <8 x i32> %broadcast.splat333, %711
  %721 = sext <8 x i32> %720 to <8 x i64>
  %722 = getelementptr float, ptr %185, <8 x i64> %721
  %wide.masked.gather334 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %722, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %723 = add <8 x i32> %broadcast.splat336, %711
  %724 = sext <8 x i32> %723 to <8 x i64>
  %725 = getelementptr float, ptr %187, <8 x i64> %724
  %wide.masked.gather337 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %725, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %726 = add <8 x i32> %broadcast.splat339, %711
  %727 = sext <8 x i32> %726 to <8 x i64>
  %728 = getelementptr float, ptr %189, <8 x i64> %727
  %wide.masked.gather340 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %728, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %729 = add <8 x i32> %broadcast.splat342, %711
  %730 = sext <8 x i32> %729 to <8 x i64>
  %731 = getelementptr float, ptr %191, <8 x i64> %730
  %wide.masked.gather343 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %731, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %732 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather334, %wide.masked.gather334
  %733 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather337, %wide.masked.gather337
  %734 = fadd reassoc ninf nsz <8 x float> %733, %732
  %735 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather340, %wide.masked.gather340
  %736 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather343, %wide.masked.gather343
  %737 = fadd reassoc ninf nsz <8 x float> %736, %735
  %738 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %734, <8 x float> %737)
  %739 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather331, splat (float -2.000000e+00)
  %740 = fadd reassoc ninf nsz <8 x float> %739, splat (float 3.000000e+00)
  %741 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %740, <8 x float> splat (float 3.000000e+00))
  %742 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %741, <8 x float> splat (float 1.000000e+00))
  %743 = fmul reassoc ninf nsz <8 x float> %742, %broadcast.splat237
  %744 = fmul reassoc ninf nsz <8 x float> %742, %742
  %745 = fmul reassoc ninf nsz <8 x float> %744, %broadcast.splat239
  %746 = fcmp reassoc ninf nsz olt <8 x float> %738, %745
  %747 = xor <8 x i1> %746, splat (i1 true)
  %748 = select <8 x i1> %broadcast.splat, <8 x i1> %747, <8 x i1> zeroinitializer
  %749 = fcmp reassoc ninf nsz olt <8 x float> %719, %743
  %750 = xor <8 x i1> %749, splat (i1 true)
  %751 = select <8 x i1> %748, <8 x i1> %750, <8 x i1> zeroinitializer
  %752 = fmul reassoc ninf nsz <8 x float> %743, splat (float 4.000000e+00)
  %753 = fdiv reassoc ninf nsz <8 x float> %719, %752
  %754 = fcmp reassoc ninf nsz ogt <8 x float> %753, splat (float 1.000000e+00)
  %755 = select <8 x i1> %754, <8 x float> splat (float 1.000000e+00), <8 x float> %753
  %756 = fmul reassoc ninf nsz <8 x float> %755, splat (float 0x3FD99999A0000000)
  %757 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %756
  %758 = select <8 x i1> %748, <8 x i1> %749, <8 x i1> zeroinitializer
  %759 = fmul reassoc ninf nsz <8 x float> %719, splat (float 0x3FC3333340000000)
  %760 = fdiv reassoc ninf nsz <8 x float> %759, %743
  %761 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %760
  %762 = select <8 x i1> %broadcast.splat, <8 x i1> %746, <8 x i1> zeroinitializer
  %763 = fmul reassoc ninf nsz <8 x float> %743, splat (float 1.500000e+00)
  %764 = fcmp reassoc ninf nsz uge <8 x float> %719, %763
  %765 = select <8 x i1> %762, <8 x i1> %764, <8 x i1> zeroinitializer
  %766 = fsub reassoc ninf nsz <8 x float> %719, %763
  %767 = fdiv reassoc ninf nsz <8 x float> %766, %763
  %768 = fcmp reassoc ninf nsz ogt <8 x float> %767, splat (float 1.000000e+00)
  %769 = select <8 x i1> %768, <8 x float> splat (float 1.000000e+00), <8 x float> %767
  %770 = fmul reassoc ninf nsz <8 x float> %769, splat (float 0x3FC99999A0000000)
  %771 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %770
  %772 = fmul reassoc ninf nsz <8 x float> %719, splat (float 0x3FEE666660000000)
  %773 = fdiv reassoc ninf nsz <8 x float> %772, %763
  %774 = fadd reassoc ninf nsz <8 x float> %773, splat (float 0x3FA99999A0000000)
  %775 = or <8 x i1> %758, %214
  %776 = or <8 x i1> %775, %762
  %777 = or <8 x i1> %776, %751
  %predphi348 = select <8 x i1> %765, <8 x float> %771, <8 x float> %774
  %predphi349 = select <8 x i1> %758, <8 x float> %761, <8 x float> %predphi348
  %predphi350 = select <8 x i1> %751, <8 x float> %757, <8 x float> %predphi349
  %predphi351 = select <8 x i1> %broadcast.splat, <8 x float> %predphi350, <8 x float> splat (float 1.000000e+00)
  %778 = fcmp reassoc ninf nsz ogt <8 x float> %738, splat (float 0x3EB0C6F7A0000000)
  %779 = select <8 x i1> %777, <8 x i1> %778, <8 x i1> zeroinitializer
  %780 = fcmp reassoc ninf nsz ogt <8 x float> %734, splat (float 0x3EB0C6F7A0000000)
  %781 = fcmp reassoc ninf nsz ogt <8 x float> %737, splat (float 0x3EB0C6F7A0000000)
  %782 = select <8 x i1> %780, <8 x i1> %781, <8 x i1> zeroinitializer
  %783 = select <8 x i1> %779, <8 x i1> %782, <8 x i1> zeroinitializer
  %784 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather340, %wide.masked.gather334
  %785 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather343, %wide.masked.gather337
  %786 = fadd reassoc ninf nsz <8 x float> %785, %784
  %787 = fmul reassoc ninf nsz <8 x float> %737, %734
  %788 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %787)
  %789 = fdiv reassoc ninf nsz <8 x float> %786, %788
  %790 = fcmp reassoc ninf nsz ule <8 x float> %738, %745
  %791 = fcmp reassoc ninf nsz uge <8 x float> %789, splat (float 0x3FC99999A0000000)
  %.not386 = select <8 x i1> %790, <8 x i1> splat (i1 true), <8 x i1> %791
  %792 = select <8 x i1> %783, <8 x i1> %.not386, <8 x i1> zeroinitializer
  %793 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %789, <8 x float> zeroinitializer)
  %794 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %738)
  %795 = fmul reassoc ninf nsz <8 x float> %794, %broadcast.splat256
  %796 = fmul reassoc ninf nsz <8 x float> %795, %793
  %.fr387 = freeze <8 x float> %796
  %797 = fcmp reassoc nsz ogt <8 x float> %.fr387, splat (float 3.000000e+00)
  %798 = xor <8 x i1> %797, splat (i1 true)
  %799 = and <8 x i1> %792, %798
  %800 = fcmp reassoc nsz olt <8 x float> %.fr387, splat (float -3.000000e+00)
  %801 = xor <8 x i1> %800, splat (i1 true)
  %802 = and <8 x i1> %799, %801
  %803 = fmul reassoc ninf nsz <8 x float> %.fr387, %.fr387
  %804 = fadd reassoc ninf nsz <8 x float> %803, splat (float 2.700000e+01)
  %805 = fmul reassoc ninf nsz <8 x float> %804, %.fr387
  %806 = fmul reassoc ninf nsz <8 x float> %803, splat (float 9.000000e+00)
  %807 = fadd reassoc ninf nsz <8 x float> %806, splat (float 2.700000e+01)
  %808 = fdiv reassoc ninf nsz <8 x float> %805, %807
  %809 = fadd reassoc ninf nsz <8 x float> %808, splat (float 1.000000e+00)
  %810 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %789
  %811 = fmul reassoc ninf nsz <8 x float> %810, %719
  %812 = and <8 x i1> %799, %800
  %813 = and <8 x i1> %792, %797
  %814 = xor <8 x i1> %782, splat (i1 true)
  %815 = select <8 x i1> %779, <8 x i1> %814, <8 x i1> zeroinitializer
  %816 = xor <8 x i1> %778, splat (i1 true)
  %817 = select <8 x i1> %777, <8 x i1> %816, <8 x i1> zeroinitializer
  %818 = select <8 x i1> %792, <8 x i1> splat (i1 true), <8 x i1> %817
  %819 = select <8 x i1> %818, <8 x i1> splat (i1 true), <8 x i1> %815
  %predphi358 = select <8 x i1> %819, <8 x float> %719, <8 x float> %811
  %predphi361 = select <8 x i1> %813, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi362 = select <8 x i1> %802, <8 x float> %809, <8 x float> %predphi361
  %predphi363 = select <8 x i1> %812, <8 x float> zeroinitializer, <8 x float> %predphi362
  %820 = fmul reassoc ninf nsz <8 x float> %predphi363, %predphi351
  %821 = fmul reassoc ninf nsz <8 x float> %820, %predphi358
  %822 = fadd reassoc ninf nsz <8 x float> %821, %vec.phi321
  %823 = fadd reassoc ninf nsz <8 x float> %820, %vec.phi320
  %vec.ind.next323 = add <8 x i32> %vec.ind322, splat (i32 8)
  %lsr.iv.next452 = add i64 %lsr.iv451, 8
  %824 = icmp eq i64 %lsr.iv.next452, 0
  br i1 %824, label %vec.epilog.middle.block308, label %vec.epilog.vector.body318, !llvm.loop !14

vec.epilog.middle.block308:                       ; preds = %vec.epilog.vector.body318
  %825 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %823)
  %826 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %822)
  br i1 %cmp.n365, label %for_loop_test23.after_for22_crit_edge.us, label %for_loop_body20.us.preheader

for_loop_body20.us.preheader:                     ; preds = %vec.epilog.middle.block308, %vec.epilog.iter.check311, %vector.scevcheck164, %iter.check183
  %indvars.iv.ph = phi i64 [ %n.vec188, %vec.epilog.iter.check311 ], [ 0, %iter.check183 ], [ 0, %vector.scevcheck164 ], [ %n.vec315, %vec.epilog.middle.block308 ]
  %.16696.us.ph = phi float [ %704, %vec.epilog.iter.check311 ], [ %.065100.us, %iter.check183 ], [ %.065100.us, %vector.scevcheck164 ], [ %825, %vec.epilog.middle.block308 ]
  %.16895.us.ph = phi float [ %705, %vec.epilog.iter.check311 ], [ %.06799.us, %iter.check183 ], [ %.06799.us, %vector.scevcheck164 ], [ %826, %vec.epilog.middle.block308 ]
  %827 = trunc i64 %indvars.iv.ph to i32
  %828 = shl nuw i32 %827, 1
  %829 = add i64 %218, %indvars.iv.ph
  br label %for_loop_body20.us

for_loop_body20.us:                               ; preds = %after_if50.us, %for_loop_body20.us.preheader
  %lsr.iv477 = phi i64 [ %829, %for_loop_body20.us.preheader ], [ %lsr.iv.next478, %after_if50.us ]
  %lsr.iv475 = phi i32 [ %lsr.iv473, %for_loop_body20.us.preheader ], [ %lsr.iv.next476, %after_if50.us ]
  %lsr.iv471 = phi i32 [ %lsr.iv469, %for_loop_body20.us.preheader ], [ %lsr.iv.next472, %after_if50.us ]
  %lsr.iv467 = phi i32 [ %lsr.iv465, %for_loop_body20.us.preheader ], [ %lsr.iv.next468, %after_if50.us ]
  %lsr.iv463 = phi i32 [ %lsr.iv461, %for_loop_body20.us.preheader ], [ %lsr.iv.next464, %after_if50.us ]
  %lsr.iv459 = phi i32 [ %lsr.iv457, %for_loop_body20.us.preheader ], [ %lsr.iv.next460, %after_if50.us ]
  %lsr.iv455 = phi i32 [ %lsr.iv453, %for_loop_body20.us.preheader ], [ %lsr.iv.next456, %after_if50.us ]
  %.16696.us = phi float [ %918, %after_if50.us ], [ %.16696.us.ph, %for_loop_body20.us.preheader ]
  %.16895.us = phi float [ %917, %after_if50.us ], [ %.16895.us.ph, %for_loop_body20.us.preheader ]
  %830 = add i32 %828, %lsr.iv475
  %831 = sext i32 %830 to i64
  %832 = getelementptr float, ptr %183, i64 %831
  %833 = load float, ptr %832, align 4
  %834 = add i32 %828, %lsr.iv471
  %835 = sext i32 %834 to i64
  %836 = getelementptr float, ptr %106, i64 %835
  %837 = load float, ptr %836, align 4
  %838 = fsub reassoc ninf nsz float %833, %837
  %839 = tail call noundef float @llvm.fabs.f32(float %838)
  %840 = add i32 %828, %lsr.iv467
  %841 = sext i32 %840 to i64
  %842 = getelementptr float, ptr %185, i64 %841
  %843 = load float, ptr %842, align 4
  %844 = add i32 %828, %lsr.iv463
  %845 = sext i32 %844 to i64
  %846 = getelementptr float, ptr %187, i64 %845
  %847 = load float, ptr %846, align 4
  %848 = add i32 %828, %lsr.iv459
  %849 = sext i32 %848 to i64
  %850 = getelementptr float, ptr %189, i64 %849
  %851 = load float, ptr %850, align 4
  %852 = add i32 %828, %lsr.iv455
  %853 = sext i32 %852 to i64
  %854 = getelementptr float, ptr %191, i64 %853
  %855 = load float, ptr %854, align 4
  %856 = fmul reassoc ninf nsz float %843, %843
  %857 = fmul reassoc ninf nsz float %847, %847
  %858 = fadd reassoc ninf nsz float %857, %856
  %859 = fmul reassoc ninf nsz float %851, %851
  %860 = fmul reassoc ninf nsz float %855, %855
  %861 = fadd reassoc ninf nsz float %860, %859
  %862 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %858, float %861)
  %factor.us = fmul reassoc ninf nsz float %837, -2.000000e+00
  %863 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %864 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %863, float 3.000000e+00)
  %865 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %864, float 1.000000e+00)
  %866 = fmul reassoc ninf nsz float %865, %162
  %867 = fmul reassoc ninf nsz float %865, %865
  %868 = fmul reassoc ninf nsz float %867, %172
  br i1 %163, label %true_block24.us, label %after_if26.us

true_block24.us:                                  ; preds = %for_loop_body20.us
  %869 = fcmp reassoc ninf nsz olt float %862, %868
  br i1 %869, label %true_block27.us, label %false_block28.us

false_block28.us:                                 ; preds = %true_block24.us
  %870 = fcmp reassoc ninf nsz olt float %839, %866
  br i1 %870, label %true_block36.us, label %false_block37.us

false_block37.us:                                 ; preds = %false_block28.us
  %871 = fmul reassoc ninf nsz float %866, 4.000000e+00
  %872 = fdiv reassoc ninf nsz float %839, %871
  %873 = fcmp reassoc ninf nsz ogt float %872, 1.000000e+00
  %spec.store.select1.us = select i1 %873, float 1.000000e+00, float %872
  %874 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %875 = fsub reassoc ninf nsz float 0x3FE6666680000000, %874
  br label %after_if26.us

true_block36.us:                                  ; preds = %false_block28.us
  %876 = fmul reassoc ninf nsz float %839, 0x3FC3333340000000
  %877 = fdiv reassoc ninf nsz float %876, %866
  %878 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %877
  br label %after_if26.us

true_block27.us:                                  ; preds = %true_block24.us
  %879 = fmul reassoc ninf nsz float %866, 1.500000e+00
  %880 = fcmp reassoc ninf nsz olt float %839, %879
  br i1 %880, label %true_block30.us, label %false_block31.us

false_block31.us:                                 ; preds = %true_block27.us
  %881 = fsub reassoc ninf nsz float %839, %879
  %882 = fdiv reassoc ninf nsz float %881, %879
  %883 = fcmp reassoc ninf nsz ogt float %882, 1.000000e+00
  %spec.store.select.us = select i1 %883, float 1.000000e+00, float %882
  %884 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %885 = fsub reassoc ninf nsz float 1.000000e+00, %884
  br label %after_if26.us

true_block30.us:                                  ; preds = %true_block27.us
  %886 = fmul reassoc ninf nsz float %839, 0x3FEE666660000000
  %887 = fdiv reassoc ninf nsz float %886, %879
  %888 = fadd reassoc ninf nsz float %887, 0x3FA99999A0000000
  br label %after_if26.us

after_if26.us:                                    ; preds = %true_block30.us, %false_block31.us, %true_block36.us, %false_block37.us, %for_loop_body20.us
  %.061.us = phi float [ %888, %true_block30.us ], [ %885, %false_block31.us ], [ %878, %true_block36.us ], [ %875, %false_block37.us ], [ 1.000000e+00, %for_loop_body20.us ]
  %889 = fcmp reassoc ninf nsz ogt float %862, 0x3EB0C6F7A0000000
  br i1 %889, label %true_block42.us, label %after_if50.us

true_block42.us:                                  ; preds = %after_if26.us
  %890 = fcmp reassoc ninf nsz ogt float %858, 0x3EB0C6F7A0000000
  %891 = fcmp reassoc ninf nsz ogt float %861, 0x3EB0C6F7A0000000
  %.056.us = select i1 %890, i1 %891, i1 false
  br i1 %.056.us, label %true_block48.us, label %after_if50.us

true_block48.us:                                  ; preds = %true_block42.us
  %892 = fmul reassoc ninf nsz float %851, %843
  %893 = fmul reassoc ninf nsz float %855, %847
  %894 = fadd reassoc ninf nsz float %893, %892
  %895 = fmul reassoc ninf nsz float %861, %858
  %896 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %895)
  %897 = fdiv reassoc ninf nsz float %894, %896
  %898 = fcmp reassoc ninf nsz ogt float %862, %868
  %899 = fcmp reassoc ninf nsz olt float %897, 0x3FC99999A0000000
  %.055.us = select i1 %898, i1 %899, i1 false
  br i1 %.055.us, label %true_block54.us, label %false_block55.us

false_block55.us:                                 ; preds = %true_block48.us
  %900 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %897, float 0.000000e+00)
  %901 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %862)
  %902 = fmul reassoc ninf nsz float %901, %160
  %903 = fmul reassoc ninf nsz float %902, %900
  %904 = fcmp reassoc ninf nsz ogt float %903, 3.000000e+00
  br i1 %904, label %after_if50.us, label %false_block58.us

false_block58.us:                                 ; preds = %false_block55.us
  %905 = fcmp reassoc ninf nsz olt float %903, -3.000000e+00
  br i1 %905, label %after_if50.us, label %false_block61.us

false_block61.us:                                 ; preds = %false_block58.us
  %906 = fmul reassoc ninf nsz float %903, %903
  %907 = fadd reassoc ninf nsz float %906, 2.700000e+01
  %908 = fmul reassoc ninf nsz float %907, %903
  %909 = fmul reassoc ninf nsz float %906, 9.000000e+00
  %910 = fadd reassoc ninf nsz float %909, 2.700000e+01
  %911 = fdiv reassoc ninf nsz float %908, %910
  %912 = fadd reassoc ninf nsz float %911, 1.000000e+00
  br label %after_if50.us

true_block54.us:                                  ; preds = %true_block48.us
  %913 = fsub reassoc ninf nsz float 1.500000e+00, %897
  %914 = fmul reassoc ninf nsz float %913, %839
  br label %after_if50.us

after_if50.us:                                    ; preds = %true_block54.us, %false_block61.us, %false_block58.us, %false_block55.us, %true_block42.us, %after_if26.us
  %.062.us = phi float [ %914, %true_block54.us ], [ %839, %true_block42.us ], [ %839, %after_if26.us ], [ %839, %false_block55.us ], [ %839, %false_block61.us ], [ %839, %false_block58.us ]
  %.058.us = phi float [ 1.000000e+00, %true_block54.us ], [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %after_if26.us ], [ 2.000000e+00, %false_block55.us ], [ %912, %false_block61.us ], [ 0.000000e+00, %false_block58.us ]
  %915 = fmul reassoc ninf nsz float %.058.us, %.061.us
  %916 = fmul reassoc ninf nsz float %915, %.062.us
  %917 = fadd reassoc ninf nsz float %916, %.16895.us
  %918 = fadd reassoc ninf nsz float %915, %.16696.us
  %lsr.iv.next456 = add i32 %lsr.iv455, 2
  %lsr.iv.next460 = add i32 %lsr.iv459, 2
  %lsr.iv.next464 = add i32 %lsr.iv463, 2
  %lsr.iv.next468 = add i32 %lsr.iv467, 2
  %lsr.iv.next472 = add i32 %lsr.iv471, 2
  %lsr.iv.next476 = add i32 %lsr.iv475, 2
  %lsr.iv.next478 = add i64 %lsr.iv477, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next478, 0
  br i1 %exitcond.not, label %for_loop_test23.after_for22_crit_edge.us.loopexit, label %for_loop_body20.us, !llvm.loop !15

for_loop_test23.after_for22_crit_edge.us.loopexit: ; preds = %after_if50.us
  br label %for_loop_test23.after_for22_crit_edge.us

for_loop_test23.after_for22_crit_edge.us:         ; preds = %for_loop_test23.after_for22_crit_edge.us.loopexit, %vec.epilog.middle.block308, %middle.block180
  %.lcssa140 = phi float [ %705, %middle.block180 ], [ %826, %vec.epilog.middle.block308 ], [ %917, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %704, %middle.block180 ], [ %825, %vec.epilog.middle.block308 ], [ %918, %for_loop_test23.after_for22_crit_edge.us.loopexit ]
  %919 = add nuw nsw i32 %.064101.us, 1
  %lsr.iv.next454 = add i32 %lsr.iv453, %211
  %lsr.iv.next458 = add i32 %lsr.iv457, %208
  %lsr.iv.next462 = add i32 %lsr.iv461, %205
  %lsr.iv.next466 = add i32 %lsr.iv465, %202
  %lsr.iv.next470 = add i32 %lsr.iv469, %199
  %lsr.iv.next474 = add i32 %lsr.iv473, %196
  %exitcond123.not = icmp eq i32 %919, %164
  br i1 %exitcond123.not, label %after_for18, label %iter.check183

after_for18:                                      ; preds = %for_loop_test23.after_for22_crit_edge.us
  %920 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %920, label %for_loop_body66.lr.ph.split.us, label %false_block64

for_loop_body66.lr.ph.split.us:                   ; preds = %after_for18, %for_loop_body16.lr.ph, %true_block13
  %921 = getelementptr i8, ptr %75, i64 4
  %922 = getelementptr i8, ptr %75, i64 8
  %923 = load ptr, ptr %922, align 8
  %924 = load i32, ptr %921, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %66, i32 1)
  %smax129 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  %wide.trip.count127 = zext i32 %smax to i64
  %925 = add nsw i64 %wide.trip.count127, -1
  %926 = mul i32 %54, %924
  %927 = add i32 %58, %926
  %min.iters.check = icmp slt i32 %66, 4
  %928 = trunc nsw i64 %925 to i32
  %invariant.op447 = add i32 %927, %928
  %invariant.op449 = add i32 %115, %928
  %929 = icmp ugt i64 %925, 4294967295
  %min.iters.check142 = icmp slt i32 %66, 32
  %n.vec = and i64 %wide.trip.count127, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count127
  %n.vec.remaining = and i64 %wide.trip.count127, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec156 = and i64 %wide.trip.count127, 2147483644
  %cmp.n162 = icmp eq i64 %n.vec156, %wide.trip.count127
  %xtraiter = and i64 %wide.trip.count127, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %930 = lshr i64 %wide.trip.count127, 2
  %931 = mul nsw i64 %930, -4
  %932 = zext i32 %115 to i64
  %933 = zext i32 %108 to i64
  %934 = zext i32 %927 to i64
  %935 = zext i32 %924 to i64
  %936 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test73.after_for72_crit_edge.us, %for_loop_body66.lr.ph.split.us
  %lsr.iv497 = phi i64 [ %lsr.iv.next498, %for_loop_test73.after_for72_crit_edge.us ], [ %934, %for_loop_body66.lr.ph.split.us ]
  %lsr.iv495 = phi i64 [ %lsr.iv.next496, %for_loop_test73.after_for72_crit_edge.us ], [ %932, %for_loop_body66.lr.ph.split.us ]
  %.051110.us = phi i32 [ 0, %for_loop_body66.lr.ph.split.us ], [ %1041, %for_loop_test73.after_for72_crit_edge.us ]
  %.052109.us = phi float [ 0.000000e+00, %for_loop_body66.lr.ph.split.us ], [ %.lcssa141, %for_loop_test73.after_for72_crit_edge.us ]
  %lsr512 = trunc i64 %lsr.iv497 to i32
  %lsr510 = trunc i64 %lsr.iv495 to i32
  br i1 %min.iters.check, label %for_loop_body70.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %937 = mul i32 %108, %.051110.us
  %938 = add i32 %115, %937
  %939 = mul i32 %924, %.051110.us
  %940 = add i32 %927, %939
  %.reass448 = add i32 %939, %invariant.op447
  %941 = icmp slt i32 %.reass448, %940
  %.reass450 = add i32 %937, %invariant.op449
  %942 = icmp slt i32 %.reass450, %938
  %943 = or i1 %942, %929
  %944 = or i1 %941, %943
  br i1 %944, label %for_loop_body70.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check142, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %945 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.052109.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv487 = phi i32 [ %lsr.iv.next488, %vector.body ], [ %lsr510, %vector.ph ]
  %lsr.iv483 = phi i32 [ %lsr.iv.next484, %vector.body ], [ %lsr512, %vector.ph ]
  %lsr.iv479 = phi i64 [ %lsr.iv.next480, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %945, %vector.ph ], [ %964, %vector.body ]
  %vec.phi143 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %965, %vector.body ]
  %vec.phi144 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %966, %vector.body ]
  %vec.phi145 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %967, %vector.body ]
  %946 = sext i32 %lsr.iv483 to i64
  %947 = getelementptr float, ptr %923, i64 %946
  %948 = getelementptr i8, ptr %947, i64 32
  %949 = getelementptr i8, ptr %947, i64 64
  %950 = getelementptr i8, ptr %947, i64 96
  %wide.load = load <8 x float>, ptr %947, align 4
  %wide.load146 = load <8 x float>, ptr %948, align 4
  %wide.load147 = load <8 x float>, ptr %949, align 4
  %wide.load148 = load <8 x float>, ptr %950, align 4
  %951 = sext i32 %lsr.iv487 to i64
  %952 = getelementptr float, ptr %106, i64 %951
  %953 = getelementptr i8, ptr %952, i64 32
  %954 = getelementptr i8, ptr %952, i64 64
  %955 = getelementptr i8, ptr %952, i64 96
  %wide.load149 = load <8 x float>, ptr %952, align 4
  %wide.load150 = load <8 x float>, ptr %953, align 4
  %wide.load151 = load <8 x float>, ptr %954, align 4
  %wide.load152 = load <8 x float>, ptr %955, align 4
  %956 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load149
  %957 = fsub reassoc ninf nsz <8 x float> %wide.load146, %wide.load150
  %958 = fsub reassoc ninf nsz <8 x float> %wide.load147, %wide.load151
  %959 = fsub reassoc ninf nsz <8 x float> %wide.load148, %wide.load152
  %960 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %956)
  %961 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %957)
  %962 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %958)
  %963 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %959)
  %964 = fadd reassoc ninf nsz <8 x float> %960, %vec.phi
  %965 = fadd reassoc ninf nsz <8 x float> %961, %vec.phi143
  %966 = fadd reassoc ninf nsz <8 x float> %962, %vec.phi144
  %967 = fadd reassoc ninf nsz <8 x float> %963, %vec.phi145
  %lsr.iv.next480 = add nsw i64 %lsr.iv479, -32
  %lsr.iv.next484 = add i32 %lsr.iv483, 32
  %lsr.iv.next488 = add i32 %lsr.iv487, 32
  %968 = icmp eq i64 %lsr.iv.next480, 0
  br i1 %968, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %965, %964
  %bin.rdx153 = fadd reassoc ninf nsz <8 x float> %966, %bin.rdx
  %bin.rdx154 = fadd reassoc ninf nsz <8 x float> %967, %bin.rdx153
  %969 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx154)
  br i1 %cmp.n, label %for_loop_test73.after_for72_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body70.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %969, %vec.epilog.iter.check ], [ %.052109.us, %vector.main.loop.iter.check ]
  %970 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %971 = add i64 %931, %vec.epilog.resume.val
  %972 = trunc i64 %vec.epilog.resume.val to i32
  %973 = add i32 %lsr512, %972
  %974 = add i32 %lsr510, %972
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv493 = phi i32 [ %lsr.iv.next494, %vec.epilog.vector.body ], [ %974, %vec.epilog.ph ]
  %lsr.iv491 = phi i32 [ %lsr.iv.next492, %vec.epilog.vector.body ], [ %973, %vec.epilog.ph ]
  %lsr.iv489 = phi i64 [ %lsr.iv.next490, %vec.epilog.vector.body ], [ %971, %vec.epilog.ph ]
  %vec.phi158 = phi <4 x float> [ %970, %vec.epilog.ph ], [ %981, %vec.epilog.vector.body ]
  %975 = sext i32 %lsr.iv491 to i64
  %976 = getelementptr float, ptr %923, i64 %975
  %wide.load159 = load <4 x float>, ptr %976, align 4
  %977 = sext i32 %lsr.iv493 to i64
  %978 = getelementptr float, ptr %106, i64 %977
  %wide.load160 = load <4 x float>, ptr %978, align 4
  %979 = fsub reassoc ninf nsz <4 x float> %wide.load159, %wide.load160
  %980 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %979)
  %981 = fadd reassoc ninf nsz <4 x float> %980, %vec.phi158
  %lsr.iv.next490 = add i64 %lsr.iv489, 4
  %lsr.iv.next492 = add i32 %lsr.iv491, 4
  %lsr.iv.next494 = add i32 %lsr.iv493, 4
  %982 = icmp eq i64 %lsr.iv.next490, 0
  br i1 %982, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %983 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %981)
  br i1 %cmp.n162, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader

for_loop_body70.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv124.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec156, %vec.epilog.middle.block ]
  %.1105.us.ph = phi float [ %969, %vec.epilog.iter.check ], [ %.052109.us, %iter.check ], [ %.052109.us, %vector.scevcheck ], [ %983, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body70.us.prol.loopexit, label %for_loop_body70.us.prol.preheader

for_loop_body70.us.prol.preheader:                ; preds = %for_loop_body70.us.preheader
  br label %for_loop_body70.us.prol

for_loop_body70.us.prol:                          ; preds = %for_loop_body70.us.prol, %for_loop_body70.us.prol.preheader
  %lsr.iv500 = phi i64 [ %936, %for_loop_body70.us.prol.preheader ], [ %lsr.iv.next501, %for_loop_body70.us.prol ]
  %indvars.iv124.prol = phi i64 [ %indvars.iv.next125.prol, %for_loop_body70.us.prol ], [ %indvars.iv124.ph, %for_loop_body70.us.prol.preheader ]
  %.1105.us.prol = phi float [ %994, %for_loop_body70.us.prol ], [ %.1105.us.ph, %for_loop_body70.us.prol.preheader ]
  %984 = add i64 %lsr.iv497, %indvars.iv124.prol
  %tmp499 = trunc i64 %984 to i32
  %985 = sext i32 %tmp499 to i64
  %986 = getelementptr float, ptr %923, i64 %985
  %987 = load float, ptr %986, align 4
  %988 = add i64 %lsr.iv495, %indvars.iv124.prol
  %tmp = trunc i64 %988 to i32
  %989 = sext i32 %tmp to i64
  %990 = getelementptr float, ptr %106, i64 %989
  %991 = load float, ptr %990, align 4
  %992 = fsub reassoc ninf nsz float %987, %991
  %993 = tail call noundef float @llvm.fabs.f32(float %992)
  %994 = fadd reassoc ninf nsz float %993, %.1105.us.prol
  %indvars.iv.next125.prol = add nuw nsw i64 %indvars.iv124.prol, 1
  %lsr.iv.next501 = add nsw i64 %lsr.iv500, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next501, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body70.us.prol.loopexit.loopexit, label %for_loop_body70.us.prol, !llvm.loop !18

for_loop_body70.us.prol.loopexit.loopexit:        ; preds = %for_loop_body70.us.prol
  br label %for_loop_body70.us.prol.loopexit

for_loop_body70.us.prol.loopexit:                 ; preds = %for_loop_body70.us.prol.loopexit.loopexit, %for_loop_body70.us.preheader
  %.lcssa405.unr = phi float [ poison, %for_loop_body70.us.preheader ], [ %994, %for_loop_body70.us.prol.loopexit.loopexit ]
  %indvars.iv124.unr = phi i64 [ %indvars.iv124.ph, %for_loop_body70.us.preheader ], [ %indvars.iv.next125.prol, %for_loop_body70.us.prol.loopexit.loopexit ]
  %.1105.us.unr = phi float [ %.1105.us.ph, %for_loop_body70.us.preheader ], [ %994, %for_loop_body70.us.prol.loopexit.loopexit ]
  %995 = sub nsw i64 %indvars.iv124.ph, %wide.trip.count127
  %996 = icmp ugt i64 %995, -4
  br i1 %996, label %for_loop_test73.after_for72_crit_edge.us, label %for_loop_body70.us.preheader.new

for_loop_body70.us.preheader.new:                 ; preds = %for_loop_body70.us.prol.loopexit
  br label %for_loop_body70.us

for_loop_body70.us:                               ; preds = %for_loop_body70.us, %for_loop_body70.us.preheader.new
  %indvars.iv124 = phi i64 [ %indvars.iv124.unr, %for_loop_body70.us.preheader.new ], [ %indvars.iv.next125.3, %for_loop_body70.us ]
  %.1105.us = phi float [ %.1105.us.unr, %for_loop_body70.us.preheader.new ], [ %1040, %for_loop_body70.us ]
  %997 = add i64 %lsr.iv497, %indvars.iv124
  %tmp509 = trunc i64 %997 to i32
  %998 = sext i32 %tmp509 to i64
  %999 = getelementptr float, ptr %923, i64 %998
  %1000 = load float, ptr %999, align 4
  %1001 = add i64 %lsr.iv495, %indvars.iv124
  %tmp508 = trunc i64 %1001 to i32
  %1002 = sext i32 %tmp508 to i64
  %1003 = getelementptr float, ptr %106, i64 %1002
  %1004 = load float, ptr %1003, align 4
  %1005 = fsub reassoc ninf nsz float %1000, %1004
  %1006 = tail call noundef float @llvm.fabs.f32(float %1005)
  %1007 = fadd reassoc ninf nsz float %1006, %.1105.us
  %1008 = add i64 %997, 1
  %tmp507 = trunc i64 %1008 to i32
  %1009 = sext i32 %tmp507 to i64
  %1010 = getelementptr float, ptr %923, i64 %1009
  %1011 = load float, ptr %1010, align 4
  %1012 = add i64 %1001, 1
  %tmp506 = trunc i64 %1012 to i32
  %1013 = sext i32 %tmp506 to i64
  %1014 = getelementptr float, ptr %106, i64 %1013
  %1015 = load float, ptr %1014, align 4
  %1016 = fsub reassoc ninf nsz float %1011, %1015
  %1017 = tail call noundef float @llvm.fabs.f32(float %1016)
  %1018 = fadd reassoc ninf nsz float %1017, %1007
  %1019 = add i64 %997, 2
  %tmp505 = trunc i64 %1019 to i32
  %1020 = sext i32 %tmp505 to i64
  %1021 = getelementptr float, ptr %923, i64 %1020
  %1022 = load float, ptr %1021, align 4
  %1023 = add i64 %1001, 2
  %tmp504 = trunc i64 %1023 to i32
  %1024 = sext i32 %tmp504 to i64
  %1025 = getelementptr float, ptr %106, i64 %1024
  %1026 = load float, ptr %1025, align 4
  %1027 = fsub reassoc ninf nsz float %1022, %1026
  %1028 = tail call noundef float @llvm.fabs.f32(float %1027)
  %1029 = fadd reassoc ninf nsz float %1028, %1018
  %1030 = add i64 %997, 3
  %tmp503 = trunc i64 %1030 to i32
  %1031 = sext i32 %tmp503 to i64
  %1032 = getelementptr float, ptr %923, i64 %1031
  %1033 = load float, ptr %1032, align 4
  %1034 = add i64 %1001, 3
  %tmp502 = trunc i64 %1034 to i32
  %1035 = sext i32 %tmp502 to i64
  %1036 = getelementptr float, ptr %106, i64 %1035
  %1037 = load float, ptr %1036, align 4
  %1038 = fsub reassoc ninf nsz float %1033, %1037
  %1039 = tail call noundef float @llvm.fabs.f32(float %1038)
  %1040 = fadd reassoc ninf nsz float %1039, %1029
  %indvars.iv.next125.3 = add nuw nsw i64 %indvars.iv124, 4
  %exitcond128.not.3 = icmp eq i64 %wide.trip.count127, %indvars.iv.next125.3
  br i1 %exitcond128.not.3, label %for_loop_test73.after_for72_crit_edge.us.loopexit, label %for_loop_body70.us, !llvm.loop !20

for_loop_test73.after_for72_crit_edge.us.loopexit: ; preds = %for_loop_body70.us
  br label %for_loop_test73.after_for72_crit_edge.us

for_loop_test73.after_for72_crit_edge.us:         ; preds = %for_loop_test73.after_for72_crit_edge.us.loopexit, %for_loop_body70.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa141 = phi float [ %969, %middle.block ], [ %983, %vec.epilog.middle.block ], [ %.lcssa405.unr, %for_loop_body70.us.prol.loopexit ], [ %1040, %for_loop_test73.after_for72_crit_edge.us.loopexit ]
  %1041 = add nuw nsw i32 %.051110.us, 1
  %lsr.iv.next498 = add i64 %lsr.iv497, %935
  %lsr.iv.next496 = add i64 %lsr.iv495, %933
  %exitcond130.not = icmp eq i32 %1041, %smax129
  br i1 %exitcond130.not, label %after_for68, label %iter.check

false_block64:                                    ; preds = %after_for18
  %1042 = fdiv reassoc ninf nsz float %.lcssa140, %.lcssa
  br label %after_if65

after_if65:                                       ; preds = %after_for68, %false_block64
  %.053 = phi float [ %1057, %after_for68 ], [ %1042, %false_block64 ]
  %1043 = getelementptr i8, ptr %75, i64 224
  %1044 = load float, ptr %1043, align 4
  %1045 = getelementptr i8, ptr %75, i64 228
  %1046 = load float, ptr %1045, align 4
  %1047 = fmul reassoc ninf nsz float %1046, %158
  %1048 = fsub reassoc ninf nsz float %.053, %1047
  %1049 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1048, float 0.000000e+00)
  %neg = fneg reassoc ninf nsz float %1044
  %1050 = fmul reassoc ninf nsz float %1049, %neg
  %1051 = tail call noundef float @expf(float noundef %1050) #9
  %1052 = fmul reassoc ninf nsz float %.070, %.071
  %1053 = fmul reassoc ninf nsz float %1052, %1051
  %1054 = fcmp reassoc ninf nsz ult float %1053, 0x3EB0C6F7A0000000
  br i1 %1054, label %after_if3, label %for_loop_body77.lr.ph

after_for68:                                      ; preds = %for_loop_test73.after_for72_crit_edge.us
  %1055 = mul i32 %66, %62
  %1056 = sitofp i32 %1055 to float
  %1057 = fdiv reassoc ninf nsz float %.lcssa141, %1056
  br label %after_if65

for_loop_body77.lr.ph:                            ; preds = %after_if65
  %1058 = load ptr, ptr %0, align 8
  %1059 = getelementptr i8, ptr %1058, i64 136
  %1060 = getelementptr i8, ptr %1058, i64 132
  %1061 = getelementptr i8, ptr %1058, i64 152
  %1062 = getelementptr i8, ptr %1058, i64 148
  %smax131 = tail call i32 @llvm.smax.i32(i32 %66, i32 1)
  %smax133 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  br label %for_loop_body77

for_loop_body77:                                  ; preds = %after_for86, %for_loop_body77.lr.ph
  %lsr.iv513 = phi i32 [ %54, %for_loop_body77.lr.ph ], [ %lsr.iv.next514, %after_for86 ]
  %.049115 = phi i32 [ 0, %for_loop_body77.lr.ph ], [ %1083, %after_for86 ]
  %1063 = load ptr, ptr %3, align 8
  %1064 = getelementptr inbounds nuw i8, ptr %1063, i64 32872
  %1065 = load ptr, ptr %1064, align 8
  %1066 = getelementptr inbounds nuw i8, ptr %1065, i64 24
  %1067 = load i1, ptr %1066, align 1
  br i1 %1067, label %true_block81, label %for_loop_body84.preheader

true_block81:                                     ; preds = %for_loop_body77
  %1068 = uitofp nneg i32 %.049115 to float
  %1069 = fmul reassoc ninf nsz float %1068, 0x401921FB60000000
  %1070 = getelementptr inbounds nuw i8, ptr %1065, i64 28
  %1071 = load float, ptr %1070, align 4
  %1072 = fmul reassoc ninf nsz float %1069, %1071
  %1073 = tail call noundef float @cosf(float noundef %1072) #9
  %1074 = fmul reassoc ninf nsz float %1073, 5.000000e-01
  %1075 = fsub reassoc ninf nsz float 5.000000e-01, %1074
  br label %for_loop_body84.preheader

for_loop_body84.preheader:                        ; preds = %true_block81, %for_loop_body77
  %.048 = phi float [ %1075, %true_block81 ], [ 1.000000e+00, %for_loop_body77 ]
  %1076 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.048, float 0x3F1A36E2E0000000)
  %1077 = fmul reassoc ninf nsz float %1076, %1053
  br label %for_loop_body84

for_loop_body84:                                  ; preds = %after_if90, %for_loop_body84.preheader
  %.047114 = phi i32 [ %1110, %after_if90 ], [ 0, %for_loop_body84.preheader ]
  %1078 = load ptr, ptr %3, align 8
  %1079 = getelementptr inbounds nuw i8, ptr %1078, i64 32872
  %1080 = load ptr, ptr %1079, align 8
  %1081 = getelementptr inbounds nuw i8, ptr %1080, i64 32
  %1082 = load i1, ptr %1081, align 1
  br i1 %1082, label %true_block88, label %after_if90

after_for86:                                      ; preds = %after_if90
  %1083 = add nuw nsw i32 %.049115, 1
  %lsr.iv.next514 = add i32 %lsr.iv513, 1
  %exitcond134.not = icmp eq i32 %1083, %smax133
  br i1 %exitcond134.not, label %after_if3.loopexit, label %for_loop_body77

true_block88:                                     ; preds = %for_loop_body84
  %1084 = uitofp nneg i32 %.047114 to float
  %1085 = fmul reassoc ninf nsz float %1084, 0x401921FB60000000
  %1086 = getelementptr inbounds nuw i8, ptr %1080, i64 36
  %1087 = load float, ptr %1086, align 4
  %1088 = fmul reassoc ninf nsz float %1085, %1087
  %1089 = tail call noundef float @cosf(float noundef %1088) #9
  %1090 = fmul reassoc ninf nsz float %1089, 5.000000e-01
  %1091 = fsub reassoc ninf nsz float 5.000000e-01, %1090
  br label %after_if90

after_if90:                                       ; preds = %true_block88, %for_loop_body84
  %.0 = phi float [ %1091, %true_block88 ], [ 1.000000e+00, %for_loop_body84 ]
  %1092 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0, float 0x3F1A36E2E0000000)
  %1093 = fmul reassoc ninf nsz float %1077, %1092
  %1094 = load ptr, ptr %1059, align 8
  %1095 = load i32, ptr %1060, align 4
  %1096 = mul i32 %lsr.iv513, %1095
  %1097 = add i32 %58, %.047114
  %1098 = add i32 %1097, %1096
  %1099 = sext i32 %1098 to i64
  %1100 = getelementptr float, ptr %1094, i64 %1099
  %1101 = atomicrmw fadd ptr %1100, float %1093 seq_cst, align 4
  %1102 = fmul reassoc ninf nsz float %1092, %1076
  %1103 = load ptr, ptr %1061, align 8
  %1104 = load i32, ptr %1062, align 4
  %1105 = mul i32 %lsr.iv513, %1104
  %1106 = add i32 %1097, %1105
  %1107 = sext i32 %1106 to i64
  %1108 = getelementptr float, ptr %1103, i64 %1107
  %1109 = atomicrmw fadd ptr %1108, float %1102 seq_cst, align 4
  %1110 = add nuw nsw i32 %.047114, 1
  %exitcond132.not = icmp eq i32 %smax131, %1110
  br i1 %exitcond132.not, label %after_for86, label %for_loop_body84
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
