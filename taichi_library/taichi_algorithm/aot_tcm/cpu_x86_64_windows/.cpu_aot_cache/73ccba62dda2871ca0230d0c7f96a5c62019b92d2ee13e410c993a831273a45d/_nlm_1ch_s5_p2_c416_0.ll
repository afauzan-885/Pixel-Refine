; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_1ch_s5_p2_c416_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load float, ptr %1, align 4
  %3 = fmul reassoc ninf nsz float %2, %2
  %4 = fdiv reassoc ninf nsz float 1.000000e+00, %3
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 20
  store float %4, ptr %9, align 4
  %10 = fmul reassoc ninf nsz float %3, 3.500000e+00
  %11 = fadd reassoc ninf nsz float %10, 0x3F60624DE0000000
  %12 = load ptr, ptr %5, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 16
  store float %11, ptr %15, align 4
  %16 = fmul reassoc ninf nsz float %2, 0x3FE6666660000000
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 48
  %19 = load float, ptr %18, align 4
  %20 = fmul reassoc ninf nsz float %16, %19
  %21 = load ptr, ptr %5, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 24
  store float %20, ptr %24, align 4
  %25 = load ptr, ptr %context, align 8
  %26 = getelementptr i8, ptr %25, i64 32
  %27 = load i32, ptr %26, align 4
  %28 = load ptr, ptr %5, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 8
  store i32 %27, ptr %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %27, i32 0)
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 36
  %35 = load i32, ptr %34, align 4
  %36 = load ptr, ptr %5, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 12
  store i32 %35, ptr %39, align 4
  %40 = tail call i32 @llvm.smax.i32(i32 %35, i32 0)
  %41 = load ptr, ptr %5, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 4
  store i32 %40, ptr %44, align 4
  %45 = mul i32 %40, %32
  %46 = load ptr, ptr %5, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  store i32 %45, ptr %48, align 4
  ret void
}

define void @_nlm_1ch_s5_p2_c416_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 44
  %21 = load float, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 8
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = add i32 %16, -5
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %25, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.05782 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %538, %after_if47 ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.05782, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.05782
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %32, %.05782
  %36 = and i1 %34, %35
  %.neg63 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg63
  %38 = mul i32 %37, %30
  %39 = sub i32 %.05782, %38
  %40 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %41 = load i32, ptr %40, align 4
  %42 = add i32 %41, -1
  %43 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %44 = load i32, ptr %43, align 4
  %45 = add i32 %44, -1
  %46 = load ptr, ptr %23, align 8
  %47 = load i32, ptr %24, align 4
  %48 = add i32 %39, -1
  %49 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %50 = tail call i32 @llvm.smin.i32(i32 %45, i32 %49)
  %51 = add i32 %37, -1
  %52 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %53 = tail call i32 @llvm.smin.i32(i32 %42, i32 %52)
  %54 = mul i32 %47, %53
  %55 = add i32 %54, %50
  %56 = sext i32 %55 to i64
  %57 = getelementptr float, ptr %46, i64 %56
  %58 = load float, ptr %57, align 4
  %59 = fmul reassoc ninf nsz float %58, %58
  %60 = tail call i32 @llvm.smax.i32(i32 %39, i32 0)
  %61 = tail call i32 @llvm.smin.i32(i32 %45, i32 %60)
  %62 = add i32 %54, %61
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, ptr %46, i64 %63
  %65 = load float, ptr %64, align 4
  %66 = fadd reassoc ninf nsz float %65, %58
  %67 = fmul reassoc ninf nsz float %65, %65
  %68 = fadd reassoc ninf nsz float %67, %59
  %69 = add i32 %39, 1
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = tail call i32 @llvm.smin.i32(i32 %45, i32 %70)
  %72 = add i32 %54, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %46, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = fadd reassoc ninf nsz float %75, %66
  %77 = fmul reassoc ninf nsz float %75, %75
  %78 = fadd reassoc ninf nsz float %77, %68
  %79 = tail call i32 @llvm.smax.i32(i32 %37, i32 0)
  %80 = tail call i32 @llvm.smin.i32(i32 %42, i32 %79)
  %81 = mul i32 %47, %80
  %82 = add i32 %81, %50
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %46, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fadd reassoc ninf nsz float %85, %76
  %87 = fmul reassoc ninf nsz float %85, %85
  %88 = fadd reassoc ninf nsz float %87, %78
  %89 = add i32 %81, %61
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %46, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = fadd reassoc ninf nsz float %92, %86
  %94 = fmul reassoc ninf nsz float %92, %92
  %95 = fadd reassoc ninf nsz float %94, %88
  %96 = add i32 %81, %71
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %46, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = fadd reassoc ninf nsz float %99, %93
  %101 = fmul reassoc ninf nsz float %99, %99
  %102 = fadd reassoc ninf nsz float %101, %95
  %103 = add i32 %37, 1
  %104 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %42, i32 %104)
  %106 = mul i32 %47, %105
  %107 = add i32 %106, %50
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %46, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = fadd reassoc ninf nsz float %110, %100
  %112 = fmul reassoc ninf nsz float %110, %110
  %113 = fadd reassoc ninf nsz float %112, %102
  %114 = add i32 %106, %61
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %46, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = fadd reassoc ninf nsz float %117, %111
  %119 = fmul reassoc ninf nsz float %117, %117
  %120 = fadd reassoc ninf nsz float %119, %113
  %121 = add i32 %106, %71
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %46, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fadd reassoc ninf nsz float %124, %118
  %126 = fmul reassoc ninf nsz float %124, %124
  %127 = fadd reassoc ninf nsz float %126, %120
  %128 = fmul reassoc ninf nsz float %125, 0x3FBC71C720000000
  %129 = fmul reassoc ninf nsz float %127, 0x3FBC71C720000000
  %130 = fmul reassoc ninf nsz float %128, %128
  %131 = fsub reassoc ninf nsz float %129, %130
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float 0.000000e+00)
  %133 = fmul reassoc ninf nsz float %132, -3.500000e+02
  %134 = tail call noundef float @expf(float noundef %133) #8
  %135 = fsub reassoc ninf nsz float 1.000000e+00, %134
  %136 = add i32 %39, -2
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %45, i32 %137)
  %139 = add i32 %37, -2
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = tail call i32 @llvm.smin.i32(i32 %42, i32 %140)
  %142 = add i32 %39, 2
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %45, i32 %143)
  %145 = add i32 %37, 2
  %146 = tail call i32 @llvm.smax.i32(i32 %145, i32 0)
  %147 = tail call i32 @llvm.smin.i32(i32 %42, i32 %146)
  %148 = sub i32 %lsr.iv, %38
  %149 = add i32 %31, -5
  %150 = add i32 %149, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv100 = phi i32 [ %150, %for_loop_body ], [ %lsr.iv.next101, %for_loop_inc10 ]
  %.04381 = phi i32 [ -5, %for_loop_body ], [ %153, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %151 = add i32 %.04381, %37
  %152 = icmp slt i32 %151, 0
  br i1 %152, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %153 = add nsw i32 %.04381, 1
  %lsr.iv.next101 = add i32 %lsr.iv100, 1
  %exitcond85.not = icmp eq i32 %153, 6
  br i1 %exitcond85.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %154 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %154, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %155 = load i32, ptr %40, align 4
  %.not64 = icmp slt i32 %151, %155
  br i1 %.not64, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %156 = tail call i32 @llvm.smax.i32(i32 %151, i32 2)
  %157 = add nsw i32 %156, -2
  %158 = tail call i32 @llvm.smin.i32(i32 %42, i32 %157)
  %159 = tail call i32 @llvm.smax.i32(i32 %151, i32 1)
  %160 = add nsw i32 %159, -1
  %161 = tail call i32 @llvm.smin.i32(i32 %42, i32 %160)
  %162 = tail call i32 @llvm.smin.i32(i32 %42, i32 %151)
  %163 = add nuw i32 %151, 1
  %164 = tail call i32 @llvm.smax.i32(i32 %163, i32 0)
  %165 = tail call i32 @llvm.smin.i32(i32 %42, i32 %164)
  %166 = add nuw i32 %151, 2
  %167 = tail call i32 @llvm.smax.i32(i32 %166, i32 0)
  %168 = tail call i32 @llvm.smin.i32(i32 %42, i32 %167)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv97 = phi i32 [ %148, %for_loop_body16.preheader ], [ %lsr.iv.next98, %for_loop_inc17 ]
  %.04178 = phi i32 [ %173, %for_loop_inc17 ], [ -5, %for_loop_body16.preheader ]
  %.377 = phi float [ %.246, %for_loop_inc17 ], [ %.14580, %for_loop_body16.preheader ]
  %.35076 = phi float [ %.249, %for_loop_inc17 ], [ %.14879, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv97, i32 1)
  %169 = sub i32 %148, %umin
  %umin99 = call i32 @llvm.umin.i32(i32 %lsr.iv97, i32 2)
  %170 = sub i32 %148, %umin99
  %171 = add i32 %39, %.04178
  %172 = icmp slt i32 %171, 0
  br i1 %172, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %485, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %494, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %173 = add nsw i32 %.04178, 1
  %lsr.iv.next98 = add i32 %lsr.iv97, 1
  %exitcond.not = icmp eq i32 %173, 6
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %174 = load i32, ptr %43, align 4
  %.not65 = icmp slt i32 %171, %174
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %175 = or i32 %.04178, %.04381
  %spec.select.not = icmp eq i32 %175, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %176 = load ptr, ptr %23, align 8
  %177 = load i32, ptr %24, align 4
  %178 = add i32 %.04178, %170
  %179 = add i32 %178, 5
  %180 = tail call i32 @llvm.smin.i32(i32 %45, i32 %179)
  %181 = mul i32 %177, %141
  %182 = mul i32 %177, %158
  %183 = add i32 %181, %138
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %176, i64 %184
  %186 = load float, ptr %185, align 4
  %187 = add i32 %182, %180
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, ptr %176, i64 %188
  %190 = load float, ptr %189, align 4
  %191 = fsub reassoc ninf nsz float %186, %190
  %192 = fmul reassoc ninf nsz float %191, %191
  %193 = add i32 %.04178, %169
  %194 = add i32 %193, 5
  %195 = tail call i32 @llvm.smin.i32(i32 %45, i32 %194)
  %196 = add i32 %181, %50
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %176, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = add i32 %182, %195
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %176, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = fsub reassoc ninf nsz float %199, %203
  %205 = fmul reassoc ninf nsz float %204, %204
  %206 = fadd reassoc ninf nsz float %205, %192
  %207 = tail call i32 @llvm.smin.i32(i32 %45, i32 %171)
  %208 = add i32 %181, %61
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, ptr %176, i64 %209
  %211 = load float, ptr %210, align 4
  %212 = add i32 %182, %207
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, ptr %176, i64 %213
  %215 = load float, ptr %214, align 4
  %216 = fsub reassoc ninf nsz float %211, %215
  %217 = fmul reassoc ninf nsz float %216, %216
  %218 = fadd reassoc ninf nsz float %217, %206
  %219 = add i32 %171, 1
  %220 = tail call i32 @llvm.smin.i32(i32 %45, i32 %219)
  %221 = add i32 %181, %71
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %176, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = add i32 %182, %220
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %176, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = fsub reassoc ninf nsz float %224, %228
  %230 = fmul reassoc ninf nsz float %229, %229
  %231 = fadd reassoc ninf nsz float %230, %218
  %232 = add i32 %171, 2
  %233 = tail call i32 @llvm.smax.i32(i32 %232, i32 0)
  %234 = tail call i32 @llvm.smin.i32(i32 %45, i32 %233)
  %235 = add i32 %181, %144
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %176, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = add i32 %182, %234
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, ptr %176, i64 %240
  %242 = load float, ptr %241, align 4
  %243 = fsub reassoc ninf nsz float %238, %242
  %244 = fmul reassoc ninf nsz float %243, %243
  %245 = fadd reassoc ninf nsz float %244, %231
  %246 = mul i32 %177, %53
  %247 = mul i32 %177, %161
  %248 = add i32 %246, %138
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, ptr %176, i64 %249
  %251 = load float, ptr %250, align 4
  %252 = add i32 %247, %180
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, ptr %176, i64 %253
  %255 = load float, ptr %254, align 4
  %256 = fsub reassoc ninf nsz float %251, %255
  %257 = fmul reassoc ninf nsz float %256, %256
  %258 = fadd reassoc ninf nsz float %257, %245
  %259 = add i32 %246, %50
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, ptr %176, i64 %260
  %262 = load float, ptr %261, align 4
  %263 = add i32 %247, %195
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %176, i64 %264
  %266 = load float, ptr %265, align 4
  %267 = fsub reassoc ninf nsz float %262, %266
  %268 = fmul reassoc ninf nsz float %267, %267
  %269 = fadd reassoc ninf nsz float %268, %258
  %270 = add i32 %246, %61
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %176, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = add i32 %247, %207
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, ptr %176, i64 %275
  %277 = load float, ptr %276, align 4
  %278 = fsub reassoc ninf nsz float %273, %277
  %279 = fmul reassoc ninf nsz float %278, %278
  %280 = fadd reassoc ninf nsz float %279, %269
  %281 = add i32 %246, %71
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, ptr %176, i64 %282
  %284 = load float, ptr %283, align 4
  %285 = add i32 %247, %220
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, ptr %176, i64 %286
  %288 = load float, ptr %287, align 4
  %289 = fsub reassoc ninf nsz float %284, %288
  %290 = fmul reassoc ninf nsz float %289, %289
  %291 = fadd reassoc ninf nsz float %290, %280
  %292 = add i32 %246, %144
  %293 = sext i32 %292 to i64
  %294 = getelementptr float, ptr %176, i64 %293
  %295 = load float, ptr %294, align 4
  %296 = add i32 %247, %234
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %176, i64 %297
  %299 = load float, ptr %298, align 4
  %300 = fsub reassoc ninf nsz float %295, %299
  %301 = fmul reassoc ninf nsz float %300, %300
  %302 = fadd reassoc ninf nsz float %301, %291
  %303 = mul i32 %177, %80
  %304 = mul i32 %177, %162
  %305 = add i32 %303, %138
  %306 = sext i32 %305 to i64
  %307 = getelementptr float, ptr %176, i64 %306
  %308 = load float, ptr %307, align 4
  %309 = add i32 %304, %180
  %310 = sext i32 %309 to i64
  %311 = getelementptr float, ptr %176, i64 %310
  %312 = load float, ptr %311, align 4
  %313 = fsub reassoc ninf nsz float %308, %312
  %314 = fmul reassoc ninf nsz float %313, %313
  %315 = fadd reassoc ninf nsz float %314, %302
  %316 = add i32 %303, %50
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %176, i64 %317
  %319 = load float, ptr %318, align 4
  %320 = add i32 %304, %195
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %176, i64 %321
  %323 = load float, ptr %322, align 4
  %324 = fsub reassoc ninf nsz float %319, %323
  %325 = fmul reassoc ninf nsz float %324, %324
  %326 = fadd reassoc ninf nsz float %325, %315
  %327 = add i32 %303, %61
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %176, i64 %328
  %330 = load float, ptr %329, align 4
  %331 = add i32 %304, %207
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %176, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = fsub reassoc ninf nsz float %330, %334
  %336 = fmul reassoc ninf nsz float %335, %335
  %337 = fadd reassoc ninf nsz float %336, %326
  %338 = add i32 %303, %71
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, ptr %176, i64 %339
  %341 = load float, ptr %340, align 4
  %342 = add i32 %304, %220
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %176, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = fsub reassoc ninf nsz float %341, %345
  %347 = fmul reassoc ninf nsz float %346, %346
  %348 = fadd reassoc ninf nsz float %347, %337
  %349 = add i32 %303, %144
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, ptr %176, i64 %350
  %352 = load float, ptr %351, align 4
  %353 = add i32 %304, %234
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, ptr %176, i64 %354
  %356 = load float, ptr %355, align 4
  %357 = fsub reassoc ninf nsz float %352, %356
  %358 = fmul reassoc ninf nsz float %357, %357
  %359 = fadd reassoc ninf nsz float %358, %348
  %360 = mul i32 %177, %105
  %361 = mul i32 %177, %165
  %362 = add i32 %360, %138
  %363 = sext i32 %362 to i64
  %364 = getelementptr float, ptr %176, i64 %363
  %365 = load float, ptr %364, align 4
  %366 = add i32 %361, %180
  %367 = sext i32 %366 to i64
  %368 = getelementptr float, ptr %176, i64 %367
  %369 = load float, ptr %368, align 4
  %370 = fsub reassoc ninf nsz float %365, %369
  %371 = fmul reassoc ninf nsz float %370, %370
  %372 = fadd reassoc ninf nsz float %371, %359
  %373 = add i32 %360, %50
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %176, i64 %374
  %376 = load float, ptr %375, align 4
  %377 = add i32 %361, %195
  %378 = sext i32 %377 to i64
  %379 = getelementptr float, ptr %176, i64 %378
  %380 = load float, ptr %379, align 4
  %381 = fsub reassoc ninf nsz float %376, %380
  %382 = fmul reassoc ninf nsz float %381, %381
  %383 = fadd reassoc ninf nsz float %382, %372
  %384 = add i32 %360, %61
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, ptr %176, i64 %385
  %387 = load float, ptr %386, align 4
  %388 = add i32 %361, %207
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %176, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = fsub reassoc ninf nsz float %387, %391
  %393 = fmul reassoc ninf nsz float %392, %392
  %394 = fadd reassoc ninf nsz float %393, %383
  %395 = add i32 %360, %71
  %396 = sext i32 %395 to i64
  %397 = getelementptr float, ptr %176, i64 %396
  %398 = load float, ptr %397, align 4
  %399 = add i32 %361, %220
  %400 = sext i32 %399 to i64
  %401 = getelementptr float, ptr %176, i64 %400
  %402 = load float, ptr %401, align 4
  %403 = fsub reassoc ninf nsz float %398, %402
  %404 = fmul reassoc ninf nsz float %403, %403
  %405 = fadd reassoc ninf nsz float %404, %394
  %406 = add i32 %360, %144
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %176, i64 %407
  %409 = load float, ptr %408, align 4
  %410 = add i32 %361, %234
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, ptr %176, i64 %411
  %413 = load float, ptr %412, align 4
  %414 = fsub reassoc ninf nsz float %409, %413
  %415 = fmul reassoc ninf nsz float %414, %414
  %416 = fadd reassoc ninf nsz float %415, %405
  %417 = mul i32 %177, %147
  %418 = mul i32 %177, %168
  %419 = add i32 %417, %138
  %420 = sext i32 %419 to i64
  %421 = getelementptr float, ptr %176, i64 %420
  %422 = load float, ptr %421, align 4
  %423 = add i32 %418, %180
  %424 = sext i32 %423 to i64
  %425 = getelementptr float, ptr %176, i64 %424
  %426 = load float, ptr %425, align 4
  %427 = fsub reassoc ninf nsz float %422, %426
  %428 = fmul reassoc ninf nsz float %427, %427
  %429 = fadd reassoc ninf nsz float %428, %416
  %430 = add i32 %417, %50
  %431 = sext i32 %430 to i64
  %432 = getelementptr float, ptr %176, i64 %431
  %433 = load float, ptr %432, align 4
  %434 = add i32 %418, %195
  %435 = sext i32 %434 to i64
  %436 = getelementptr float, ptr %176, i64 %435
  %437 = load float, ptr %436, align 4
  %438 = fsub reassoc ninf nsz float %433, %437
  %439 = fmul reassoc ninf nsz float %438, %438
  %440 = fadd reassoc ninf nsz float %439, %429
  %441 = add i32 %417, %61
  %442 = sext i32 %441 to i64
  %443 = getelementptr float, ptr %176, i64 %442
  %444 = load float, ptr %443, align 4
  %445 = add i32 %418, %207
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, ptr %176, i64 %446
  %448 = load float, ptr %447, align 4
  %449 = fsub reassoc ninf nsz float %444, %448
  %450 = fmul reassoc ninf nsz float %449, %449
  %451 = fadd reassoc ninf nsz float %450, %440
  %452 = add i32 %417, %71
  %453 = sext i32 %452 to i64
  %454 = getelementptr float, ptr %176, i64 %453
  %455 = load float, ptr %454, align 4
  %456 = add i32 %418, %220
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, ptr %176, i64 %457
  %459 = load float, ptr %458, align 4
  %460 = fsub reassoc ninf nsz float %455, %459
  %461 = fmul reassoc ninf nsz float %460, %460
  %462 = fadd reassoc ninf nsz float %461, %451
  %463 = add i32 %417, %144
  %464 = sext i32 %463 to i64
  %465 = getelementptr float, ptr %176, i64 %464
  %466 = load float, ptr %465, align 4
  %467 = add i32 %418, %234
  %468 = sext i32 %467 to i64
  %469 = getelementptr float, ptr %176, i64 %468
  %470 = load float, ptr %469, align 4
  %471 = fsub reassoc ninf nsz float %466, %470
  %472 = fmul reassoc ninf nsz float %471, %471
  %473 = fadd reassoc ninf nsz float %472, %462
  %474 = fmul reassoc ninf nsz float %473, 0x3FA47AE140000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %474, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %475 = load ptr, ptr %3, align 8
  %476 = getelementptr inbounds nuw i8, ptr %475, i64 32872
  %477 = load ptr, ptr %476, align 8
  %478 = getelementptr inbounds nuw i8, ptr %477, i64 16
  %479 = load float, ptr %478, align 4
  %480 = fcmp reassoc ninf nsz ugt float %.039, %479
  br i1 %480, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %481 = getelementptr inbounds nuw i8, ptr %477, i64 20
  %482 = load float, ptr %481, align 4
  %483 = fmul reassoc ninf nsz float %482, %neg44
  %484 = tail call noundef float @expf(float noundef %483) #8
  %485 = fadd reassoc ninf nsz float %484, %.35076
  %486 = load ptr, ptr %23, align 8
  %487 = load i32, ptr %24, align 4
  %488 = mul i32 %lsr.iv100, %487
  %489 = add i32 %171, %488
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, ptr %486, i64 %490
  %492 = load float, ptr %491, align 4
  %493 = fmul reassoc ninf nsz float %492, %484
  %494 = fadd reassoc ninf nsz float %493, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %495 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %135, float 0x3FE6666660000000)
  %496 = fdiv reassoc ninf nsz float %.044, %.047
  %497 = load ptr, ptr %23, align 8
  %498 = load i32, ptr %24, align 4
  %499 = mul i32 %498, %37
  %500 = add i32 %499, %39
  %501 = sext i32 %500 to i64
  %502 = getelementptr float, ptr %497, i64 %501
  %503 = load float, ptr %502, align 4
  %504 = fsub reassoc ninf nsz float %503, %496
  %505 = tail call noundef float @llvm.fabs.f32(float %504)
  %506 = load ptr, ptr %3, align 8
  %507 = getelementptr inbounds nuw i8, ptr %506, i64 32872
  %508 = load ptr, ptr %507, align 8
  %509 = getelementptr inbounds nuw i8, ptr %508, i64 24
  %510 = load float, ptr %509, align 4
  %511 = fsub reassoc ninf nsz float %505, %510
  %512 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %511, float 0.000000e+00)
  %513 = fcmp reassoc ninf nsz oge float %504, 0.000000e+00
  %514 = uitofp i1 %513 to float
  %515 = fcmp reassoc ninf nsz ole float %504, 0.000000e+00
  %516 = uitofp i1 %515 to float
  %517 = fsub reassoc ninf nsz float %514, %516
  %518 = fmul reassoc ninf nsz float %495, %21
  %519 = fmul reassoc ninf nsz float %518, %517
  %520 = fmul reassoc ninf nsz float %519, %512
  %521 = fadd reassoc ninf nsz float %520, %496
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %522 = load ptr, ptr %23, align 8
  %523 = load i32, ptr %24, align 4
  %524 = mul i32 %523, %37
  %525 = add i32 %524, %39
  %526 = sext i32 %525 to i64
  %527 = getelementptr float, ptr %522, i64 %526
  %528 = load float, ptr %527, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %528, %false_block46 ], [ %521, %true_block45 ]
  %529 = load ptr, ptr %0, align 8
  %530 = getelementptr i8, ptr %529, i64 24
  %531 = load ptr, ptr %530, align 8
  %532 = getelementptr i8, ptr %529, i64 20
  %533 = load i32, ptr %532, align 4
  %534 = mul i32 %533, %37
  %535 = add i32 %534, %39
  %536 = sext i32 %535 to i64
  %537 = getelementptr float, ptr %531, i64 %536
  store float %.sink, ptr %537, align 4
  %538 = add nsw i32 %.05782, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond86.not = icmp eq i32 %538, %18
  br i1 %exitcond86.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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
declare i32 @llvm.usub.sat.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #6

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
