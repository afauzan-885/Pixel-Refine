; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_ha_green_direct_kernel_c706_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 52
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 48
  %4 = load float, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 16
  store float %4, ptr %9, align 4
  %10 = fsub reassoc ninf nsz float %2, %4
  %11 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %10, float 1.000000e+00)
  %12 = fdiv reassoc ninf nsz float 1.000000e+00, %11
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 20
  store float %12, ptr %16, align 4
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 56
  %19 = load i32, ptr %18, align 4
  %20 = load ptr, ptr %5, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 8
  store i32 %19, ptr %23, align 4
  %24 = tail call i32 @llvm.smax.i32(i32 %19, i32 0)
  %25 = load ptr, ptr %context, align 8
  %26 = getelementptr i8, ptr %25, i64 60
  %27 = load i32, ptr %26, align 4
  %28 = load ptr, ptr %5, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 12
  store i32 %27, ptr %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %27, i32 0)
  %33 = load ptr, ptr %5, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 4
  store i32 %32, ptr %36, align 4
  %37 = mul i32 %32, %24
  %38 = load ptr, ptr %5, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  store i32 %37, ptr %40, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_ha_green_direct_kernel_c706_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
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
  %20 = getelementptr i8, ptr %19, i64 64
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 68
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 72
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 76
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 8
  %30 = getelementptr i8, ptr %19, i64 4
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.0419 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %244, %after_if3 ]
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 4
  %35 = load i32, ptr %34, align 4
  %36 = sdiv i32 %.0419, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.0419
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.0419, %37
  %41 = and i1 %39, %40
  %.neg7 = sext i1 %41 to i32
  %42 = add i32 %36, %.neg7
  %43 = mul i32 %35, -1
  %44 = mul i32 %43, %42
  %45 = add i32 %.0419, %44
  %46 = sdiv i32 %42, 2
  %47 = icmp slt i32 %42, 0
  %48 = shl nsw i32 %46, 1
  %49 = icmp ne i32 %48, %42
  %50 = and i1 %47, %49
  %.neg8 = sext i1 %50 to i32
  %51 = add nsw i32 %46, %.neg8
  %52 = shl i32 %51, 1
  %53 = sdiv i32 %45, 2
  %54 = icmp slt i32 %45, 0
  %55 = shl nsw i32 %53, 1
  %56 = icmp ne i32 %45, %55
  %57 = and i1 %54, %56
  %.neg9 = sext i1 %57 to i32
  %58 = add nsw i32 %53, %.neg9
  %59 = shl i32 %58, 1
  %.not = icmp eq i32 %42, %52
  %.not10 = icmp eq i32 %45, %59
  %60 = select i1 %.not10, i32 %21, i32 %23
  %61 = select i1 %.not10, i32 %25, i32 %27
  %62 = select i1 %.not, i32 %60, i32 %61
  %63 = getelementptr inbounds nuw i8, ptr %33, i64 8
  %64 = load i32, ptr %63, align 4
  %65 = add i32 %64, -1
  %66 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %67 = tail call i32 @llvm.smin.i32(i32 %65, i32 %66)
  %68 = getelementptr inbounds nuw i8, ptr %33, i64 12
  %69 = load i32, ptr %68, align 4
  %70 = add i32 %69, -1
  %71 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %72 = tail call i32 @llvm.smin.i32(i32 %70, i32 %71)
  %73 = load ptr, ptr %29, align 8
  %74 = load i32, ptr %30, align 4
  %75 = mul i32 %67, %74
  %76 = add i32 %72, %75
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, ptr %73, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = getelementptr inbounds nuw i8, ptr %33, i64 16
  %81 = load float, ptr %80, align 4
  %82 = fsub reassoc ninf nsz float %79, %81
  %83 = getelementptr inbounds nuw i8, ptr %33, i64 20
  %84 = load float, ptr %83, align 4
  %85 = fmul reassoc ninf nsz float %82, %84
  %86 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %85, float 0.000000e+00)
  %87 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %86, float 1.000000e+00)
  switch i32 %62, label %false_block2 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %.not12 = icmp eq i32 %62, 1
  %88 = load ptr, ptr %0, align 8
  %89 = getelementptr i8, ptr %88, i64 36
  %90 = load float, ptr %89, align 4
  %91 = getelementptr i8, ptr %88, i64 44
  %92 = load float, ptr %91, align 4
  %93 = select reassoc ninf nsz i1 %.not12, float %90, float %92
  %94 = fmul reassoc ninf nsz float %93, %87
  br label %after_if3

false_block2:                                     ; preds = %for_loop_body
  %95 = add i32 %45, -1
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = tail call i32 @llvm.smin.i32(i32 %70, i32 %96)
  %98 = add i32 %97, %75
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %73, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fsub reassoc ninf nsz float %101, %81
  %103 = fmul reassoc ninf nsz float %102, %84
  %104 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %103, float 0.000000e+00)
  %105 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %104, float 1.000000e+00)
  %106 = load ptr, ptr %0, align 8
  %107 = getelementptr i8, ptr %106, i64 36
  %108 = load float, ptr %107, align 4
  %109 = fmul reassoc ninf nsz float %105, %108
  %110 = add i32 %45, 1
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = tail call i32 @llvm.smin.i32(i32 %70, i32 %111)
  %113 = add i32 %112, %75
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %73, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = fsub reassoc ninf nsz float %116, %81
  %118 = fmul reassoc ninf nsz float %117, %84
  %119 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0.000000e+00)
  %120 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %119, float 1.000000e+00)
  %121 = fmul reassoc ninf nsz float %120, %108
  %122 = add i32 %42, -1
  %123 = tail call i32 @llvm.smax.i32(i32 %122, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %65, i32 %123)
  %125 = mul i32 %124, %74
  %126 = add i32 %125, %72
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %73, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fsub reassoc ninf nsz float %129, %81
  %131 = fmul reassoc ninf nsz float %130, %84
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float 0.000000e+00)
  %133 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %132, float 1.000000e+00)
  %134 = getelementptr i8, ptr %106, i64 44
  %135 = load float, ptr %134, align 4
  %136 = fmul reassoc ninf nsz float %133, %135
  %137 = add i32 %42, 1
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  %139 = tail call i32 @llvm.smin.i32(i32 %65, i32 %138)
  %140 = mul i32 %139, %74
  %141 = add i32 %140, %72
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %73, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = fsub reassoc ninf nsz float %144, %81
  %146 = fmul reassoc ninf nsz float %145, %84
  %147 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %146, float 0.000000e+00)
  %148 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %147, float 1.000000e+00)
  %149 = fmul reassoc ninf nsz float %148, %135
  %.not11 = icmp eq i32 %62, 0
  %150 = getelementptr i8, ptr %106, i64 32
  %151 = load float, ptr %150, align 4
  %152 = getelementptr i8, ptr %106, i64 40
  %153 = load float, ptr %152, align 4
  %154 = select reassoc ninf nsz i1 %.not11, float %151, float %153
  %155 = fmul reassoc ninf nsz float %154, %87
  %156 = add i32 %45, -2
  %157 = tail call i32 @llvm.smax.i32(i32 %156, i32 0)
  %158 = tail call i32 @llvm.smin.i32(i32 %70, i32 %157)
  %159 = add i32 %158, %75
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %73, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = fsub reassoc ninf nsz float %162, %81
  %164 = fmul reassoc ninf nsz float %163, %84
  %165 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %164, float 0.000000e+00)
  %166 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %165, float 1.000000e+00)
  %167 = add i32 %45, 2
  %168 = tail call i32 @llvm.smax.i32(i32 %167, i32 0)
  %169 = tail call i32 @llvm.smin.i32(i32 %70, i32 %168)
  %170 = add i32 %169, %75
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %73, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fsub reassoc ninf nsz float %173, %81
  %175 = fmul reassoc ninf nsz float %174, %84
  %176 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %175, float 0.000000e+00)
  %177 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %176, float 1.000000e+00)
  %178 = add i32 %42, -2
  %179 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %180 = tail call i32 @llvm.smin.i32(i32 %65, i32 %179)
  %181 = mul i32 %180, %74
  %182 = add i32 %181, %72
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %73, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = fsub reassoc ninf nsz float %185, %81
  %187 = fmul reassoc ninf nsz float %186, %84
  %188 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %187, float 0.000000e+00)
  %189 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %188, float 1.000000e+00)
  %190 = fneg reassoc ninf nsz float %154
  %.neg13 = fmul reassoc ninf nsz float %189, %190
  %191 = add i32 %42, 2
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %65, i32 %192)
  %194 = mul i32 %193, %74
  %195 = add i32 %194, %72
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %73, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = fsub reassoc ninf nsz float %198, %81
  %200 = fmul reassoc ninf nsz float %199, %84
  %201 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %200, float 0.000000e+00)
  %202 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %201, float 1.000000e+00)
  %.neg14 = fmul reassoc ninf nsz float %202, %190
  %203 = fsub reassoc ninf nsz float %109, %121
  %204 = tail call noundef float @llvm.fabs.f32(float %203)
  %factor = fmul reassoc ninf nsz float %155, 2.000000e+00
  %205 = fadd reassoc ninf nsz float %177, %166
  %206 = fmul reassoc ninf nsz float %205, %154
  %207 = fsub reassoc ninf nsz float %factor, %206
  %208 = tail call noundef float @llvm.fabs.f32(float %207)
  %209 = fadd reassoc ninf nsz float %208, %204
  %210 = fsub reassoc ninf nsz float %136, %149
  %211 = tail call noundef float @llvm.fabs.f32(float %210)
  %.neg15 = fadd reassoc ninf nsz float %.neg13, %factor
  %212 = fadd reassoc ninf nsz float %.neg15, %.neg14
  %213 = tail call noundef float @llvm.fabs.f32(float %212)
  %214 = fadd reassoc ninf nsz float %213, %211
  %215 = fsub reassoc ninf nsz float %209, %214
  %216 = tail call noundef float @llvm.fabs.f32(float %215)
  %217 = fadd reassoc ninf nsz float %121, %109
  %218 = fadd reassoc ninf nsz float %149, %136
  %219 = fadd reassoc ninf nsz float %218, %217
  %220 = fmul reassoc ninf nsz float %219, 2.500000e-01
  %221 = fmul reassoc ninf nsz float %155, 4.000000e+00
  %.neg17 = fsub reassoc ninf nsz float %221, %206
  %.neg18 = fadd reassoc ninf nsz float %.neg17, %.neg13
  %222 = fadd reassoc ninf nsz float %.neg18, %.neg14
  %223 = fmul reassoc ninf nsz float %222, 1.250000e-01
  %224 = fadd reassoc ninf nsz float %223, %220
  %225 = fmul reassoc ninf nsz float %217, 5.000000e-01
  %226 = fmul reassoc ninf nsz float %207, 2.500000e-01
  %227 = fadd reassoc ninf nsz float %226, %225
  %228 = fmul reassoc ninf nsz float %218, 5.000000e-01
  %229 = fmul reassoc ninf nsz float %212, 2.500000e-01
  %230 = fadd reassoc ninf nsz float %229, %228
  %231 = fcmp reassoc ninf nsz olt float %216, 0x3FA1EB8520000000
  %232 = fcmp reassoc ninf nsz olt float %209, %214
  %233 = select reassoc ninf nsz i1 %232, float %227, float %230
  %234 = select reassoc ninf nsz i1 %231, float %224, float %233
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  %.sink29 = phi ptr [ %106, %false_block2 ], [ %88, %true_block1 ]
  %.sink = phi float [ %234, %false_block2 ], [ %94, %true_block1 ]
  %235 = getelementptr i8, ptr %.sink29, i64 24
  %236 = load ptr, ptr %235, align 8
  %237 = getelementptr i8, ptr %.sink29, i64 20
  %238 = load i32, ptr %237, align 4
  %239 = sub i32 %238, %35
  %240 = mul i32 %239, %42
  %241 = add i32 %.0419, %240
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %236, i64 %242
  store float %.sink, ptr %243, align 4
  %244 = add nsw i32 %.0419, 1
  %exitcond.not = icmp eq i32 %18, %244
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
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
