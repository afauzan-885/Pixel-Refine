; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.22 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @mean_division_vec3_weight_kernel_c102_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 96
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 100
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 4
  store i32 %6, ptr %11, align 4
  %12 = mul i32 %6, %3
  %13 = load ptr, ptr %7, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  store i32 %12, ptr %15, align 4
  ret void
}

define void @mean_division_vec3_weight_kernel_c102_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #6
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
  %21 = getelementptr i8, ptr %20, i64 40
  %22 = getelementptr i8, ptr %20, i64 28
  %23 = getelementptr i8, ptr %20, i64 32
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if6, %for_loop_body.lr.ph
  %.08 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %197, %after_if6 ]
  %24 = load ptr, ptr %3, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 4
  %28 = load i32, ptr %27, align 4
  %29 = sdiv i32 %.08, %28
  %30 = mul i32 %29, %28
  %31 = xor i32 %28, %.08
  %32 = icmp slt i32 %31, 0
  %33 = icmp ne i32 %.08, %30
  %34 = and i1 %32, %33
  %.neg7 = sext i1 %34 to i32
  %35 = add i32 %29, %.neg7
  %36 = load ptr, ptr %21, align 8
  %37 = load i32, ptr %22, align 4
  %38 = load i32, ptr %23, align 4
  %39 = sub i32 %37, %28
  %40 = mul i32 %39, %35
  %41 = add i32 %.08, %40
  %42 = mul i32 %41, %38
  %43 = sext i32 %42 to i64
  %44 = getelementptr float, ptr %36, i64 %43
  %45 = load float, ptr %44, align 4
  %46 = fcmp reassoc ninf nsz ogt float %45, 0x3E45798EE0000000
  %47 = load ptr, ptr %0, align 8
  br i1 %46, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if6
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %48 = getelementptr i8, ptr %47, i64 16
  %49 = load ptr, ptr %48, align 8
  %50 = getelementptr i8, ptr %47, i64 4
  %51 = load i32, ptr %50, align 4
  %52 = getelementptr i8, ptr %47, i64 8
  %53 = load i32, ptr %52, align 4
  %54 = sub i32 %51, %28
  %55 = mul i32 %54, %35
  %56 = add i32 %.08, %55
  %57 = mul i32 %56, %53
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, ptr %49, i64 %58
  %60 = load float, ptr %59, align 4
  %61 = fdiv reassoc ninf nsz float %60, %45
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %62 = getelementptr i8, ptr %47, i64 64
  %63 = load ptr, ptr %62, align 8
  %64 = getelementptr i8, ptr %47, i64 52
  %65 = load i32, ptr %64, align 4
  %66 = getelementptr i8, ptr %47, i64 56
  %67 = load i32, ptr %66, align 4
  %68 = sub i32 %65, %28
  %69 = mul i32 %68, %35
  %70 = add i32 %.08, %69
  %71 = mul i32 %70, %67
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %63, i64 %72
  %74 = load float, ptr %73, align 4
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %.sink = phi float [ %74, %false_block ], [ %61, %true_block ]
  %75 = getelementptr i8, ptr %47, i64 88
  %76 = load ptr, ptr %75, align 8
  %77 = getelementptr i8, ptr %47, i64 76
  %78 = load i32, ptr %77, align 4
  %79 = getelementptr i8, ptr %47, i64 80
  %80 = load i32, ptr %79, align 4
  %81 = sub i32 %78, %28
  %82 = mul i32 %81, %35
  %83 = add i32 %.08, %82
  %84 = mul i32 %83, %80
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %76, i64 %85
  store float %.sink, ptr %86, align 4
  %87 = load ptr, ptr %21, align 8
  %88 = load i32, ptr %22, align 4
  %89 = load i32, ptr %23, align 4
  %90 = sub i32 %88, %28
  %91 = mul i32 %90, %35
  %92 = add i32 %.08, %91
  %93 = mul i32 %92, %89
  %94 = add i32 %93, 1
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %87, i64 %95
  %97 = load float, ptr %96, align 4
  %98 = fcmp reassoc ninf nsz ogt float %97, 0x3E45798EE0000000
  %99 = load ptr, ptr %0, align 8
  br i1 %98, label %true_block1, label %false_block2

true_block1:                                      ; preds = %after_if
  %100 = getelementptr i8, ptr %99, i64 16
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr i8, ptr %99, i64 4
  %103 = load i32, ptr %102, align 4
  %104 = getelementptr i8, ptr %99, i64 8
  %105 = load i32, ptr %104, align 4
  %106 = sub i32 %103, %28
  %107 = mul i32 %106, %35
  %108 = add i32 %.08, %107
  %109 = mul i32 %108, %105
  %110 = add i32 %109, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %101, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = fdiv reassoc ninf nsz float %113, %97
  br label %after_if3

false_block2:                                     ; preds = %after_if
  %115 = getelementptr i8, ptr %99, i64 64
  %116 = load ptr, ptr %115, align 8
  %117 = getelementptr i8, ptr %99, i64 52
  %118 = load i32, ptr %117, align 4
  %119 = getelementptr i8, ptr %99, i64 56
  %120 = load i32, ptr %119, align 4
  %121 = sub i32 %118, %28
  %122 = mul i32 %121, %35
  %123 = add i32 %.08, %122
  %124 = mul i32 %123, %120
  %125 = add i32 %124, 1
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %116, i64 %126
  %128 = load float, ptr %127, align 4
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  %.sink20 = phi float [ %128, %false_block2 ], [ %114, %true_block1 ]
  %129 = getelementptr i8, ptr %99, i64 88
  %130 = load ptr, ptr %129, align 8
  %131 = getelementptr i8, ptr %99, i64 76
  %132 = load i32, ptr %131, align 4
  %133 = getelementptr i8, ptr %99, i64 80
  %134 = load i32, ptr %133, align 4
  %135 = sub i32 %132, %28
  %136 = mul i32 %135, %35
  %137 = add i32 %.08, %136
  %138 = mul i32 %137, %134
  %139 = add i32 %138, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %130, i64 %140
  store float %.sink20, ptr %141, align 4
  %142 = load ptr, ptr %21, align 8
  %143 = load i32, ptr %22, align 4
  %144 = load i32, ptr %23, align 4
  %145 = sub i32 %143, %28
  %146 = mul i32 %145, %35
  %147 = add i32 %.08, %146
  %148 = mul i32 %147, %144
  %149 = add i32 %148, 2
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %142, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = fcmp reassoc ninf nsz ogt float %152, 0x3E45798EE0000000
  %154 = load ptr, ptr %0, align 8
  br i1 %153, label %true_block4, label %false_block5

true_block4:                                      ; preds = %after_if3
  %155 = getelementptr i8, ptr %154, i64 16
  %156 = load ptr, ptr %155, align 8
  %157 = getelementptr i8, ptr %154, i64 4
  %158 = load i32, ptr %157, align 4
  %159 = getelementptr i8, ptr %154, i64 8
  %160 = load i32, ptr %159, align 4
  %161 = sub i32 %158, %28
  %162 = mul i32 %161, %35
  %163 = add i32 %.08, %162
  %164 = mul i32 %163, %160
  %165 = add i32 %164, 2
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %156, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = fdiv reassoc ninf nsz float %168, %152
  br label %after_if6

false_block5:                                     ; preds = %after_if3
  %170 = getelementptr i8, ptr %154, i64 64
  %171 = load ptr, ptr %170, align 8
  %172 = getelementptr i8, ptr %154, i64 52
  %173 = load i32, ptr %172, align 4
  %174 = getelementptr i8, ptr %154, i64 56
  %175 = load i32, ptr %174, align 4
  %176 = sub i32 %173, %28
  %177 = mul i32 %176, %35
  %178 = add i32 %.08, %177
  %179 = mul i32 %178, %175
  %180 = add i32 %179, 2
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %171, i64 %181
  %183 = load float, ptr %182, align 4
  br label %after_if6

after_if6:                                        ; preds = %false_block5, %true_block4
  %.sink36 = phi float [ %183, %false_block5 ], [ %169, %true_block4 ]
  %184 = getelementptr i8, ptr %154, i64 88
  %185 = load ptr, ptr %184, align 8
  %186 = getelementptr i8, ptr %154, i64 76
  %187 = load i32, ptr %186, align 4
  %188 = getelementptr i8, ptr %154, i64 80
  %189 = load i32, ptr %188, align 4
  %190 = sub i32 %187, %28
  %191 = mul i32 %190, %35
  %192 = add i32 %.08, %191
  %193 = mul i32 %192, %189
  %194 = add i32 %193, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %185, i64 %195
  store float %.sink36, ptr %196, align 4
  %197 = add nsw i32 %.08, 1
  %exitcond.not = icmp eq i32 %18, %197
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.22, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
