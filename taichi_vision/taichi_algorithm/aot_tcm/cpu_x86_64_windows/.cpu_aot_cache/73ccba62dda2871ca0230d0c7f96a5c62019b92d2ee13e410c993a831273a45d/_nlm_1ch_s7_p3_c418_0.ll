; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_1ch_s7_p3_c418_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_nlm_1ch_s7_p3_c418_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %25 = add i32 %16, -7
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %25, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.05782 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %319, %after_if47 ]
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
  %134 = tail call noundef float @expf(float noundef %133) #9
  %135 = fsub reassoc ninf nsz float 1.000000e+00, %134
  %136 = add i32 %39, -3
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %45, i32 %137)
  %139 = add i32 %39, -2
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = tail call i32 @llvm.smin.i32(i32 %45, i32 %140)
  %142 = add i32 %39, 2
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %45, i32 %143)
  %145 = add i32 %39, 3
  %146 = tail call i32 @llvm.smax.i32(i32 %145, i32 0)
  %147 = tail call i32 @llvm.smin.i32(i32 %45, i32 %146)
  %broadcast.splatinsert98 = insertelement <8 x i32> poison, i32 %37, i64 0
  %broadcast.splat99 = shufflevector <8 x i32> %broadcast.splatinsert98, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert100 = insertelement <8 x i32> poison, i32 %42, i64 0
  %broadcast.splat101 = shufflevector <8 x i32> %broadcast.splatinsert100, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert106 = insertelement <8 x i32> poison, i32 %138, i64 0
  %broadcast.splat107 = shufflevector <8 x i32> %broadcast.splatinsert106, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert111 = insertelement <8 x i32> poison, i32 %141, i64 0
  %broadcast.splat112 = shufflevector <8 x i32> %broadcast.splatinsert111, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert117 = insertelement <8 x i32> poison, i32 %50, i64 0
  %broadcast.splat118 = shufflevector <8 x i32> %broadcast.splatinsert117, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert123 = insertelement <8 x i32> poison, i32 %61, i64 0
  %broadcast.splat124 = shufflevector <8 x i32> %broadcast.splatinsert123, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert129 = insertelement <8 x i32> poison, i32 %71, i64 0
  %broadcast.splat130 = shufflevector <8 x i32> %broadcast.splatinsert129, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert135 = insertelement <8 x i32> poison, i32 %144, i64 0
  %broadcast.splat136 = shufflevector <8 x i32> %broadcast.splatinsert135, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert141 = insertelement <8 x i32> poison, i32 %147, i64 0
  %broadcast.splat142 = shufflevector <8 x i32> %broadcast.splatinsert141, <8 x i32> poison, <8 x i32> zeroinitializer
  %148 = add <8 x i32> %broadcast.splat99, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %149 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %148, <8 x i32> zeroinitializer)
  %150 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat101, <8 x i32> %149)
  %151 = sub i32 %lsr.iv, %38
  %152 = add i32 %31, -7
  %153 = add i32 %152, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv149 = phi i32 [ %153, %for_loop_body ], [ %lsr.iv.next150, %for_loop_inc10 ]
  %.04381 = phi i32 [ -7, %for_loop_body ], [ %156, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %154 = add i32 %.04381, %37
  %155 = icmp slt i32 %154, 0
  br i1 %155, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %156 = add nsw i32 %.04381, 1
  %lsr.iv.next150 = add i32 %lsr.iv149, 1
  %exitcond86.not = icmp eq i32 %156, 8
  br i1 %exitcond86.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %157 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %157, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %158 = load i32, ptr %40, align 4
  %.not64 = icmp slt i32 %154, %158
  br i1 %.not64, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %broadcast.splatinsert102 = insertelement <8 x i32> poison, i32 %154, i64 0
  %broadcast.splat103 = shufflevector <8 x i32> %broadcast.splatinsert102, <8 x i32> poison, <8 x i32> zeroinitializer
  %159 = add <8 x i32> %broadcast.splat103, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %160 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %159, <8 x i32> zeroinitializer)
  %161 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat101, <8 x i32> %160)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv147 = phi i32 [ %151, %for_loop_body16.preheader ], [ %lsr.iv.next148, %for_loop_inc17 ]
  %.04178 = phi i32 [ %165, %for_loop_inc17 ], [ -7, %for_loop_body16.preheader ]
  %.377 = phi float [ %.246, %for_loop_inc17 ], [ %.14580, %for_loop_body16.preheader ]
  %.35076 = phi float [ %.249, %for_loop_inc17 ], [ %.14879, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv147, i32 3)
  %162 = sub i32 %151, %umin
  %163 = add i32 %39, %.04178
  %164 = icmp slt i32 %163, 0
  br i1 %164, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %266, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %275, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %165 = add nsw i32 %.04178, 1
  %lsr.iv.next148 = add i32 %lsr.iv147, 1
  %exitcond85.not = icmp eq i32 %165, 8
  br i1 %exitcond85.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %166 = load i32, ptr %43, align 4
  %.not65 = icmp slt i32 %163, %166
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %167 = or i32 %.04178, %.04381
  %spec.select.not = icmp eq i32 %167, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %168 = load ptr, ptr %23, align 8
  %169 = add i32 %163, 3
  %170 = tail call i32 @llvm.smax.i32(i32 %169, i32 0)
  %171 = tail call i32 @llvm.smin.i32(i32 %45, i32 %170)
  %172 = add i32 %163, 2
  %173 = tail call i32 @llvm.smax.i32(i32 %172, i32 0)
  %174 = tail call i32 @llvm.smin.i32(i32 %45, i32 %173)
  %175 = add i32 %163, 1
  %176 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %177 = tail call i32 @llvm.smin.i32(i32 %45, i32 %176)
  %178 = tail call i32 @llvm.smin.i32(i32 %45, i32 %163)
  %179 = tail call i32 @llvm.smax.i32(i32 %163, i32 1)
  %180 = add nsw i32 %179, -1
  %181 = tail call i32 @llvm.smin.i32(i32 %45, i32 %180)
  %182 = tail call i32 @llvm.smax.i32(i32 %163, i32 2)
  %183 = add nsw i32 %182, -2
  %184 = tail call i32 @llvm.smin.i32(i32 %45, i32 %183)
  %185 = add i32 %.04178, %162
  %186 = add i32 %185, 7
  %187 = tail call i32 @llvm.smin.i32(i32 %45, i32 %186)
  %188 = load i32, ptr %24, align 4
  %broadcast.splatinsert104 = insertelement <8 x i32> poison, i32 %188, i64 0
  %broadcast.splat105 = shufflevector <8 x i32> %broadcast.splatinsert104, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert108 = insertelement <8 x i32> poison, i32 %187, i64 0
  %broadcast.splat109 = shufflevector <8 x i32> %broadcast.splatinsert108, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert114 = insertelement <8 x i32> poison, i32 %184, i64 0
  %broadcast.splat115 = shufflevector <8 x i32> %broadcast.splatinsert114, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert120 = insertelement <8 x i32> poison, i32 %181, i64 0
  %broadcast.splat121 = shufflevector <8 x i32> %broadcast.splatinsert120, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert126 = insertelement <8 x i32> poison, i32 %178, i64 0
  %broadcast.splat127 = shufflevector <8 x i32> %broadcast.splatinsert126, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert132 = insertelement <8 x i32> poison, i32 %177, i64 0
  %broadcast.splat133 = shufflevector <8 x i32> %broadcast.splatinsert132, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert138 = insertelement <8 x i32> poison, i32 %174, i64 0
  %broadcast.splat139 = shufflevector <8 x i32> %broadcast.splatinsert138, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert144 = insertelement <8 x i32> poison, i32 %171, i64 0
  %broadcast.splat145 = shufflevector <8 x i32> %broadcast.splatinsert144, <8 x i32> poison, <8 x i32> zeroinitializer
  %189 = mul <8 x i32> %broadcast.splat105, %150
  %190 = add <8 x i32> %189, %broadcast.splat142
  %191 = sext <8 x i32> %190 to <8 x i64>
  %192 = getelementptr float, ptr %168, <8 x i64> %191
  %wide.masked.gather143 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %192, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %193 = mul <8 x i32> %broadcast.splat105, %161
  %194 = add <8 x i32> %193, %broadcast.splat145
  %195 = sext <8 x i32> %194 to <8 x i64>
  %196 = getelementptr float, ptr %168, <8 x i64> %195
  %wide.masked.gather146 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %196, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %197 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather143, %wide.masked.gather146
  %198 = fmul reassoc ninf nsz <8 x float> %197, %197
  %199 = add <8 x i32> %189, %broadcast.splat136
  %200 = sext <8 x i32> %199 to <8 x i64>
  %201 = getelementptr float, ptr %168, <8 x i64> %200
  %wide.masked.gather137 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %201, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %202 = add <8 x i32> %193, %broadcast.splat139
  %203 = sext <8 x i32> %202 to <8 x i64>
  %204 = getelementptr float, ptr %168, <8 x i64> %203
  %wide.masked.gather140 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %204, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %205 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather137, %wide.masked.gather140
  %206 = fmul reassoc ninf nsz <8 x float> %205, %205
  %207 = add <8 x i32> %189, %broadcast.splat130
  %208 = sext <8 x i32> %207 to <8 x i64>
  %209 = getelementptr float, ptr %168, <8 x i64> %208
  %wide.masked.gather131 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %209, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %210 = add <8 x i32> %193, %broadcast.splat133
  %211 = sext <8 x i32> %210 to <8 x i64>
  %212 = getelementptr float, ptr %168, <8 x i64> %211
  %wide.masked.gather134 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %212, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %213 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather131, %wide.masked.gather134
  %214 = fmul reassoc ninf nsz <8 x float> %213, %213
  %215 = add <8 x i32> %189, %broadcast.splat124
  %216 = sext <8 x i32> %215 to <8 x i64>
  %217 = getelementptr float, ptr %168, <8 x i64> %216
  %wide.masked.gather125 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %217, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %218 = add <8 x i32> %193, %broadcast.splat127
  %219 = sext <8 x i32> %218 to <8 x i64>
  %220 = getelementptr float, ptr %168, <8 x i64> %219
  %wide.masked.gather128 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %220, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %221 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather125, %wide.masked.gather128
  %222 = fmul reassoc ninf nsz <8 x float> %221, %221
  %223 = add <8 x i32> %189, %broadcast.splat118
  %224 = sext <8 x i32> %223 to <8 x i64>
  %225 = getelementptr float, ptr %168, <8 x i64> %224
  %wide.masked.gather119 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %225, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %226 = add <8 x i32> %193, %broadcast.splat121
  %227 = sext <8 x i32> %226 to <8 x i64>
  %228 = getelementptr float, ptr %168, <8 x i64> %227
  %wide.masked.gather122 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %228, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %229 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather119, %wide.masked.gather122
  %230 = fmul reassoc ninf nsz <8 x float> %229, %229
  %231 = add <8 x i32> %189, %broadcast.splat112
  %232 = sext <8 x i32> %231 to <8 x i64>
  %233 = getelementptr float, ptr %168, <8 x i64> %232
  %wide.masked.gather113 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %233, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %234 = add <8 x i32> %193, %broadcast.splat115
  %235 = sext <8 x i32> %234 to <8 x i64>
  %236 = getelementptr float, ptr %168, <8 x i64> %235
  %wide.masked.gather116 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %236, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %237 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather113, %wide.masked.gather116
  %238 = fmul reassoc ninf nsz <8 x float> %237, %237
  %239 = add <8 x i32> %189, %broadcast.splat107
  %240 = sext <8 x i32> %239 to <8 x i64>
  %241 = getelementptr float, ptr %168, <8 x i64> %240
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %241, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %242 = add <8 x i32> %193, %broadcast.splat109
  %243 = sext <8 x i32> %242 to <8 x i64>
  %244 = getelementptr float, ptr %168, <8 x i64> %243
  %wide.masked.gather110 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %244, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %245 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather110
  %246 = fmul reassoc ninf nsz <8 x float> %245, %245
  %247 = fadd reassoc ninf nsz <8 x float> %238, %246
  %248 = fadd reassoc ninf nsz <8 x float> %230, %247
  %249 = fadd reassoc ninf nsz <8 x float> %222, %248
  %250 = fadd reassoc ninf nsz <8 x float> %214, %249
  %251 = fadd reassoc ninf nsz <8 x float> %206, %250
  %252 = fadd reassoc ninf nsz <8 x float> %198, %251
  %253 = insertelement <8 x float> %252, float 0.000000e+00, i64 7
  %254 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %253)
  %255 = fmul reassoc ninf nsz float %254, 0x3F94E5E0A0000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %255, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %256 = load ptr, ptr %3, align 8
  %257 = getelementptr inbounds nuw i8, ptr %256, i64 32872
  %258 = load ptr, ptr %257, align 8
  %259 = getelementptr inbounds nuw i8, ptr %258, i64 16
  %260 = load float, ptr %259, align 4
  %261 = fcmp reassoc ninf nsz ugt float %.039, %260
  br i1 %261, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %262 = getelementptr inbounds nuw i8, ptr %258, i64 20
  %263 = load float, ptr %262, align 4
  %264 = fmul reassoc ninf nsz float %263, %neg44
  %265 = tail call noundef float @expf(float noundef %264) #9
  %266 = fadd reassoc ninf nsz float %265, %.35076
  %267 = load ptr, ptr %23, align 8
  %268 = load i32, ptr %24, align 4
  %269 = mul i32 %lsr.iv149, %268
  %270 = add i32 %163, %269
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %267, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = fmul reassoc ninf nsz float %273, %265
  %275 = fadd reassoc ninf nsz float %274, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %276 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %135, float 0x3FE6666660000000)
  %277 = fdiv reassoc ninf nsz float %.044, %.047
  %278 = load ptr, ptr %23, align 8
  %279 = load i32, ptr %24, align 4
  %280 = mul i32 %279, %37
  %281 = add i32 %280, %39
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, ptr %278, i64 %282
  %284 = load float, ptr %283, align 4
  %285 = fsub reassoc ninf nsz float %284, %277
  %286 = tail call noundef float @llvm.fabs.f32(float %285)
  %287 = load ptr, ptr %3, align 8
  %288 = getelementptr inbounds nuw i8, ptr %287, i64 32872
  %289 = load ptr, ptr %288, align 8
  %290 = getelementptr inbounds nuw i8, ptr %289, i64 24
  %291 = load float, ptr %290, align 4
  %292 = fsub reassoc ninf nsz float %286, %291
  %293 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %292, float 0.000000e+00)
  %294 = fcmp reassoc ninf nsz oge float %285, 0.000000e+00
  %295 = uitofp i1 %294 to float
  %296 = fcmp reassoc ninf nsz ole float %285, 0.000000e+00
  %297 = uitofp i1 %296 to float
  %298 = fsub reassoc ninf nsz float %295, %297
  %299 = fmul reassoc ninf nsz float %276, %21
  %300 = fmul reassoc ninf nsz float %299, %298
  %301 = fmul reassoc ninf nsz float %300, %293
  %302 = fadd reassoc ninf nsz float %301, %277
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %303 = load ptr, ptr %23, align 8
  %304 = load i32, ptr %24, align 4
  %305 = mul i32 %304, %37
  %306 = add i32 %305, %39
  %307 = sext i32 %306 to i64
  %308 = getelementptr float, ptr %303, i64 %307
  %309 = load float, ptr %308, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %309, %false_block46 ], [ %302, %true_block45 ]
  %310 = load ptr, ptr %0, align 8
  %311 = getelementptr i8, ptr %310, i64 24
  %312 = load ptr, ptr %311, align 8
  %313 = getelementptr i8, ptr %310, i64 20
  %314 = load i32, ptr %313, align 4
  %315 = mul i32 %314, %37
  %316 = add i32 %315, %39
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %312, i64 %317
  store float %.sink, ptr %318, align 4
  %319 = add nsw i32 %.05782, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond87.not = icmp eq i32 %319, %18
  br i1 %exitcond87.not, label %after_for.loopexit, label %for_loop_body
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #9
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
declare i32 @llvm.usub.sat.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #6

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
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #9 = { nounwind }

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
