; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.18 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @compose_spatial_weights_rgb_mean_kernel_c98_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = icmp sgt i32 %2, 1
  %9 = load ptr, ptr %3, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 32872
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 28
  store i1 %8, ptr %12, align 1
  %13 = add nsw i32 %2, -1
  %14 = sitofp i32 %13 to float
  %15 = fdiv reassoc ninf nsz float 1.000000e+00, %14
  %.02 = select i1 %8, float %15, float 0.000000e+00
  %16 = load ptr, ptr %3, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32
  store float %.02, ptr %19, align 4
  %20 = load ptr, ptr %context, align 8
  %21 = getelementptr i8, ptr %20, i64 76
  %22 = load i32, ptr %21, align 4
  %23 = load ptr, ptr %3, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 32872
  %25 = load ptr, ptr %24, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 16
  store i32 %22, ptr %26, align 4
  %27 = icmp sgt i32 %22, 1
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 40
  store i1 %27, ptr %31, align 1
  %32 = add nsw i32 %22, -1
  %33 = sitofp i32 %32 to float
  %34 = fdiv reassoc ninf nsz float 1.000000e+00, %33
  %.0 = select i1 %27, float %34, float 0.000000e+00
  %35 = load ptr, ptr %3, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 44
  store float %.0, ptr %38, align 4
  %39 = load ptr, ptr %context, align 8
  %40 = getelementptr i8, ptr %39, i64 24
  %41 = load i32, ptr %40, align 4
  %42 = load ptr, ptr %3, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 12
  store i32 %41, ptr %45, align 4
  %46 = load ptr, ptr %context, align 8
  %47 = getelementptr i8, ptr %46, i64 40
  %48 = load i32, ptr %47, align 4
  %49 = load ptr, ptr %3, align 8
  %50 = getelementptr inbounds nuw i8, ptr %49, i64 32872
  %51 = load ptr, ptr %50, align 8
  %52 = getelementptr inbounds nuw i8, ptr %51, i64 20
  store i32 %48, ptr %52, align 4
  %53 = load ptr, ptr %context, align 8
  %54 = getelementptr i8, ptr %53, i64 88
  %55 = load i32, ptr %54, align 4
  %56 = load ptr, ptr %3, align 8
  %57 = getelementptr inbounds nuw i8, ptr %56, i64 32872
  %58 = load ptr, ptr %57, align 8
  %59 = getelementptr inbounds nuw i8, ptr %58, i64 24
  store i32 %55, ptr %59, align 4
  %60 = tail call i32 @llvm.smax.i32(i32 %55, i32 0)
  %61 = load ptr, ptr %context, align 8
  %62 = getelementptr i8, ptr %61, i64 92
  %63 = load i32, ptr %62, align 4
  %64 = load ptr, ptr %3, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 32872
  %66 = load ptr, ptr %65, align 8
  %67 = getelementptr inbounds nuw i8, ptr %66, i64 36
  store i32 %63, ptr %67, align 4
  %68 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %69 = load ptr, ptr %3, align 8
  %70 = getelementptr inbounds nuw i8, ptr %69, i64 32872
  %71 = load ptr, ptr %70, align 8
  %72 = getelementptr inbounds nuw i8, ptr %71, i64 4
  store i32 %68, ptr %72, align 4
  %73 = mul i32 %68, %60
  %74 = load ptr, ptr %3, align 8
  %75 = getelementptr inbounds nuw i8, ptr %74, i64 32872
  %76 = load ptr, ptr %75, align 8
  store i32 %73, ptr %76, align 4
  ret void
}

define void @compose_spatial_weights_rgb_mean_kernel_c98_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 80
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 84
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 96
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 100
  %27 = load float, ptr %26, align 4
  %28 = fcmp reassoc ninf nsz one float %25, 1.000000e+00
  %29 = fcmp reassoc ninf nsz ogt float %27, 0.000000e+00
  %30 = icmp slt i32 %16, %18
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = add i32 %21, -1
  %32 = add i32 %23, -1
  %33 = getelementptr i8, ptr %19, i64 32
  %34 = fsub reassoc ninf nsz float 1.000000e+00, %27
  %35 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %34, float 0x3EE4F8B580000000)
  %36 = getelementptr i8, ptr %19, i64 64
  %37 = getelementptr i8, ptr %19, i64 60
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if41, %for_loop_body.lr.ph
  %.04377 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %284, %after_if41 ]
  %38 = load ptr, ptr %3, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 4
  %42 = load i32, ptr %41, align 4
  %43 = sdiv i32 %.04377, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.04377
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %44, %.04377
  %48 = and i1 %46, %47
  %.neg54 = sext i1 %48 to i32
  %49 = add i32 %43, %.neg54
  %50 = mul i32 %49, %42
  %51 = sub i32 %.04377, %50
  %52 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %53 = load i32, ptr %52, align 4
  %reass.sub = sub i32 %49, %53
  %54 = add i32 %reass.sub, 1
  %55 = tail call i32 @llvm.smax.i32(i32 %54, i32 0)
  %56 = add i32 %31, %55
  %57 = sdiv i32 %56, %21
  %58 = mul i32 %57, %21
  %59 = xor i32 %56, %21
  %60 = icmp slt i32 %59, 0
  %61 = icmp ne i32 %58, %56
  %62 = and i1 %61, %60
  %.neg55 = sext i1 %62 to i32
  %63 = add i32 %57, %.neg55
  %64 = getelementptr inbounds nuw i8, ptr %40, i64 12
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = sdiv i32 %49, %21
  %68 = mul i32 %67, %21
  %69 = xor i32 %49, %21
  %70 = icmp slt i32 %69, 0
  %71 = icmp ne i32 %68, %49
  %72 = and i1 %71, %70
  %.neg56 = sext i1 %72 to i32
  %73 = add i32 %67, %.neg56
  %74 = tail call i32 @llvm.smin.i32(i32 %66, i32 %73)
  %75 = getelementptr inbounds nuw i8, ptr %40, i64 16
  %76 = load i32, ptr %75, align 4
  %reass.sub78 = sub i32 %51, %76
  %77 = add i32 %reass.sub78, 1
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = add i32 %32, %78
  %80 = sdiv i32 %79, %23
  %81 = mul i32 %80, %23
  %82 = xor i32 %79, %23
  %83 = icmp slt i32 %82, 0
  %84 = icmp ne i32 %81, %79
  %85 = and i1 %84, %83
  %.neg57 = sext i1 %85 to i32
  %86 = add i32 %80, %.neg57
  %87 = add i32 %74, 1
  %88 = icmp slt i32 %63, %87
  br i1 %88, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %89 = getelementptr inbounds nuw i8, ptr %40, i64 20
  %90 = load i32, ptr %89, align 4
  %91 = add i32 %90, -1
  %92 = sdiv i32 %51, %23
  %93 = icmp ne i32 %.04377, %50
  %94 = xor i32 %51, %23
  %95 = icmp slt i32 %94, 0
  %96 = and i1 %93, %95
  %97 = mul i32 %92, %23
  %98 = icmp ne i32 %97, %51
  %99 = and i1 %96, %98
  %.neg58 = sext i1 %99 to i32
  %100 = add i32 %92, %.neg58
  %101 = tail call i32 @llvm.smin.i32(i32 %91, i32 %100)
  %102 = add i32 %101, 1
  %103 = icmp slt i32 %86, %102
  %.fr = freeze i1 %103
  br i1 %.fr, label %for_loop_body1.us.preheader, label %for_loop_body1.preheader

for_loop_body1.preheader:                         ; preds = %for_loop_body1.lr.ph
  %104 = sext i32 %63 to i64
  %wide.trip.count = sext i32 %87 to i64
  %105 = sub nsw i64 %wide.trip.count, %104
  %xtraiter = and i64 %105, 1
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_body1.prol.loopexit, label %for_loop_body1.prol

for_loop_body1.prol:                              ; preds = %for_loop_body1.preheader
  %106 = load ptr, ptr %33, align 8
  %107 = getelementptr i32, ptr %106, i64 %104
  %108 = load i32, ptr %107, align 4
  %109 = sub i32 %49, %108
  %110 = icmp sgt i32 %109, -1
  br i1 %110, label %true_block.prol, label %after_if7.prol

true_block.prol:                                  ; preds = %for_loop_body1.prol
  %111 = getelementptr inbounds nuw i8, ptr %40, i64 24
  %112 = load i32, ptr %111, align 4
  %113 = sub i32 %112, %108
  %114 = tail call i32 @llvm.smin.i32(i32 %53, i32 %113)
  %115 = icmp slt i32 %109, %114
  br i1 %115, label %true_block5.prol, label %after_if7.prol

true_block5.prol:                                 ; preds = %true_block.prol
  %116 = getelementptr inbounds nuw i8, ptr %40, i64 28
  %117 = load i1, ptr %116, align 1
  br i1 %117, label %true_block8.prol, label %after_if7.prol

true_block8.prol:                                 ; preds = %true_block5.prol
  %118 = uitofp nneg i32 %109 to float
  %119 = fmul reassoc ninf nsz float %118, 0x401921FB60000000
  %120 = getelementptr inbounds nuw i8, ptr %40, i64 32
  %121 = load float, ptr %120, align 4
  %122 = fmul reassoc ninf nsz float %119, %121
  %123 = tail call noundef float @cosf(float noundef %122) #8
  br label %after_if7.prol

after_if7.prol:                                   ; preds = %true_block8.prol, %true_block5.prol, %true_block.prol, %for_loop_body1.prol
  %indvars.iv.next.prol = add nsw i64 %104, 1
  br label %for_loop_body1.prol.loopexit

for_loop_body1.prol.loopexit:                     ; preds = %after_if7.prol, %for_loop_body1.preheader
  %indvars.iv.unr = phi i64 [ %104, %for_loop_body1.preheader ], [ %indvars.iv.next.prol, %after_if7.prol ]
  %124 = add nsw i64 %wide.trip.count, -1
  %125 = icmp eq i64 %124, %104
  br i1 %125, label %after_for3, label %for_loop_body1.preheader93

for_loop_body1.preheader93:                       ; preds = %for_loop_body1.prol.loopexit
  br label %for_loop_body1

for_loop_body1.us.preheader:                      ; preds = %for_loop_body1.lr.ph
  %126 = sext i32 %86 to i64
  %127 = sext i32 %102 to i64
  %128 = sext i32 %63 to i64
  %wide.trip.count87 = sext i32 %87 to i64
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %after_if7.us, %for_loop_body1.us.preheader
  %indvars.iv84 = phi i64 [ %128, %for_loop_body1.us.preheader ], [ %indvars.iv.next85, %after_if7.us ]
  %.03069.us = phi float [ 0.000000e+00, %for_loop_body1.us.preheader ], [ %.1.us, %after_if7.us ]
  %.03168.us = phi float [ 0.000000e+00, %for_loop_body1.us.preheader ], [ %.132.us, %after_if7.us ]
  %.03767.us = phi float [ 0.000000e+00, %for_loop_body1.us.preheader ], [ %.138.us, %after_if7.us ]
  %lsr101 = trunc i64 %indvars.iv84 to i32
  %129 = load ptr, ptr %33, align 8
  %130 = getelementptr i32, ptr %129, i64 %indvars.iv84
  %131 = load i32, ptr %130, align 4
  %132 = sub i32 %49, %131
  %133 = icmp sgt i32 %132, -1
  br i1 %133, label %true_block.us, label %after_if7.us

true_block.us:                                    ; preds = %for_loop_body1.us
  %134 = load ptr, ptr %3, align 8
  %135 = getelementptr inbounds nuw i8, ptr %134, i64 32872
  %136 = load ptr, ptr %135, align 8
  %137 = getelementptr inbounds nuw i8, ptr %136, i64 24
  %138 = load i32, ptr %137, align 4
  %139 = sub i32 %138, %131
  %140 = load i32, ptr %52, align 4
  %141 = tail call i32 @llvm.smin.i32(i32 %140, i32 %139)
  %142 = icmp slt i32 %132, %141
  br i1 %142, label %true_block5.us, label %after_if7.us

true_block5.us:                                   ; preds = %true_block.us
  %143 = getelementptr inbounds nuw i8, ptr %136, i64 28
  %144 = load i1, ptr %143, align 1
  br i1 %144, label %true_block8.us, label %after_if10.us

true_block8.us:                                   ; preds = %true_block5.us
  %145 = uitofp nneg i32 %132 to float
  %146 = fmul reassoc ninf nsz float %145, 0x401921FB60000000
  %147 = getelementptr inbounds nuw i8, ptr %136, i64 32
  %148 = load float, ptr %147, align 4
  %149 = fmul reassoc ninf nsz float %146, %148
  %150 = tail call noundef float @cosf(float noundef %149) #8
  %151 = fmul reassoc ninf nsz float %150, 5.000000e-01
  %152 = fsub reassoc ninf nsz float 5.000000e-01, %151
  br label %after_if10.us

after_if10.us:                                    ; preds = %true_block8.us, %true_block5.us
  %.027.us = phi float [ %152, %true_block8.us ], [ 1.000000e+00, %true_block5.us ]
  %153 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.027.us, float 0x3F1A36E2E0000000)
  %154 = load ptr, ptr %0, align 8
  %155 = getelementptr i8, ptr %154, i64 48
  br label %for_loop_body11.us

after_if7.us.loopexit:                            ; preds = %after_if20.us
  br label %after_if7.us

after_if7.us:                                     ; preds = %after_if7.us.loopexit, %true_block.us, %for_loop_body1.us
  %.138.us = phi float [ %.03767.us, %true_block.us ], [ %.03767.us, %for_loop_body1.us ], [ %.340.us, %after_if7.us.loopexit ]
  %.132.us = phi float [ %.03168.us, %true_block.us ], [ %.03168.us, %for_loop_body1.us ], [ %.334.us, %after_if7.us.loopexit ]
  %.1.us = phi float [ %.03069.us, %true_block.us ], [ %.03069.us, %for_loop_body1.us ], [ %.3.us, %after_if7.us.loopexit ]
  %indvars.iv.next85 = add nsw i64 %indvars.iv84, 1
  %exitcond88.not = icmp eq i64 %indvars.iv.next85, %wide.trip.count87
  br i1 %exitcond88.not, label %after_for3.loopexit, label %for_loop_body1.us

for_loop_body11.us:                               ; preds = %after_if20.us, %after_if10.us
  %156 = phi ptr [ %154, %after_if10.us ], [ %210, %after_if20.us ]
  %indvars.iv81 = phi i64 [ %126, %after_if10.us ], [ %indvars.iv.next82, %after_if20.us ]
  %.263.us = phi float [ %.03069.us, %after_if10.us ], [ %.3.us, %after_if20.us ]
  %.23362.us = phi float [ %.03168.us, %after_if10.us ], [ %.334.us, %after_if20.us ]
  %.23961.us = phi float [ %.03767.us, %after_if10.us ], [ %.340.us, %after_if20.us ]
  %lsr100 = trunc i64 %indvars.iv81 to i32
  %157 = load ptr, ptr %155, align 8
  %158 = shl nsw i64 %indvars.iv81, 2
  %scevgep99 = getelementptr i8, ptr %157, i64 %158
  %159 = load i32, ptr %scevgep99, align 4
  %160 = sub i32 %51, %159
  %161 = icmp sgt i32 %160, -1
  br i1 %161, label %true_block15.us, label %after_if20.us

true_block15.us:                                  ; preds = %for_loop_body11.us
  %162 = load ptr, ptr %3, align 8
  %163 = getelementptr inbounds nuw i8, ptr %162, i64 32872
  %164 = load ptr, ptr %163, align 8
  %165 = getelementptr inbounds nuw i8, ptr %164, i64 36
  %166 = load i32, ptr %165, align 4
  %167 = sub i32 %166, %159
  %168 = load i32, ptr %75, align 4
  %169 = tail call i32 @llvm.smin.i32(i32 %168, i32 %167)
  %170 = icmp slt i32 %160, %169
  br i1 %170, label %true_block18.us, label %after_if20.us

true_block18.us:                                  ; preds = %true_block15.us
  %171 = getelementptr inbounds nuw i8, ptr %164, i64 40
  %172 = load i1, ptr %171, align 1
  br i1 %172, label %true_block21.us, label %after_if23.us

true_block21.us:                                  ; preds = %true_block18.us
  %173 = uitofp nneg i32 %160 to float
  %174 = fmul reassoc ninf nsz float %173, 0x401921FB60000000
  %175 = getelementptr inbounds nuw i8, ptr %164, i64 44
  %176 = load float, ptr %175, align 4
  %177 = fmul reassoc ninf nsz float %174, %176
  %178 = tail call noundef float @cosf(float noundef %177) #8
  %179 = fmul reassoc ninf nsz float %178, 5.000000e-01
  %180 = fsub reassoc ninf nsz float 5.000000e-01, %179
  %.pre = load ptr, ptr %0, align 8
  br label %after_if23.us

after_if23.us:                                    ; preds = %true_block21.us, %true_block18.us
  %181 = phi ptr [ %.pre, %true_block21.us ], [ %156, %true_block18.us ]
  %.0.us = phi float [ %180, %true_block21.us ], [ 1.000000e+00, %true_block18.us ]
  %182 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0.us, float 0x3F1A36E2E0000000)
  %183 = fmul reassoc ninf nsz float %182, %153
  %184 = getelementptr i8, ptr %181, i64 16
  %185 = load ptr, ptr %184, align 8
  %186 = getelementptr i8, ptr %181, i64 4
  %187 = load i32, ptr %186, align 4
  %188 = getelementptr i8, ptr %181, i64 8
  %189 = load i32, ptr %188, align 4
  %190 = mul i32 %lsr101, %187
  %191 = add i32 %lsr100, %190
  %192 = mul i32 %191, %189
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, ptr %185, i64 %193
  %195 = load float, ptr %194, align 4
  %196 = fmul reassoc ninf nsz float %195, %183
  %197 = fadd reassoc ninf nsz float %196, %.23961.us
  %198 = add i32 %192, 1
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, ptr %185, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = fmul reassoc ninf nsz float %201, %183
  %203 = fadd reassoc ninf nsz float %202, %.23362.us
  %204 = add i32 %192, 2
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, ptr %185, i64 %205
  %207 = load float, ptr %206, align 4
  %208 = fmul reassoc ninf nsz float %207, %183
  %209 = fadd reassoc ninf nsz float %208, %.263.us
  br label %after_if20.us

after_if20.us:                                    ; preds = %after_if23.us, %true_block15.us, %for_loop_body11.us
  %210 = phi ptr [ %181, %after_if23.us ], [ %156, %true_block15.us ], [ %156, %for_loop_body11.us ]
  %.340.us = phi float [ %197, %after_if23.us ], [ %.23961.us, %true_block15.us ], [ %.23961.us, %for_loop_body11.us ]
  %.334.us = phi float [ %203, %after_if23.us ], [ %.23362.us, %true_block15.us ], [ %.23362.us, %for_loop_body11.us ]
  %.3.us = phi float [ %209, %after_if23.us ], [ %.263.us, %true_block15.us ], [ %.263.us, %for_loop_body11.us ]
  %indvars.iv.next82 = add nsw i64 %indvars.iv81, 1
  %211 = icmp slt i64 %indvars.iv.next82, %127
  br i1 %211, label %for_loop_body11.us, label %after_if7.us.loopexit

after_for.loopexit:                               ; preds = %after_if41
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if7.1, %for_loop_body1.preheader93
  %indvars.iv = phi i64 [ %indvars.iv.next.1, %after_if7.1 ], [ %indvars.iv.unr, %for_loop_body1.preheader93 ]
  %212 = load ptr, ptr %33, align 8
  %213 = shl i64 %indvars.iv, 2
  %scevgep96 = getelementptr i8, ptr %212, i64 %213
  %214 = load i32, ptr %scevgep96, align 4
  %215 = sub i32 %49, %214
  %216 = icmp sgt i32 %215, -1
  br i1 %216, label %true_block, label %after_if7

after_for3.loopexit:                              ; preds = %after_if7.us
  br label %after_for3

after_for3.loopexit94:                            ; preds = %after_if7.1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit94, %after_for3.loopexit, %for_loop_body1.prol.loopexit, %for_loop_body
  %.037.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ 0.000000e+00, %for_loop_body1.prol.loopexit ], [ %.138.us, %after_for3.loopexit ], [ 0.000000e+00, %after_for3.loopexit94 ]
  %.031.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ 0.000000e+00, %for_loop_body1.prol.loopexit ], [ %.132.us, %after_for3.loopexit ], [ 0.000000e+00, %after_for3.loopexit94 ]
  %.030.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ 0.000000e+00, %for_loop_body1.prol.loopexit ], [ %.1.us, %after_for3.loopexit ], [ 0.000000e+00, %after_for3.loopexit94 ]
  br i1 %28, label %true_block24, label %after_if26

true_block:                                       ; preds = %for_loop_body1
  %217 = load ptr, ptr %3, align 8
  %218 = getelementptr inbounds nuw i8, ptr %217, i64 32872
  %219 = load ptr, ptr %218, align 8
  %220 = getelementptr inbounds nuw i8, ptr %219, i64 24
  %221 = load i32, ptr %220, align 4
  %222 = sub i32 %221, %214
  %223 = load i32, ptr %52, align 4
  %224 = tail call i32 @llvm.smin.i32(i32 %223, i32 %222)
  %225 = icmp slt i32 %215, %224
  br i1 %225, label %true_block5, label %after_if7

true_block5:                                      ; preds = %true_block
  %226 = getelementptr inbounds nuw i8, ptr %219, i64 28
  %227 = load i1, ptr %226, align 1
  br i1 %227, label %true_block8, label %after_if7

after_if7:                                        ; preds = %true_block8, %true_block5, %true_block, %for_loop_body1
  %228 = load ptr, ptr %33, align 8
  %229 = getelementptr i8, ptr %228, i64 %213
  %230 = getelementptr i8, ptr %229, i64 4
  %231 = load i32, ptr %230, align 4
  %232 = sub i32 %49, %231
  %233 = icmp sgt i32 %232, -1
  br i1 %233, label %true_block.1, label %after_if7.1

true_block.1:                                     ; preds = %after_if7
  %234 = load ptr, ptr %3, align 8
  %235 = getelementptr inbounds nuw i8, ptr %234, i64 32872
  %236 = load ptr, ptr %235, align 8
  %237 = getelementptr inbounds nuw i8, ptr %236, i64 24
  %238 = load i32, ptr %237, align 4
  %239 = sub i32 %238, %231
  %240 = load i32, ptr %52, align 4
  %241 = tail call i32 @llvm.smin.i32(i32 %240, i32 %239)
  %242 = icmp slt i32 %232, %241
  br i1 %242, label %true_block5.1, label %after_if7.1

true_block5.1:                                    ; preds = %true_block.1
  %243 = getelementptr inbounds nuw i8, ptr %236, i64 28
  %244 = load i1, ptr %243, align 1
  br i1 %244, label %true_block8.1, label %after_if7.1

true_block8.1:                                    ; preds = %true_block5.1
  %245 = uitofp nneg i32 %232 to float
  %246 = fmul reassoc ninf nsz float %245, 0x401921FB60000000
  %247 = getelementptr inbounds nuw i8, ptr %236, i64 32
  %248 = load float, ptr %247, align 4
  %249 = fmul reassoc ninf nsz float %246, %248
  %250 = tail call noundef float @cosf(float noundef %249) #8
  br label %after_if7.1

after_if7.1:                                      ; preds = %true_block8.1, %true_block5.1, %true_block.1, %after_if7
  %indvars.iv.next.1 = add nsw i64 %indvars.iv, 2
  %exitcond.not.1 = icmp eq i64 %wide.trip.count, %indvars.iv.next.1
  br i1 %exitcond.not.1, label %after_for3.loopexit94, label %for_loop_body1

true_block8:                                      ; preds = %true_block5
  %251 = uitofp nneg i32 %215 to float
  %252 = fmul reassoc ninf nsz float %251, 0x401921FB60000000
  %253 = getelementptr inbounds nuw i8, ptr %219, i64 32
  %254 = load float, ptr %253, align 4
  %255 = fmul reassoc ninf nsz float %252, %254
  %256 = tail call noundef float @cosf(float noundef %255) #8
  br label %after_if7

true_block24:                                     ; preds = %after_for3
  %257 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.037.lcssa, float 0.000000e+00)
  %258 = tail call noundef float @powf(float noundef %257, float noundef %25) #8
  br label %after_if26

after_if26:                                       ; preds = %true_block24, %after_for3
  %.441 = phi float [ %258, %true_block24 ], [ %.037.lcssa, %after_for3 ]
  br i1 %29, label %true_block27, label %after_if29

true_block27:                                     ; preds = %after_if26
  %259 = fsub reassoc ninf nsz float %.441, %27
  %260 = fdiv reassoc ninf nsz float %259, %35
  %261 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %260, float 1.000000e+00)
  %262 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %261, float 0.000000e+00)
  br label %after_if29

after_if29:                                       ; preds = %true_block27, %after_if26
  %.542 = phi float [ %262, %true_block27 ], [ %.441, %after_if26 ]
  br i1 %28, label %true_block30, label %after_if32

true_block30:                                     ; preds = %after_if29
  %263 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.031.lcssa, float 0.000000e+00)
  %264 = tail call noundef float @powf(float noundef %263, float noundef %25) #8
  br label %after_if32

after_if32:                                       ; preds = %true_block30, %after_if29
  %.435 = phi float [ %264, %true_block30 ], [ %.031.lcssa, %after_if29 ]
  br i1 %29, label %true_block33, label %after_if35

true_block33:                                     ; preds = %after_if32
  %265 = fsub reassoc ninf nsz float %.435, %27
  %266 = fdiv reassoc ninf nsz float %265, %35
  %267 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %266, float 1.000000e+00)
  %268 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %267, float 0.000000e+00)
  br label %after_if35

after_if35:                                       ; preds = %true_block33, %after_if32
  %.536 = phi float [ %268, %true_block33 ], [ %.435, %after_if32 ]
  br i1 %28, label %true_block36, label %after_if38

true_block36:                                     ; preds = %after_if35
  %269 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.030.lcssa, float 0.000000e+00)
  %270 = tail call noundef float @powf(float noundef %269, float noundef %25) #8
  br label %after_if38

after_if38:                                       ; preds = %true_block36, %after_if35
  %.4 = phi float [ %270, %true_block36 ], [ %.030.lcssa, %after_if35 ]
  br i1 %29, label %true_block39, label %after_if41

true_block39:                                     ; preds = %after_if38
  %271 = fsub reassoc ninf nsz float %.4, %27
  %272 = fdiv reassoc ninf nsz float %271, %35
  %273 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %272, float 1.000000e+00)
  %274 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %273, float 0.000000e+00)
  br label %after_if41

after_if41:                                       ; preds = %true_block39, %after_if38
  %.5 = phi float [ %274, %true_block39 ], [ %.4, %after_if38 ]
  %275 = fadd reassoc ninf nsz float %.536, %.542
  %276 = fadd reassoc ninf nsz float %275, %.5
  %277 = fmul reassoc ninf nsz float %276, 0x3FD5555560000000
  %278 = load ptr, ptr %36, align 8
  %279 = load i32, ptr %37, align 4
  %280 = mul i32 %279, %49
  %281 = add i32 %280, %51
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, ptr %278, i64 %282
  store float %277, ptr %283, align 4
  %284 = add nsw i32 %.04377, 1
  %exitcond89.not = icmp eq i32 %284, %18
  br i1 %exitcond89.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @cosf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @powf(float noundef, float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.18, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
