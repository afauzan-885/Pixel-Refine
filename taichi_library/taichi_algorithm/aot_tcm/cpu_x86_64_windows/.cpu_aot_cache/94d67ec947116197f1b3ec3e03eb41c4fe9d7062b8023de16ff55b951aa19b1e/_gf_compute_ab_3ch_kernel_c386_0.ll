; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.17 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gf_compute_ab_3ch_kernel_c386_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 228
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 232
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

define void @_gf_compute_ab_3ch_kernel_c386_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 224
  %21 = load float, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 8
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 24
  %26 = getelementptr i8, ptr %19, i64 20
  %27 = getelementptr i8, ptr %19, i64 88
  %28 = getelementptr i8, ptr %19, i64 84
  %29 = getelementptr i8, ptr %19, i64 40
  %30 = getelementptr i8, ptr %19, i64 36
  %31 = getelementptr i8, ptr %19, i64 104
  %32 = getelementptr i8, ptr %19, i64 100
  %33 = getelementptr i8, ptr %19, i64 56
  %34 = getelementptr i8, ptr %19, i64 52
  %35 = getelementptr i8, ptr %19, i64 120
  %36 = getelementptr i8, ptr %19, i64 116
  %37 = getelementptr i8, ptr %19, i64 72
  %38 = getelementptr i8, ptr %19, i64 68
  %39 = getelementptr i8, ptr %19, i64 136
  %40 = getelementptr i8, ptr %19, i64 132
  %41 = getelementptr i8, ptr %19, i64 152
  %42 = getelementptr i8, ptr %19, i64 148
  %43 = getelementptr i8, ptr %19, i64 168
  %44 = getelementptr i8, ptr %19, i64 164
  %45 = getelementptr i8, ptr %19, i64 184
  %46 = getelementptr i8, ptr %19, i64 180
  %47 = getelementptr i8, ptr %19, i64 200
  %48 = getelementptr i8, ptr %19, i64 196
  %49 = getelementptr i8, ptr %19, i64 216
  %50 = getelementptr i8, ptr %19, i64 212
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %186, %for_loop_body ]
  %51 = load ptr, ptr %3, align 8
  %52 = getelementptr inbounds nuw i8, ptr %51, i64 32872
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 4
  %55 = load i32, ptr %54, align 4
  %56 = sdiv i32 %.05, %55
  %57 = mul i32 %56, %55
  %58 = xor i32 %55, %.05
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %.05, %57
  %61 = and i1 %59, %60
  %.neg4 = sext i1 %61 to i32
  %62 = add i32 %56, %.neg4
  %63 = load ptr, ptr %23, align 8
  %64 = load i32, ptr %24, align 4
  %65 = sub i32 %64, %55
  %66 = mul i32 %65, %62
  %67 = add i32 %.05, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %63, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = load ptr, ptr %25, align 8
  %72 = load i32, ptr %26, align 4
  %73 = sub i32 %72, %55
  %74 = mul i32 %73, %62
  %75 = add i32 %.05, %74
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %71, i64 %76
  %78 = load float, ptr %77, align 4
  %79 = fadd reassoc ninf nsz float %70, %21
  %80 = fdiv reassoc ninf nsz float 1.000000e+00, %79
  %81 = load ptr, ptr %27, align 8
  %82 = load i32, ptr %28, align 4
  %83 = sub i32 %82, %55
  %84 = mul i32 %83, %62
  %85 = add i32 %.05, %84
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %81, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = load ptr, ptr %29, align 8
  %90 = load i32, ptr %30, align 4
  %91 = sub i32 %90, %55
  %92 = mul i32 %91, %62
  %93 = add i32 %.05, %92
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %89, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = fmul reassoc ninf nsz float %96, %78
  %98 = fsub reassoc ninf nsz float %88, %97
  %99 = load ptr, ptr %31, align 8
  %100 = load i32, ptr %32, align 4
  %101 = sub i32 %100, %55
  %102 = mul i32 %101, %62
  %103 = add i32 %.05, %102
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %99, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = load ptr, ptr %33, align 8
  %108 = load i32, ptr %34, align 4
  %109 = sub i32 %108, %55
  %110 = mul i32 %109, %62
  %111 = add i32 %.05, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %107, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = fmul reassoc ninf nsz float %114, %78
  %116 = fsub reassoc ninf nsz float %106, %115
  %117 = load ptr, ptr %35, align 8
  %118 = load i32, ptr %36, align 4
  %119 = sub i32 %118, %55
  %120 = mul i32 %119, %62
  %121 = add i32 %.05, %120
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %117, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = load ptr, ptr %37, align 8
  %126 = load i32, ptr %38, align 4
  %127 = sub i32 %126, %55
  %128 = mul i32 %127, %62
  %129 = add i32 %.05, %128
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %125, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = fmul reassoc ninf nsz float %132, %78
  %134 = fsub reassoc ninf nsz float %124, %133
  %135 = fmul reassoc ninf nsz float %98, %80
  %136 = load ptr, ptr %39, align 8
  %137 = load i32, ptr %40, align 4
  %138 = sub i32 %137, %55
  %139 = mul i32 %138, %62
  %140 = add i32 %.05, %139
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %136, i64 %141
  store float %135, ptr %142, align 4
  %143 = fmul reassoc ninf nsz float %116, %80
  %144 = load ptr, ptr %41, align 8
  %145 = load i32, ptr %42, align 4
  %146 = sub i32 %145, %55
  %147 = mul i32 %146, %62
  %148 = add i32 %.05, %147
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %144, i64 %149
  store float %143, ptr %150, align 4
  %151 = fmul reassoc ninf nsz float %134, %80
  %152 = load ptr, ptr %43, align 8
  %153 = load i32, ptr %44, align 4
  %154 = sub i32 %153, %55
  %155 = mul i32 %154, %62
  %156 = add i32 %.05, %155
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %152, i64 %157
  store float %151, ptr %158, align 4
  %159 = fmul reassoc ninf nsz float %135, %78
  %160 = fsub reassoc ninf nsz float %96, %159
  %161 = load ptr, ptr %45, align 8
  %162 = load i32, ptr %46, align 4
  %163 = sub i32 %162, %55
  %164 = mul i32 %163, %62
  %165 = add i32 %.05, %164
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %161, i64 %166
  store float %160, ptr %167, align 4
  %168 = fmul reassoc ninf nsz float %143, %78
  %169 = fsub reassoc ninf nsz float %114, %168
  %170 = load ptr, ptr %47, align 8
  %171 = load i32, ptr %48, align 4
  %172 = sub i32 %171, %55
  %173 = mul i32 %172, %62
  %174 = add i32 %.05, %173
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %170, i64 %175
  store float %169, ptr %176, align 4
  %177 = fmul reassoc ninf nsz float %151, %78
  %178 = fsub reassoc ninf nsz float %132, %177
  %179 = load ptr, ptr %49, align 8
  %180 = load i32, ptr %50, align 4
  %181 = sub i32 %180, %55
  %182 = mul i32 %181, %62
  %183 = add i32 %.05, %182
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %179, i64 %184
  store float %178, ptr %185, align 4
  %186 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %186
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.17, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
