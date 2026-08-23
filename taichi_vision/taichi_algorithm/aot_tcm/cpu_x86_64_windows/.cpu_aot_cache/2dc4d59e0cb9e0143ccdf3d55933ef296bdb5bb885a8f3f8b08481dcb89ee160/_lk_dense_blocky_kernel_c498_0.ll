; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.11 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_lk_dense_blocky_kernel_c498_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_lk_dense_blocky_kernel_c498_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 16
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 8
  %26 = sub i32 0, %21
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.06277 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %124, %after_if ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.06277, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.06277
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.06277, %33
  %37 = and i1 %35, %36
  %.neg71 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg71
  %39 = mul i32 %31, -1
  %40 = mul i32 %39, %38
  %41 = add i32 %26, %.06277
  %42 = add i32 %41, %40
  %43 = sitofp i32 %42 to float
  %44 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %45 = load float, ptr %44, align 4
  %46 = fmul reassoc ninf nsz float %45, %43
  %47 = sub i32 %38, %21
  %48 = sitofp i32 %47 to float
  %49 = fmul reassoc ninf nsz float %45, %48
  %50 = fadd reassoc ninf nsz float %46, 5.000000e-01
  %51 = tail call reassoc ninf nsz float @llvm.floor.f32(float %50)
  %52 = fptosi float %51 to i32
  %53 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %54 = load i32, ptr %53, align 4
  %55 = add i32 %54, -1
  %56 = tail call i32 @llvm.smin.i32(i32 %52, i32 %55)
  %57 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %58 = fadd reassoc ninf nsz float %49, 5.000000e-01
  %59 = tail call reassoc ninf nsz float @llvm.floor.f32(float %58)
  %60 = fptosi float %59 to i32
  %61 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %62 = load i32, ptr %61, align 4
  %63 = add i32 %62, -1
  %64 = tail call i32 @llvm.smin.i32(i32 %60, i32 %63)
  %65 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %66 = load ptr, ptr %23, align 8
  %67 = load i32, ptr %24, align 4
  %68 = load i32, ptr %25, align 4
  %69 = mul i32 %65, %67
  %70 = add i32 %57, %69
  %71 = mul i32 %70, %68
  %72 = add i32 %71, 2
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %66, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = fcmp reassoc ninf nsz ogt float %75, 5.000000e-01
  br i1 %76, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %77 = sext i32 %71 to i64
  %78 = getelementptr float, ptr %66, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = load ptr, ptr %0, align 8
  %81 = getelementptr i8, ptr %80, i64 40
  %82 = load ptr, ptr %81, align 8
  %83 = getelementptr i8, ptr %80, i64 28
  %84 = load i32, ptr %83, align 4
  %85 = getelementptr i8, ptr %80, i64 32
  %86 = load i32, ptr %85, align 4
  %87 = sub i32 %84, %31
  %88 = mul i32 %87, %38
  %89 = add i32 %.06277, %88
  %90 = mul i32 %89, %86
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %82, i64 %91
  store float %79, ptr %92, align 4
  %93 = load ptr, ptr %23, align 8
  %94 = load i32, ptr %24, align 4
  %95 = load i32, ptr %25, align 4
  %96 = mul i32 %94, %65
  %97 = add i32 %96, %57
  %98 = mul i32 %97, %95
  %99 = add i32 %98, 1
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %93, i64 %100
  %102 = load float, ptr %101, align 4
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %103 = add nsw i32 %65, -1
  %104 = tail call i32 @llvm.smin.i32(i32 %103, i32 %63)
  %105 = tail call i32 @llvm.smax.i32(i32 %104, i32 0)
  %106 = add nsw i32 %57, -1
  %107 = tail call i32 @llvm.smin.i32(i32 %106, i32 %55)
  %108 = tail call i32 @llvm.smax.i32(i32 %107, i32 0)
  %109 = mul i32 %105, %67
  %110 = add i32 %108, %109
  %111 = mul i32 %110, %68
  %112 = add i32 %111, 2
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %66, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = fcmp reassoc ninf nsz ule float %115, 5.000000e-01
  br i1 %116, label %after_if3, label %true_block1

after_if:                                         ; preds = %after_if69, %true_block
  %.sink.in = phi ptr [ %264, %after_if69 ], [ %83, %true_block ]
  %.sink81.in = phi ptr [ %266, %after_if69 ], [ %85, %true_block ]
  %.sink78.in = phi ptr [ %262, %after_if69 ], [ %81, %true_block ]
  %.8.sink = phi float [ %.8, %after_if69 ], [ %102, %true_block ]
  %.sink78 = load ptr, ptr %.sink78.in, align 8
  %.sink81 = load i32, ptr %.sink81.in, align 4
  %.sink = load i32, ptr %.sink.in, align 4
  %117 = sub i32 %.sink, %31
  %118 = mul i32 %117, %38
  %119 = add i32 %.06277, %118
  %120 = mul i32 %119, %.sink81
  %121 = add i32 %120, 1
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %.sink78, i64 %122
  store float %.8.sink, ptr %123, align 4
  %124 = add nsw i32 %.06277, 1
  %exitcond.not = icmp eq i32 %18, %124
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block1:                                      ; preds = %false_block
  %125 = sext i32 %111 to i64
  %126 = getelementptr float, ptr %66, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %111, 1
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %66, i64 %129
  %131 = load float, ptr %130, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %false_block
  %.053 = phi float [ %127, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.045 = phi float [ %131, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.037 = phi i32 [ 1, %true_block1 ], [ 0, %false_block ]
  %.036 = phi float [ 2.000000e+00, %true_block1 ], [ 9.999990e+05, %false_block ]
  %132 = tail call i32 @llvm.smin.i32(i32 %57, i32 %55)
  %133 = tail call i32 @llvm.smax.i32(i32 %132, i32 0)
  %134 = add i32 %109, %133
  %135 = mul i32 %134, %68
  %136 = add i32 %135, 2
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %66, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = fcmp reassoc ninf nsz ogt float %139, 5.000000e-01
  br i1 %140, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %141 = sext i32 %135 to i64
  %142 = getelementptr float, ptr %66, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = add i32 %135, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %66, i64 %145
  %147 = load float, ptr %146, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.154 = phi float [ %143, %true_block4 ], [ %.053, %after_if3 ]
  %.146 = phi float [ %147, %true_block4 ], [ %.045, %after_if3 ]
  %.138 = phi i32 [ 1, %true_block4 ], [ %.037, %after_if3 ]
  %.1 = phi float [ 1.000000e+00, %true_block4 ], [ %.036, %after_if3 ]
  %148 = add nuw i32 %57, 1
  %149 = tail call i32 @llvm.smin.i32(i32 %148, i32 %55)
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = add i32 %150, %109
  %152 = mul i32 %151, %68
  %153 = add i32 %152, 2
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %66, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = fcmp reassoc ninf nsz ogt float %156, 5.000000e-01
  br i1 %157, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if6
  %158 = icmp eq i32 %.138, 0
  %159 = fcmp reassoc ninf nsz ogt float %.1, 2.000000e+00
  %spec.select = select i1 %158, i1 true, i1 %159
  br i1 %spec.select, label %true_block19, label %after_if15

after_if15:                                       ; preds = %true_block19, %true_block13, %after_if6
  %.255 = phi float [ %172, %true_block19 ], [ %.154, %true_block13 ], [ %.154, %after_if6 ]
  %.247 = phi float [ %176, %true_block19 ], [ %.146, %true_block13 ], [ %.146, %after_if6 ]
  %.239 = phi i32 [ 1, %true_block19 ], [ 1, %true_block13 ], [ %.138, %after_if6 ]
  %.2 = phi float [ 2.000000e+00, %true_block19 ], [ %.1, %true_block13 ], [ %.1, %after_if6 ]
  %160 = tail call i32 @llvm.smin.i32(i32 %65, i32 %63)
  %161 = tail call i32 @llvm.smax.i32(i32 %160, i32 0)
  %162 = mul i32 %161, %67
  %163 = add i32 %108, %162
  %164 = mul i32 %163, %68
  %165 = add i32 %164, 2
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %66, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = fcmp reassoc ninf nsz ogt float %168, 5.000000e-01
  br i1 %169, label %true_block22, label %after_if24

true_block19:                                     ; preds = %true_block13
  %170 = sext i32 %152 to i64
  %171 = getelementptr float, ptr %66, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = add i32 %152, 1
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, ptr %66, i64 %174
  %176 = load float, ptr %175, align 4
  br label %after_if15

true_block22:                                     ; preds = %after_if15
  %177 = icmp eq i32 %.239, 0
  %178 = fcmp reassoc ninf nsz ogt float %.2, 1.000000e+00
  %spec.select72 = select i1 %177, i1 true, i1 %178
  br i1 %spec.select72, label %true_block28, label %after_if24

after_if24:                                       ; preds = %true_block28, %true_block22, %after_if15
  %.356 = phi float [ %188, %true_block28 ], [ %.255, %true_block22 ], [ %.255, %after_if15 ]
  %.348 = phi float [ %192, %true_block28 ], [ %.247, %true_block22 ], [ %.247, %after_if15 ]
  %.340 = phi i32 [ 1, %true_block28 ], [ 1, %true_block22 ], [ %.239, %after_if15 ]
  %.3 = phi float [ 1.000000e+00, %true_block28 ], [ %.2, %true_block22 ], [ %.2, %after_if15 ]
  %179 = add i32 %133, %162
  %180 = mul i32 %179, %68
  %181 = add i32 %180, 2
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %66, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = fcmp reassoc ninf nsz ogt float %184, 5.000000e-01
  br i1 %185, label %true_block31, label %after_if33

true_block28:                                     ; preds = %true_block22
  %186 = sext i32 %164 to i64
  %187 = getelementptr float, ptr %66, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = add i32 %164, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %66, i64 %190
  %192 = load float, ptr %191, align 4
  br label %after_if24

true_block31:                                     ; preds = %after_if24
  %193 = sext i32 %180 to i64
  %194 = getelementptr float, ptr %66, i64 %193
  %195 = load float, ptr %194, align 4
  %196 = add i32 %180, 1
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %66, i64 %197
  %199 = load float, ptr %198, align 4
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if24
  %.457 = phi float [ %195, %true_block31 ], [ %.356, %after_if24 ]
  %.449 = phi float [ %199, %true_block31 ], [ %.348, %after_if24 ]
  %.441 = phi i32 [ 1, %true_block31 ], [ %.340, %after_if24 ]
  %.4 = phi float [ 0.000000e+00, %true_block31 ], [ %.3, %after_if24 ]
  %200 = add i32 %150, %162
  %201 = mul i32 %200, %68
  %202 = add i32 %201, 2
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %66, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = fcmp reassoc ninf nsz ogt float %205, 5.000000e-01
  br i1 %206, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if33
  %207 = icmp eq i32 %.441, 0
  %208 = fcmp reassoc ninf nsz ogt float %.4, 1.000000e+00
  %spec.select73 = select i1 %207, i1 true, i1 %208
  br i1 %spec.select73, label %true_block46, label %after_if42

after_if42:                                       ; preds = %true_block46, %true_block40, %after_if33
  %.558 = phi float [ %222, %true_block46 ], [ %.457, %true_block40 ], [ %.457, %after_if33 ]
  %.550 = phi float [ %226, %true_block46 ], [ %.449, %true_block40 ], [ %.449, %after_if33 ]
  %.542 = phi i32 [ 1, %true_block46 ], [ 1, %true_block40 ], [ %.441, %after_if33 ]
  %.5 = phi float [ 1.000000e+00, %true_block46 ], [ %.4, %true_block40 ], [ %.4, %after_if33 ]
  %209 = add nuw i32 %65, 1
  %210 = tail call i32 @llvm.smin.i32(i32 %209, i32 %63)
  %211 = tail call i32 @llvm.smax.i32(i32 %210, i32 0)
  %212 = mul i32 %211, %67
  %213 = add i32 %108, %212
  %214 = mul i32 %213, %68
  %215 = add i32 %214, 2
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %66, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = fcmp reassoc ninf nsz ogt float %218, 5.000000e-01
  br i1 %219, label %true_block49, label %after_if51

true_block46:                                     ; preds = %true_block40
  %220 = sext i32 %201 to i64
  %221 = getelementptr float, ptr %66, i64 %220
  %222 = load float, ptr %221, align 4
  %223 = add i32 %201, 1
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %66, i64 %224
  %226 = load float, ptr %225, align 4
  br label %after_if42

true_block49:                                     ; preds = %after_if42
  %227 = icmp eq i32 %.542, 0
  %228 = fcmp reassoc ninf nsz ogt float %.5, 2.000000e+00
  %spec.select74 = select i1 %227, i1 true, i1 %228
  br i1 %spec.select74, label %true_block55, label %after_if51

after_if51:                                       ; preds = %true_block55, %true_block49, %after_if42
  %.659 = phi float [ %238, %true_block55 ], [ %.558, %true_block49 ], [ %.558, %after_if42 ]
  %.651 = phi float [ %242, %true_block55 ], [ %.550, %true_block49 ], [ %.550, %after_if42 ]
  %.643 = phi i32 [ 1, %true_block55 ], [ 1, %true_block49 ], [ %.542, %after_if42 ]
  %.6 = phi float [ 2.000000e+00, %true_block55 ], [ %.5, %true_block49 ], [ %.5, %after_if42 ]
  %229 = add i32 %212, %133
  %230 = mul i32 %229, %68
  %231 = add i32 %230, 2
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, ptr %66, i64 %232
  %234 = load float, ptr %233, align 4
  %235 = fcmp reassoc ninf nsz ogt float %234, 5.000000e-01
  br i1 %235, label %true_block58, label %after_if60

true_block55:                                     ; preds = %true_block49
  %236 = sext i32 %214 to i64
  %237 = getelementptr float, ptr %66, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = add i32 %214, 1
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, ptr %66, i64 %240
  %242 = load float, ptr %241, align 4
  br label %after_if51

true_block58:                                     ; preds = %after_if51
  %243 = icmp eq i32 %.643, 0
  %244 = fcmp reassoc ninf nsz ogt float %.6, 1.000000e+00
  %spec.select75 = select i1 %243, i1 true, i1 %244
  br i1 %spec.select75, label %true_block64, label %after_if60

after_if60:                                       ; preds = %true_block64, %true_block58, %after_if51
  %.760 = phi float [ %254, %true_block64 ], [ %.659, %true_block58 ], [ %.659, %after_if51 ]
  %.752 = phi float [ %258, %true_block64 ], [ %.651, %true_block58 ], [ %.651, %after_if51 ]
  %.744 = phi i32 [ 1, %true_block64 ], [ 1, %true_block58 ], [ %.643, %after_if51 ]
  %.7 = phi float [ 1.000000e+00, %true_block64 ], [ %.6, %true_block58 ], [ %.6, %after_if51 ]
  %245 = add i32 %150, %212
  %246 = mul i32 %245, %68
  %247 = add i32 %246, 2
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %66, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = fcmp reassoc ninf nsz ogt float %250, 5.000000e-01
  br i1 %251, label %true_block67, label %after_if69

true_block64:                                     ; preds = %true_block58
  %252 = sext i32 %230 to i64
  %253 = getelementptr float, ptr %66, i64 %252
  %254 = load float, ptr %253, align 4
  %255 = add i32 %230, 1
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, ptr %66, i64 %256
  %258 = load float, ptr %257, align 4
  br label %after_if60

true_block67:                                     ; preds = %after_if60
  %259 = icmp eq i32 %.744, 0
  %260 = fcmp reassoc ninf nsz ogt float %.7, 2.000000e+00
  %spec.select76 = select i1 %259, i1 true, i1 %260
  br i1 %spec.select76, label %true_block73, label %after_if69

after_if69:                                       ; preds = %true_block73, %true_block67, %after_if60
  %.861 = phi float [ %276, %true_block73 ], [ %.760, %true_block67 ], [ %.760, %after_if60 ]
  %.8 = phi float [ %280, %true_block73 ], [ %.752, %true_block67 ], [ %.752, %after_if60 ]
  %261 = load ptr, ptr %0, align 8
  %262 = getelementptr i8, ptr %261, i64 40
  %263 = load ptr, ptr %262, align 8
  %264 = getelementptr i8, ptr %261, i64 28
  %265 = load i32, ptr %264, align 4
  %266 = getelementptr i8, ptr %261, i64 32
  %267 = load i32, ptr %266, align 4
  %268 = sub i32 %265, %31
  %269 = mul i32 %268, %38
  %270 = add i32 %.06277, %269
  %271 = mul i32 %270, %267
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, ptr %263, i64 %272
  store float %.861, ptr %273, align 4
  br label %after_if

true_block73:                                     ; preds = %true_block67
  %274 = sext i32 %246 to i64
  %275 = getelementptr float, ptr %66, i64 %274
  %276 = load float, ptr %275, align 4
  %277 = add i32 %246, 1
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, ptr %66, i64 %278
  %280 = load float, ptr %279, align 4
  br label %after_if69
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.11, align 8
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
