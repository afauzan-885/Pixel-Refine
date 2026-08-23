; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_1ch_s3_p1_c414_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_nlm_1ch_s3_p1_c414_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %25 = add i32 %16, -3
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %25, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.05782 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %333, %after_if47 ]
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
  %136 = sub i32 %lsr.iv, %38
  %137 = add i32 %31, -3
  %138 = add i32 %137, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv99 = phi i32 [ %138, %for_loop_body ], [ %lsr.iv.next100, %for_loop_inc10 ]
  %.04381 = phi i32 [ -3, %for_loop_body ], [ %141, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %139 = add i32 %.04381, %37
  %140 = icmp slt i32 %139, 0
  br i1 %140, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %141 = add nsw i32 %.04381, 1
  %lsr.iv.next100 = add i32 %lsr.iv99, 1
  %exitcond85.not = icmp eq i32 %141, 4
  br i1 %exitcond85.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %142 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %142, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %143 = load i32, ptr %40, align 4
  %.not64 = icmp slt i32 %139, %143
  br i1 %.not64, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %144 = tail call i32 @llvm.smax.i32(i32 %139, i32 1)
  %145 = add nsw i32 %144, -1
  %146 = tail call i32 @llvm.smin.i32(i32 %42, i32 %145)
  %147 = tail call i32 @llvm.smin.i32(i32 %42, i32 %139)
  %148 = add nuw i32 %139, 1
  %149 = tail call i32 @llvm.smax.i32(i32 %148, i32 0)
  %150 = tail call i32 @llvm.smin.i32(i32 %42, i32 %149)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv97 = phi i32 [ %136, %for_loop_body16.preheader ], [ %lsr.iv.next98, %for_loop_inc17 ]
  %.04178 = phi i32 [ %154, %for_loop_inc17 ], [ -3, %for_loop_body16.preheader ]
  %.377 = phi float [ %.246, %for_loop_inc17 ], [ %.14580, %for_loop_body16.preheader ]
  %.35076 = phi float [ %.249, %for_loop_inc17 ], [ %.14879, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv97, i32 1)
  %151 = sub i32 %136, %umin
  %152 = add i32 %39, %.04178
  %153 = icmp slt i32 %152, 0
  br i1 %153, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %280, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %289, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %154 = add nsw i32 %.04178, 1
  %lsr.iv.next98 = add i32 %lsr.iv97, 1
  %exitcond.not = icmp eq i32 %154, 4
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %155 = load i32, ptr %43, align 4
  %.not65 = icmp slt i32 %152, %155
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %156 = or i32 %.04178, %.04381
  %spec.select.not = icmp eq i32 %156, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %157 = load ptr, ptr %23, align 8
  %158 = load i32, ptr %24, align 4
  %159 = add i32 %.04178, %151
  %160 = add i32 %159, 3
  %161 = tail call i32 @llvm.smin.i32(i32 %45, i32 %160)
  %162 = mul i32 %158, %53
  %163 = mul i32 %158, %146
  %164 = add i32 %162, %50
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %157, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = add i32 %163, %161
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %157, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = fsub reassoc ninf nsz float %167, %171
  %173 = fmul reassoc ninf nsz float %172, %172
  %174 = tail call i32 @llvm.smin.i32(i32 %45, i32 %152)
  %175 = add i32 %162, %61
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %157, i64 %176
  %178 = load float, ptr %177, align 4
  %179 = add i32 %163, %174
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %157, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = fsub reassoc ninf nsz float %178, %182
  %184 = fmul reassoc ninf nsz float %183, %183
  %185 = fadd reassoc ninf nsz float %184, %173
  %186 = add i32 %152, 1
  %187 = tail call i32 @llvm.smin.i32(i32 %45, i32 %186)
  %188 = add i32 %162, %71
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, ptr %157, i64 %189
  %191 = load float, ptr %190, align 4
  %192 = add i32 %163, %187
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, ptr %157, i64 %193
  %195 = load float, ptr %194, align 4
  %196 = fsub reassoc ninf nsz float %191, %195
  %197 = fmul reassoc ninf nsz float %196, %196
  %198 = fadd reassoc ninf nsz float %197, %185
  %199 = mul i32 %158, %80
  %200 = mul i32 %158, %147
  %201 = add i32 %199, %50
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %157, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = add i32 %200, %161
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %157, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = fsub reassoc ninf nsz float %204, %208
  %210 = fmul reassoc ninf nsz float %209, %209
  %211 = fadd reassoc ninf nsz float %210, %198
  %212 = add i32 %199, %61
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, ptr %157, i64 %213
  %215 = load float, ptr %214, align 4
  %216 = add i32 %200, %174
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %157, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fsub reassoc ninf nsz float %215, %219
  %221 = fmul reassoc ninf nsz float %220, %220
  %222 = fadd reassoc ninf nsz float %221, %211
  %223 = add i32 %199, %71
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %157, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = add i32 %200, %187
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, ptr %157, i64 %228
  %230 = load float, ptr %229, align 4
  %231 = fsub reassoc ninf nsz float %226, %230
  %232 = fmul reassoc ninf nsz float %231, %231
  %233 = fadd reassoc ninf nsz float %232, %222
  %234 = mul i32 %158, %105
  %235 = mul i32 %158, %150
  %236 = add i32 %234, %50
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, ptr %157, i64 %237
  %239 = load float, ptr %238, align 4
  %240 = add i32 %235, %161
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %157, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = fsub reassoc ninf nsz float %239, %243
  %245 = fmul reassoc ninf nsz float %244, %244
  %246 = fadd reassoc ninf nsz float %245, %233
  %247 = add i32 %234, %61
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %157, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = add i32 %235, %174
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, ptr %157, i64 %252
  %254 = load float, ptr %253, align 4
  %255 = fsub reassoc ninf nsz float %250, %254
  %256 = fmul reassoc ninf nsz float %255, %255
  %257 = fadd reassoc ninf nsz float %256, %246
  %258 = add i32 %234, %71
  %259 = sext i32 %258 to i64
  %260 = getelementptr float, ptr %157, i64 %259
  %261 = load float, ptr %260, align 4
  %262 = add i32 %235, %187
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %157, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = fsub reassoc ninf nsz float %261, %265
  %267 = fmul reassoc ninf nsz float %266, %266
  %268 = fadd reassoc ninf nsz float %267, %257
  %269 = fmul reassoc ninf nsz float %268, 0x3FBC71C720000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %269, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %270 = load ptr, ptr %3, align 8
  %271 = getelementptr inbounds nuw i8, ptr %270, i64 32872
  %272 = load ptr, ptr %271, align 8
  %273 = getelementptr inbounds nuw i8, ptr %272, i64 16
  %274 = load float, ptr %273, align 4
  %275 = fcmp reassoc ninf nsz ugt float %.039, %274
  br i1 %275, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %276 = getelementptr inbounds nuw i8, ptr %272, i64 20
  %277 = load float, ptr %276, align 4
  %278 = fmul reassoc ninf nsz float %277, %neg44
  %279 = tail call noundef float @expf(float noundef %278) #8
  %280 = fadd reassoc ninf nsz float %279, %.35076
  %281 = load ptr, ptr %23, align 8
  %282 = load i32, ptr %24, align 4
  %283 = mul i32 %lsr.iv99, %282
  %284 = add i32 %152, %283
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, ptr %281, i64 %285
  %287 = load float, ptr %286, align 4
  %288 = fmul reassoc ninf nsz float %287, %279
  %289 = fadd reassoc ninf nsz float %288, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %290 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %135, float 0x3FE6666660000000)
  %291 = fdiv reassoc ninf nsz float %.044, %.047
  %292 = load ptr, ptr %23, align 8
  %293 = load i32, ptr %24, align 4
  %294 = mul i32 %293, %37
  %295 = add i32 %294, %39
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, ptr %292, i64 %296
  %298 = load float, ptr %297, align 4
  %299 = fsub reassoc ninf nsz float %298, %291
  %300 = tail call noundef float @llvm.fabs.f32(float %299)
  %301 = load ptr, ptr %3, align 8
  %302 = getelementptr inbounds nuw i8, ptr %301, i64 32872
  %303 = load ptr, ptr %302, align 8
  %304 = getelementptr inbounds nuw i8, ptr %303, i64 24
  %305 = load float, ptr %304, align 4
  %306 = fsub reassoc ninf nsz float %300, %305
  %307 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %306, float 0.000000e+00)
  %308 = fcmp reassoc ninf nsz oge float %299, 0.000000e+00
  %309 = uitofp i1 %308 to float
  %310 = fcmp reassoc ninf nsz ole float %299, 0.000000e+00
  %311 = uitofp i1 %310 to float
  %312 = fsub reassoc ninf nsz float %309, %311
  %313 = fmul reassoc ninf nsz float %290, %21
  %314 = fmul reassoc ninf nsz float %313, %312
  %315 = fmul reassoc ninf nsz float %314, %307
  %316 = fadd reassoc ninf nsz float %315, %291
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %317 = load ptr, ptr %23, align 8
  %318 = load i32, ptr %24, align 4
  %319 = mul i32 %318, %37
  %320 = add i32 %319, %39
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %317, i64 %321
  %323 = load float, ptr %322, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %323, %false_block46 ], [ %316, %true_block45 ]
  %324 = load ptr, ptr %0, align 8
  %325 = getelementptr i8, ptr %324, i64 24
  %326 = load ptr, ptr %325, align 8
  %327 = getelementptr i8, ptr %324, i64 20
  %328 = load i32, ptr %327, align 4
  %329 = mul i32 %328, %37
  %330 = add i32 %329, %39
  %331 = sext i32 %330 to i64
  %332 = getelementptr float, ptr %326, i64 %331
  store float %.sink, ptr %332, align 4
  %333 = add nsw i32 %.05782, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond86.not = icmp eq i32 %333, %18
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
  %4 = alloca %struct.RuntimeContext.0, align 8
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
