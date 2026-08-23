; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_lk_dense_interpolate_kernel_c496_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_lk_dense_interpolate_kernel_c496_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.011 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %217, %after_if ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.011, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.011
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.011, %33
  %37 = and i1 %35, %36
  %.neg5 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg5
  %39 = mul i32 %31, -1
  %40 = mul i32 %39, %38
  %41 = add i32 %26, %.011
  %42 = add i32 %41, %40
  %43 = sitofp i32 %42 to float
  %44 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %45 = load float, ptr %44, align 4
  %46 = fmul reassoc ninf nsz float %45, %43
  %47 = sub i32 %38, %21
  %48 = sitofp i32 %47 to float
  %49 = fmul reassoc ninf nsz float %45, %48
  %50 = tail call reassoc ninf nsz float @llvm.floor.f32(float %46)
  %51 = fptosi float %50 to i32
  %52 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %53 = load i32, ptr %52, align 4
  %54 = add i32 %53, -1
  %55 = tail call i32 @llvm.smin.i32(i32 %51, i32 %54)
  %56 = tail call i32 @llvm.smax.i32(i32 %55, i32 0)
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %49)
  %58 = fptosi float %57 to i32
  %59 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %60, -1
  %62 = tail call i32 @llvm.smin.i32(i32 %58, i32 %61)
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %64 = add nuw i32 %56, 1
  %65 = tail call i32 @llvm.smin.i32(i32 %64, i32 %54)
  %66 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %67 = add nuw i32 %63, 1
  %68 = tail call i32 @llvm.smin.i32(i32 %67, i32 %61)
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = uitofp nneg i32 %56 to float
  %71 = fsub reassoc ninf nsz float %46, %70
  %72 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %71, float 1.000000e+00)
  %73 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %72, float 0.000000e+00)
  %74 = uitofp nneg i32 %63 to float
  %75 = fsub reassoc ninf nsz float %49, %74
  %76 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %75, float 1.000000e+00)
  %77 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %76, float 0.000000e+00)
  %78 = fmul reassoc ninf nsz float %73, %73
  %factor = fmul reassoc ninf nsz float %73, -2.000000e+00
  %79 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %80 = fmul reassoc ninf nsz float %78, %79
  %81 = fmul reassoc ninf nsz float %77, %77
  %factor10 = fmul reassoc ninf nsz float %77, -2.000000e+00
  %82 = fadd reassoc ninf nsz float %factor10, 3.000000e+00
  %83 = fmul reassoc ninf nsz float %81, %82
  %84 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %85 = fsub reassoc ninf nsz float 1.000000e+00, %83
  %86 = load ptr, ptr %23, align 8
  %87 = load i32, ptr %24, align 4
  %88 = load i32, ptr %25, align 4
  %89 = mul i32 %63, %87
  %90 = add i32 %56, %89
  %91 = mul i32 %90, %88
  %92 = add i32 %91, 2
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %86, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fmul reassoc ninf nsz float %85, %95
  %97 = fmul reassoc ninf nsz float %96, %84
  %98 = add i32 %66, %89
  %99 = mul i32 %98, %88
  %100 = add i32 %99, 2
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %86, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = fmul reassoc ninf nsz float %85, %103
  %105 = fmul reassoc ninf nsz float %104, %80
  %106 = mul i32 %69, %87
  %107 = add i32 %106, %56
  %108 = mul i32 %107, %88
  %109 = add i32 %108, 2
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %86, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fmul reassoc ninf nsz float %83, %112
  %114 = fmul reassoc ninf nsz float %113, %84
  %115 = add i32 %66, %106
  %116 = mul i32 %115, %88
  %117 = add i32 %116, 2
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, ptr %86, i64 %118
  %120 = load float, ptr %119, align 4
  %121 = fmul reassoc ninf nsz float %83, %120
  %122 = fmul reassoc ninf nsz float %121, %80
  %123 = fadd reassoc ninf nsz float %122, %105
  %124 = fadd reassoc ninf nsz float %123, %97
  %125 = fadd reassoc ninf nsz float %124, %114
  %126 = fcmp reassoc ninf nsz ogt float %125, 0x3EB0C6F7A0000000
  br i1 %126, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %127 = sext i32 %91 to i64
  %128 = getelementptr float, ptr %86, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fmul reassoc ninf nsz float %129, %97
  %131 = sext i32 %99 to i64
  %132 = getelementptr float, ptr %86, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = fmul reassoc ninf nsz float %133, %105
  %135 = fadd reassoc ninf nsz float %134, %130
  %136 = sext i32 %108 to i64
  %137 = getelementptr float, ptr %86, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = fmul reassoc ninf nsz float %138, %114
  %140 = fadd reassoc ninf nsz float %135, %139
  %141 = sext i32 %116 to i64
  %142 = getelementptr float, ptr %86, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = fmul reassoc ninf nsz float %143, %122
  %145 = fadd reassoc ninf nsz float %140, %144
  %146 = fdiv reassoc ninf nsz float %145, %125
  %147 = load ptr, ptr %0, align 8
  %148 = getelementptr i8, ptr %147, i64 40
  %149 = load ptr, ptr %148, align 8
  %150 = getelementptr i8, ptr %147, i64 28
  %151 = load i32, ptr %150, align 4
  %152 = getelementptr i8, ptr %147, i64 32
  %153 = load i32, ptr %152, align 4
  %154 = sub i32 %151, %31
  %155 = mul i32 %154, %38
  %156 = add i32 %.011, %155
  %157 = mul i32 %156, %153
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %149, i64 %158
  store float %146, ptr %159, align 4
  %160 = load ptr, ptr %23, align 8
  %161 = load i32, ptr %24, align 4
  %162 = load i32, ptr %25, align 4
  %163 = mul i32 %161, %63
  %164 = add i32 %163, %56
  %165 = mul i32 %164, %162
  %166 = add i32 %165, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %160, i64 %167
  %169 = load float, ptr %168, align 4
  %170 = fmul reassoc ninf nsz float %169, %97
  %171 = add i32 %163, %66
  %172 = mul i32 %171, %162
  %173 = add i32 %172, 1
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, ptr %160, i64 %174
  %176 = load float, ptr %175, align 4
  %177 = fmul reassoc ninf nsz float %176, %105
  %178 = fadd reassoc ninf nsz float %177, %170
  %179 = mul i32 %161, %69
  %180 = add i32 %179, %56
  %181 = mul i32 %180, %162
  %182 = add i32 %181, 1
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %160, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = fmul reassoc ninf nsz float %185, %114
  %187 = fadd reassoc ninf nsz float %178, %186
  %188 = add i32 %179, %66
  %189 = mul i32 %188, %162
  %190 = add i32 %189, 1
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %160, i64 %191
  %193 = load float, ptr %192, align 4
  %194 = fmul reassoc ninf nsz float %193, %122
  %195 = fadd reassoc ninf nsz float %187, %194
  %196 = fdiv reassoc ninf nsz float %195, %125
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %197 = load ptr, ptr %0, align 8
  %198 = getelementptr i8, ptr %197, i64 40
  %199 = load ptr, ptr %198, align 8
  %200 = getelementptr i8, ptr %197, i64 28
  %201 = load i32, ptr %200, align 4
  %202 = getelementptr i8, ptr %197, i64 32
  %203 = load i32, ptr %202, align 4
  %204 = sub i32 %201, %31
  %205 = mul i32 %204, %38
  %206 = add i32 %.011, %205
  %207 = mul i32 %206, %203
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %199, i64 %208
  store float 0.000000e+00, ptr %209, align 4
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %.sink20.in = phi ptr [ %200, %false_block ], [ %150, %true_block ]
  %.sink18.in = phi ptr [ %202, %false_block ], [ %152, %true_block ]
  %.sink13.in = phi ptr [ %198, %false_block ], [ %148, %true_block ]
  %.sink = phi float [ 0.000000e+00, %false_block ], [ %196, %true_block ]
  %.sink13 = load ptr, ptr %.sink13.in, align 8
  %.sink18 = load i32, ptr %.sink18.in, align 4
  %.sink20 = load i32, ptr %.sink20.in, align 4
  %210 = sub i32 %.sink20, %31
  %211 = mul i32 %210, %38
  %212 = add i32 %.011, %211
  %213 = mul i32 %212, %.sink18
  %214 = add i32 %213, 1
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, ptr %.sink13, i64 %215
  store float %.sink, ptr %216, align 4
  %217 = add nsw i32 %.011, 1
  %exitcond.not = icmp eq i32 %18, %217
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.9, align 8
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
