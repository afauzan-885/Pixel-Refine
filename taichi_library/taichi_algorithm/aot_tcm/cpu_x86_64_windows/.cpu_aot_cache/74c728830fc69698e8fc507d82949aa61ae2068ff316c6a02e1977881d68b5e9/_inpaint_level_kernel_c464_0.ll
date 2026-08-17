; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_inpaint_level_kernel_c464_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 56
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 60
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 12
  store i32 %11, ptr %15, align 4
  %16 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %17 = load ptr, ptr %3, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 4
  store i32 %16, ptr %20, align 4
  %21 = mul i32 %16, %8
  %22 = load ptr, ptr %3, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  store i32 %21, ptr %24, align 4
  ret void
}

define void @_inpaint_level_kernel_c464_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 64
  %21 = load float, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 68
  %23 = load float, ptr %22, align 4
  %24 = fptosi float %23 to i32
  %25 = fmul reassoc ninf nsz float %23, %23
  %26 = add i32 %24, 2
  %neg = xor i32 %24, -1
  %27 = icmp slt i32 %16, %18
  br i1 %27, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %28 = getelementptr i8, ptr %19, i64 32
  %29 = getelementptr i8, ptr %19, i64 28
  %30 = icmp sle i32 %26, %neg
  %31 = getelementptr i8, ptr %19, i64 48
  %32 = getelementptr i8, ptr %19, i64 44
  %33 = getelementptr i8, ptr %19, i64 16
  %34 = getelementptr i8, ptr %19, i64 4
  %35 = getelementptr i8, ptr %19, i64 8
  %36 = shl i32 %24, 1
  %37 = add i32 %36, 3
  %38 = sub i32 -1, %24
  %39 = add i32 %16, -1
  %40 = sub i32 %39, %24
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %lsr.iv109 = phi i32 [ %40, %for_loop_body.lr.ph ], [ %lsr.iv.next110, %for_loop_inc ]
  %.03698 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %117, %for_loop_inc ]
  %41 = load ptr, ptr %3, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 4
  %45 = load i32, ptr %44, align 4
  %46 = sdiv i32 %.03698, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.03698
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %47, %.03698
  %51 = and i1 %49, %50
  %.neg44 = sext i1 %51 to i32
  %52 = add i32 %46, %.neg44
  %53 = mul i32 %52, %45
  %54 = sub i32 %.03698, %53
  %55 = load ptr, ptr %28, align 8
  %56 = load i32, ptr %29, align 4
  %57 = mul i32 %52, %56
  %58 = add i32 %54, %57
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, ptr %55, i64 %59
  %61 = load float, ptr %60, align 4
  %62 = fsub reassoc ninf nsz float %61, %21
  %63 = tail call noundef float @llvm.fabs.f32(float %62)
  %64 = fcmp reassoc ninf nsz ogt float %63, 5.000000e-01
  %brmerge = select i1 %64, i1 true, i1 %30
  br i1 %brmerge, label %for_loop_inc, label %for_loop_body1.lr.ph

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %65 = getelementptr inbounds nuw i8, ptr %43, i64 8
  %66 = getelementptr inbounds nuw i8, ptr %43, i64 12
  %67 = add i32 %38, %46
  %68 = add i32 %67, %.neg44
  %69 = sub i32 %lsr.iv109, %53
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_body1.lr.ph
  %lsr.iv107 = phi i32 [ %lsr.iv.next108, %for_loop_test8.after_for7_crit_edge.us ], [ %68, %for_loop_body1.lr.ph ]
  %.02583.us = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %116, %for_loop_test8.after_for7_crit_edge.us ]
  %.02682.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi59.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.02781.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi58.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.03080.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi57.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.03379.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi.us, %for_loop_test8.after_for7_crit_edge.us ]
  %70 = add i32 %.02583.us, %52
  %71 = mul i32 %.02583.us, %.02583.us
  %72 = icmp slt i32 %70, 0
  br i1 %72, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.lr.ph.split.us91

for_loop_body5.us88:                              ; preds = %for_loop_body5.us88.preheader, %for_loop_inc6.us
  %lsr.iv = phi i32 [ 0, %for_loop_body5.us88.preheader ], [ %lsr.iv.next, %for_loop_inc6.us ]
  %.252.us = phi float [ %.1.us, %for_loop_inc6.us ], [ %.02682.us, %for_loop_body5.us88.preheader ]
  %.22951.us = phi float [ %.128.us, %for_loop_inc6.us ], [ %.02781.us, %for_loop_body5.us88.preheader ]
  %.23250.us = phi float [ %.131.us, %for_loop_inc6.us ], [ %.03080.us, %for_loop_body5.us88.preheader ]
  %.23549.us = phi float [ %.134.us, %for_loop_inc6.us ], [ %.03379.us, %for_loop_body5.us88.preheader ]
  %73 = add i32 %neg, %lsr.iv
  %74 = add i32 %69, %lsr.iv
  %75 = icmp slt i32 %74, 0
  br i1 %75, label %for_loop_inc6.us, label %false_block16.us

false_block16.us:                                 ; preds = %for_loop_body5.us88
  %76 = load i32, ptr %66, align 4
  %.not48.us = icmp slt i32 %74, %76
  br i1 %.not48.us, label %after_if20.us, label %for_loop_inc6.us

after_if20.us:                                    ; preds = %false_block16.us
  %77 = load ptr, ptr %31, align 8
  %78 = load i32, ptr %32, align 4
  %79 = mul i32 %lsr.iv107, %78
  %80 = add i32 %74, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %77, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = fcmp reassoc ninf nsz olt float %83, 5.000000e-01
  br i1 %84, label %for_loop_inc6.us, label %after_if24.us

after_if24.us:                                    ; preds = %after_if20.us
  %85 = mul i32 %73, %73
  %86 = add i32 %85, %71
  %87 = sitofp i32 %86 to float
  %88 = fcmp reassoc ninf nsz olt float %25, %87
  %89 = icmp slt i32 %86, 1
  %or.cond.us = or i1 %89, %88
  br i1 %or.cond.us, label %for_loop_inc6.us, label %after_if32.us

after_if32.us:                                    ; preds = %after_if24.us
  %90 = fdiv reassoc ninf nsz float 1.000000e+00, %87
  %91 = fadd reassoc ninf nsz float %90, %.23549.us
  %92 = load ptr, ptr %33, align 8
  %93 = load i32, ptr %34, align 4
  %94 = load i32, ptr %35, align 4
  %95 = mul i32 %lsr.iv107, %93
  %96 = add i32 %74, %95
  %97 = mul i32 %96, %94
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %92, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fmul reassoc ninf nsz float %100, %90
  %102 = fadd reassoc ninf nsz float %101, %.23250.us
  %103 = add i32 %97, 1
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %92, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = fmul reassoc ninf nsz float %106, %90
  %108 = fadd reassoc ninf nsz float %107, %.22951.us
  %109 = add i32 %97, 2
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %92, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fmul reassoc ninf nsz float %112, %90
  %114 = fadd reassoc ninf nsz float %113, %.252.us
  br label %for_loop_inc6.us

for_loop_inc6.us:                                 ; preds = %after_if32.us, %after_if24.us, %after_if20.us, %false_block16.us, %for_loop_body5.us88
  %.134.us = phi float [ %.23549.us, %false_block16.us ], [ %.23549.us, %after_if20.us ], [ %.23549.us, %after_if24.us ], [ %91, %after_if32.us ], [ %.23549.us, %for_loop_body5.us88 ]
  %.131.us = phi float [ %.23250.us, %false_block16.us ], [ %.23250.us, %after_if20.us ], [ %.23250.us, %after_if24.us ], [ %102, %after_if32.us ], [ %.23250.us, %for_loop_body5.us88 ]
  %.128.us = phi float [ %.22951.us, %false_block16.us ], [ %.22951.us, %after_if20.us ], [ %.22951.us, %after_if24.us ], [ %108, %after_if32.us ], [ %.22951.us, %for_loop_body5.us88 ]
  %.1.us = phi float [ %.252.us, %false_block16.us ], [ %.252.us, %after_if20.us ], [ %.252.us, %after_if24.us ], [ %114, %after_if32.us ], [ %.252.us, %for_loop_body5.us88 ]
  %lsr.iv.next = add nuw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %37, %lsr.iv.next
  br i1 %exitcond.not, label %for_loop_test8.after_for7_crit_edge.us.loopexit, label %for_loop_body5.us88

for_loop_body5.lr.ph.split.us91:                  ; preds = %for_loop_body1.us
  %115 = load i32, ptr %65, align 4
  %.not.us = icmp sge i32 %70, %115
  %.not.fr.us = freeze i1 %.not.us
  br i1 %.not.fr.us, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us88.preheader

for_loop_body5.us88.preheader:                    ; preds = %for_loop_body5.lr.ph.split.us91
  br label %for_loop_body5.us88

for_loop_test8.after_for7_crit_edge.us.loopexit:  ; preds = %for_loop_inc6.us
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_test8.after_for7_crit_edge.us.loopexit, %for_loop_body5.lr.ph.split.us91, %for_loop_body1.us
  %.us-phi.us = phi float [ %.03379.us, %for_loop_body1.us ], [ %.03379.us, %for_loop_body5.lr.ph.split.us91 ], [ %.134.us, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi57.us = phi float [ %.03080.us, %for_loop_body1.us ], [ %.03080.us, %for_loop_body5.lr.ph.split.us91 ], [ %.131.us, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi58.us = phi float [ %.02781.us, %for_loop_body1.us ], [ %.02781.us, %for_loop_body5.lr.ph.split.us91 ], [ %.128.us, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi59.us = phi float [ %.02682.us, %for_loop_body1.us ], [ %.02682.us, %for_loop_body5.lr.ph.split.us91 ], [ %.1.us, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %116 = add nsw i32 %.02583.us, 1
  %lsr.iv.next108 = add i32 %lsr.iv107, 1
  %exitcond101.not = icmp eq i32 %116, %26
  br i1 %exitcond101.not, label %after_for3, label %for_loop_body1.us

for_loop_inc:                                     ; preds = %true_block34, %after_for3, %for_loop_body
  %117 = add nsw i32 %.03698, 1
  %lsr.iv.next110 = add i32 %lsr.iv109, 1
  %exitcond102.not = icmp eq i32 %117, %18
  br i1 %exitcond102.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3:                                       ; preds = %for_loop_test8.after_for7_crit_edge.us
  %118 = fcmp reassoc ninf nsz ogt float %.us-phi.us, 0x3D71979980000000
  br i1 %118, label %true_block34, label %for_loop_inc

true_block34:                                     ; preds = %after_for3
  %119 = fdiv reassoc ninf nsz float 1.000000e+00, %.us-phi.us
  %120 = fmul reassoc ninf nsz float %.us-phi57.us, %119
  %121 = load ptr, ptr %33, align 8
  %122 = load i32, ptr %34, align 4
  %123 = load i32, ptr %35, align 4
  %124 = mul i32 %122, %52
  %125 = add i32 %124, %54
  %126 = mul i32 %125, %123
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %121, i64 %127
  store float %120, ptr %128, align 4
  %129 = fmul reassoc ninf nsz float %.us-phi58.us, %119
  %130 = load ptr, ptr %33, align 8
  %131 = load i32, ptr %34, align 4
  %132 = load i32, ptr %35, align 4
  %133 = mul i32 %131, %52
  %134 = add i32 %133, %54
  %135 = mul i32 %134, %132
  %136 = add i32 %135, 1
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %130, i64 %137
  store float %129, ptr %138, align 4
  %139 = fmul reassoc ninf nsz float %.us-phi59.us, %119
  %140 = load ptr, ptr %33, align 8
  %141 = load i32, ptr %34, align 4
  %142 = load i32, ptr %35, align 4
  %143 = mul i32 %141, %52
  %144 = add i32 %143, %54
  %145 = mul i32 %144, %142
  %146 = add i32 %145, 2
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %140, i64 %147
  store float %139, ptr %148, align 4
  %149 = load ptr, ptr %31, align 8
  %150 = load i32, ptr %32, align 4
  %151 = mul i32 %150, %52
  %152 = add i32 %151, %54
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %149, i64 %153
  store float 1.000000e+00, ptr %154, align 4
  br label %for_loop_inc
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

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
