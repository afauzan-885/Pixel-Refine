; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_zncc_spatial_kernel_c298_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = load ptr, ptr %context, align 8
  %9 = getelementptr i8, ptr %8, i64 20
  %10 = load i32, ptr %9, align 4
  %11 = load ptr, ptr %3, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 12
  store i32 %10, ptr %14, align 4
  %15 = load ptr, ptr %context, align 8
  %16 = getelementptr i8, ptr %15, i64 64
  %17 = load i32, ptr %16, align 4
  %18 = tail call i32 @llvm.smax.i32(i32 %17, i32 0)
  %19 = getelementptr i8, ptr %15, i64 68
  %20 = load i32, ptr %19, align 4
  %21 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %22 = load ptr, ptr %3, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 4
  store i32 %21, ptr %25, align 4
  %26 = mul i32 %21, %18
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  store i32 %26, ptr %29, align 4
  ret void
}

define void @_zncc_spatial_kernel_c298_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 92
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 80
  %23 = load float, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 88
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 84
  %27 = load float, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 40
  %30 = getelementptr i8, ptr %19, i64 36
  %31 = getelementptr i8, ptr %19, i64 56
  %32 = getelementptr i8, ptr %19, i64 52
  %33 = getelementptr i8, ptr %19, i64 8
  %34 = getelementptr i8, ptr %19, i64 4
  %35 = getelementptr i8, ptr %19, i64 24
  %36 = getelementptr i8, ptr %19, i64 20
  %37 = getelementptr i8, ptr %19, i64 72
  %38 = getelementptr i8, ptr %19, i64 68
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for27, %for_loop_body.lr.ph
  %.01831 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %189, %after_for27 ]
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 4
  %43 = load i32, ptr %42, align 4
  %44 = sdiv i32 %.01831, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.01831
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %45, %.01831
  %49 = and i1 %47, %48
  %.neg27 = sext i1 %49 to i32
  %50 = add i32 %44, %.neg27
  %51 = mul i32 %50, %43
  %52 = sub i32 %.01831, %51
  %53 = mul i32 %50, %21
  %54 = mul i32 %52, %21
  %55 = getelementptr inbounds nuw i8, ptr %41, i64 8
  %56 = load i32, ptr %55, align 4
  %57 = add i32 %53, -1
  %58 = add i32 %57, %56
  %59 = getelementptr inbounds nuw i8, ptr %41, i64 12
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %54, -1
  %62 = add i32 %61, %60
  %63 = load ptr, ptr %29, align 8
  %64 = load i32, ptr %30, align 4
  %65 = mul i32 %58, %64
  %66 = add i32 %62, %65
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %63, i64 %67
  %69 = load float, ptr %68, align 4
  %70 = icmp sgt i32 %57, -1
  br i1 %70, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_for27
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %71 = mul i32 %57, %64
  %72 = add i32 %62, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %63, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = fsub reassoc ninf nsz float %69, %75
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.020 = phi float [ %76, %true_block ], [ %69, %for_loop_body ]
  %77 = icmp sgt i32 %61, -1
  br i1 %77, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %78 = add i32 %65, %61
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, ptr %63, i64 %79
  %81 = load float, ptr %80, align 4
  %82 = fsub reassoc ninf nsz float %.020, %81
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %.121 = phi float [ %82, %true_block1 ], [ %.020, %after_if ]
  %83 = or i32 %61, %57
  %spec.store.select = icmp sgt i32 %83, -1
  br i1 %spec.store.select, label %true_block8, label %after_if10

true_block8:                                      ; preds = %after_if3
  %84 = mul i32 %57, %64
  %85 = add i32 %61, %84
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %63, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = fadd reassoc ninf nsz float %88, %.121
  br label %after_if10

after_if10:                                       ; preds = %true_block8, %after_if3
  %.222 = phi float [ %89, %true_block8 ], [ %.121, %after_if3 ]
  %90 = load ptr, ptr %31, align 8
  %91 = load i32, ptr %32, align 4
  %92 = mul i32 %91, %58
  %93 = add i32 %92, %62
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %90, i64 %94
  %96 = load float, ptr %95, align 4
  br i1 %70, label %true_block11, label %after_if13

true_block11:                                     ; preds = %after_if10
  %97 = mul i32 %91, %57
  %98 = add i32 %97, %62
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %90, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fsub reassoc ninf nsz float %96, %101
  br label %after_if13

after_if13:                                       ; preds = %true_block11, %after_if10
  %.019 = phi float [ %102, %true_block11 ], [ %96, %after_if10 ]
  br i1 %77, label %true_block15, label %after_if17

true_block15:                                     ; preds = %after_if13
  %103 = add i32 %92, %61
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %90, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = fsub reassoc ninf nsz float %.019, %106
  br label %after_if17

after_if17:                                       ; preds = %true_block15, %after_if13
  %.1 = phi float [ %107, %true_block15 ], [ %.019, %after_if13 ]
  br i1 %spec.store.select, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if17
  %108 = mul i32 %91, %57
  %109 = add i32 %108, %61
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %90, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fadd reassoc ninf nsz float %112, %.1
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if17
  %.2 = phi float [ %113, %true_block22 ], [ %.1, %after_if17 ]
  %114 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %115 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %116 = mul i32 %115, %114
  %117 = icmp sgt i32 %116, 0
  br i1 %117, label %for_loop_body25.lr.ph, label %after_for27

for_loop_body25.lr.ph:                            ; preds = %after_if24
  %118 = load ptr, ptr %33, align 8
  %119 = load i32, ptr %34, align 4
  %120 = load ptr, ptr %35, align 8
  %121 = load i32, ptr %36, align 4
  %xtraiter = and i32 %116, 1
  %122 = icmp eq i32 %116, 1
  br i1 %122, label %after_for27.loopexit.unr-lcssa, label %for_loop_body25.lr.ph.new

for_loop_body25.lr.ph.new:                        ; preds = %for_loop_body25.lr.ph
  %unroll_iter = and i32 %116, 2147483646
  br label %for_loop_body25

for_loop_body25:                                  ; preds = %for_loop_body25, %for_loop_body25.lr.ph.new
  %.030 = phi i32 [ 0, %for_loop_body25.lr.ph.new ], [ %154, %for_loop_body25 ]
  %.01729 = phi float [ 0.000000e+00, %for_loop_body25.lr.ph.new ], [ %153, %for_loop_body25 ]
  %123 = udiv i32 %.030, %115
  %.recomposed = urem i32 %.030, %115
  %124 = add i32 %123, %53
  %125 = add i32 %.recomposed, %54
  %126 = mul i32 %119, %124
  %127 = add i32 %125, %126
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %118, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = mul i32 %121, %123
  %132 = add i32 %131, %.recomposed
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %120, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = fmul reassoc ninf nsz float %135, %130
  %137 = fadd reassoc ninf nsz float %136, %.01729
  %138 = add i32 %.030, 1
  %139 = udiv i32 %138, %115
  %.recomposed36 = urem i32 %138, %115
  %140 = add i32 %139, %53
  %141 = add i32 %.recomposed36, %54
  %142 = mul i32 %119, %140
  %143 = add i32 %141, %142
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %118, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = mul i32 %121, %139
  %148 = add i32 %147, %.recomposed36
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %120, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = fmul reassoc ninf nsz float %151, %146
  %153 = fadd reassoc ninf nsz float %152, %137
  %154 = add nuw i32 %.030, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %154
  br i1 %niter.ncmp.1, label %after_for27.loopexit.unr-lcssa.loopexit, label %for_loop_body25

after_for27.loopexit.unr-lcssa.loopexit:          ; preds = %for_loop_body25
  br label %after_for27.loopexit.unr-lcssa

after_for27.loopexit.unr-lcssa:                   ; preds = %after_for27.loopexit.unr-lcssa.loopexit, %for_loop_body25.lr.ph
  %.lcssa.ph = phi float [ poison, %for_loop_body25.lr.ph ], [ %153, %after_for27.loopexit.unr-lcssa.loopexit ]
  %.030.unr = phi i32 [ 0, %for_loop_body25.lr.ph ], [ %154, %after_for27.loopexit.unr-lcssa.loopexit ]
  %.01729.unr = phi float [ 0.000000e+00, %for_loop_body25.lr.ph ], [ %153, %after_for27.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for27, label %for_loop_body25.epil

for_loop_body25.epil:                             ; preds = %after_for27.loopexit.unr-lcssa
  %155 = udiv i32 %.030.unr, %115
  %.recomposed37 = urem i32 %.030.unr, %115
  %156 = add i32 %155, %53
  %157 = add i32 %.recomposed37, %54
  %158 = mul i32 %119, %156
  %159 = add i32 %157, %158
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %118, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = mul i32 %121, %155
  %164 = add i32 %163, %.recomposed37
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %120, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = fmul reassoc ninf nsz float %167, %162
  %169 = fadd reassoc ninf nsz float %168, %.01729.unr
  br label %after_for27

after_for27:                                      ; preds = %for_loop_body25.epil, %after_for27.loopexit.unr-lcssa, %after_if24
  %.017.lcssa = phi float [ 0.000000e+00, %after_if24 ], [ %.lcssa.ph, %after_for27.loopexit.unr-lcssa ], [ %169, %for_loop_body25.epil ]
  %170 = fmul reassoc ninf nsz float %.222, %23
  %171 = fdiv reassoc ninf nsz float %170, %25
  %172 = fsub reassoc ninf nsz float %.017.lcssa, %171
  %173 = fmul reassoc ninf nsz float %.222, %.222
  %174 = fdiv reassoc ninf nsz float %173, %25
  %175 = fsub reassoc ninf nsz float %.2, %174
  %176 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %175, float 0.000000e+00)
  %177 = fmul reassoc ninf nsz float %176, %27
  %178 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %177, float 0x3D71979980000000)
  %179 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %178)
  %180 = fdiv reassoc ninf nsz float %172, %179
  %181 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %180, float -1.000000e+00)
  %182 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %181, float 1.000000e+00)
  %183 = load ptr, ptr %37, align 8
  %184 = load i32, ptr %38, align 4
  %185 = mul i32 %184, %50
  %186 = add i32 %185, %52
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, ptr %183, i64 %187
  store float %182, ptr %188, align 4
  %189 = add nsw i32 %.01831, 1
  %exitcond32.not = icmp eq i32 %189, %18
  br i1 %exitcond32.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
