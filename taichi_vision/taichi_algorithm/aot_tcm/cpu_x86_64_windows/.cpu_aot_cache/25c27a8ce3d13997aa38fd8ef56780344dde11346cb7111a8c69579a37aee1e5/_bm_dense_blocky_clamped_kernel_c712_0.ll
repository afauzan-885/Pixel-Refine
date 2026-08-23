; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.13 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bm_dense_blocky_clamped_kernel_c712_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 24
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 28
  %4 = load i32, ptr %3, align 4
  %5 = load i32, ptr %0, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 16
  store i32 %5, ptr %10, align 4
  %11 = load ptr, ptr %context, align 8
  %12 = getelementptr i8, ptr %11, i64 4
  %13 = load i32, ptr %12, align 4
  %14 = load ptr, ptr %6, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 32872
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 12
  store i32 %13, ptr %17, align 4
  %18 = load ptr, ptr %context, align 8
  %19 = getelementptr i8, ptr %18, i64 48
  %20 = load i32, ptr %19, align 4
  %21 = sitofp i32 %20 to float
  %22 = fdiv reassoc ninf nsz float 1.000000e+00, %21
  %23 = load ptr, ptr %6, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 32872
  %25 = load ptr, ptr %24, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 8
  store float %22, ptr %26, align 4
  %27 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %28 = tail call i32 @llvm.smax.i32(i32 %4, i32 0)
  %29 = load ptr, ptr %6, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  store i32 %28, ptr %32, align 4
  %33 = mul i32 %28, %27
  %34 = load ptr, ptr %6, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  store i32 %33, ptr %36, align 4
  ret void
}

define void @_bm_dense_blocky_clamped_kernel_c712_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #7
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
  %20 = getelementptr i8, ptr %19, i64 52
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 56
  %23 = load float, ptr %22, align 4
  %24 = fcmp reassoc ninf nsz ogt float %23, 0.000000e+00
  %25 = icmp slt i32 %16, %18
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = getelementptr i8, ptr %19, i64 16
  %27 = getelementptr i8, ptr %19, i64 4
  %28 = getelementptr i8, ptr %19, i64 8
  %29 = getelementptr i8, ptr %19, i64 40
  %30 = getelementptr i8, ptr %19, i64 28
  %31 = getelementptr i8, ptr %19, i64 32
  %32 = sub i32 0, %21
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if78, %for_loop_body.lr.ph
  %.06784 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %264, %after_if78 ]
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 4
  %37 = load i32, ptr %36, align 4
  %38 = sdiv i32 %.06784, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.06784
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.06784, %39
  %43 = and i1 %41, %42
  %.neg78 = sext i1 %43 to i32
  %44 = add i32 %38, %.neg78
  %45 = mul i32 %37, -1
  %46 = mul i32 %45, %44
  %47 = add i32 %32, %.06784
  %48 = add i32 %47, %46
  %49 = sitofp i32 %48 to float
  %50 = getelementptr inbounds nuw i8, ptr %35, i64 8
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sub i32 %44, %21
  %54 = sitofp i32 %53 to float
  %55 = fmul reassoc ninf nsz float %51, %54
  %56 = fadd reassoc ninf nsz float %52, 5.000000e-01
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %58 = fptosi float %57 to i32
  %59 = getelementptr inbounds nuw i8, ptr %35, i64 12
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %60, -1
  %62 = tail call i32 @llvm.smin.i32(i32 %58, i32 %61)
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %64 = fadd reassoc ninf nsz float %55, 5.000000e-01
  %65 = tail call reassoc ninf nsz float @llvm.floor.f32(float %64)
  %66 = fptosi float %65 to i32
  %67 = getelementptr inbounds nuw i8, ptr %35, i64 16
  %68 = load i32, ptr %67, align 4
  %69 = add i32 %68, -1
  %70 = tail call i32 @llvm.smin.i32(i32 %66, i32 %69)
  %71 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %72 = load ptr, ptr %26, align 8
  %73 = load i32, ptr %27, align 4
  %74 = load i32, ptr %28, align 4
  %75 = mul i32 %71, %73
  %76 = add i32 %63, %75
  %77 = mul i32 %76, %74
  %78 = add i32 %77, 2
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, ptr %72, i64 %79
  %81 = load float, ptr %80, align 4
  %82 = fcmp reassoc ninf nsz ogt float %81, 5.000000e-01
  br i1 %82, label %after_if.sink.split, label %false_block

after_for.loopexit:                               ; preds = %after_if78
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

false_block:                                      ; preds = %for_loop_body
  %83 = add nsw i32 %71, -1
  %84 = tail call i32 @llvm.smin.i32(i32 %83, i32 %69)
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = add nsw i32 %63, -1
  %87 = tail call i32 @llvm.smin.i32(i32 %86, i32 %61)
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = mul i32 %85, %73
  %90 = add i32 %88, %89
  %91 = mul i32 %90, %74
  %92 = add i32 %91, 2
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %72, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fcmp reassoc ninf nsz ule float %95, 5.000000e-01
  br i1 %96, label %after_if3, label %true_block1

after_if.sink.split:                              ; preds = %true_block67, %for_loop_body
  %.sink = phi i32 [ %225, %true_block67 ], [ %77, %for_loop_body ]
  %97 = sext i32 %.sink to i64
  %98 = getelementptr float, ptr %72, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = add i32 %.sink, 1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %72, i64 %101
  %103 = load float, ptr %102, align 4
  br label %after_if

after_if:                                         ; preds = %true_block67, %after_if60, %after_if.sink.split
  %.057 = phi float [ %.865, %true_block67 ], [ %.865, %after_if60 ], [ %99, %after_if.sink.split ]
  %.049 = phi float [ %.8, %true_block67 ], [ %.8, %after_if60 ], [ %103, %after_if.sink.split ]
  br i1 %24, label %true_block76, label %after_if78

true_block1:                                      ; preds = %false_block
  %104 = sext i32 %91 to i64
  %105 = getelementptr float, ptr %72, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = add i32 %91, 1
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %72, i64 %108
  %110 = load float, ptr %109, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %false_block
  %.158 = phi float [ %106, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.150 = phi float [ %110, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.041 = phi i32 [ 1, %true_block1 ], [ 0, %false_block ]
  %.040 = phi float [ 2.000000e+00, %true_block1 ], [ 9.999990e+05, %false_block ]
  %111 = tail call i32 @llvm.smin.i32(i32 %63, i32 %61)
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = add i32 %89, %112
  %114 = mul i32 %113, %74
  %115 = add i32 %114, 2
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %72, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = fcmp reassoc ninf nsz ogt float %118, 5.000000e-01
  br i1 %119, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %120 = sext i32 %114 to i64
  %121 = getelementptr float, ptr %72, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %114, 1
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %72, i64 %124
  %126 = load float, ptr %125, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.259 = phi float [ %122, %true_block4 ], [ %.158, %after_if3 ]
  %.251 = phi float [ %126, %true_block4 ], [ %.150, %after_if3 ]
  %.142 = phi i32 [ 1, %true_block4 ], [ %.041, %after_if3 ]
  %.1 = phi float [ 1.000000e+00, %true_block4 ], [ %.040, %after_if3 ]
  %127 = add nuw i32 %63, 1
  %128 = tail call i32 @llvm.smin.i32(i32 %127, i32 %61)
  %129 = tail call i32 @llvm.smax.i32(i32 %128, i32 0)
  %130 = add i32 %129, %89
  %131 = mul i32 %130, %74
  %132 = add i32 %131, 2
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %72, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = fcmp reassoc ninf nsz ogt float %135, 5.000000e-01
  br i1 %136, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if6
  %137 = icmp eq i32 %.142, 0
  %138 = fcmp reassoc ninf nsz ogt float %.1, 2.000000e+00
  %spec.select = select i1 %137, i1 true, i1 %138
  br i1 %spec.select, label %true_block19, label %after_if15

after_if15:                                       ; preds = %true_block19, %true_block13, %after_if6
  %.360 = phi float [ %151, %true_block19 ], [ %.259, %true_block13 ], [ %.259, %after_if6 ]
  %.352 = phi float [ %155, %true_block19 ], [ %.251, %true_block13 ], [ %.251, %after_if6 ]
  %.243 = phi i32 [ 1, %true_block19 ], [ 1, %true_block13 ], [ %.142, %after_if6 ]
  %.2 = phi float [ 2.000000e+00, %true_block19 ], [ %.1, %true_block13 ], [ %.1, %after_if6 ]
  %139 = tail call i32 @llvm.smin.i32(i32 %71, i32 %69)
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = mul i32 %140, %73
  %142 = add i32 %88, %141
  %143 = mul i32 %142, %74
  %144 = add i32 %143, 2
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %72, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = fcmp reassoc ninf nsz ogt float %147, 5.000000e-01
  br i1 %148, label %true_block22, label %after_if24

true_block19:                                     ; preds = %true_block13
  %149 = sext i32 %131 to i64
  %150 = getelementptr float, ptr %72, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = add i32 %131, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %72, i64 %153
  %155 = load float, ptr %154, align 4
  br label %after_if15

true_block22:                                     ; preds = %after_if15
  %156 = icmp eq i32 %.243, 0
  %157 = fcmp reassoc ninf nsz ogt float %.2, 1.000000e+00
  %spec.select79 = select i1 %156, i1 true, i1 %157
  br i1 %spec.select79, label %true_block28, label %after_if24

after_if24:                                       ; preds = %true_block28, %true_block22, %after_if15
  %.461 = phi float [ %167, %true_block28 ], [ %.360, %true_block22 ], [ %.360, %after_if15 ]
  %.453 = phi float [ %171, %true_block28 ], [ %.352, %true_block22 ], [ %.352, %after_if15 ]
  %.344 = phi i32 [ 1, %true_block28 ], [ 1, %true_block22 ], [ %.243, %after_if15 ]
  %.3 = phi float [ 1.000000e+00, %true_block28 ], [ %.2, %true_block22 ], [ %.2, %after_if15 ]
  %158 = add i32 %112, %141
  %159 = mul i32 %158, %74
  %160 = add i32 %159, 2
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %72, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = fcmp reassoc ninf nsz ogt float %163, 5.000000e-01
  br i1 %164, label %true_block31, label %after_if33

true_block28:                                     ; preds = %true_block22
  %165 = sext i32 %143 to i64
  %166 = getelementptr float, ptr %72, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = add i32 %143, 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %72, i64 %169
  %171 = load float, ptr %170, align 4
  br label %after_if24

true_block31:                                     ; preds = %after_if24
  %172 = sext i32 %159 to i64
  %173 = getelementptr float, ptr %72, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = add i32 %159, 1
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %72, i64 %176
  %178 = load float, ptr %177, align 4
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if24
  %.562 = phi float [ %174, %true_block31 ], [ %.461, %after_if24 ]
  %.554 = phi float [ %178, %true_block31 ], [ %.453, %after_if24 ]
  %.445 = phi i32 [ 1, %true_block31 ], [ %.344, %after_if24 ]
  %.4 = phi float [ 0.000000e+00, %true_block31 ], [ %.3, %after_if24 ]
  %179 = add i32 %129, %141
  %180 = mul i32 %179, %74
  %181 = add i32 %180, 2
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %72, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = fcmp reassoc ninf nsz ogt float %184, 5.000000e-01
  br i1 %185, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if33
  %186 = icmp eq i32 %.445, 0
  %187 = fcmp reassoc ninf nsz ogt float %.4, 1.000000e+00
  %spec.select80 = select i1 %186, i1 true, i1 %187
  br i1 %spec.select80, label %true_block46, label %after_if42

after_if42:                                       ; preds = %true_block46, %true_block40, %after_if33
  %.663 = phi float [ %201, %true_block46 ], [ %.562, %true_block40 ], [ %.562, %after_if33 ]
  %.655 = phi float [ %205, %true_block46 ], [ %.554, %true_block40 ], [ %.554, %after_if33 ]
  %.546 = phi i32 [ 1, %true_block46 ], [ 1, %true_block40 ], [ %.445, %after_if33 ]
  %.5 = phi float [ 1.000000e+00, %true_block46 ], [ %.4, %true_block40 ], [ %.4, %after_if33 ]
  %188 = add nuw i32 %71, 1
  %189 = tail call i32 @llvm.smin.i32(i32 %188, i32 %69)
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %191 = mul i32 %190, %73
  %192 = add i32 %88, %191
  %193 = mul i32 %192, %74
  %194 = add i32 %193, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %72, i64 %195
  %197 = load float, ptr %196, align 4
  %198 = fcmp reassoc ninf nsz ogt float %197, 5.000000e-01
  br i1 %198, label %true_block49, label %after_if51

true_block46:                                     ; preds = %true_block40
  %199 = sext i32 %180 to i64
  %200 = getelementptr float, ptr %72, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = add i32 %180, 1
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %72, i64 %203
  %205 = load float, ptr %204, align 4
  br label %after_if42

true_block49:                                     ; preds = %after_if42
  %206 = icmp eq i32 %.546, 0
  %207 = fcmp reassoc ninf nsz ogt float %.5, 2.000000e+00
  %spec.select81 = select i1 %206, i1 true, i1 %207
  br i1 %spec.select81, label %true_block55, label %after_if51

after_if51:                                       ; preds = %true_block55, %true_block49, %after_if42
  %.764 = phi float [ %217, %true_block55 ], [ %.663, %true_block49 ], [ %.663, %after_if42 ]
  %.756 = phi float [ %221, %true_block55 ], [ %.655, %true_block49 ], [ %.655, %after_if42 ]
  %.647 = phi i32 [ 1, %true_block55 ], [ 1, %true_block49 ], [ %.546, %after_if42 ]
  %.6 = phi float [ 2.000000e+00, %true_block55 ], [ %.5, %true_block49 ], [ %.5, %after_if42 ]
  %208 = add i32 %191, %112
  %209 = mul i32 %208, %74
  %210 = add i32 %209, 2
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %72, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fcmp reassoc ninf nsz ogt float %213, 5.000000e-01
  br i1 %214, label %true_block58, label %after_if60

true_block55:                                     ; preds = %true_block49
  %215 = sext i32 %193 to i64
  %216 = getelementptr float, ptr %72, i64 %215
  %217 = load float, ptr %216, align 4
  %218 = add i32 %193, 1
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, ptr %72, i64 %219
  %221 = load float, ptr %220, align 4
  br label %after_if51

true_block58:                                     ; preds = %after_if51
  %222 = icmp eq i32 %.647, 0
  %223 = fcmp reassoc ninf nsz ogt float %.6, 1.000000e+00
  %spec.select82 = select i1 %222, i1 true, i1 %223
  br i1 %spec.select82, label %true_block64, label %after_if60

after_if60:                                       ; preds = %true_block64, %true_block58, %after_if51
  %.865 = phi float [ %233, %true_block64 ], [ %.764, %true_block58 ], [ %.764, %after_if51 ]
  %.8 = phi float [ %237, %true_block64 ], [ %.756, %true_block58 ], [ %.756, %after_if51 ]
  %.748 = phi i32 [ 1, %true_block64 ], [ 1, %true_block58 ], [ %.647, %after_if51 ]
  %.7 = phi float [ 1.000000e+00, %true_block64 ], [ %.6, %true_block58 ], [ %.6, %after_if51 ]
  %224 = add i32 %129, %191
  %225 = mul i32 %224, %74
  %226 = add i32 %225, 2
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %72, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = fcmp reassoc ninf nsz ogt float %229, 5.000000e-01
  br i1 %230, label %true_block67, label %after_if

true_block64:                                     ; preds = %true_block58
  %231 = sext i32 %209 to i64
  %232 = getelementptr float, ptr %72, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = add i32 %209, 1
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %72, i64 %235
  %237 = load float, ptr %236, align 4
  br label %after_if60

true_block67:                                     ; preds = %after_if60
  %238 = icmp eq i32 %.748, 0
  %239 = fcmp reassoc ninf nsz ogt float %.7, 2.000000e+00
  %spec.select83 = select i1 %238, i1 true, i1 %239
  br i1 %spec.select83, label %after_if.sink.split, label %after_if

true_block76:                                     ; preds = %after_if
  %240 = fmul reassoc ninf nsz float %.057, %.057
  %241 = fmul reassoc ninf nsz float %.049, %.049
  %242 = fadd reassoc ninf nsz float %241, %240
  %243 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %242)
  %244 = fcmp reassoc ninf nsz ogt float %243, %23
  br i1 %244, label %true_block79, label %after_if78

after_if78:                                       ; preds = %true_block79, %true_block76, %after_if
  %.966 = phi float [ %267, %true_block79 ], [ %.057, %true_block76 ], [ %.057, %after_if ]
  %.9 = phi float [ %268, %true_block79 ], [ %.049, %true_block76 ], [ %.049, %after_if ]
  %245 = load ptr, ptr %29, align 8
  %246 = load i32, ptr %30, align 4
  %247 = load i32, ptr %31, align 4
  %248 = sub i32 %246, %37
  %249 = mul i32 %248, %44
  %250 = add i32 %.06784, %249
  %251 = mul i32 %250, %247
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, ptr %245, i64 %252
  store float %.966, ptr %253, align 4
  %254 = load ptr, ptr %29, align 8
  %255 = load i32, ptr %30, align 4
  %256 = load i32, ptr %31, align 4
  %257 = sub i32 %255, %37
  %258 = mul i32 %257, %44
  %259 = add i32 %.06784, %258
  %260 = mul i32 %259, %256
  %261 = add i32 %260, 1
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %254, i64 %262
  store float %.9, ptr %263, align 4
  %264 = add nsw i32 %.06784, 1
  %exitcond.not = icmp eq i32 %18, %264
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block79:                                     ; preds = %true_block76
  %265 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %243, float 0x3EB0C6F7A0000000)
  %266 = fdiv reassoc ninf nsz float %23, %265
  %267 = fmul reassoc ninf nsz float %266, %.057
  %268 = fmul reassoc ninf nsz float %266, %.049
  br label %after_if78
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.13, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #7
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #7
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !10

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !12

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #7
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
!10 = distinct !{!10, !11}
!11 = !{!"llvm.loop.mustprogress"}
!12 = distinct !{!12, !11}
