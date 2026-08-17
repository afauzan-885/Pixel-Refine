; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_canny_nms_kernel_c398_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 64
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 68
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
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

define void @_canny_nms_kernel_c398_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 8
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 24
  %24 = getelementptr i8, ptr %20, i64 20
  %25 = getelementptr i8, ptr %20, i64 56
  %26 = getelementptr i8, ptr %20, i64 52
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %.0815 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %60, %for_loop_inc ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.0815, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.0815
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.0815, %33
  %37 = and i1 %35, %36
  %.neg13 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg13
  %39 = mul i32 %38, %31
  %40 = load ptr, ptr %21, align 8
  %41 = load i32, ptr %22, align 4
  %42 = sub i32 %41, %31
  %43 = mul i32 %42, %38
  %44 = add i32 %.0815, %43
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, ptr %40, i64 %45
  %47 = load float, ptr %46, align 4
  %48 = load ptr, ptr %23, align 8
  %49 = load i32, ptr %24, align 4
  %50 = sub i32 %49, %31
  %51 = mul i32 %50, %38
  %52 = add i32 %.0815, %51
  %53 = sext i32 %52 to i64
  %54 = getelementptr float, ptr %48, i64 %53
  %55 = load float, ptr %54, align 4
  %56 = tail call noundef float @llvm.fabs.f32(float %47)
  %57 = tail call noundef float @llvm.fabs.f32(float %55)
  %58 = fadd reassoc ninf nsz float %57, %56
  %59 = fcmp reassoc ninf nsz olt float %58, 0x3EB0C6F7A0000000
  br i1 %59, label %true_block, label %after_if

for_loop_inc:                                     ; preds = %false_block14, %true_block13, %true_block
  %60 = add nsw i32 %.0815, 1
  %exitcond.not = icmp eq i32 %18, %60
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %61 = load ptr, ptr %25, align 8
  %62 = load i32, ptr %26, align 4
  %63 = sub i32 %62, %31
  %64 = mul i32 %63, %38
  %65 = add i32 %.0815, %64
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %61, i64 %66
  store float 0.000000e+00, ptr %67, align 4
  br label %for_loop_inc

after_if:                                         ; preds = %for_loop_body
  %68 = fmul reassoc ninf nsz float %57, 0x4003504F20000000
  %69 = fcmp reassoc ninf nsz ogt float %56, %68
  br i1 %69, label %true_block1, label %false_block2

true_block1:                                      ; preds = %after_if
  %70 = mul i32 %31, -1
  %71 = mul i32 %70, %38
  %72 = add i32 %.0815, %71
  %73 = add i32 %72, -1
  %74 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %75 = load i32, ptr %74, align 4
  %76 = add i32 %75, -1
  %77 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %76, i32 %77)
  %79 = add i32 %72, 1
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %76, i32 %80)
  %82 = load ptr, ptr %0, align 8
  %83 = getelementptr i8, ptr %82, i64 40
  %84 = load ptr, ptr %83, align 8
  %85 = getelementptr i8, ptr %82, i64 36
  %86 = load i32, ptr %85, align 4
  %87 = mul i32 %86, %38
  %88 = add i32 %87, %78
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, ptr %84, i64 %89
  %91 = add i32 %87, %81
  br label %after_if3

false_block2:                                     ; preds = %after_if
  %92 = fmul reassoc ninf nsz float %56, 0x4003504F20000000
  %93 = fcmp reassoc ninf nsz ogt float %57, %92
  br i1 %93, label %true_block4, label %false_block5

after_if3:                                        ; preds = %false_block8, %true_block7, %true_block4, %true_block1
  %.sink17 = phi i32 [ %158, %true_block7 ], [ %171, %false_block8 ], [ %124, %true_block4 ], [ %91, %true_block1 ]
  %.sink = phi ptr [ %138, %true_block7 ], [ %138, %false_block8 ], [ %114, %true_block4 ], [ %84, %true_block1 ]
  %.07.in = phi ptr [ %154, %true_block7 ], [ %167, %false_block8 ], [ %121, %true_block4 ], [ %90, %true_block1 ]
  %.07 = load float, ptr %.07.in, align 4
  %94 = fadd reassoc ninf nsz float %58, 0x3EB0C6F7A0000000
  %95 = fcmp reassoc ninf nsz ult float %94, %.07
  br i1 %95, label %after_if12.thread, label %after_if12

after_if12.thread:                                ; preds = %after_if3
  %96 = load ptr, ptr %25, align 8
  %97 = load i32, ptr %26, align 4
  %98 = sub i32 %97, %31
  %99 = mul i32 %98, %38
  %100 = add i32 %.0815, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %96, i64 %101
  br label %false_block14

true_block4:                                      ; preds = %false_block2
  %103 = add i32 %38, -1
  %104 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %105 = load i32, ptr %104, align 4
  %106 = add i32 %105, -1
  %107 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %106, i32 %107)
  %109 = add i32 %38, 1
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = tail call i32 @llvm.smin.i32(i32 %106, i32 %110)
  %112 = load ptr, ptr %0, align 8
  %113 = getelementptr i8, ptr %112, i64 40
  %114 = load ptr, ptr %113, align 8
  %115 = getelementptr i8, ptr %112, i64 36
  %116 = load i32, ptr %115, align 4
  %117 = mul i32 %116, %108
  %118 = sub i32 %117, %39
  %119 = add i32 %.0815, %118
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %114, i64 %120
  %122 = mul i32 %116, %111
  %123 = sub i32 %122, %39
  %124 = add i32 %.0815, %123
  br label %after_if3

false_block5:                                     ; preds = %false_block2
  %125 = fmul reassoc ninf nsz float %55, %47
  %126 = fcmp reassoc ninf nsz ult float %125, 0.000000e+00
  %127 = add i32 %38, -1
  %128 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %129 = load i32, ptr %128, align 4
  %130 = add i32 %129, -1
  %131 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %132 = load i32, ptr %131, align 4
  %133 = add i32 %132, -1
  %134 = tail call i32 @llvm.smax.i32(i32 %127, i32 0)
  %135 = tail call i32 @llvm.smin.i32(i32 %130, i32 %134)
  %136 = load ptr, ptr %0, align 8
  %137 = getelementptr i8, ptr %136, i64 40
  %138 = load ptr, ptr %137, align 8
  %139 = getelementptr i8, ptr %136, i64 36
  %140 = load i32, ptr %139, align 4
  %141 = mul i32 %140, %135
  %142 = add i32 %38, 1
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %130, i32 %143)
  %145 = mul i32 %140, %144
  br i1 %126, label %false_block8, label %true_block7

true_block7:                                      ; preds = %false_block5
  %146 = mul i32 %31, -1
  %147 = mul i32 %146, %38
  %148 = add i32 %.0815, %147
  %149 = add i32 %148, -1
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = tail call i32 @llvm.smin.i32(i32 %133, i32 %150)
  %152 = add i32 %141, %151
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %138, i64 %153
  %155 = add i32 %148, 1
  %156 = tail call i32 @llvm.smax.i32(i32 %155, i32 0)
  %157 = tail call i32 @llvm.smin.i32(i32 %133, i32 %156)
  %158 = add i32 %145, %157
  br label %after_if3

false_block8:                                     ; preds = %false_block5
  %159 = mul i32 %31, -1
  %160 = mul i32 %159, %38
  %161 = add i32 %.0815, %160
  %162 = add i32 %161, 1
  %163 = tail call i32 @llvm.smax.i32(i32 %162, i32 0)
  %164 = tail call i32 @llvm.smin.i32(i32 %133, i32 %163)
  %165 = add i32 %141, %164
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %138, i64 %166
  %168 = add i32 %161, -1
  %169 = tail call i32 @llvm.smax.i32(i32 %168, i32 0)
  %170 = tail call i32 @llvm.smin.i32(i32 %133, i32 %169)
  %171 = add i32 %145, %170
  br label %after_if3

after_if12:                                       ; preds = %after_if3
  %172 = sext i32 %.sink17 to i64
  %173 = getelementptr float, ptr %.sink, i64 %172
  %.06 = load float, ptr %173, align 4
  %174 = fcmp reassoc ninf nsz ult float %94, %.06
  %175 = load ptr, ptr %25, align 8
  %176 = load i32, ptr %26, align 4
  %177 = sub i32 %176, %31
  %178 = mul i32 %177, %38
  %179 = add i32 %.0815, %178
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %175, i64 %180
  br i1 %174, label %false_block14, label %true_block13

true_block13:                                     ; preds = %after_if12
  store float %58, ptr %181, align 4
  br label %for_loop_inc

false_block14:                                    ; preds = %after_if12, %after_if12.thread
  %182 = phi ptr [ %102, %after_if12.thread ], [ %181, %after_if12 ]
  store float 0.000000e+00, ptr %182, align 4
  br label %for_loop_inc
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

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
