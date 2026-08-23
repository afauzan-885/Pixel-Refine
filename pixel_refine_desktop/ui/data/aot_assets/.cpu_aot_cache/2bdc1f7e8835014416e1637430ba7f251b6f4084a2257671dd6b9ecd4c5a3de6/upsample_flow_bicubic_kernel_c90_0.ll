; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @upsample_flow_bicubic_kernel_c90_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %15 = getelementptr i8, ptr %14, i64 24
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 28
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

define void @upsample_flow_bicubic_kernel_c90_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #6
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
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load float, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 16
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 8
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = getelementptr i8, ptr %19, i64 28
  %28 = getelementptr i8, ptr %19, i64 32
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if378, %for_loop_body.lr.ph
  %.0130626 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %982, %after_if378 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.0130626, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.0130626
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.0130626, %35
  %39 = and i1 %37, %38
  %.neg244 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg244
  %41 = mul i32 %33, -1
  %42 = mul i32 %41, %40
  %43 = add i32 %.0130626, %42
  %44 = sitofp i32 %40 to float
  %45 = fdiv reassoc ninf nsz float %44, %21
  %46 = sitofp i32 %43 to float
  %47 = fdiv reassoc ninf nsz float %46, %21
  %48 = tail call reassoc ninf nsz float @llvm.floor.f32(float %45)
  %49 = fptosi float %48 to i32
  %50 = tail call reassoc ninf nsz float @llvm.floor.f32(float %47)
  %51 = fptosi float %50 to i32
  %52 = sitofp i32 %49 to float
  %53 = fsub reassoc ninf nsz float %45, %52
  %54 = sitofp i32 %51 to float
  %55 = fsub reassoc ninf nsz float %47, %54
  %56 = add i32 %49, -1
  %57 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %58 = load i32, ptr %57, align 4
  %59 = add i32 %58, -1
  %60 = tail call i32 @llvm.smin.i32(i32 %56, i32 %59)
  %61 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %62 = add i32 %51, -1
  %63 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %64 = load i32, ptr %63, align 4
  %65 = add i32 %64, -1
  %66 = tail call i32 @llvm.smin.i32(i32 %62, i32 %65)
  %67 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %68 = fsub reassoc ninf nsz float -1.000000e+00, %53
  %69 = tail call noundef float @llvm.fabs.f32(float %68)
  %70 = fcmp reassoc ninf nsz ole float %69, 1.000000e+00
  br i1 %70, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if378
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %71 = fmul reassoc ninf nsz float %68, %68
  %72 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add = fadd reassoc ninf nsz float %72, -2.500000e+00
  %reass.mul247 = fmul reassoc ninf nsz float %71, %reass.add
  %73 = fadd reassoc ninf nsz float %reass.mul247, 1.000000e+00
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %74 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %74, label %true_block1, label %after_if

after_if:                                         ; preds = %true_block1, %false_block, %true_block
  %.0129 = phi float [ %73, %true_block ], [ %82, %true_block1 ], [ 0.000000e+00, %false_block ]
  %75 = fsub reassoc ninf nsz float -1.000000e+00, %55
  %76 = tail call noundef float @llvm.fabs.f32(float %75)
  %77 = fcmp reassoc ninf nsz ole float %76, 1.000000e+00
  br i1 %77, label %true_block4, label %false_block5

true_block1:                                      ; preds = %false_block
  %78 = fmul reassoc ninf nsz float %68, %68
  %79 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg245 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %80 = fsub reassoc ninf nsz float 2.500000e+00, %79
  %reass.mul = fmul reassoc ninf nsz float %78, %80
  %81 = fadd reassoc ninf nsz float %.neg245, 2.000000e+00
  %82 = fadd reassoc ninf nsz float %81, %reass.mul
  br label %after_if

true_block4:                                      ; preds = %after_if
  %83 = fmul reassoc ninf nsz float %75, %75
  %84 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add252 = fadd reassoc ninf nsz float %84, -2.500000e+00
  %reass.mul253 = fmul reassoc ninf nsz float %83, %reass.add252
  %85 = fadd reassoc ninf nsz float %reass.mul253, 1.000000e+00
  br label %after_if6

false_block5:                                     ; preds = %after_if
  %86 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %86, label %true_block7, label %after_if6

after_if6:                                        ; preds = %true_block7, %false_block5, %true_block4
  %.0128 = phi float [ %85, %true_block4 ], [ %104, %true_block7 ], [ 0.000000e+00, %false_block5 ]
  %87 = load ptr, ptr %23, align 8
  %88 = load i32, ptr %24, align 4
  %89 = load i32, ptr %25, align 4
  %90 = mul i32 %88, %61
  %91 = add i32 %90, %67
  %92 = mul i32 %91, %89
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %87, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fmul reassoc ninf nsz float %.0128, %.0129
  %97 = fmul reassoc ninf nsz float %96, %95
  %98 = tail call i32 @llvm.smin.i32(i32 %51, i32 %65)
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  br i1 %70, label %true_block10, label %false_block11

true_block7:                                      ; preds = %false_block5
  %100 = fmul reassoc ninf nsz float %75, %75
  %101 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg248 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %102 = fsub reassoc ninf nsz float 2.500000e+00, %101
  %reass.mul250 = fmul reassoc ninf nsz float %100, %102
  %103 = fadd reassoc ninf nsz float %.neg248, 2.000000e+00
  %104 = fadd reassoc ninf nsz float %103, %reass.mul250
  br label %after_if6

true_block10:                                     ; preds = %after_if6
  %105 = fmul reassoc ninf nsz float %68, %68
  %106 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add258 = fadd reassoc ninf nsz float %106, -2.500000e+00
  %reass.mul259 = fmul reassoc ninf nsz float %105, %reass.add258
  %107 = fadd reassoc ninf nsz float %reass.mul259, 1.000000e+00
  br label %after_if12

false_block11:                                    ; preds = %after_if6
  %108 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %108, label %true_block13, label %after_if12

after_if12:                                       ; preds = %true_block13, %false_block11, %true_block10
  %.0127 = phi float [ %107, %true_block10 ], [ %115, %true_block13 ], [ 0.000000e+00, %false_block11 ]
  %109 = tail call float @llvm.fabs.f32(float %55)
  %110 = fcmp reassoc ninf nsz ole float %109, 1.000000e+00
  br i1 %110, label %true_block16, label %false_block17

true_block13:                                     ; preds = %false_block11
  %111 = fmul reassoc ninf nsz float %68, %68
  %112 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg254 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %113 = fsub reassoc ninf nsz float 2.500000e+00, %112
  %reass.mul256 = fmul reassoc ninf nsz float %111, %113
  %114 = fadd reassoc ninf nsz float %.neg254, 2.000000e+00
  %115 = fadd reassoc ninf nsz float %114, %reass.mul256
  br label %after_if12

true_block16:                                     ; preds = %after_if12
  %116 = fmul reassoc ninf nsz float %55, %55
  %117 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add264 = fadd reassoc ninf nsz float %117, -2.500000e+00
  %reass.mul265 = fmul reassoc ninf nsz float %116, %reass.add264
  %118 = fadd reassoc ninf nsz float %reass.mul265, 1.000000e+00
  br label %after_if18

false_block17:                                    ; preds = %after_if12
  %119 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %119, label %true_block19, label %after_if18

after_if18:                                       ; preds = %true_block19, %false_block17, %true_block16
  %.0126 = phi float [ %118, %true_block16 ], [ %135, %true_block19 ], [ 0.000000e+00, %false_block17 ]
  %120 = add i32 %90, %99
  %121 = mul i32 %120, %89
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %87, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fmul reassoc ninf nsz float %.0126, %.0127
  %126 = fmul reassoc ninf nsz float %125, %124
  %127 = fadd reassoc ninf nsz float %126, %97
  %128 = add i32 %51, 1
  %129 = tail call i32 @llvm.smin.i32(i32 %128, i32 %65)
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  br i1 %70, label %true_block22, label %false_block23

true_block19:                                     ; preds = %false_block17
  %131 = fmul reassoc ninf nsz float %55, %55
  %132 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg260 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %133 = fsub reassoc ninf nsz float 2.500000e+00, %132
  %reass.mul262 = fmul reassoc ninf nsz float %131, %133
  %134 = fadd reassoc ninf nsz float %.neg260, 2.000000e+00
  %135 = fadd reassoc ninf nsz float %134, %reass.mul262
  br label %after_if18

true_block22:                                     ; preds = %after_if18
  %136 = fmul reassoc ninf nsz float %68, %68
  %137 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add270 = fadd reassoc ninf nsz float %137, -2.500000e+00
  %reass.mul271 = fmul reassoc ninf nsz float %136, %reass.add270
  %138 = fadd reassoc ninf nsz float %reass.mul271, 1.000000e+00
  br label %after_if24

false_block23:                                    ; preds = %after_if18
  %139 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %139, label %true_block25, label %after_if24

after_if24:                                       ; preds = %true_block25, %false_block23, %true_block22
  %.0125 = phi float [ %138, %true_block22 ], [ %147, %true_block25 ], [ 0.000000e+00, %false_block23 ]
  %140 = fsub reassoc ninf nsz float 1.000000e+00, %55
  %141 = tail call noundef float @llvm.fabs.f32(float %140)
  %142 = fcmp reassoc ninf nsz ole float %141, 1.000000e+00
  br i1 %142, label %true_block28, label %false_block29

true_block25:                                     ; preds = %false_block23
  %143 = fmul reassoc ninf nsz float %68, %68
  %144 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg266 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %145 = fsub reassoc ninf nsz float 2.500000e+00, %144
  %reass.mul268 = fmul reassoc ninf nsz float %143, %145
  %146 = fadd reassoc ninf nsz float %.neg266, 2.000000e+00
  %147 = fadd reassoc ninf nsz float %146, %reass.mul268
  br label %after_if24

true_block28:                                     ; preds = %after_if24
  %148 = fmul reassoc ninf nsz float %140, %140
  %149 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add276 = fadd reassoc ninf nsz float %149, -2.500000e+00
  %reass.mul277 = fmul reassoc ninf nsz float %148, %reass.add276
  %150 = fadd reassoc ninf nsz float %reass.mul277, 1.000000e+00
  br label %after_if30

false_block29:                                    ; preds = %after_if24
  %151 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %151, label %true_block31, label %after_if30

after_if30:                                       ; preds = %true_block31, %false_block29, %true_block28
  %.0124 = phi float [ %150, %true_block28 ], [ %167, %true_block31 ], [ 0.000000e+00, %false_block29 ]
  %152 = add i32 %90, %130
  %153 = mul i32 %152, %89
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %87, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = fmul reassoc ninf nsz float %.0124, %.0125
  %158 = fmul reassoc ninf nsz float %157, %156
  %159 = fadd reassoc ninf nsz float %127, %158
  %160 = add i32 %51, 2
  %161 = tail call i32 @llvm.smin.i32(i32 %160, i32 %65)
  %162 = tail call i32 @llvm.smax.i32(i32 %161, i32 0)
  br i1 %70, label %true_block34, label %false_block35

true_block31:                                     ; preds = %false_block29
  %163 = fmul reassoc ninf nsz float %140, %140
  %164 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg272 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %165 = fsub reassoc ninf nsz float 2.500000e+00, %164
  %reass.mul274 = fmul reassoc ninf nsz float %163, %165
  %166 = fadd reassoc ninf nsz float %.neg272, 2.000000e+00
  %167 = fadd reassoc ninf nsz float %166, %reass.mul274
  br label %after_if30

true_block34:                                     ; preds = %after_if30
  %168 = fmul reassoc ninf nsz float %68, %68
  %169 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add282 = fadd reassoc ninf nsz float %169, -2.500000e+00
  %reass.mul283 = fmul reassoc ninf nsz float %168, %reass.add282
  %170 = fadd reassoc ninf nsz float %reass.mul283, 1.000000e+00
  br label %after_if36

false_block35:                                    ; preds = %after_if30
  %171 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %171, label %true_block37, label %after_if36

after_if36:                                       ; preds = %true_block37, %false_block35, %true_block34
  %.0123 = phi float [ %170, %true_block34 ], [ %179, %true_block37 ], [ 0.000000e+00, %false_block35 ]
  %172 = fsub reassoc ninf nsz float 2.000000e+00, %55
  %173 = tail call noundef float @llvm.fabs.f32(float %172)
  %174 = fcmp reassoc ninf nsz ole float %173, 1.000000e+00
  br i1 %174, label %true_block40, label %false_block41

true_block37:                                     ; preds = %false_block35
  %175 = fmul reassoc ninf nsz float %68, %68
  %176 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg278 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %177 = fsub reassoc ninf nsz float 2.500000e+00, %176
  %reass.mul280 = fmul reassoc ninf nsz float %175, %177
  %178 = fadd reassoc ninf nsz float %.neg278, 2.000000e+00
  %179 = fadd reassoc ninf nsz float %178, %reass.mul280
  br label %after_if36

true_block40:                                     ; preds = %after_if36
  %180 = fmul reassoc ninf nsz float %172, %172
  %181 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add288 = fadd reassoc ninf nsz float %181, -2.500000e+00
  %reass.mul289 = fmul reassoc ninf nsz float %180, %reass.add288
  %182 = fadd reassoc ninf nsz float %reass.mul289, 1.000000e+00
  br label %after_if42

false_block41:                                    ; preds = %after_if36
  %183 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %183, label %true_block43, label %after_if42

after_if42:                                       ; preds = %true_block43, %false_block41, %true_block40
  %.0122 = phi float [ %182, %true_block40 ], [ %200, %true_block43 ], [ 0.000000e+00, %false_block41 ]
  %184 = add i32 %90, %162
  %185 = mul i32 %184, %89
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %87, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = fmul reassoc ninf nsz float %.0122, %.0123
  %190 = fmul reassoc ninf nsz float %189, %188
  %191 = fadd reassoc ninf nsz float %159, %190
  %192 = tail call i32 @llvm.smin.i32(i32 %49, i32 %59)
  %193 = tail call i32 @llvm.smax.i32(i32 %192, i32 0)
  %194 = tail call float @llvm.fabs.f32(float %53)
  %195 = fcmp reassoc ninf nsz ole float %194, 1.000000e+00
  br i1 %195, label %true_block46, label %false_block47

true_block43:                                     ; preds = %false_block41
  %196 = fmul reassoc ninf nsz float %172, %172
  %197 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg284 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %198 = fsub reassoc ninf nsz float 2.500000e+00, %197
  %reass.mul286 = fmul reassoc ninf nsz float %196, %198
  %199 = fadd reassoc ninf nsz float %.neg284, 2.000000e+00
  %200 = fadd reassoc ninf nsz float %199, %reass.mul286
  br label %after_if42

true_block46:                                     ; preds = %after_if42
  %201 = fmul reassoc ninf nsz float %53, %53
  %202 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add294 = fadd reassoc ninf nsz float %202, -2.500000e+00
  %reass.mul295 = fmul reassoc ninf nsz float %201, %reass.add294
  %203 = fadd reassoc ninf nsz float %reass.mul295, 1.000000e+00
  br label %after_if48

false_block47:                                    ; preds = %after_if42
  %204 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %204, label %true_block49, label %after_if48

after_if48:                                       ; preds = %true_block49, %false_block47, %true_block46
  %.0121 = phi float [ %203, %true_block46 ], [ %209, %true_block49 ], [ 0.000000e+00, %false_block47 ]
  br i1 %77, label %true_block52, label %false_block53

true_block49:                                     ; preds = %false_block47
  %205 = fmul reassoc ninf nsz float %53, %53
  %206 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg290 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %207 = fsub reassoc ninf nsz float 2.500000e+00, %206
  %reass.mul292 = fmul reassoc ninf nsz float %205, %207
  %208 = fadd reassoc ninf nsz float %.neg290, 2.000000e+00
  %209 = fadd reassoc ninf nsz float %208, %reass.mul292
  br label %after_if48

true_block52:                                     ; preds = %after_if48
  %210 = fmul reassoc ninf nsz float %75, %75
  %211 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add300 = fadd reassoc ninf nsz float %211, -2.500000e+00
  %reass.mul301 = fmul reassoc ninf nsz float %210, %reass.add300
  %212 = fadd reassoc ninf nsz float %reass.mul301, 1.000000e+00
  br label %after_if54

false_block53:                                    ; preds = %after_if48
  %213 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %213, label %true_block55, label %after_if54

after_if54:                                       ; preds = %true_block55, %false_block53, %true_block52
  %.0120 = phi float [ %212, %true_block52 ], [ %227, %true_block55 ], [ 0.000000e+00, %false_block53 ]
  %214 = mul i32 %88, %193
  %215 = add i32 %214, %67
  %216 = mul i32 %215, %89
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %87, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %.0120, %.0121
  %221 = fmul reassoc ninf nsz float %220, %219
  %222 = fadd reassoc ninf nsz float %191, %221
  br i1 %195, label %true_block58, label %false_block59

true_block55:                                     ; preds = %false_block53
  %223 = fmul reassoc ninf nsz float %75, %75
  %224 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg296 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %225 = fsub reassoc ninf nsz float 2.500000e+00, %224
  %reass.mul298 = fmul reassoc ninf nsz float %223, %225
  %226 = fadd reassoc ninf nsz float %.neg296, 2.000000e+00
  %227 = fadd reassoc ninf nsz float %226, %reass.mul298
  br label %after_if54

true_block58:                                     ; preds = %after_if54
  %228 = fmul reassoc ninf nsz float %53, %53
  %229 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add306 = fadd reassoc ninf nsz float %229, -2.500000e+00
  %reass.mul307 = fmul reassoc ninf nsz float %228, %reass.add306
  %230 = fadd reassoc ninf nsz float %reass.mul307, 1.000000e+00
  br label %after_if60

false_block59:                                    ; preds = %after_if54
  %231 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %231, label %true_block61, label %after_if60

after_if60:                                       ; preds = %true_block61, %false_block59, %true_block58
  %.0119 = phi float [ %230, %true_block58 ], [ %236, %true_block61 ], [ 0.000000e+00, %false_block59 ]
  br i1 %110, label %true_block64, label %false_block65

true_block61:                                     ; preds = %false_block59
  %232 = fmul reassoc ninf nsz float %53, %53
  %233 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg302 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %234 = fsub reassoc ninf nsz float 2.500000e+00, %233
  %reass.mul304 = fmul reassoc ninf nsz float %232, %234
  %235 = fadd reassoc ninf nsz float %.neg302, 2.000000e+00
  %236 = fadd reassoc ninf nsz float %235, %reass.mul304
  br label %after_if60

true_block64:                                     ; preds = %after_if60
  %237 = fmul reassoc ninf nsz float %55, %55
  %238 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add312 = fadd reassoc ninf nsz float %238, -2.500000e+00
  %reass.mul313 = fmul reassoc ninf nsz float %237, %reass.add312
  %239 = fadd reassoc ninf nsz float %reass.mul313, 1.000000e+00
  br label %after_if66

false_block65:                                    ; preds = %after_if60
  %240 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %240, label %true_block67, label %after_if66

after_if66:                                       ; preds = %true_block67, %false_block65, %true_block64
  %.0118 = phi float [ %239, %true_block64 ], [ %253, %true_block67 ], [ 0.000000e+00, %false_block65 ]
  %241 = add i32 %214, %99
  %242 = mul i32 %241, %89
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, ptr %87, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = fmul reassoc ninf nsz float %.0118, %.0119
  %247 = fmul reassoc ninf nsz float %246, %245
  %248 = fadd reassoc ninf nsz float %222, %247
  br i1 %195, label %true_block70, label %false_block71

true_block67:                                     ; preds = %false_block65
  %249 = fmul reassoc ninf nsz float %55, %55
  %250 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg308 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %251 = fsub reassoc ninf nsz float 2.500000e+00, %250
  %reass.mul310 = fmul reassoc ninf nsz float %249, %251
  %252 = fadd reassoc ninf nsz float %.neg308, 2.000000e+00
  %253 = fadd reassoc ninf nsz float %252, %reass.mul310
  br label %after_if66

true_block70:                                     ; preds = %after_if66
  %254 = fmul reassoc ninf nsz float %53, %53
  %255 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add318 = fadd reassoc ninf nsz float %255, -2.500000e+00
  %reass.mul319 = fmul reassoc ninf nsz float %254, %reass.add318
  %256 = fadd reassoc ninf nsz float %reass.mul319, 1.000000e+00
  br label %after_if72

false_block71:                                    ; preds = %after_if66
  %257 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %257, label %true_block73, label %after_if72

after_if72:                                       ; preds = %true_block73, %false_block71, %true_block70
  %.0117 = phi float [ %256, %true_block70 ], [ %262, %true_block73 ], [ 0.000000e+00, %false_block71 ]
  br i1 %142, label %true_block76, label %false_block77

true_block73:                                     ; preds = %false_block71
  %258 = fmul reassoc ninf nsz float %53, %53
  %259 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg314 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %260 = fsub reassoc ninf nsz float 2.500000e+00, %259
  %reass.mul316 = fmul reassoc ninf nsz float %258, %260
  %261 = fadd reassoc ninf nsz float %.neg314, 2.000000e+00
  %262 = fadd reassoc ninf nsz float %261, %reass.mul316
  br label %after_if72

true_block76:                                     ; preds = %after_if72
  %263 = fmul reassoc ninf nsz float %140, %140
  %264 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add324 = fadd reassoc ninf nsz float %264, -2.500000e+00
  %reass.mul325 = fmul reassoc ninf nsz float %263, %reass.add324
  %265 = fadd reassoc ninf nsz float %reass.mul325, 1.000000e+00
  br label %after_if78

false_block77:                                    ; preds = %after_if72
  %266 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %266, label %true_block79, label %after_if78

after_if78:                                       ; preds = %true_block79, %false_block77, %true_block76
  %.0116 = phi float [ %265, %true_block76 ], [ %279, %true_block79 ], [ 0.000000e+00, %false_block77 ]
  %267 = add i32 %214, %130
  %268 = mul i32 %267, %89
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, ptr %87, i64 %269
  %271 = load float, ptr %270, align 4
  %272 = fmul reassoc ninf nsz float %.0116, %.0117
  %273 = fmul reassoc ninf nsz float %272, %271
  %274 = fadd reassoc ninf nsz float %248, %273
  br i1 %195, label %true_block82, label %false_block83

true_block79:                                     ; preds = %false_block77
  %275 = fmul reassoc ninf nsz float %140, %140
  %276 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg320 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %277 = fsub reassoc ninf nsz float 2.500000e+00, %276
  %reass.mul322 = fmul reassoc ninf nsz float %275, %277
  %278 = fadd reassoc ninf nsz float %.neg320, 2.000000e+00
  %279 = fadd reassoc ninf nsz float %278, %reass.mul322
  br label %after_if78

true_block82:                                     ; preds = %after_if78
  %280 = fmul reassoc ninf nsz float %53, %53
  %281 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add330 = fadd reassoc ninf nsz float %281, -2.500000e+00
  %reass.mul331 = fmul reassoc ninf nsz float %280, %reass.add330
  %282 = fadd reassoc ninf nsz float %reass.mul331, 1.000000e+00
  br label %after_if84

false_block83:                                    ; preds = %after_if78
  %283 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %283, label %true_block85, label %after_if84

after_if84:                                       ; preds = %true_block85, %false_block83, %true_block82
  %.0115 = phi float [ %282, %true_block82 ], [ %288, %true_block85 ], [ 0.000000e+00, %false_block83 ]
  br i1 %174, label %true_block88, label %false_block89

true_block85:                                     ; preds = %false_block83
  %284 = fmul reassoc ninf nsz float %53, %53
  %285 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg326 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %286 = fsub reassoc ninf nsz float 2.500000e+00, %285
  %reass.mul328 = fmul reassoc ninf nsz float %284, %286
  %287 = fadd reassoc ninf nsz float %.neg326, 2.000000e+00
  %288 = fadd reassoc ninf nsz float %287, %reass.mul328
  br label %after_if84

true_block88:                                     ; preds = %after_if84
  %289 = fmul reassoc ninf nsz float %172, %172
  %290 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add336 = fadd reassoc ninf nsz float %290, -2.500000e+00
  %reass.mul337 = fmul reassoc ninf nsz float %289, %reass.add336
  %291 = fadd reassoc ninf nsz float %reass.mul337, 1.000000e+00
  br label %after_if90

false_block89:                                    ; preds = %after_if84
  %292 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %292, label %true_block91, label %after_if90

after_if90:                                       ; preds = %true_block91, %false_block89, %true_block88
  %.0114 = phi float [ %291, %true_block88 ], [ %311, %true_block91 ], [ 0.000000e+00, %false_block89 ]
  %293 = add i32 %214, %162
  %294 = mul i32 %293, %89
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %87, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = fmul reassoc ninf nsz float %.0114, %.0115
  %299 = fmul reassoc ninf nsz float %298, %297
  %300 = fadd reassoc ninf nsz float %274, %299
  %301 = add i32 %49, 1
  %302 = tail call i32 @llvm.smin.i32(i32 %301, i32 %59)
  %303 = tail call i32 @llvm.smax.i32(i32 %302, i32 0)
  %304 = fsub reassoc ninf nsz float 1.000000e+00, %53
  %305 = tail call noundef float @llvm.fabs.f32(float %304)
  %306 = fcmp reassoc ninf nsz ole float %305, 1.000000e+00
  br i1 %306, label %true_block94, label %false_block95

true_block91:                                     ; preds = %false_block89
  %307 = fmul reassoc ninf nsz float %172, %172
  %308 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg332 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %309 = fsub reassoc ninf nsz float 2.500000e+00, %308
  %reass.mul334 = fmul reassoc ninf nsz float %307, %309
  %310 = fadd reassoc ninf nsz float %.neg332, 2.000000e+00
  %311 = fadd reassoc ninf nsz float %310, %reass.mul334
  br label %after_if90

true_block94:                                     ; preds = %after_if90
  %312 = fmul reassoc ninf nsz float %304, %304
  %313 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add342 = fadd reassoc ninf nsz float %313, -2.500000e+00
  %reass.mul343 = fmul reassoc ninf nsz float %312, %reass.add342
  %314 = fadd reassoc ninf nsz float %reass.mul343, 1.000000e+00
  br label %after_if96

false_block95:                                    ; preds = %after_if90
  %315 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %315, label %true_block97, label %after_if96

after_if96:                                       ; preds = %true_block97, %false_block95, %true_block94
  %.0113 = phi float [ %314, %true_block94 ], [ %320, %true_block97 ], [ 0.000000e+00, %false_block95 ]
  br i1 %77, label %true_block100, label %false_block101

true_block97:                                     ; preds = %false_block95
  %316 = fmul reassoc ninf nsz float %304, %304
  %317 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg338 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %318 = fsub reassoc ninf nsz float 2.500000e+00, %317
  %reass.mul340 = fmul reassoc ninf nsz float %316, %318
  %319 = fadd reassoc ninf nsz float %.neg338, 2.000000e+00
  %320 = fadd reassoc ninf nsz float %319, %reass.mul340
  br label %after_if96

true_block100:                                    ; preds = %after_if96
  %321 = fmul reassoc ninf nsz float %75, %75
  %322 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add348 = fadd reassoc ninf nsz float %322, -2.500000e+00
  %reass.mul349 = fmul reassoc ninf nsz float %321, %reass.add348
  %323 = fadd reassoc ninf nsz float %reass.mul349, 1.000000e+00
  br label %after_if102

false_block101:                                   ; preds = %after_if96
  %324 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %324, label %true_block103, label %after_if102

after_if102:                                      ; preds = %true_block103, %false_block101, %true_block100
  %.0112 = phi float [ %323, %true_block100 ], [ %338, %true_block103 ], [ 0.000000e+00, %false_block101 ]
  %325 = mul i32 %88, %303
  %326 = add i32 %325, %67
  %327 = mul i32 %326, %89
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %87, i64 %328
  %330 = load float, ptr %329, align 4
  %331 = fmul reassoc ninf nsz float %.0112, %.0113
  %332 = fmul reassoc ninf nsz float %331, %330
  %333 = fadd reassoc ninf nsz float %300, %332
  br i1 %306, label %true_block106, label %false_block107

true_block103:                                    ; preds = %false_block101
  %334 = fmul reassoc ninf nsz float %75, %75
  %335 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg344 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %336 = fsub reassoc ninf nsz float 2.500000e+00, %335
  %reass.mul346 = fmul reassoc ninf nsz float %334, %336
  %337 = fadd reassoc ninf nsz float %.neg344, 2.000000e+00
  %338 = fadd reassoc ninf nsz float %337, %reass.mul346
  br label %after_if102

true_block106:                                    ; preds = %after_if102
  %339 = fmul reassoc ninf nsz float %304, %304
  %340 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add354 = fadd reassoc ninf nsz float %340, -2.500000e+00
  %reass.mul355 = fmul reassoc ninf nsz float %339, %reass.add354
  %341 = fadd reassoc ninf nsz float %reass.mul355, 1.000000e+00
  br label %after_if108

false_block107:                                   ; preds = %after_if102
  %342 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %342, label %true_block109, label %after_if108

after_if108:                                      ; preds = %true_block109, %false_block107, %true_block106
  %.0111 = phi float [ %341, %true_block106 ], [ %347, %true_block109 ], [ 0.000000e+00, %false_block107 ]
  br i1 %110, label %true_block112, label %false_block113

true_block109:                                    ; preds = %false_block107
  %343 = fmul reassoc ninf nsz float %304, %304
  %344 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg350 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %345 = fsub reassoc ninf nsz float 2.500000e+00, %344
  %reass.mul352 = fmul reassoc ninf nsz float %343, %345
  %346 = fadd reassoc ninf nsz float %.neg350, 2.000000e+00
  %347 = fadd reassoc ninf nsz float %346, %reass.mul352
  br label %after_if108

true_block112:                                    ; preds = %after_if108
  %348 = fmul reassoc ninf nsz float %55, %55
  %349 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add360 = fadd reassoc ninf nsz float %349, -2.500000e+00
  %reass.mul361 = fmul reassoc ninf nsz float %348, %reass.add360
  %350 = fadd reassoc ninf nsz float %reass.mul361, 1.000000e+00
  br label %after_if114

false_block113:                                   ; preds = %after_if108
  %351 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %351, label %true_block115, label %after_if114

after_if114:                                      ; preds = %true_block115, %false_block113, %true_block112
  %.0110 = phi float [ %350, %true_block112 ], [ %364, %true_block115 ], [ 0.000000e+00, %false_block113 ]
  %352 = add i32 %325, %99
  %353 = mul i32 %352, %89
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, ptr %87, i64 %354
  %356 = load float, ptr %355, align 4
  %357 = fmul reassoc ninf nsz float %.0110, %.0111
  %358 = fmul reassoc ninf nsz float %357, %356
  %359 = fadd reassoc ninf nsz float %333, %358
  br i1 %306, label %true_block118, label %false_block119

true_block115:                                    ; preds = %false_block113
  %360 = fmul reassoc ninf nsz float %55, %55
  %361 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg356 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %362 = fsub reassoc ninf nsz float 2.500000e+00, %361
  %reass.mul358 = fmul reassoc ninf nsz float %360, %362
  %363 = fadd reassoc ninf nsz float %.neg356, 2.000000e+00
  %364 = fadd reassoc ninf nsz float %363, %reass.mul358
  br label %after_if114

true_block118:                                    ; preds = %after_if114
  %365 = fmul reassoc ninf nsz float %304, %304
  %366 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add366 = fadd reassoc ninf nsz float %366, -2.500000e+00
  %reass.mul367 = fmul reassoc ninf nsz float %365, %reass.add366
  %367 = fadd reassoc ninf nsz float %reass.mul367, 1.000000e+00
  br label %after_if120

false_block119:                                   ; preds = %after_if114
  %368 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %368, label %true_block121, label %after_if120

after_if120:                                      ; preds = %true_block121, %false_block119, %true_block118
  %.0109 = phi float [ %367, %true_block118 ], [ %373, %true_block121 ], [ 0.000000e+00, %false_block119 ]
  br i1 %142, label %true_block124, label %false_block125

true_block121:                                    ; preds = %false_block119
  %369 = fmul reassoc ninf nsz float %304, %304
  %370 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg362 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %371 = fsub reassoc ninf nsz float 2.500000e+00, %370
  %reass.mul364 = fmul reassoc ninf nsz float %369, %371
  %372 = fadd reassoc ninf nsz float %.neg362, 2.000000e+00
  %373 = fadd reassoc ninf nsz float %372, %reass.mul364
  br label %after_if120

true_block124:                                    ; preds = %after_if120
  %374 = fmul reassoc ninf nsz float %140, %140
  %375 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add372 = fadd reassoc ninf nsz float %375, -2.500000e+00
  %reass.mul373 = fmul reassoc ninf nsz float %374, %reass.add372
  %376 = fadd reassoc ninf nsz float %reass.mul373, 1.000000e+00
  br label %after_if126

false_block125:                                   ; preds = %after_if120
  %377 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %377, label %true_block127, label %after_if126

after_if126:                                      ; preds = %true_block127, %false_block125, %true_block124
  %.0108 = phi float [ %376, %true_block124 ], [ %390, %true_block127 ], [ 0.000000e+00, %false_block125 ]
  %378 = add i32 %325, %130
  %379 = mul i32 %378, %89
  %380 = sext i32 %379 to i64
  %381 = getelementptr float, ptr %87, i64 %380
  %382 = load float, ptr %381, align 4
  %383 = fmul reassoc ninf nsz float %.0108, %.0109
  %384 = fmul reassoc ninf nsz float %383, %382
  %385 = fadd reassoc ninf nsz float %359, %384
  br i1 %306, label %true_block130, label %false_block131

true_block127:                                    ; preds = %false_block125
  %386 = fmul reassoc ninf nsz float %140, %140
  %387 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg368 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %388 = fsub reassoc ninf nsz float 2.500000e+00, %387
  %reass.mul370 = fmul reassoc ninf nsz float %386, %388
  %389 = fadd reassoc ninf nsz float %.neg368, 2.000000e+00
  %390 = fadd reassoc ninf nsz float %389, %reass.mul370
  br label %after_if126

true_block130:                                    ; preds = %after_if126
  %391 = fmul reassoc ninf nsz float %304, %304
  %392 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add378 = fadd reassoc ninf nsz float %392, -2.500000e+00
  %reass.mul379 = fmul reassoc ninf nsz float %391, %reass.add378
  %393 = fadd reassoc ninf nsz float %reass.mul379, 1.000000e+00
  br label %after_if132

false_block131:                                   ; preds = %after_if126
  %394 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %394, label %true_block133, label %after_if132

after_if132:                                      ; preds = %true_block133, %false_block131, %true_block130
  %.0107 = phi float [ %393, %true_block130 ], [ %399, %true_block133 ], [ 0.000000e+00, %false_block131 ]
  br i1 %174, label %true_block136, label %false_block137

true_block133:                                    ; preds = %false_block131
  %395 = fmul reassoc ninf nsz float %304, %304
  %396 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg374 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %397 = fsub reassoc ninf nsz float 2.500000e+00, %396
  %reass.mul376 = fmul reassoc ninf nsz float %395, %397
  %398 = fadd reassoc ninf nsz float %.neg374, 2.000000e+00
  %399 = fadd reassoc ninf nsz float %398, %reass.mul376
  br label %after_if132

true_block136:                                    ; preds = %after_if132
  %400 = fmul reassoc ninf nsz float %172, %172
  %401 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add384 = fadd reassoc ninf nsz float %401, -2.500000e+00
  %reass.mul385 = fmul reassoc ninf nsz float %400, %reass.add384
  %402 = fadd reassoc ninf nsz float %reass.mul385, 1.000000e+00
  br label %after_if138

false_block137:                                   ; preds = %after_if132
  %403 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %403, label %true_block139, label %after_if138

after_if138:                                      ; preds = %true_block139, %false_block137, %true_block136
  %.0106 = phi float [ %402, %true_block136 ], [ %422, %true_block139 ], [ 0.000000e+00, %false_block137 ]
  %404 = add i32 %325, %162
  %405 = mul i32 %404, %89
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %87, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = fmul reassoc ninf nsz float %.0106, %.0107
  %410 = fmul reassoc ninf nsz float %409, %408
  %411 = fadd reassoc ninf nsz float %385, %410
  %412 = add i32 %49, 2
  %413 = tail call i32 @llvm.smin.i32(i32 %412, i32 %59)
  %414 = tail call i32 @llvm.smax.i32(i32 %413, i32 0)
  %415 = fsub reassoc ninf nsz float 2.000000e+00, %53
  %416 = tail call noundef float @llvm.fabs.f32(float %415)
  %417 = fcmp reassoc ninf nsz ole float %416, 1.000000e+00
  br i1 %417, label %true_block142, label %false_block143

true_block139:                                    ; preds = %false_block137
  %418 = fmul reassoc ninf nsz float %172, %172
  %419 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg380 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %420 = fsub reassoc ninf nsz float 2.500000e+00, %419
  %reass.mul382 = fmul reassoc ninf nsz float %418, %420
  %421 = fadd reassoc ninf nsz float %.neg380, 2.000000e+00
  %422 = fadd reassoc ninf nsz float %421, %reass.mul382
  br label %after_if138

true_block142:                                    ; preds = %after_if138
  %423 = fmul reassoc ninf nsz float %415, %415
  %424 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add390 = fadd reassoc ninf nsz float %424, -2.500000e+00
  %reass.mul391 = fmul reassoc ninf nsz float %423, %reass.add390
  %425 = fadd reassoc ninf nsz float %reass.mul391, 1.000000e+00
  br label %after_if144

false_block143:                                   ; preds = %after_if138
  %426 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %426, label %true_block145, label %after_if144

after_if144:                                      ; preds = %true_block145, %false_block143, %true_block142
  %.0105 = phi float [ %425, %true_block142 ], [ %431, %true_block145 ], [ 0.000000e+00, %false_block143 ]
  br i1 %77, label %true_block148, label %false_block149

true_block145:                                    ; preds = %false_block143
  %427 = fmul reassoc ninf nsz float %415, %415
  %428 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg386 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %429 = fsub reassoc ninf nsz float 2.500000e+00, %428
  %reass.mul388 = fmul reassoc ninf nsz float %427, %429
  %430 = fadd reassoc ninf nsz float %.neg386, 2.000000e+00
  %431 = fadd reassoc ninf nsz float %430, %reass.mul388
  br label %after_if144

true_block148:                                    ; preds = %after_if144
  %432 = fmul reassoc ninf nsz float %75, %75
  %433 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add396 = fadd reassoc ninf nsz float %433, -2.500000e+00
  %reass.mul397 = fmul reassoc ninf nsz float %432, %reass.add396
  %434 = fadd reassoc ninf nsz float %reass.mul397, 1.000000e+00
  br label %after_if150

false_block149:                                   ; preds = %after_if144
  %435 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %435, label %true_block151, label %after_if150

after_if150:                                      ; preds = %true_block151, %false_block149, %true_block148
  %.0104 = phi float [ %434, %true_block148 ], [ %449, %true_block151 ], [ 0.000000e+00, %false_block149 ]
  %436 = mul i32 %88, %414
  %437 = add i32 %436, %67
  %438 = mul i32 %437, %89
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %87, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = fmul reassoc ninf nsz float %.0104, %.0105
  %443 = fmul reassoc ninf nsz float %442, %441
  %444 = fadd reassoc ninf nsz float %411, %443
  br i1 %417, label %true_block154, label %false_block155

true_block151:                                    ; preds = %false_block149
  %445 = fmul reassoc ninf nsz float %75, %75
  %446 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg392 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %447 = fsub reassoc ninf nsz float 2.500000e+00, %446
  %reass.mul394 = fmul reassoc ninf nsz float %445, %447
  %448 = fadd reassoc ninf nsz float %.neg392, 2.000000e+00
  %449 = fadd reassoc ninf nsz float %448, %reass.mul394
  br label %after_if150

true_block154:                                    ; preds = %after_if150
  %450 = fmul reassoc ninf nsz float %415, %415
  %451 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add402 = fadd reassoc ninf nsz float %451, -2.500000e+00
  %reass.mul403 = fmul reassoc ninf nsz float %450, %reass.add402
  %452 = fadd reassoc ninf nsz float %reass.mul403, 1.000000e+00
  br label %after_if156

false_block155:                                   ; preds = %after_if150
  %453 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %453, label %true_block157, label %after_if156

after_if156:                                      ; preds = %true_block157, %false_block155, %true_block154
  %.0103 = phi float [ %452, %true_block154 ], [ %458, %true_block157 ], [ 0.000000e+00, %false_block155 ]
  br i1 %110, label %true_block160, label %false_block161

true_block157:                                    ; preds = %false_block155
  %454 = fmul reassoc ninf nsz float %415, %415
  %455 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg398 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %456 = fsub reassoc ninf nsz float 2.500000e+00, %455
  %reass.mul400 = fmul reassoc ninf nsz float %454, %456
  %457 = fadd reassoc ninf nsz float %.neg398, 2.000000e+00
  %458 = fadd reassoc ninf nsz float %457, %reass.mul400
  br label %after_if156

true_block160:                                    ; preds = %after_if156
  %459 = fmul reassoc ninf nsz float %55, %55
  %460 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add408 = fadd reassoc ninf nsz float %460, -2.500000e+00
  %reass.mul409 = fmul reassoc ninf nsz float %459, %reass.add408
  %461 = fadd reassoc ninf nsz float %reass.mul409, 1.000000e+00
  br label %after_if162

false_block161:                                   ; preds = %after_if156
  %462 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %462, label %true_block163, label %after_if162

after_if162:                                      ; preds = %true_block163, %false_block161, %true_block160
  %.0102 = phi float [ %461, %true_block160 ], [ %475, %true_block163 ], [ 0.000000e+00, %false_block161 ]
  %463 = add i32 %436, %99
  %464 = mul i32 %463, %89
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %87, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = fmul reassoc ninf nsz float %.0102, %.0103
  %469 = fmul reassoc ninf nsz float %468, %467
  %470 = fadd reassoc ninf nsz float %444, %469
  br i1 %417, label %true_block166, label %false_block167

true_block163:                                    ; preds = %false_block161
  %471 = fmul reassoc ninf nsz float %55, %55
  %472 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg404 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %473 = fsub reassoc ninf nsz float 2.500000e+00, %472
  %reass.mul406 = fmul reassoc ninf nsz float %471, %473
  %474 = fadd reassoc ninf nsz float %.neg404, 2.000000e+00
  %475 = fadd reassoc ninf nsz float %474, %reass.mul406
  br label %after_if162

true_block166:                                    ; preds = %after_if162
  %476 = fmul reassoc ninf nsz float %415, %415
  %477 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add414 = fadd reassoc ninf nsz float %477, -2.500000e+00
  %reass.mul415 = fmul reassoc ninf nsz float %476, %reass.add414
  %478 = fadd reassoc ninf nsz float %reass.mul415, 1.000000e+00
  br label %after_if168

false_block167:                                   ; preds = %after_if162
  %479 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %479, label %true_block169, label %after_if168

after_if168:                                      ; preds = %true_block169, %false_block167, %true_block166
  %.0101 = phi float [ %478, %true_block166 ], [ %484, %true_block169 ], [ 0.000000e+00, %false_block167 ]
  br i1 %142, label %true_block172, label %false_block173

true_block169:                                    ; preds = %false_block167
  %480 = fmul reassoc ninf nsz float %415, %415
  %481 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg410 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %482 = fsub reassoc ninf nsz float 2.500000e+00, %481
  %reass.mul412 = fmul reassoc ninf nsz float %480, %482
  %483 = fadd reassoc ninf nsz float %.neg410, 2.000000e+00
  %484 = fadd reassoc ninf nsz float %483, %reass.mul412
  br label %after_if168

true_block172:                                    ; preds = %after_if168
  %485 = fmul reassoc ninf nsz float %140, %140
  %486 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add420 = fadd reassoc ninf nsz float %486, -2.500000e+00
  %reass.mul421 = fmul reassoc ninf nsz float %485, %reass.add420
  %487 = fadd reassoc ninf nsz float %reass.mul421, 1.000000e+00
  br label %after_if174

false_block173:                                   ; preds = %after_if168
  %488 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %488, label %true_block175, label %after_if174

after_if174:                                      ; preds = %true_block175, %false_block173, %true_block172
  %.0100 = phi float [ %487, %true_block172 ], [ %501, %true_block175 ], [ 0.000000e+00, %false_block173 ]
  %489 = add i32 %436, %130
  %490 = mul i32 %489, %89
  %491 = sext i32 %490 to i64
  %492 = getelementptr float, ptr %87, i64 %491
  %493 = load float, ptr %492, align 4
  %494 = fmul reassoc ninf nsz float %.0100, %.0101
  %495 = fmul reassoc ninf nsz float %494, %493
  %496 = fadd reassoc ninf nsz float %470, %495
  br i1 %417, label %true_block178, label %false_block179

true_block175:                                    ; preds = %false_block173
  %497 = fmul reassoc ninf nsz float %140, %140
  %498 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg416 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %499 = fsub reassoc ninf nsz float 2.500000e+00, %498
  %reass.mul418 = fmul reassoc ninf nsz float %497, %499
  %500 = fadd reassoc ninf nsz float %.neg416, 2.000000e+00
  %501 = fadd reassoc ninf nsz float %500, %reass.mul418
  br label %after_if174

true_block178:                                    ; preds = %after_if174
  %502 = fmul reassoc ninf nsz float %415, %415
  %503 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add426 = fadd reassoc ninf nsz float %503, -2.500000e+00
  %reass.mul427 = fmul reassoc ninf nsz float %502, %reass.add426
  %504 = fadd reassoc ninf nsz float %reass.mul427, 1.000000e+00
  br label %after_if180

false_block179:                                   ; preds = %after_if174
  %505 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %505, label %true_block181, label %after_if180

after_if180:                                      ; preds = %true_block181, %false_block179, %true_block178
  %.099 = phi float [ %504, %true_block178 ], [ %510, %true_block181 ], [ 0.000000e+00, %false_block179 ]
  br i1 %174, label %true_block184, label %false_block185

true_block181:                                    ; preds = %false_block179
  %506 = fmul reassoc ninf nsz float %415, %415
  %507 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg422 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %508 = fsub reassoc ninf nsz float 2.500000e+00, %507
  %reass.mul424 = fmul reassoc ninf nsz float %506, %508
  %509 = fadd reassoc ninf nsz float %.neg422, 2.000000e+00
  %510 = fadd reassoc ninf nsz float %509, %reass.mul424
  br label %after_if180

true_block184:                                    ; preds = %after_if180
  %511 = fmul reassoc ninf nsz float %172, %172
  %512 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add432 = fadd reassoc ninf nsz float %512, -2.500000e+00
  %reass.mul433 = fmul reassoc ninf nsz float %511, %reass.add432
  %513 = fadd reassoc ninf nsz float %reass.mul433, 1.000000e+00
  br label %after_if186

false_block185:                                   ; preds = %after_if180
  %514 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %514, label %true_block187, label %after_if186

after_if186:                                      ; preds = %true_block187, %false_block185, %true_block184
  %.098 = phi float [ %513, %true_block184 ], [ %537, %true_block187 ], [ 0.000000e+00, %false_block185 ]
  %515 = add i32 %436, %162
  %516 = mul i32 %515, %89
  %517 = sext i32 %516 to i64
  %518 = getelementptr float, ptr %87, i64 %517
  %519 = load float, ptr %518, align 4
  %520 = fmul reassoc ninf nsz float %.098, %.099
  %521 = fmul reassoc ninf nsz float %520, %519
  %522 = fadd reassoc ninf nsz float %496, %521
  %523 = fmul reassoc ninf nsz float %522, %21
  %524 = load ptr, ptr %26, align 8
  %525 = load i32, ptr %27, align 4
  %526 = load i32, ptr %28, align 4
  %527 = sub i32 %525, %33
  %528 = mul i32 %527, %40
  %529 = add i32 %.0130626, %528
  %530 = mul i32 %529, %526
  %531 = sext i32 %530 to i64
  %532 = getelementptr float, ptr %524, i64 %531
  store float %523, ptr %532, align 4
  br i1 %70, label %true_block190, label %false_block191

true_block187:                                    ; preds = %false_block185
  %533 = fmul reassoc ninf nsz float %172, %172
  %534 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg428 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %535 = fsub reassoc ninf nsz float 2.500000e+00, %534
  %reass.mul430 = fmul reassoc ninf nsz float %533, %535
  %536 = fadd reassoc ninf nsz float %.neg428, 2.000000e+00
  %537 = fadd reassoc ninf nsz float %536, %reass.mul430
  br label %after_if186

true_block190:                                    ; preds = %after_if186
  %538 = fmul reassoc ninf nsz float %68, %68
  %539 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add438 = fadd reassoc ninf nsz float %539, -2.500000e+00
  %reass.mul439 = fmul reassoc ninf nsz float %538, %reass.add438
  %540 = fadd reassoc ninf nsz float %reass.mul439, 1.000000e+00
  br label %after_if192

false_block191:                                   ; preds = %after_if186
  %541 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %541, label %true_block193, label %after_if192

after_if192:                                      ; preds = %true_block193, %false_block191, %true_block190
  %.097 = phi float [ %540, %true_block190 ], [ %546, %true_block193 ], [ 0.000000e+00, %false_block191 ]
  br i1 %77, label %true_block196, label %false_block197

true_block193:                                    ; preds = %false_block191
  %542 = fmul reassoc ninf nsz float %68, %68
  %543 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg434 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %544 = fsub reassoc ninf nsz float 2.500000e+00, %543
  %reass.mul436 = fmul reassoc ninf nsz float %542, %544
  %545 = fadd reassoc ninf nsz float %.neg434, 2.000000e+00
  %546 = fadd reassoc ninf nsz float %545, %reass.mul436
  br label %after_if192

true_block196:                                    ; preds = %after_if192
  %547 = fmul reassoc ninf nsz float %75, %75
  %548 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add444 = fadd reassoc ninf nsz float %548, -2.500000e+00
  %reass.mul445 = fmul reassoc ninf nsz float %547, %reass.add444
  %549 = fadd reassoc ninf nsz float %reass.mul445, 1.000000e+00
  br label %after_if198

false_block197:                                   ; preds = %after_if192
  %550 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %550, label %true_block199, label %after_if198

after_if198:                                      ; preds = %true_block199, %false_block197, %true_block196
  %.096 = phi float [ %549, %true_block196 ], [ %567, %true_block199 ], [ 0.000000e+00, %false_block197 ]
  %551 = load ptr, ptr %23, align 8
  %552 = load i32, ptr %24, align 4
  %553 = load i32, ptr %25, align 4
  %554 = mul i32 %552, %61
  %555 = add i32 %554, %67
  %556 = mul i32 %555, %553
  %557 = add i32 %556, 1
  %558 = sext i32 %557 to i64
  %559 = getelementptr float, ptr %551, i64 %558
  %560 = load float, ptr %559, align 4
  %561 = fmul reassoc ninf nsz float %.096, %.097
  %562 = fmul reassoc ninf nsz float %561, %560
  br i1 %70, label %true_block202, label %false_block203

true_block199:                                    ; preds = %false_block197
  %563 = fmul reassoc ninf nsz float %75, %75
  %564 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg440 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %565 = fsub reassoc ninf nsz float 2.500000e+00, %564
  %reass.mul442 = fmul reassoc ninf nsz float %563, %565
  %566 = fadd reassoc ninf nsz float %.neg440, 2.000000e+00
  %567 = fadd reassoc ninf nsz float %566, %reass.mul442
  br label %after_if198

true_block202:                                    ; preds = %after_if198
  %568 = fmul reassoc ninf nsz float %68, %68
  %569 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add450 = fadd reassoc ninf nsz float %569, -2.500000e+00
  %reass.mul451 = fmul reassoc ninf nsz float %568, %reass.add450
  %570 = fadd reassoc ninf nsz float %reass.mul451, 1.000000e+00
  br label %after_if204

false_block203:                                   ; preds = %after_if198
  %571 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %571, label %true_block205, label %after_if204

after_if204:                                      ; preds = %true_block205, %false_block203, %true_block202
  %.095 = phi float [ %570, %true_block202 ], [ %576, %true_block205 ], [ 0.000000e+00, %false_block203 ]
  br i1 %110, label %true_block208, label %false_block209

true_block205:                                    ; preds = %false_block203
  %572 = fmul reassoc ninf nsz float %68, %68
  %573 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg446 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %574 = fsub reassoc ninf nsz float 2.500000e+00, %573
  %reass.mul448 = fmul reassoc ninf nsz float %572, %574
  %575 = fadd reassoc ninf nsz float %.neg446, 2.000000e+00
  %576 = fadd reassoc ninf nsz float %575, %reass.mul448
  br label %after_if204

true_block208:                                    ; preds = %after_if204
  %577 = fmul reassoc ninf nsz float %55, %55
  %578 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add456 = fadd reassoc ninf nsz float %578, -2.500000e+00
  %reass.mul457 = fmul reassoc ninf nsz float %577, %reass.add456
  %579 = fadd reassoc ninf nsz float %reass.mul457, 1.000000e+00
  br label %after_if210

false_block209:                                   ; preds = %after_if204
  %580 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %580, label %true_block211, label %after_if210

after_if210:                                      ; preds = %true_block211, %false_block209, %true_block208
  %.094 = phi float [ %579, %true_block208 ], [ %594, %true_block211 ], [ 0.000000e+00, %false_block209 ]
  %581 = add i32 %554, %99
  %582 = mul i32 %581, %553
  %583 = add i32 %582, 1
  %584 = sext i32 %583 to i64
  %585 = getelementptr float, ptr %551, i64 %584
  %586 = load float, ptr %585, align 4
  %587 = fmul reassoc ninf nsz float %.094, %.095
  %588 = fmul reassoc ninf nsz float %587, %586
  %589 = fadd reassoc ninf nsz float %588, %562
  br i1 %70, label %true_block214, label %false_block215

true_block211:                                    ; preds = %false_block209
  %590 = fmul reassoc ninf nsz float %55, %55
  %591 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg452 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %592 = fsub reassoc ninf nsz float 2.500000e+00, %591
  %reass.mul454 = fmul reassoc ninf nsz float %590, %592
  %593 = fadd reassoc ninf nsz float %.neg452, 2.000000e+00
  %594 = fadd reassoc ninf nsz float %593, %reass.mul454
  br label %after_if210

true_block214:                                    ; preds = %after_if210
  %595 = fmul reassoc ninf nsz float %68, %68
  %596 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add462 = fadd reassoc ninf nsz float %596, -2.500000e+00
  %reass.mul463 = fmul reassoc ninf nsz float %595, %reass.add462
  %597 = fadd reassoc ninf nsz float %reass.mul463, 1.000000e+00
  br label %after_if216

false_block215:                                   ; preds = %after_if210
  %598 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %598, label %true_block217, label %after_if216

after_if216:                                      ; preds = %true_block217, %false_block215, %true_block214
  %.093 = phi float [ %597, %true_block214 ], [ %603, %true_block217 ], [ 0.000000e+00, %false_block215 ]
  br i1 %142, label %true_block220, label %false_block221

true_block217:                                    ; preds = %false_block215
  %599 = fmul reassoc ninf nsz float %68, %68
  %600 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg458 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %601 = fsub reassoc ninf nsz float 2.500000e+00, %600
  %reass.mul460 = fmul reassoc ninf nsz float %599, %601
  %602 = fadd reassoc ninf nsz float %.neg458, 2.000000e+00
  %603 = fadd reassoc ninf nsz float %602, %reass.mul460
  br label %after_if216

true_block220:                                    ; preds = %after_if216
  %604 = fmul reassoc ninf nsz float %140, %140
  %605 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add468 = fadd reassoc ninf nsz float %605, -2.500000e+00
  %reass.mul469 = fmul reassoc ninf nsz float %604, %reass.add468
  %606 = fadd reassoc ninf nsz float %reass.mul469, 1.000000e+00
  br label %after_if222

false_block221:                                   ; preds = %after_if216
  %607 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %607, label %true_block223, label %after_if222

after_if222:                                      ; preds = %true_block223, %false_block221, %true_block220
  %.092 = phi float [ %606, %true_block220 ], [ %621, %true_block223 ], [ 0.000000e+00, %false_block221 ]
  %608 = add i32 %554, %130
  %609 = mul i32 %608, %553
  %610 = add i32 %609, 1
  %611 = sext i32 %610 to i64
  %612 = getelementptr float, ptr %551, i64 %611
  %613 = load float, ptr %612, align 4
  %614 = fmul reassoc ninf nsz float %.092, %.093
  %615 = fmul reassoc ninf nsz float %614, %613
  %616 = fadd reassoc ninf nsz float %589, %615
  br i1 %70, label %true_block226, label %false_block227

true_block223:                                    ; preds = %false_block221
  %617 = fmul reassoc ninf nsz float %140, %140
  %618 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg464 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %619 = fsub reassoc ninf nsz float 2.500000e+00, %618
  %reass.mul466 = fmul reassoc ninf nsz float %617, %619
  %620 = fadd reassoc ninf nsz float %.neg464, 2.000000e+00
  %621 = fadd reassoc ninf nsz float %620, %reass.mul466
  br label %after_if222

true_block226:                                    ; preds = %after_if222
  %622 = fmul reassoc ninf nsz float %68, %68
  %623 = fmul reassoc ninf nsz float %69, 1.500000e+00
  %reass.add474 = fadd reassoc ninf nsz float %623, -2.500000e+00
  %reass.mul475 = fmul reassoc ninf nsz float %622, %reass.add474
  %624 = fadd reassoc ninf nsz float %reass.mul475, 1.000000e+00
  br label %after_if228

false_block227:                                   ; preds = %after_if222
  %625 = fcmp reassoc ninf nsz olt float %69, 2.000000e+00
  br i1 %625, label %true_block229, label %after_if228

after_if228:                                      ; preds = %true_block229, %false_block227, %true_block226
  %.091 = phi float [ %624, %true_block226 ], [ %630, %true_block229 ], [ 0.000000e+00, %false_block227 ]
  br i1 %174, label %true_block232, label %false_block233

true_block229:                                    ; preds = %false_block227
  %626 = fmul reassoc ninf nsz float %68, %68
  %627 = fmul reassoc ninf nsz float %69, 5.000000e-01
  %.neg470 = fmul reassoc ninf nsz float %69, -4.000000e+00
  %628 = fsub reassoc ninf nsz float 2.500000e+00, %627
  %reass.mul472 = fmul reassoc ninf nsz float %626, %628
  %629 = fadd reassoc ninf nsz float %.neg470, 2.000000e+00
  %630 = fadd reassoc ninf nsz float %629, %reass.mul472
  br label %after_if228

true_block232:                                    ; preds = %after_if228
  %631 = fmul reassoc ninf nsz float %172, %172
  %632 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add480 = fadd reassoc ninf nsz float %632, -2.500000e+00
  %reass.mul481 = fmul reassoc ninf nsz float %631, %reass.add480
  %633 = fadd reassoc ninf nsz float %reass.mul481, 1.000000e+00
  br label %after_if234

false_block233:                                   ; preds = %after_if228
  %634 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %634, label %true_block235, label %after_if234

after_if234:                                      ; preds = %true_block235, %false_block233, %true_block232
  %.090 = phi float [ %633, %true_block232 ], [ %648, %true_block235 ], [ 0.000000e+00, %false_block233 ]
  %635 = add i32 %554, %162
  %636 = mul i32 %635, %553
  %637 = add i32 %636, 1
  %638 = sext i32 %637 to i64
  %639 = getelementptr float, ptr %551, i64 %638
  %640 = load float, ptr %639, align 4
  %641 = fmul reassoc ninf nsz float %.090, %.091
  %642 = fmul reassoc ninf nsz float %641, %640
  %643 = fadd reassoc ninf nsz float %616, %642
  br i1 %195, label %true_block238, label %false_block239

true_block235:                                    ; preds = %false_block233
  %644 = fmul reassoc ninf nsz float %172, %172
  %645 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg476 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %646 = fsub reassoc ninf nsz float 2.500000e+00, %645
  %reass.mul478 = fmul reassoc ninf nsz float %644, %646
  %647 = fadd reassoc ninf nsz float %.neg476, 2.000000e+00
  %648 = fadd reassoc ninf nsz float %647, %reass.mul478
  br label %after_if234

true_block238:                                    ; preds = %after_if234
  %649 = fmul reassoc ninf nsz float %53, %53
  %650 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add486 = fadd reassoc ninf nsz float %650, -2.500000e+00
  %reass.mul487 = fmul reassoc ninf nsz float %649, %reass.add486
  %651 = fadd reassoc ninf nsz float %reass.mul487, 1.000000e+00
  br label %after_if240

false_block239:                                   ; preds = %after_if234
  %652 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %652, label %true_block241, label %after_if240

after_if240:                                      ; preds = %true_block241, %false_block239, %true_block238
  %.089 = phi float [ %651, %true_block238 ], [ %657, %true_block241 ], [ 0.000000e+00, %false_block239 ]
  br i1 %77, label %true_block244, label %false_block245

true_block241:                                    ; preds = %false_block239
  %653 = fmul reassoc ninf nsz float %53, %53
  %654 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg482 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %655 = fsub reassoc ninf nsz float 2.500000e+00, %654
  %reass.mul484 = fmul reassoc ninf nsz float %653, %655
  %656 = fadd reassoc ninf nsz float %.neg482, 2.000000e+00
  %657 = fadd reassoc ninf nsz float %656, %reass.mul484
  br label %after_if240

true_block244:                                    ; preds = %after_if240
  %658 = fmul reassoc ninf nsz float %75, %75
  %659 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add492 = fadd reassoc ninf nsz float %659, -2.500000e+00
  %reass.mul493 = fmul reassoc ninf nsz float %658, %reass.add492
  %660 = fadd reassoc ninf nsz float %reass.mul493, 1.000000e+00
  br label %after_if246

false_block245:                                   ; preds = %after_if240
  %661 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %661, label %true_block247, label %after_if246

after_if246:                                      ; preds = %true_block247, %false_block245, %true_block244
  %.088 = phi float [ %660, %true_block244 ], [ %676, %true_block247 ], [ 0.000000e+00, %false_block245 ]
  %662 = mul i32 %552, %193
  %663 = add i32 %662, %67
  %664 = mul i32 %663, %553
  %665 = add i32 %664, 1
  %666 = sext i32 %665 to i64
  %667 = getelementptr float, ptr %551, i64 %666
  %668 = load float, ptr %667, align 4
  %669 = fmul reassoc ninf nsz float %.088, %.089
  %670 = fmul reassoc ninf nsz float %669, %668
  %671 = fadd reassoc ninf nsz float %643, %670
  br i1 %195, label %true_block250, label %false_block251

true_block247:                                    ; preds = %false_block245
  %672 = fmul reassoc ninf nsz float %75, %75
  %673 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg488 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %674 = fsub reassoc ninf nsz float 2.500000e+00, %673
  %reass.mul490 = fmul reassoc ninf nsz float %672, %674
  %675 = fadd reassoc ninf nsz float %.neg488, 2.000000e+00
  %676 = fadd reassoc ninf nsz float %675, %reass.mul490
  br label %after_if246

true_block250:                                    ; preds = %after_if246
  %677 = fmul reassoc ninf nsz float %53, %53
  %678 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add498 = fadd reassoc ninf nsz float %678, -2.500000e+00
  %reass.mul499 = fmul reassoc ninf nsz float %677, %reass.add498
  %679 = fadd reassoc ninf nsz float %reass.mul499, 1.000000e+00
  br label %after_if252

false_block251:                                   ; preds = %after_if246
  %680 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %680, label %true_block253, label %after_if252

after_if252:                                      ; preds = %true_block253, %false_block251, %true_block250
  %.087 = phi float [ %679, %true_block250 ], [ %685, %true_block253 ], [ 0.000000e+00, %false_block251 ]
  br i1 %110, label %true_block256, label %false_block257

true_block253:                                    ; preds = %false_block251
  %681 = fmul reassoc ninf nsz float %53, %53
  %682 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg494 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %683 = fsub reassoc ninf nsz float 2.500000e+00, %682
  %reass.mul496 = fmul reassoc ninf nsz float %681, %683
  %684 = fadd reassoc ninf nsz float %.neg494, 2.000000e+00
  %685 = fadd reassoc ninf nsz float %684, %reass.mul496
  br label %after_if252

true_block256:                                    ; preds = %after_if252
  %686 = fmul reassoc ninf nsz float %55, %55
  %687 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add504 = fadd reassoc ninf nsz float %687, -2.500000e+00
  %reass.mul505 = fmul reassoc ninf nsz float %686, %reass.add504
  %688 = fadd reassoc ninf nsz float %reass.mul505, 1.000000e+00
  br label %after_if258

false_block257:                                   ; preds = %after_if252
  %689 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %689, label %true_block259, label %after_if258

after_if258:                                      ; preds = %true_block259, %false_block257, %true_block256
  %.086 = phi float [ %688, %true_block256 ], [ %703, %true_block259 ], [ 0.000000e+00, %false_block257 ]
  %690 = add i32 %662, %99
  %691 = mul i32 %690, %553
  %692 = add i32 %691, 1
  %693 = sext i32 %692 to i64
  %694 = getelementptr float, ptr %551, i64 %693
  %695 = load float, ptr %694, align 4
  %696 = fmul reassoc ninf nsz float %.086, %.087
  %697 = fmul reassoc ninf nsz float %696, %695
  %698 = fadd reassoc ninf nsz float %671, %697
  br i1 %195, label %true_block262, label %false_block263

true_block259:                                    ; preds = %false_block257
  %699 = fmul reassoc ninf nsz float %55, %55
  %700 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg500 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %701 = fsub reassoc ninf nsz float 2.500000e+00, %700
  %reass.mul502 = fmul reassoc ninf nsz float %699, %701
  %702 = fadd reassoc ninf nsz float %.neg500, 2.000000e+00
  %703 = fadd reassoc ninf nsz float %702, %reass.mul502
  br label %after_if258

true_block262:                                    ; preds = %after_if258
  %704 = fmul reassoc ninf nsz float %53, %53
  %705 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add510 = fadd reassoc ninf nsz float %705, -2.500000e+00
  %reass.mul511 = fmul reassoc ninf nsz float %704, %reass.add510
  %706 = fadd reassoc ninf nsz float %reass.mul511, 1.000000e+00
  br label %after_if264

false_block263:                                   ; preds = %after_if258
  %707 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %707, label %true_block265, label %after_if264

after_if264:                                      ; preds = %true_block265, %false_block263, %true_block262
  %.085 = phi float [ %706, %true_block262 ], [ %712, %true_block265 ], [ 0.000000e+00, %false_block263 ]
  br i1 %142, label %true_block268, label %false_block269

true_block265:                                    ; preds = %false_block263
  %708 = fmul reassoc ninf nsz float %53, %53
  %709 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg506 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %710 = fsub reassoc ninf nsz float 2.500000e+00, %709
  %reass.mul508 = fmul reassoc ninf nsz float %708, %710
  %711 = fadd reassoc ninf nsz float %.neg506, 2.000000e+00
  %712 = fadd reassoc ninf nsz float %711, %reass.mul508
  br label %after_if264

true_block268:                                    ; preds = %after_if264
  %713 = fmul reassoc ninf nsz float %140, %140
  %714 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add516 = fadd reassoc ninf nsz float %714, -2.500000e+00
  %reass.mul517 = fmul reassoc ninf nsz float %713, %reass.add516
  %715 = fadd reassoc ninf nsz float %reass.mul517, 1.000000e+00
  br label %after_if270

false_block269:                                   ; preds = %after_if264
  %716 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %716, label %true_block271, label %after_if270

after_if270:                                      ; preds = %true_block271, %false_block269, %true_block268
  %.084 = phi float [ %715, %true_block268 ], [ %730, %true_block271 ], [ 0.000000e+00, %false_block269 ]
  %717 = add i32 %662, %130
  %718 = mul i32 %717, %553
  %719 = add i32 %718, 1
  %720 = sext i32 %719 to i64
  %721 = getelementptr float, ptr %551, i64 %720
  %722 = load float, ptr %721, align 4
  %723 = fmul reassoc ninf nsz float %.084, %.085
  %724 = fmul reassoc ninf nsz float %723, %722
  %725 = fadd reassoc ninf nsz float %698, %724
  br i1 %195, label %true_block274, label %false_block275

true_block271:                                    ; preds = %false_block269
  %726 = fmul reassoc ninf nsz float %140, %140
  %727 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg512 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %728 = fsub reassoc ninf nsz float 2.500000e+00, %727
  %reass.mul514 = fmul reassoc ninf nsz float %726, %728
  %729 = fadd reassoc ninf nsz float %.neg512, 2.000000e+00
  %730 = fadd reassoc ninf nsz float %729, %reass.mul514
  br label %after_if270

true_block274:                                    ; preds = %after_if270
  %731 = fmul reassoc ninf nsz float %53, %53
  %732 = fmul reassoc ninf nsz float %194, 1.500000e+00
  %reass.add522 = fadd reassoc ninf nsz float %732, -2.500000e+00
  %reass.mul523 = fmul reassoc ninf nsz float %731, %reass.add522
  %733 = fadd reassoc ninf nsz float %reass.mul523, 1.000000e+00
  br label %after_if276

false_block275:                                   ; preds = %after_if270
  %734 = fcmp reassoc ninf nsz olt float %194, 2.000000e+00
  br i1 %734, label %true_block277, label %after_if276

after_if276:                                      ; preds = %true_block277, %false_block275, %true_block274
  %.083 = phi float [ %733, %true_block274 ], [ %739, %true_block277 ], [ 0.000000e+00, %false_block275 ]
  br i1 %174, label %true_block280, label %false_block281

true_block277:                                    ; preds = %false_block275
  %735 = fmul reassoc ninf nsz float %53, %53
  %736 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %.neg518 = fmul reassoc ninf nsz float %194, -4.000000e+00
  %737 = fsub reassoc ninf nsz float 2.500000e+00, %736
  %reass.mul520 = fmul reassoc ninf nsz float %735, %737
  %738 = fadd reassoc ninf nsz float %.neg518, 2.000000e+00
  %739 = fadd reassoc ninf nsz float %738, %reass.mul520
  br label %after_if276

true_block280:                                    ; preds = %after_if276
  %740 = fmul reassoc ninf nsz float %172, %172
  %741 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add528 = fadd reassoc ninf nsz float %741, -2.500000e+00
  %reass.mul529 = fmul reassoc ninf nsz float %740, %reass.add528
  %742 = fadd reassoc ninf nsz float %reass.mul529, 1.000000e+00
  br label %after_if282

false_block281:                                   ; preds = %after_if276
  %743 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %743, label %true_block283, label %after_if282

after_if282:                                      ; preds = %true_block283, %false_block281, %true_block280
  %.082 = phi float [ %742, %true_block280 ], [ %757, %true_block283 ], [ 0.000000e+00, %false_block281 ]
  %744 = add i32 %662, %162
  %745 = mul i32 %744, %553
  %746 = add i32 %745, 1
  %747 = sext i32 %746 to i64
  %748 = getelementptr float, ptr %551, i64 %747
  %749 = load float, ptr %748, align 4
  %750 = fmul reassoc ninf nsz float %.082, %.083
  %751 = fmul reassoc ninf nsz float %750, %749
  %752 = fadd reassoc ninf nsz float %725, %751
  br i1 %306, label %true_block286, label %false_block287

true_block283:                                    ; preds = %false_block281
  %753 = fmul reassoc ninf nsz float %172, %172
  %754 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg524 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %755 = fsub reassoc ninf nsz float 2.500000e+00, %754
  %reass.mul526 = fmul reassoc ninf nsz float %753, %755
  %756 = fadd reassoc ninf nsz float %.neg524, 2.000000e+00
  %757 = fadd reassoc ninf nsz float %756, %reass.mul526
  br label %after_if282

true_block286:                                    ; preds = %after_if282
  %758 = fmul reassoc ninf nsz float %304, %304
  %759 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add534 = fadd reassoc ninf nsz float %759, -2.500000e+00
  %reass.mul535 = fmul reassoc ninf nsz float %758, %reass.add534
  %760 = fadd reassoc ninf nsz float %reass.mul535, 1.000000e+00
  br label %after_if288

false_block287:                                   ; preds = %after_if282
  %761 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %761, label %true_block289, label %after_if288

after_if288:                                      ; preds = %true_block289, %false_block287, %true_block286
  %.081 = phi float [ %760, %true_block286 ], [ %766, %true_block289 ], [ 0.000000e+00, %false_block287 ]
  br i1 %77, label %true_block292, label %false_block293

true_block289:                                    ; preds = %false_block287
  %762 = fmul reassoc ninf nsz float %304, %304
  %763 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg530 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %764 = fsub reassoc ninf nsz float 2.500000e+00, %763
  %reass.mul532 = fmul reassoc ninf nsz float %762, %764
  %765 = fadd reassoc ninf nsz float %.neg530, 2.000000e+00
  %766 = fadd reassoc ninf nsz float %765, %reass.mul532
  br label %after_if288

true_block292:                                    ; preds = %after_if288
  %767 = fmul reassoc ninf nsz float %75, %75
  %768 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add540 = fadd reassoc ninf nsz float %768, -2.500000e+00
  %reass.mul541 = fmul reassoc ninf nsz float %767, %reass.add540
  %769 = fadd reassoc ninf nsz float %reass.mul541, 1.000000e+00
  br label %after_if294

false_block293:                                   ; preds = %after_if288
  %770 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %770, label %true_block295, label %after_if294

after_if294:                                      ; preds = %true_block295, %false_block293, %true_block292
  %.080 = phi float [ %769, %true_block292 ], [ %785, %true_block295 ], [ 0.000000e+00, %false_block293 ]
  %771 = mul i32 %552, %303
  %772 = add i32 %771, %67
  %773 = mul i32 %772, %553
  %774 = add i32 %773, 1
  %775 = sext i32 %774 to i64
  %776 = getelementptr float, ptr %551, i64 %775
  %777 = load float, ptr %776, align 4
  %778 = fmul reassoc ninf nsz float %.080, %.081
  %779 = fmul reassoc ninf nsz float %778, %777
  %780 = fadd reassoc ninf nsz float %752, %779
  br i1 %306, label %true_block298, label %false_block299

true_block295:                                    ; preds = %false_block293
  %781 = fmul reassoc ninf nsz float %75, %75
  %782 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg536 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %783 = fsub reassoc ninf nsz float 2.500000e+00, %782
  %reass.mul538 = fmul reassoc ninf nsz float %781, %783
  %784 = fadd reassoc ninf nsz float %.neg536, 2.000000e+00
  %785 = fadd reassoc ninf nsz float %784, %reass.mul538
  br label %after_if294

true_block298:                                    ; preds = %after_if294
  %786 = fmul reassoc ninf nsz float %304, %304
  %787 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add546 = fadd reassoc ninf nsz float %787, -2.500000e+00
  %reass.mul547 = fmul reassoc ninf nsz float %786, %reass.add546
  %788 = fadd reassoc ninf nsz float %reass.mul547, 1.000000e+00
  br label %after_if300

false_block299:                                   ; preds = %after_if294
  %789 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %789, label %true_block301, label %after_if300

after_if300:                                      ; preds = %true_block301, %false_block299, %true_block298
  %.079 = phi float [ %788, %true_block298 ], [ %794, %true_block301 ], [ 0.000000e+00, %false_block299 ]
  br i1 %110, label %true_block304, label %false_block305

true_block301:                                    ; preds = %false_block299
  %790 = fmul reassoc ninf nsz float %304, %304
  %791 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg542 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %792 = fsub reassoc ninf nsz float 2.500000e+00, %791
  %reass.mul544 = fmul reassoc ninf nsz float %790, %792
  %793 = fadd reassoc ninf nsz float %.neg542, 2.000000e+00
  %794 = fadd reassoc ninf nsz float %793, %reass.mul544
  br label %after_if300

true_block304:                                    ; preds = %after_if300
  %795 = fmul reassoc ninf nsz float %55, %55
  %796 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add552 = fadd reassoc ninf nsz float %796, -2.500000e+00
  %reass.mul553 = fmul reassoc ninf nsz float %795, %reass.add552
  %797 = fadd reassoc ninf nsz float %reass.mul553, 1.000000e+00
  br label %after_if306

false_block305:                                   ; preds = %after_if300
  %798 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %798, label %true_block307, label %after_if306

after_if306:                                      ; preds = %true_block307, %false_block305, %true_block304
  %.078 = phi float [ %797, %true_block304 ], [ %812, %true_block307 ], [ 0.000000e+00, %false_block305 ]
  %799 = add i32 %771, %99
  %800 = mul i32 %799, %553
  %801 = add i32 %800, 1
  %802 = sext i32 %801 to i64
  %803 = getelementptr float, ptr %551, i64 %802
  %804 = load float, ptr %803, align 4
  %805 = fmul reassoc ninf nsz float %.078, %.079
  %806 = fmul reassoc ninf nsz float %805, %804
  %807 = fadd reassoc ninf nsz float %780, %806
  br i1 %306, label %true_block310, label %false_block311

true_block307:                                    ; preds = %false_block305
  %808 = fmul reassoc ninf nsz float %55, %55
  %809 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg548 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %810 = fsub reassoc ninf nsz float 2.500000e+00, %809
  %reass.mul550 = fmul reassoc ninf nsz float %808, %810
  %811 = fadd reassoc ninf nsz float %.neg548, 2.000000e+00
  %812 = fadd reassoc ninf nsz float %811, %reass.mul550
  br label %after_if306

true_block310:                                    ; preds = %after_if306
  %813 = fmul reassoc ninf nsz float %304, %304
  %814 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add558 = fadd reassoc ninf nsz float %814, -2.500000e+00
  %reass.mul559 = fmul reassoc ninf nsz float %813, %reass.add558
  %815 = fadd reassoc ninf nsz float %reass.mul559, 1.000000e+00
  br label %after_if312

false_block311:                                   ; preds = %after_if306
  %816 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %816, label %true_block313, label %after_if312

after_if312:                                      ; preds = %true_block313, %false_block311, %true_block310
  %.077 = phi float [ %815, %true_block310 ], [ %821, %true_block313 ], [ 0.000000e+00, %false_block311 ]
  br i1 %142, label %true_block316, label %false_block317

true_block313:                                    ; preds = %false_block311
  %817 = fmul reassoc ninf nsz float %304, %304
  %818 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg554 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %819 = fsub reassoc ninf nsz float 2.500000e+00, %818
  %reass.mul556 = fmul reassoc ninf nsz float %817, %819
  %820 = fadd reassoc ninf nsz float %.neg554, 2.000000e+00
  %821 = fadd reassoc ninf nsz float %820, %reass.mul556
  br label %after_if312

true_block316:                                    ; preds = %after_if312
  %822 = fmul reassoc ninf nsz float %140, %140
  %823 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add564 = fadd reassoc ninf nsz float %823, -2.500000e+00
  %reass.mul565 = fmul reassoc ninf nsz float %822, %reass.add564
  %824 = fadd reassoc ninf nsz float %reass.mul565, 1.000000e+00
  br label %after_if318

false_block317:                                   ; preds = %after_if312
  %825 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %825, label %true_block319, label %after_if318

after_if318:                                      ; preds = %true_block319, %false_block317, %true_block316
  %.076 = phi float [ %824, %true_block316 ], [ %839, %true_block319 ], [ 0.000000e+00, %false_block317 ]
  %826 = add i32 %771, %130
  %827 = mul i32 %826, %553
  %828 = add i32 %827, 1
  %829 = sext i32 %828 to i64
  %830 = getelementptr float, ptr %551, i64 %829
  %831 = load float, ptr %830, align 4
  %832 = fmul reassoc ninf nsz float %.076, %.077
  %833 = fmul reassoc ninf nsz float %832, %831
  %834 = fadd reassoc ninf nsz float %807, %833
  br i1 %306, label %true_block322, label %false_block323

true_block319:                                    ; preds = %false_block317
  %835 = fmul reassoc ninf nsz float %140, %140
  %836 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg560 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %837 = fsub reassoc ninf nsz float 2.500000e+00, %836
  %reass.mul562 = fmul reassoc ninf nsz float %835, %837
  %838 = fadd reassoc ninf nsz float %.neg560, 2.000000e+00
  %839 = fadd reassoc ninf nsz float %838, %reass.mul562
  br label %after_if318

true_block322:                                    ; preds = %after_if318
  %840 = fmul reassoc ninf nsz float %304, %304
  %841 = fmul reassoc ninf nsz float %305, 1.500000e+00
  %reass.add570 = fadd reassoc ninf nsz float %841, -2.500000e+00
  %reass.mul571 = fmul reassoc ninf nsz float %840, %reass.add570
  %842 = fadd reassoc ninf nsz float %reass.mul571, 1.000000e+00
  br label %after_if324

false_block323:                                   ; preds = %after_if318
  %843 = fcmp reassoc ninf nsz olt float %305, 2.000000e+00
  br i1 %843, label %true_block325, label %after_if324

after_if324:                                      ; preds = %true_block325, %false_block323, %true_block322
  %.075 = phi float [ %842, %true_block322 ], [ %848, %true_block325 ], [ 0.000000e+00, %false_block323 ]
  br i1 %174, label %true_block328, label %false_block329

true_block325:                                    ; preds = %false_block323
  %844 = fmul reassoc ninf nsz float %304, %304
  %845 = fmul reassoc ninf nsz float %305, 5.000000e-01
  %.neg566 = fmul reassoc ninf nsz float %305, -4.000000e+00
  %846 = fsub reassoc ninf nsz float 2.500000e+00, %845
  %reass.mul568 = fmul reassoc ninf nsz float %844, %846
  %847 = fadd reassoc ninf nsz float %.neg566, 2.000000e+00
  %848 = fadd reassoc ninf nsz float %847, %reass.mul568
  br label %after_if324

true_block328:                                    ; preds = %after_if324
  %849 = fmul reassoc ninf nsz float %172, %172
  %850 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add576 = fadd reassoc ninf nsz float %850, -2.500000e+00
  %reass.mul577 = fmul reassoc ninf nsz float %849, %reass.add576
  %851 = fadd reassoc ninf nsz float %reass.mul577, 1.000000e+00
  br label %after_if330

false_block329:                                   ; preds = %after_if324
  %852 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %852, label %true_block331, label %after_if330

after_if330:                                      ; preds = %true_block331, %false_block329, %true_block328
  %.074 = phi float [ %851, %true_block328 ], [ %866, %true_block331 ], [ 0.000000e+00, %false_block329 ]
  %853 = add i32 %771, %162
  %854 = mul i32 %853, %553
  %855 = add i32 %854, 1
  %856 = sext i32 %855 to i64
  %857 = getelementptr float, ptr %551, i64 %856
  %858 = load float, ptr %857, align 4
  %859 = fmul reassoc ninf nsz float %.074, %.075
  %860 = fmul reassoc ninf nsz float %859, %858
  %861 = fadd reassoc ninf nsz float %834, %860
  br i1 %417, label %true_block334, label %false_block335

true_block331:                                    ; preds = %false_block329
  %862 = fmul reassoc ninf nsz float %172, %172
  %863 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg572 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %864 = fsub reassoc ninf nsz float 2.500000e+00, %863
  %reass.mul574 = fmul reassoc ninf nsz float %862, %864
  %865 = fadd reassoc ninf nsz float %.neg572, 2.000000e+00
  %866 = fadd reassoc ninf nsz float %865, %reass.mul574
  br label %after_if330

true_block334:                                    ; preds = %after_if330
  %867 = fmul reassoc ninf nsz float %415, %415
  %868 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add582 = fadd reassoc ninf nsz float %868, -2.500000e+00
  %reass.mul583 = fmul reassoc ninf nsz float %867, %reass.add582
  %869 = fadd reassoc ninf nsz float %reass.mul583, 1.000000e+00
  br label %after_if336

false_block335:                                   ; preds = %after_if330
  %870 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %870, label %true_block337, label %after_if336

after_if336:                                      ; preds = %true_block337, %false_block335, %true_block334
  %.073 = phi float [ %869, %true_block334 ], [ %875, %true_block337 ], [ 0.000000e+00, %false_block335 ]
  br i1 %77, label %true_block340, label %false_block341

true_block337:                                    ; preds = %false_block335
  %871 = fmul reassoc ninf nsz float %415, %415
  %872 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg578 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %873 = fsub reassoc ninf nsz float 2.500000e+00, %872
  %reass.mul580 = fmul reassoc ninf nsz float %871, %873
  %874 = fadd reassoc ninf nsz float %.neg578, 2.000000e+00
  %875 = fadd reassoc ninf nsz float %874, %reass.mul580
  br label %after_if336

true_block340:                                    ; preds = %after_if336
  %876 = fmul reassoc ninf nsz float %75, %75
  %877 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add588 = fadd reassoc ninf nsz float %877, -2.500000e+00
  %reass.mul589 = fmul reassoc ninf nsz float %876, %reass.add588
  %878 = fadd reassoc ninf nsz float %reass.mul589, 1.000000e+00
  br label %after_if342

false_block341:                                   ; preds = %after_if336
  %879 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %879, label %true_block343, label %after_if342

after_if342:                                      ; preds = %true_block343, %false_block341, %true_block340
  %.072 = phi float [ %878, %true_block340 ], [ %894, %true_block343 ], [ 0.000000e+00, %false_block341 ]
  %880 = mul i32 %552, %414
  %881 = add i32 %880, %67
  %882 = mul i32 %881, %553
  %883 = add i32 %882, 1
  %884 = sext i32 %883 to i64
  %885 = getelementptr float, ptr %551, i64 %884
  %886 = load float, ptr %885, align 4
  %887 = fmul reassoc ninf nsz float %.072, %.073
  %888 = fmul reassoc ninf nsz float %887, %886
  %889 = fadd reassoc ninf nsz float %861, %888
  br i1 %417, label %true_block346, label %false_block347

true_block343:                                    ; preds = %false_block341
  %890 = fmul reassoc ninf nsz float %75, %75
  %891 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg584 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %892 = fsub reassoc ninf nsz float 2.500000e+00, %891
  %reass.mul586 = fmul reassoc ninf nsz float %890, %892
  %893 = fadd reassoc ninf nsz float %.neg584, 2.000000e+00
  %894 = fadd reassoc ninf nsz float %893, %reass.mul586
  br label %after_if342

true_block346:                                    ; preds = %after_if342
  %895 = fmul reassoc ninf nsz float %415, %415
  %896 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add594 = fadd reassoc ninf nsz float %896, -2.500000e+00
  %reass.mul595 = fmul reassoc ninf nsz float %895, %reass.add594
  %897 = fadd reassoc ninf nsz float %reass.mul595, 1.000000e+00
  br label %after_if348

false_block347:                                   ; preds = %after_if342
  %898 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %898, label %true_block349, label %after_if348

after_if348:                                      ; preds = %true_block349, %false_block347, %true_block346
  %.071 = phi float [ %897, %true_block346 ], [ %903, %true_block349 ], [ 0.000000e+00, %false_block347 ]
  br i1 %110, label %true_block352, label %false_block353

true_block349:                                    ; preds = %false_block347
  %899 = fmul reassoc ninf nsz float %415, %415
  %900 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg590 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %901 = fsub reassoc ninf nsz float 2.500000e+00, %900
  %reass.mul592 = fmul reassoc ninf nsz float %899, %901
  %902 = fadd reassoc ninf nsz float %.neg590, 2.000000e+00
  %903 = fadd reassoc ninf nsz float %902, %reass.mul592
  br label %after_if348

true_block352:                                    ; preds = %after_if348
  %904 = fmul reassoc ninf nsz float %55, %55
  %905 = fmul reassoc ninf nsz float %109, 1.500000e+00
  %reass.add600 = fadd reassoc ninf nsz float %905, -2.500000e+00
  %reass.mul601 = fmul reassoc ninf nsz float %904, %reass.add600
  %906 = fadd reassoc ninf nsz float %reass.mul601, 1.000000e+00
  br label %after_if354

false_block353:                                   ; preds = %after_if348
  %907 = fcmp reassoc ninf nsz olt float %109, 2.000000e+00
  br i1 %907, label %true_block355, label %after_if354

after_if354:                                      ; preds = %true_block355, %false_block353, %true_block352
  %.070 = phi float [ %906, %true_block352 ], [ %921, %true_block355 ], [ 0.000000e+00, %false_block353 ]
  %908 = add i32 %880, %99
  %909 = mul i32 %908, %553
  %910 = add i32 %909, 1
  %911 = sext i32 %910 to i64
  %912 = getelementptr float, ptr %551, i64 %911
  %913 = load float, ptr %912, align 4
  %914 = fmul reassoc ninf nsz float %.070, %.071
  %915 = fmul reassoc ninf nsz float %914, %913
  %916 = fadd reassoc ninf nsz float %889, %915
  br i1 %417, label %true_block358, label %false_block359

true_block355:                                    ; preds = %false_block353
  %917 = fmul reassoc ninf nsz float %55, %55
  %918 = fmul reassoc ninf nsz float %109, 5.000000e-01
  %.neg596 = fmul reassoc ninf nsz float %109, -4.000000e+00
  %919 = fsub reassoc ninf nsz float 2.500000e+00, %918
  %reass.mul598 = fmul reassoc ninf nsz float %917, %919
  %920 = fadd reassoc ninf nsz float %.neg596, 2.000000e+00
  %921 = fadd reassoc ninf nsz float %920, %reass.mul598
  br label %after_if354

true_block358:                                    ; preds = %after_if354
  %922 = fmul reassoc ninf nsz float %415, %415
  %923 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add606 = fadd reassoc ninf nsz float %923, -2.500000e+00
  %reass.mul607 = fmul reassoc ninf nsz float %922, %reass.add606
  %924 = fadd reassoc ninf nsz float %reass.mul607, 1.000000e+00
  br label %after_if360

false_block359:                                   ; preds = %after_if354
  %925 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %925, label %true_block361, label %after_if360

after_if360:                                      ; preds = %true_block361, %false_block359, %true_block358
  %.069 = phi float [ %924, %true_block358 ], [ %930, %true_block361 ], [ 0.000000e+00, %false_block359 ]
  br i1 %142, label %true_block364, label %false_block365

true_block361:                                    ; preds = %false_block359
  %926 = fmul reassoc ninf nsz float %415, %415
  %927 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg602 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %928 = fsub reassoc ninf nsz float 2.500000e+00, %927
  %reass.mul604 = fmul reassoc ninf nsz float %926, %928
  %929 = fadd reassoc ninf nsz float %.neg602, 2.000000e+00
  %930 = fadd reassoc ninf nsz float %929, %reass.mul604
  br label %after_if360

true_block364:                                    ; preds = %after_if360
  %931 = fmul reassoc ninf nsz float %140, %140
  %932 = fmul reassoc ninf nsz float %141, 1.500000e+00
  %reass.add612 = fadd reassoc ninf nsz float %932, -2.500000e+00
  %reass.mul613 = fmul reassoc ninf nsz float %931, %reass.add612
  %933 = fadd reassoc ninf nsz float %reass.mul613, 1.000000e+00
  br label %after_if366

false_block365:                                   ; preds = %after_if360
  %934 = fcmp reassoc ninf nsz olt float %141, 2.000000e+00
  br i1 %934, label %true_block367, label %after_if366

after_if366:                                      ; preds = %true_block367, %false_block365, %true_block364
  %.068 = phi float [ %933, %true_block364 ], [ %948, %true_block367 ], [ 0.000000e+00, %false_block365 ]
  %935 = add i32 %880, %130
  %936 = mul i32 %935, %553
  %937 = add i32 %936, 1
  %938 = sext i32 %937 to i64
  %939 = getelementptr float, ptr %551, i64 %938
  %940 = load float, ptr %939, align 4
  %941 = fmul reassoc ninf nsz float %.068, %.069
  %942 = fmul reassoc ninf nsz float %941, %940
  %943 = fadd reassoc ninf nsz float %916, %942
  br i1 %417, label %true_block370, label %false_block371

true_block367:                                    ; preds = %false_block365
  %944 = fmul reassoc ninf nsz float %140, %140
  %945 = fmul reassoc ninf nsz float %141, 5.000000e-01
  %.neg608 = fmul reassoc ninf nsz float %141, -4.000000e+00
  %946 = fsub reassoc ninf nsz float 2.500000e+00, %945
  %reass.mul610 = fmul reassoc ninf nsz float %944, %946
  %947 = fadd reassoc ninf nsz float %.neg608, 2.000000e+00
  %948 = fadd reassoc ninf nsz float %947, %reass.mul610
  br label %after_if366

true_block370:                                    ; preds = %after_if366
  %949 = fmul reassoc ninf nsz float %415, %415
  %950 = fmul reassoc ninf nsz float %416, 1.500000e+00
  %reass.add618 = fadd reassoc ninf nsz float %950, -2.500000e+00
  %reass.mul619 = fmul reassoc ninf nsz float %949, %reass.add618
  %951 = fadd reassoc ninf nsz float %reass.mul619, 1.000000e+00
  br label %after_if372

false_block371:                                   ; preds = %after_if366
  %952 = fcmp reassoc ninf nsz olt float %416, 2.000000e+00
  br i1 %952, label %true_block373, label %after_if372

after_if372:                                      ; preds = %true_block373, %false_block371, %true_block370
  %.067 = phi float [ %951, %true_block370 ], [ %957, %true_block373 ], [ 0.000000e+00, %false_block371 ]
  br i1 %174, label %true_block376, label %false_block377

true_block373:                                    ; preds = %false_block371
  %953 = fmul reassoc ninf nsz float %415, %415
  %954 = fmul reassoc ninf nsz float %416, 5.000000e-01
  %.neg614 = fmul reassoc ninf nsz float %416, -4.000000e+00
  %955 = fsub reassoc ninf nsz float 2.500000e+00, %954
  %reass.mul616 = fmul reassoc ninf nsz float %953, %955
  %956 = fadd reassoc ninf nsz float %.neg614, 2.000000e+00
  %957 = fadd reassoc ninf nsz float %956, %reass.mul616
  br label %after_if372

true_block376:                                    ; preds = %after_if372
  %958 = fmul reassoc ninf nsz float %172, %172
  %959 = fmul reassoc ninf nsz float %173, 1.500000e+00
  %reass.add624 = fadd reassoc ninf nsz float %959, -2.500000e+00
  %reass.mul625 = fmul reassoc ninf nsz float %958, %reass.add624
  %960 = fadd reassoc ninf nsz float %reass.mul625, 1.000000e+00
  br label %after_if378

false_block377:                                   ; preds = %after_if372
  %961 = fcmp reassoc ninf nsz olt float %173, 2.000000e+00
  br i1 %961, label %true_block379, label %after_if378

after_if378:                                      ; preds = %true_block379, %false_block377, %true_block376
  %.0 = phi float [ %960, %true_block376 ], [ %987, %true_block379 ], [ 0.000000e+00, %false_block377 ]
  %962 = add i32 %880, %162
  %963 = mul i32 %962, %553
  %964 = add i32 %963, 1
  %965 = sext i32 %964 to i64
  %966 = getelementptr float, ptr %551, i64 %965
  %967 = load float, ptr %966, align 4
  %968 = fmul reassoc ninf nsz float %.0, %.067
  %969 = fmul reassoc ninf nsz float %968, %967
  %970 = fadd reassoc ninf nsz float %943, %969
  %971 = fmul reassoc ninf nsz float %970, %21
  %972 = load ptr, ptr %26, align 8
  %973 = load i32, ptr %27, align 4
  %974 = load i32, ptr %28, align 4
  %975 = sub i32 %973, %33
  %976 = mul i32 %975, %40
  %977 = add i32 %.0130626, %976
  %978 = mul i32 %977, %974
  %979 = add i32 %978, 1
  %980 = sext i32 %979 to i64
  %981 = getelementptr float, ptr %972, i64 %980
  store float %971, ptr %981, align 4
  %982 = add nsw i32 %.0130626, 1
  %exitcond.not = icmp eq i32 %18, %982
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block379:                                    ; preds = %false_block377
  %983 = fmul reassoc ninf nsz float %172, %172
  %984 = fmul reassoc ninf nsz float %173, 5.000000e-01
  %.neg620 = fmul reassoc ninf nsz float %173, -4.000000e+00
  %985 = fsub reassoc ninf nsz float 2.500000e+00, %984
  %reass.mul622 = fmul reassoc ninf nsz float %983, %985
  %986 = fadd reassoc ninf nsz float %.neg620, 2.000000e+00
  %987 = fadd reassoc ninf nsz float %986, %reass.mul622
  br label %after_if378
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #2

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
