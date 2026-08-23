; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_demosaice_fused_kernel_c706_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 76
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 72
  %4 = load float, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32
  store float %4, ptr %9, align 4
  %10 = fsub reassoc ninf nsz float %2, %4
  %11 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %10, float 1.000000e+00)
  %12 = fdiv reassoc ninf nsz float 1.000000e+00, %11
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 36
  store float %12, ptr %16, align 4
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 88
  %19 = load i32, ptr %18, align 4
  %20 = load ptr, ptr %5, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 8
  store i32 %19, ptr %23, align 4
  %24 = load ptr, ptr %context, align 8
  %25 = icmp ult i32 %19, 3
  %switch.idx.cast = zext i32 %19 to i64
  %switch.idx.mult = shl nuw nsw i64 %switch.idx.cast, 2
  %switch.offset = add nuw nsw i64 %switch.idx.mult, 56
  %.sink = select i1 %25, i64 %switch.offset, i64 68
  %26 = getelementptr i8, ptr %24, i64 %.sink
  %.022 = load float, ptr %26, align 4
  %27 = load ptr, ptr %5, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 40
  store float %.022, ptr %30, align 4
  %31 = load ptr, ptr %context, align 8
  %32 = getelementptr i8, ptr %31, i64 92
  %33 = load i32, ptr %32, align 4
  %34 = load ptr, ptr %5, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 12
  store i32 %33, ptr %37, align 4
  %38 = icmp ult i32 %33, 3
  %switch.idx.cast41 = zext i32 %33 to i64
  %switch.idx.mult42 = shl nuw nsw i64 %switch.idx.cast41, 2
  %switch.offset43 = add nuw nsw i64 %switch.idx.mult42, 56
  %.sink35 = select i1 %38, i64 %switch.offset43, i64 68
  %39 = load ptr, ptr %context, align 8
  %40 = getelementptr i8, ptr %39, i64 %.sink35
  %.019 = load float, ptr %40, align 4
  %41 = load ptr, ptr %5, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 44
  store float %.019, ptr %44, align 4
  %45 = load ptr, ptr %context, align 8
  %46 = getelementptr i8, ptr %45, i64 96
  %47 = load i32, ptr %46, align 4
  %48 = load ptr, ptr %5, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 32872
  %50 = load ptr, ptr %49, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 16
  store i32 %47, ptr %51, align 4
  %52 = icmp ult i32 %47, 3
  %switch.idx.cast45 = zext i32 %47 to i64
  %switch.idx.mult46 = shl nuw nsw i64 %switch.idx.cast45, 2
  %switch.offset47 = add nuw nsw i64 %switch.idx.mult46, 56
  %.sink37 = select i1 %52, i64 %switch.offset47, i64 68
  %53 = load ptr, ptr %context, align 8
  %54 = getelementptr i8, ptr %53, i64 %.sink37
  %.016 = load float, ptr %54, align 4
  %55 = load ptr, ptr %5, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 32872
  %57 = load ptr, ptr %56, align 8
  %58 = getelementptr inbounds nuw i8, ptr %57, i64 48
  store float %.016, ptr %58, align 4
  %59 = load ptr, ptr %context, align 8
  %60 = getelementptr i8, ptr %59, i64 100
  %61 = load i32, ptr %60, align 4
  %62 = load ptr, ptr %5, align 8
  %63 = getelementptr inbounds nuw i8, ptr %62, i64 32872
  %64 = load ptr, ptr %63, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 20
  store i32 %61, ptr %65, align 4
  %66 = icmp ult i32 %61, 3
  %switch.idx.cast49 = zext i32 %61 to i64
  %switch.idx.mult50 = shl nuw nsw i64 %switch.idx.cast49, 2
  %switch.offset51 = add nuw nsw i64 %switch.idx.mult50, 56
  %.sink39 = select i1 %66, i64 %switch.offset51, i64 68
  %67 = load ptr, ptr %context, align 8
  %68 = getelementptr i8, ptr %67, i64 %.sink39
  %.013 = load float, ptr %68, align 4
  %69 = load ptr, ptr %5, align 8
  %70 = getelementptr inbounds nuw i8, ptr %69, i64 32872
  %71 = load ptr, ptr %70, align 8
  %72 = getelementptr inbounds nuw i8, ptr %71, i64 52
  store float %.013, ptr %72, align 4
  %73 = load ptr, ptr %context, align 8
  %74 = getelementptr i8, ptr %73, i64 80
  %75 = load i32, ptr %74, align 4
  %76 = load ptr, ptr %5, align 8
  %77 = getelementptr inbounds nuw i8, ptr %76, i64 32872
  %78 = load ptr, ptr %77, align 8
  %79 = getelementptr inbounds nuw i8, ptr %78, i64 24
  store i32 %75, ptr %79, align 4
  %80 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %81 = load ptr, ptr %context, align 8
  %82 = getelementptr i8, ptr %81, i64 84
  %83 = load i32, ptr %82, align 4
  %84 = load ptr, ptr %5, align 8
  %85 = getelementptr inbounds nuw i8, ptr %84, i64 32872
  %86 = load ptr, ptr %85, align 8
  %87 = getelementptr inbounds nuw i8, ptr %86, i64 28
  store i32 %83, ptr %87, align 4
  %88 = tail call i32 @llvm.smax.i32(i32 %83, i32 0)
  %89 = load ptr, ptr %5, align 8
  %90 = getelementptr inbounds nuw i8, ptr %89, i64 32872
  %91 = load ptr, ptr %90, align 8
  %92 = getelementptr inbounds nuw i8, ptr %91, i64 4
  store i32 %88, ptr %92, align 4
  %93 = mul i32 %88, %80
  %94 = load ptr, ptr %5, align 8
  %95 = getelementptr inbounds nuw i8, ptr %94, i64 32872
  %96 = load ptr, ptr %95, align 8
  store i32 %93, ptr %96, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_bilinear_demosaice_fused_kernel_c706_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 104
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 24
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr i8, ptr %19, i64 20
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %23, i64 4
  %27 = getelementptr i8, ptr %23, i64 8
  %28 = sext i32 %25 to i64
  %29 = getelementptr float, ptr %23, i64 %28
  %30 = add i32 %25, 1
  %31 = sext i32 %30 to i64
  %32 = getelementptr float, ptr %23, i64 %31
  %33 = add i32 %25, 2
  %34 = sext i32 %33 to i64
  %35 = getelementptr float, ptr %23, i64 %34
  %36 = shl i32 %25, 1
  %37 = sext i32 %36 to i64
  %38 = getelementptr float, ptr %23, i64 %37
  %39 = getelementptr i8, ptr %38, i64 4
  %40 = add i32 %36, 2
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, ptr %23, i64 %41
  %43 = icmp eq i32 %21, 1
  %44 = icmp slt i32 %16, %18
  br i1 %44, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %45 = getelementptr i8, ptr %19, i64 8
  %46 = getelementptr i8, ptr %19, i64 4
  %47 = sub i32 1, %16
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if39, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %47, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if39 ]
  %.02845 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %391, %after_if39 ]
  %48 = load ptr, ptr %3, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 32872
  %50 = load ptr, ptr %49, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 4
  %52 = load i32, ptr %51, align 4
  %53 = sdiv i32 %.02845, %52
  %54 = mul i32 %53, %52
  %55 = xor i32 %52, %.02845
  %56 = icmp slt i32 %55, 0
  %57 = icmp ne i32 %.02845, %54
  %58 = and i1 %56, %57
  %.neg29 = sext i1 %58 to i32
  %59 = add i32 %53, %.neg29
  %60 = mul i32 %59, %52
  %61 = mul i32 %52, -1
  %62 = mul i32 %61, %59
  %63 = add i32 %.02845, %62
  %64 = sdiv i32 %59, 2
  %65 = icmp slt i32 %59, 0
  %66 = shl nsw i32 %64, 1
  %67 = icmp ne i32 %66, %59
  %68 = and i1 %65, %67
  %.neg30 = sext i1 %68 to i32
  %69 = add nsw i32 %64, %.neg30
  %70 = shl i32 %69, 1
  %71 = sub i32 %59, %70
  %72 = sdiv i32 %63, 2
  %73 = icmp slt i32 %63, 0
  %74 = shl nsw i32 %72, 1
  %75 = icmp ne i32 %63, %74
  %76 = and i1 %73, %75
  %.neg31 = sext i1 %76 to i32
  %77 = add nsw i32 %72, %.neg31
  %78 = shl i32 %77, 1
  %79 = sub i32 %62, %78
  %80 = add i32 %.02845, %79
  %81 = add i32 %80, -1
  %.not38 = icmp eq i32 %59, %70
  %.not = icmp eq i32 %63, %78
  %spec.select57 = select i1 %.not, i64 8, i64 12
  %spec.select58 = select i1 %.not, i64 16, i64 20
  %.sink = select i1 %.not38, i64 %spec.select57, i64 %spec.select58
  %82 = getelementptr inbounds nuw i8, ptr %50, i64 %.sink
  %.027 = load i32, ptr %82, align 4
  %83 = add i32 %59, -1
  %84 = tail call i32 @llvm.smax.i32(i32 %83, i32 0)
  %85 = getelementptr inbounds nuw i8, ptr %50, i64 24
  %86 = load i32, ptr %85, align 4
  %87 = add i32 %86, -1
  %88 = add i32 %59, 1
  %89 = tail call i32 @llvm.smin.i32(i32 %87, i32 %88)
  %90 = add i32 %63, -1
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %92 = getelementptr inbounds nuw i8, ptr %50, i64 28
  %93 = load i32, ptr %92, align 4
  %94 = add i32 %93, -1
  %95 = add i32 %63, 1
  %96 = tail call i32 @llvm.smin.i32(i32 %94, i32 %95)
  %.not32 = icmp eq i32 %59, 0
  %97 = icmp eq i32 %71, 1
  %spec.select = or i1 %.not32, %97
  %.not33 = icmp eq i32 %59, %87
  %98 = sub i32 1, %71
  %.024 = select i1 %.not33, i32 %71, i32 %98
  %.not35 = icmp ne i32 %.02845, %60
  %99 = icmp ne i32 %81, 0
  %spec.select41 = and i1 %.not35, %99
  %.not36 = icmp eq i32 %63, %94
  %100 = add i32 %60, %78
  %101 = add i32 %lsr.iv, %100
  %.022 = select i1 %.not36, i32 %80, i32 %101
  %102 = load ptr, ptr %45, align 8
  %103 = load i32, ptr %46, align 4
  %104 = mul i32 %103, %59
  %105 = sub i32 %103, %52
  %106 = mul i32 %105, %59
  %107 = add i32 %.02845, %106
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %102, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = getelementptr inbounds nuw i8, ptr %50, i64 32
  %112 = load float, ptr %111, align 4
  %113 = fsub reassoc ninf nsz float %110, %112
  %114 = getelementptr inbounds nuw i8, ptr %50, i64 36
  %115 = load float, ptr %114, align 4
  %116 = fmul reassoc ninf nsz float %113, %115
  %117 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %116, float 0.000000e+00)
  %118 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %117, float 1.000000e+00)
  %119 = mul i32 %103, %84
  %120 = sub i32 %119, %60
  %121 = add i32 %.02845, %120
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %102, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fsub reassoc ninf nsz float %124, %112
  %126 = fmul reassoc ninf nsz float %125, %115
  %127 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %126, float 0.000000e+00)
  %128 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %127, float 1.000000e+00)
  %129 = mul i32 %103, %89
  %130 = sub i32 %129, %60
  %131 = add i32 %.02845, %130
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %102, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = fsub reassoc ninf nsz float %134, %112
  %136 = fmul reassoc ninf nsz float %135, %115
  %137 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %136, float 0.000000e+00)
  %138 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %137, float 1.000000e+00)
  %139 = add i32 %104, %91
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %102, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = fsub reassoc ninf nsz float %142, %112
  %144 = fmul reassoc ninf nsz float %143, %115
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %144, float 0.000000e+00)
  %146 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %145, float 1.000000e+00)
  %147 = add i32 %104, %96
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %102, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fsub reassoc ninf nsz float %150, %112
  %152 = fmul reassoc ninf nsz float %151, %115
  %153 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %152, float 0.000000e+00)
  %154 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %153, float 1.000000e+00)
  %155 = getelementptr inbounds nuw i8, ptr %50, i64 40
  %156 = load float, ptr %155, align 4
  %157 = getelementptr inbounds nuw i8, ptr %50, i64 44
  %158 = load float, ptr %157, align 4
  %159 = select reassoc ninf nsz i1 %.not, float %156, float %158
  %160 = getelementptr inbounds nuw i8, ptr %50, i64 48
  %161 = load float, ptr %160, align 4
  %162 = getelementptr inbounds nuw i8, ptr %50, i64 52
  %163 = load float, ptr %162, align 4
  %164 = select reassoc ninf nsz i1 %.not, float %161, float %163
  %165 = select reassoc ninf nsz i1 %.not38, float %159, float %164
  %166 = fmul reassoc ninf nsz float %165, %118
  %167 = select reassoc ninf nsz i1 %spec.select, float %159, float %164
  %168 = fmul reassoc ninf nsz float %167, %128
  %.not39 = icmp eq i32 %.024, 0
  %169 = select reassoc ninf nsz i1 %.not39, float %159, float %164
  %170 = fmul reassoc ninf nsz float %169, %138
  %171 = select reassoc ninf nsz i1 %spec.select41, float %158, float %156
  %172 = select reassoc ninf nsz i1 %spec.select41, float %163, float %161
  %173 = select reassoc ninf nsz i1 %.not38, float %171, float %172
  %174 = fmul reassoc ninf nsz float %173, %146
  %.not40 = icmp eq i32 %.022, 0
  %175 = select reassoc ninf nsz i1 %.not40, float %156, float %158
  %176 = select reassoc ninf nsz i1 %.not40, float %161, float %163
  %177 = select reassoc ninf nsz i1 %.not38, float %175, float %176
  %178 = fmul reassoc ninf nsz float %177, %154
  switch i32 %.027, label %false_block23 [
    i32 0, label %true_block19
    i32 2, label %true_block22
  ]

after_for.loopexit:                               ; preds = %after_if39
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block19:                                     ; preds = %for_loop_body
  %179 = add i32 %119, %91
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %102, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = fsub reassoc ninf nsz float %182, %112
  %184 = fmul reassoc ninf nsz float %183, %115
  %185 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %184, float 0.000000e+00)
  %186 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %185, float 1.000000e+00)
  %187 = add i32 %119, %96
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, ptr %102, i64 %188
  %190 = load float, ptr %189, align 4
  %191 = fsub reassoc ninf nsz float %190, %112
  %192 = fmul reassoc ninf nsz float %191, %115
  %193 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %192, float 0.000000e+00)
  %194 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %193, float 1.000000e+00)
  %195 = add i32 %129, %91
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %102, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = fsub reassoc ninf nsz float %198, %112
  %200 = fmul reassoc ninf nsz float %199, %115
  %201 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %200, float 0.000000e+00)
  %202 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %201, float 1.000000e+00)
  %203 = add i32 %129, %96
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %102, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = fsub reassoc ninf nsz float %206, %112
  %208 = fmul reassoc ninf nsz float %207, %115
  %209 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %208, float 0.000000e+00)
  %210 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %209, float 1.000000e+00)
  %211 = select reassoc ninf nsz i1 %spec.select, float %171, float %172
  %212 = fmul reassoc ninf nsz float %186, %211
  %213 = select reassoc ninf nsz i1 %spec.select, float %175, float %176
  %214 = fmul reassoc ninf nsz float %194, %213
  %215 = select reassoc ninf nsz i1 %.not39, float %171, float %172
  %216 = fmul reassoc ninf nsz float %202, %215
  %217 = select reassoc ninf nsz i1 %.not39, float %175, float %176
  %218 = fmul reassoc ninf nsz float %210, %217
  %219 = fadd reassoc ninf nsz float %170, %168
  %220 = fadd reassoc ninf nsz float %219, %174
  %221 = fadd reassoc ninf nsz float %220, %178
  %222 = fmul reassoc ninf nsz float %221, 2.500000e-01
  %223 = fadd reassoc ninf nsz float %214, %212
  %224 = fadd reassoc ninf nsz float %223, %216
  %225 = fadd reassoc ninf nsz float %224, %218
  %226 = fmul reassoc ninf nsz float %225, 2.500000e-01
  br label %after_if21

after_if21:                                       ; preds = %false_block23, %true_block22, %true_block19
  %.021 = phi float [ %166, %true_block19 ], [ %300, %true_block22 ], [ %., %false_block23 ]
  %.020 = phi float [ %222, %true_block19 ], [ %296, %true_block22 ], [ %166, %false_block23 ]
  %.019 = phi float [ %226, %true_block19 ], [ %166, %true_block22 ], [ %.46, %false_block23 ]
  %227 = load float, ptr %23, align 4
  %228 = fmul reassoc ninf nsz float %227, %.021
  %229 = load float, ptr %26, align 4
  %230 = fmul reassoc ninf nsz float %229, %.020
  %231 = fadd reassoc ninf nsz float %230, %228
  %232 = load float, ptr %27, align 4
  %233 = fmul reassoc ninf nsz float %232, %.019
  %234 = fadd reassoc ninf nsz float %231, %233
  %235 = load float, ptr %29, align 4
  %236 = fmul reassoc ninf nsz float %235, %.021
  %237 = load float, ptr %32, align 4
  %238 = fmul reassoc ninf nsz float %237, %.020
  %239 = fadd reassoc ninf nsz float %238, %236
  %240 = load float, ptr %35, align 4
  %241 = fmul reassoc ninf nsz float %240, %.019
  %242 = fadd reassoc ninf nsz float %239, %241
  %243 = load float, ptr %38, align 4
  %244 = fmul reassoc ninf nsz float %243, %.021
  %245 = load float, ptr %39, align 4
  %246 = fmul reassoc ninf nsz float %245, %.020
  %247 = fadd reassoc ninf nsz float %246, %244
  %248 = load float, ptr %42, align 4
  %249 = fmul reassoc ninf nsz float %248, %.019
  %250 = fadd reassoc ninf nsz float %247, %249
  %251 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %234, float 0.000000e+00)
  %252 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %251, float 1.000000e+00)
  br i1 %43, label %true_block37, label %false_block38

true_block22:                                     ; preds = %for_loop_body
  %253 = add i32 %119, %91
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, ptr %102, i64 %254
  %256 = load float, ptr %255, align 4
  %257 = fsub reassoc ninf nsz float %256, %112
  %258 = fmul reassoc ninf nsz float %257, %115
  %259 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %258, float 0.000000e+00)
  %260 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %259, float 1.000000e+00)
  %261 = add i32 %119, %96
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %102, i64 %262
  %264 = load float, ptr %263, align 4
  %265 = fsub reassoc ninf nsz float %264, %112
  %266 = fmul reassoc ninf nsz float %265, %115
  %267 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %266, float 0.000000e+00)
  %268 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %267, float 1.000000e+00)
  %269 = add i32 %129, %91
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, ptr %102, i64 %270
  %272 = load float, ptr %271, align 4
  %273 = fsub reassoc ninf nsz float %272, %112
  %274 = fmul reassoc ninf nsz float %273, %115
  %275 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %274, float 0.000000e+00)
  %276 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %275, float 1.000000e+00)
  %277 = add i32 %129, %96
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, ptr %102, i64 %278
  %280 = load float, ptr %279, align 4
  %281 = fsub reassoc ninf nsz float %280, %112
  %282 = fmul reassoc ninf nsz float %281, %115
  %283 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %282, float 0.000000e+00)
  %284 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %283, float 1.000000e+00)
  %285 = select reassoc ninf nsz i1 %spec.select, float %171, float %172
  %286 = fmul reassoc ninf nsz float %260, %285
  %287 = select reassoc ninf nsz i1 %spec.select, float %175, float %176
  %288 = fmul reassoc ninf nsz float %268, %287
  %289 = select reassoc ninf nsz i1 %.not39, float %171, float %172
  %290 = fmul reassoc ninf nsz float %276, %289
  %291 = select reassoc ninf nsz i1 %.not39, float %175, float %176
  %292 = fmul reassoc ninf nsz float %284, %291
  %293 = fadd reassoc ninf nsz float %170, %168
  %294 = fadd reassoc ninf nsz float %293, %174
  %295 = fadd reassoc ninf nsz float %294, %178
  %296 = fmul reassoc ninf nsz float %295, 2.500000e-01
  %297 = fadd reassoc ninf nsz float %288, %286
  %298 = fadd reassoc ninf nsz float %297, %290
  %299 = fadd reassoc ninf nsz float %298, %292
  %300 = fmul reassoc ninf nsz float %299, 2.500000e-01
  br label %after_if21

false_block23:                                    ; preds = %for_loop_body
  %spec.select43.v = select i1 %spec.select41, i64 12, i64 8
  %spec.select44.v = select i1 %spec.select41, i64 20, i64 16
  %.017.in.v = select i1 %.not38, i64 %spec.select43.v, i64 %spec.select44.v
  %.017.in = getelementptr inbounds nuw i8, ptr %50, i64 %.017.in.v
  %.017 = load i32, ptr %.017.in, align 4
  %301 = icmp eq i32 %.017, 0
  %302 = fadd reassoc ninf nsz float %174, %178
  %303 = fmul reassoc ninf nsz float %302, 5.000000e-01
  %304 = fadd reassoc ninf nsz float %168, %170
  %305 = fmul reassoc ninf nsz float %304, 5.000000e-01
  %. = select i1 %301, float %303, float %305
  %.46 = select i1 %301, float %305, float %303
  br label %after_if21

true_block37:                                     ; preds = %after_if21
  %306 = load ptr, ptr %0, align 8
  %307 = getelementptr i8, ptr %306, i64 48
  %308 = load ptr, ptr %307, align 8
  %309 = getelementptr i8, ptr %306, i64 36
  %310 = load i32, ptr %309, align 4
  %311 = getelementptr i8, ptr %306, i64 40
  %312 = load i32, ptr %311, align 4
  %313 = sub i32 %310, %52
  %314 = mul i32 %313, %59
  %315 = add i32 %.02845, %314
  %316 = mul i32 %315, %312
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %308, i64 %317
  store float %252, ptr %318, align 4
  %319 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %242, float 0.000000e+00)
  %320 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %319, float 1.000000e+00)
  %321 = load ptr, ptr %307, align 8
  %322 = load i32, ptr %309, align 4
  %323 = load i32, ptr %311, align 4
  %324 = sub i32 %322, %52
  %325 = mul i32 %324, %59
  %326 = add i32 %.02845, %325
  %327 = mul i32 %326, %323
  %328 = add i32 %327, 1
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %321, i64 %329
  store float %320, ptr %330, align 4
  %331 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %250, float 0.000000e+00)
  %332 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %331, float 1.000000e+00)
  br label %after_if39

false_block38:                                    ; preds = %after_if21
  %333 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %252)
  %334 = fmul reassoc ninf nsz float %333, 0x3FD3A00620000000
  %335 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %334
  %336 = fmul reassoc ninf nsz float %335, %333
  %337 = fadd reassoc ninf nsz float %336, 0xBFE9435AA0000000
  %338 = fmul reassoc ninf nsz float %337, %333
  %339 = fadd reassoc ninf nsz float %338, 0x3FF4E33660000000
  %340 = fmul reassoc ninf nsz float %339, %333
  %341 = load ptr, ptr %0, align 8
  %342 = getelementptr i8, ptr %341, i64 48
  %343 = load ptr, ptr %342, align 8
  %344 = getelementptr i8, ptr %341, i64 36
  %345 = load i32, ptr %344, align 4
  %346 = getelementptr i8, ptr %341, i64 40
  %347 = load i32, ptr %346, align 4
  %348 = sub i32 %345, %52
  %349 = mul i32 %348, %59
  %350 = add i32 %.02845, %349
  %351 = mul i32 %350, %347
  %352 = sext i32 %351 to i64
  %353 = getelementptr float, ptr %343, i64 %352
  store float %340, ptr %353, align 4
  %354 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %242, float 0.000000e+00)
  %355 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %354, float 1.000000e+00)
  %356 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %355)
  %357 = fmul reassoc ninf nsz float %356, 0x3FD3A00620000000
  %358 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %357
  %359 = fmul reassoc ninf nsz float %358, %356
  %360 = fadd reassoc ninf nsz float %359, 0xBFE9435AA0000000
  %361 = fmul reassoc ninf nsz float %360, %356
  %362 = fadd reassoc ninf nsz float %361, 0x3FF4E33660000000
  %363 = fmul reassoc ninf nsz float %362, %356
  %364 = load ptr, ptr %342, align 8
  %365 = load i32, ptr %344, align 4
  %366 = load i32, ptr %346, align 4
  %367 = sub i32 %365, %52
  %368 = mul i32 %367, %59
  %369 = add i32 %.02845, %368
  %370 = mul i32 %369, %366
  %371 = add i32 %370, 1
  %372 = sext i32 %371 to i64
  %373 = getelementptr float, ptr %364, i64 %372
  store float %363, ptr %373, align 4
  %374 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %250, float 0.000000e+00)
  %375 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %374, float 1.000000e+00)
  %376 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %375)
  %377 = fmul reassoc ninf nsz float %376, 0x3FD3A00620000000
  %378 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %377
  %379 = fmul reassoc ninf nsz float %378, %376
  %380 = fadd reassoc ninf nsz float %379, 0xBFE9435AA0000000
  %381 = fmul reassoc ninf nsz float %380, %376
  %382 = fadd reassoc ninf nsz float %381, 0x3FF4E33660000000
  %383 = fmul reassoc ninf nsz float %382, %376
  br label %after_if39

after_if39:                                       ; preds = %false_block38, %true_block37
  %.sink56.in = phi ptr [ %344, %false_block38 ], [ %309, %true_block37 ]
  %.sink54.in = phi ptr [ %346, %false_block38 ], [ %311, %true_block37 ]
  %.sink49.in = phi ptr [ %342, %false_block38 ], [ %307, %true_block37 ]
  %.sink47 = phi float [ %383, %false_block38 ], [ %332, %true_block37 ]
  %.sink49 = load ptr, ptr %.sink49.in, align 8
  %.sink54 = load i32, ptr %.sink54.in, align 4
  %.sink56 = load i32, ptr %.sink56.in, align 4
  %384 = sub i32 %.sink56, %52
  %385 = mul i32 %384, %59
  %386 = add i32 %.02845, %385
  %387 = mul i32 %386, %.sink54
  %388 = add i32 %387, 2
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %.sink49, i64 %389
  store float %.sink47, ptr %390, align 4
  %391 = add nsw i32 %.02845, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %18, %391
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #1

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
