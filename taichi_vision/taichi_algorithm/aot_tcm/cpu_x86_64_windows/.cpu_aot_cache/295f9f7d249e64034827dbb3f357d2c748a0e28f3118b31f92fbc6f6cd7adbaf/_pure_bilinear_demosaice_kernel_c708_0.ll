; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_pure_bilinear_demosaice_kernel_c708_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 44
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 40
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
  %18 = getelementptr i8, ptr %17, i64 48
  %19 = load i32, ptr %18, align 4
  %20 = load ptr, ptr %5, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 8
  store i32 %19, ptr %23, align 4
  %24 = tail call i32 @llvm.smax.i32(i32 %19, i32 0)
  %25 = load ptr, ptr %context, align 8
  %26 = getelementptr i8, ptr %25, i64 52
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

define void @_pure_bilinear_demosaice_kernel_c708_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 8
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 32
  %24 = getelementptr i8, ptr %20, i64 20
  %25 = getelementptr i8, ptr %20, i64 24
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %.02029 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %194, %after_if9 ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.02029, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.02029
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.02029, %32
  %36 = and i1 %34, %35
  %.neg21 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg21
  %38 = mul i32 %37, %30
  %39 = mul i32 %30, -1
  %40 = mul i32 %39, %37
  %41 = add i32 %.02029, %40
  %42 = sdiv i32 %37, 2
  %43 = icmp slt i32 %37, 0
  %44 = shl nsw i32 %42, 1
  %45 = icmp ne i32 %44, %37
  %46 = and i1 %43, %45
  %.neg22 = sext i1 %46 to i32
  %47 = add nsw i32 %42, %.neg22
  %48 = shl i32 %47, 1
  %49 = sdiv i32 %41, 2
  %50 = icmp slt i32 %41, 0
  %51 = shl nsw i32 %49, 1
  %52 = icmp ne i32 %41, %51
  %53 = and i1 %50, %52
  %.neg23 = sext i1 %53 to i32
  %54 = add nsw i32 %49, %.neg23
  %55 = shl i32 %54, 1
  %.not24 = icmp eq i32 %37, %48
  %.not = icmp eq i32 %41, %55
  %56 = load ptr, ptr %0, align 8
  %spec.select = select i1 %.not, i64 56, i64 60
  %spec.select36 = select i1 %.not, i64 64, i64 68
  %.sink = select i1 %.not24, i64 %spec.select, i64 %spec.select36
  %57 = getelementptr i8, ptr %56, i64 %.sink
  %.019 = load i32, ptr %57, align 4
  %58 = add i32 %37, -1
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %61 = load i32, ptr %60, align 4
  %62 = add i32 %61, -1
  %63 = add i32 %37, 1
  %64 = tail call i32 @llvm.smin.i32(i32 %62, i32 %63)
  %65 = add i32 %41, -1
  %66 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %67 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %68 = load i32, ptr %67, align 4
  %69 = add i32 %68, -1
  %70 = add i32 %41, 1
  %71 = tail call i32 @llvm.smin.i32(i32 %69, i32 %70)
  %72 = load ptr, ptr %21, align 8
  %73 = load i32, ptr %22, align 4
  %74 = mul i32 %73, %37
  %75 = sub i32 %73, %30
  %76 = mul i32 %75, %37
  %77 = add i32 %.02029, %76
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, ptr %72, i64 %78
  %80 = load float, ptr %79, align 4
  %81 = getelementptr inbounds nuw i8, ptr %28, i64 16
  %82 = load float, ptr %81, align 4
  %83 = fsub reassoc ninf nsz float %80, %82
  %84 = getelementptr inbounds nuw i8, ptr %28, i64 20
  %85 = load float, ptr %84, align 4
  %86 = fmul reassoc ninf nsz float %83, %85
  %87 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %86, float 0.000000e+00)
  %88 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %87, float 1.000000e+00)
  %89 = mul i32 %73, %59
  %90 = sub i32 %89, %38
  %91 = add i32 %.02029, %90
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %72, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = fsub reassoc ninf nsz float %94, %82
  %96 = fmul reassoc ninf nsz float %95, %85
  %97 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %96, float 0.000000e+00)
  %98 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %97, float 1.000000e+00)
  %99 = mul i32 %73, %64
  %100 = sub i32 %99, %38
  %101 = add i32 %.02029, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %72, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = fsub reassoc ninf nsz float %104, %82
  %106 = fmul reassoc ninf nsz float %105, %85
  %107 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %106, float 0.000000e+00)
  %108 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %107, float 1.000000e+00)
  %109 = add i32 %74, %66
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %72, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fsub reassoc ninf nsz float %112, %82
  %114 = fmul reassoc ninf nsz float %113, %85
  %115 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %114, float 0.000000e+00)
  %116 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %115, float 1.000000e+00)
  %117 = add i32 %74, %71
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, ptr %72, i64 %118
  %120 = load float, ptr %119, align 4
  %121 = fsub reassoc ninf nsz float %120, %82
  %122 = fmul reassoc ninf nsz float %121, %85
  %123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %122, float 0.000000e+00)
  %124 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %123, float 1.000000e+00)
  switch i32 %.019, label %false_block11 [
    i32 0, label %true_block7
    i32 2, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block7:                                      ; preds = %for_loop_body
  %125 = add i32 %89, %66
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %72, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fsub reassoc ninf nsz float %128, %82
  %130 = fmul reassoc ninf nsz float %129, %85
  %131 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %130, float 0.000000e+00)
  %132 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float 1.000000e+00)
  %133 = add i32 %89, %71
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %72, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = fsub reassoc ninf nsz float %136, %82
  %138 = fmul reassoc ninf nsz float %137, %85
  %139 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %138, float 0.000000e+00)
  %140 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %139, float 1.000000e+00)
  %141 = add i32 %99, %66
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %72, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = fsub reassoc ninf nsz float %144, %82
  %146 = fmul reassoc ninf nsz float %145, %85
  %147 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %146, float 0.000000e+00)
  %148 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %147, float 1.000000e+00)
  %149 = add i32 %99, %71
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %72, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = fsub reassoc ninf nsz float %152, %82
  %154 = fmul reassoc ninf nsz float %153, %85
  %155 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %154, float 0.000000e+00)
  %156 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %155, float 1.000000e+00)
  %157 = fadd reassoc ninf nsz float %108, %98
  %158 = fadd reassoc ninf nsz float %157, %116
  %159 = fadd reassoc ninf nsz float %158, %124
  %160 = fmul reassoc ninf nsz float %159, 2.500000e-01
  %161 = fadd reassoc ninf nsz float %140, %132
  %162 = fadd reassoc ninf nsz float %161, %148
  %163 = fadd reassoc ninf nsz float %162, %156
  %164 = fmul reassoc ninf nsz float %163, 2.500000e-01
  br label %after_if9

after_if9:                                        ; preds = %false_block11, %true_block10, %true_block7
  %.017 = phi float [ %88, %true_block7 ], [ %234, %true_block10 ], [ %., %false_block11 ]
  %.016 = phi float [ %160, %true_block7 ], [ %230, %true_block10 ], [ %88, %false_block11 ]
  %.015 = phi float [ %164, %true_block7 ], [ %88, %true_block10 ], [ %.31, %false_block11 ]
  %165 = load ptr, ptr %23, align 8
  %166 = load i32, ptr %24, align 4
  %167 = load i32, ptr %25, align 4
  %168 = sub i32 %166, %30
  %169 = mul i32 %168, %37
  %170 = add i32 %.02029, %169
  %171 = mul i32 %170, %167
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %165, i64 %172
  store float %.017, ptr %173, align 4
  %174 = load ptr, ptr %23, align 8
  %175 = load i32, ptr %24, align 4
  %176 = load i32, ptr %25, align 4
  %177 = sub i32 %175, %30
  %178 = mul i32 %177, %37
  %179 = add i32 %.02029, %178
  %180 = mul i32 %179, %176
  %181 = add i32 %180, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %174, i64 %182
  store float %.016, ptr %183, align 4
  %184 = load ptr, ptr %23, align 8
  %185 = load i32, ptr %24, align 4
  %186 = load i32, ptr %25, align 4
  %187 = sub i32 %185, %30
  %188 = mul i32 %187, %37
  %189 = add i32 %.02029, %188
  %190 = mul i32 %189, %186
  %191 = add i32 %190, 2
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %184, i64 %192
  store float %.015, ptr %193, align 4
  %194 = add nsw i32 %.02029, 1
  %exitcond.not = icmp eq i32 %18, %194
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %for_loop_body
  %195 = add i32 %89, %66
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %72, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = fsub reassoc ninf nsz float %198, %82
  %200 = fmul reassoc ninf nsz float %199, %85
  %201 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %200, float 0.000000e+00)
  %202 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %201, float 1.000000e+00)
  %203 = add i32 %89, %71
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %72, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = fsub reassoc ninf nsz float %206, %82
  %208 = fmul reassoc ninf nsz float %207, %85
  %209 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %208, float 0.000000e+00)
  %210 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %209, float 1.000000e+00)
  %211 = add i32 %99, %66
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %72, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = fsub reassoc ninf nsz float %214, %82
  %216 = fmul reassoc ninf nsz float %215, %85
  %217 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %216, float 0.000000e+00)
  %218 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %217, float 1.000000e+00)
  %219 = add i32 %99, %71
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, ptr %72, i64 %220
  %222 = load float, ptr %221, align 4
  %223 = fsub reassoc ninf nsz float %222, %82
  %224 = fmul reassoc ninf nsz float %223, %85
  %225 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %224, float 0.000000e+00)
  %226 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %225, float 1.000000e+00)
  %227 = fadd reassoc ninf nsz float %108, %98
  %228 = fadd reassoc ninf nsz float %227, %116
  %229 = fadd reassoc ninf nsz float %228, %124
  %230 = fmul reassoc ninf nsz float %229, 2.500000e-01
  %231 = fadd reassoc ninf nsz float %210, %202
  %232 = fadd reassoc ninf nsz float %231, %218
  %233 = fadd reassoc ninf nsz float %232, %226
  %234 = fmul reassoc ninf nsz float %233, 2.500000e-01
  br label %after_if9

false_block11:                                    ; preds = %for_loop_body
  %235 = and i32 %66, 1
  %.not26 = icmp eq i32 %235, 0
  %.37 = select i1 %.not24, i64 56, i64 64
  %.38 = select i1 %.not24, i64 60, i64 68
  %spec.select30.v = select i1 %.not26, i64 %.37, i64 %.38
  %spec.select30 = getelementptr i8, ptr %56, i64 %spec.select30.v
  %.013 = load i32, ptr %spec.select30, align 4
  %236 = icmp eq i32 %.013, 0
  %237 = fadd reassoc ninf nsz float %124, %116
  %238 = fmul reassoc ninf nsz float %237, 5.000000e-01
  %239 = fadd reassoc ninf nsz float %108, %98
  %240 = fmul reassoc ninf nsz float %239, 5.000000e-01
  %. = select i1 %236, float %238, float %240
  %.31 = select i1 %236, float %240, float %238
  br label %after_if9
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !11

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !13

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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
