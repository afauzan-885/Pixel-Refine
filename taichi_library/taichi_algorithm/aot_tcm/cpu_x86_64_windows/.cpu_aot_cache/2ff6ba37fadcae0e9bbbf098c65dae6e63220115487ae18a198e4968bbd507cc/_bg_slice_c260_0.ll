; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bg_slice_c260_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 64
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 68
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

define void @_bg_slice_c260_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 60
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 72
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 76
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 80
  %29 = load i32, ptr %28, align 4
  %30 = sitofp i32 %21 to float
  %31 = sitofp i32 %23 to float
  %32 = add i32 %25, -1
  %33 = add i32 %27, -1
  %34 = add i32 %29, -1
  %35 = icmp slt i32 %16, %18
  br i1 %35, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %36 = getelementptr i8, ptr %19, i64 8
  %37 = getelementptr i8, ptr %19, i64 4
  %38 = getelementptr i8, ptr %19, i64 32
  %39 = getelementptr i8, ptr %19, i64 20
  %40 = getelementptr i8, ptr %19, i64 24
  %41 = getelementptr i8, ptr %19, i64 48
  %42 = getelementptr i8, ptr %19, i64 44
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.047 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %221, %after_if ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.047, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.047
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %.047, %49
  %53 = and i1 %51, %52
  %.neg6 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg6
  %55 = mul i32 %47, -1
  %56 = mul i32 %55, %54
  %57 = add i32 %.047, %56
  %58 = load ptr, ptr %36, align 8
  %59 = load i32, ptr %37, align 4
  %60 = sub i32 %59, %47
  %61 = mul i32 %60, %54
  %62 = add i32 %.047, %61
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, ptr %58, i64 %63
  %65 = load float, ptr %64, align 4
  %66 = sitofp i32 %54 to float
  %67 = fdiv reassoc ninf nsz float %66, %30
  %68 = sitofp i32 %57 to float
  %69 = fdiv reassoc ninf nsz float %68, %30
  %70 = fdiv reassoc ninf nsz float %65, %31
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %67)
  %72 = fptosi float %71 to i32
  %73 = tail call reassoc ninf nsz float @llvm.floor.f32(float %69)
  %74 = fptosi float %73 to i32
  %75 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %76 = fptosi float %75 to i32
  %77 = sitofp i32 %72 to float
  %78 = fsub reassoc ninf nsz float %67, %77
  %79 = sitofp i32 %74 to float
  %80 = fsub reassoc ninf nsz float %69, %79
  %81 = sitofp i32 %76 to float
  %82 = fsub reassoc ninf nsz float %70, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %32, i32 %83)
  %85 = tail call i32 @llvm.smax.i32(i32 %74, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %33, i32 %85)
  %87 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %34, i32 %87)
  %89 = load ptr, ptr %38, align 8
  %90 = load i32, ptr %39, align 4
  %91 = load i32, ptr %40, align 4
  %92 = mul i32 %84, %90
  %93 = add i32 %86, %92
  %94 = mul i32 %93, %91
  %95 = add i32 %94, %88
  %96 = shl i32 %95, 1
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %89, i64 %97
  %99 = getelementptr i8, ptr %98, i64 4
  %100 = load float, ptr %99, align 4
  %101 = add i32 %72, 1
  %102 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %103 = tail call i32 @llvm.smin.i32(i32 %32, i32 %102)
  %104 = mul i32 %103, %90
  %105 = add i32 %104, %86
  %106 = mul i32 %105, %91
  %107 = add i32 %106, %88
  %108 = shl i32 %107, 1
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %89, i64 %109
  %111 = getelementptr i8, ptr %110, i64 4
  %112 = load float, ptr %111, align 4
  %113 = add i32 %74, 1
  %114 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %115 = tail call i32 @llvm.smin.i32(i32 %33, i32 %114)
  %116 = add i32 %115, %92
  %117 = mul i32 %116, %91
  %118 = add i32 %117, %88
  %119 = shl i32 %118, 1
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %89, i64 %120
  %122 = getelementptr i8, ptr %121, i64 4
  %123 = load float, ptr %122, align 4
  %124 = add i32 %115, %104
  %125 = mul i32 %124, %91
  %126 = add i32 %125, %88
  %127 = shl i32 %126, 1
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %89, i64 %128
  %130 = getelementptr i8, ptr %129, i64 4
  %131 = load float, ptr %130, align 4
  %132 = add i32 %76, 1
  %133 = tail call i32 @llvm.smax.i32(i32 %132, i32 0)
  %134 = tail call i32 @llvm.smin.i32(i32 %34, i32 %133)
  %135 = add i32 %94, %134
  %136 = shl i32 %135, 1
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %89, i64 %137
  %139 = getelementptr i8, ptr %138, i64 4
  %140 = load float, ptr %139, align 4
  %141 = add i32 %106, %134
  %142 = shl i32 %141, 1
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %89, i64 %143
  %145 = getelementptr i8, ptr %144, i64 4
  %146 = load float, ptr %145, align 4
  %147 = add i32 %117, %134
  %148 = shl i32 %147, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %89, i64 %149
  %151 = getelementptr i8, ptr %150, i64 4
  %152 = load float, ptr %151, align 4
  %153 = add i32 %125, %134
  %154 = shl i32 %153, 1
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %89, i64 %155
  %157 = getelementptr i8, ptr %156, i64 4
  %158 = load float, ptr %157, align 4
  %159 = fsub reassoc ninf nsz float 1.000000e+00, %78
  %160 = fmul reassoc ninf nsz float %159, %100
  %161 = fmul reassoc ninf nsz float %78, %112
  %162 = fadd reassoc ninf nsz float %160, %161
  %163 = fmul reassoc ninf nsz float %159, %123
  %164 = fmul reassoc ninf nsz float %78, %131
  %165 = fadd reassoc ninf nsz float %163, %164
  %166 = fmul reassoc ninf nsz float %159, %140
  %167 = fmul reassoc ninf nsz float %146, %78
  %168 = fadd reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %152, %159
  %170 = fmul reassoc ninf nsz float %158, %78
  %171 = fadd reassoc ninf nsz float %170, %169
  %172 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %173 = fmul reassoc ninf nsz float %162, %172
  %174 = fmul reassoc ninf nsz float %165, %80
  %175 = fadd reassoc ninf nsz float %173, %174
  %176 = fmul reassoc ninf nsz float %168, %172
  %177 = fmul reassoc ninf nsz float %171, %80
  %178 = fadd reassoc ninf nsz float %177, %176
  %179 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %180 = fmul reassoc ninf nsz float %175, %179
  %181 = fmul reassoc ninf nsz float %178, %82
  %182 = fadd reassoc ninf nsz float %181, %180
  %183 = fcmp reassoc ninf nsz ogt float %182, 0x3EB0C6F7A0000000
  br i1 %183, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %184 = load float, ptr %129, align 4
  %185 = load float, ptr %121, align 4
  %186 = load float, ptr %110, align 4
  %187 = load float, ptr %98, align 4
  %188 = fmul reassoc ninf nsz float %187, %159
  %189 = fmul reassoc ninf nsz float %186, %78
  %190 = fadd reassoc ninf nsz float %188, %189
  %191 = fmul reassoc ninf nsz float %190, %172
  %192 = fmul reassoc ninf nsz float %185, %159
  %193 = fmul reassoc ninf nsz float %184, %78
  %194 = fadd reassoc ninf nsz float %192, %193
  %195 = fmul reassoc ninf nsz float %194, %80
  %196 = fadd reassoc ninf nsz float %191, %195
  %197 = fmul reassoc ninf nsz float %196, %179
  %198 = load float, ptr %138, align 4
  %199 = fmul reassoc ninf nsz float %198, %159
  %200 = load float, ptr %144, align 4
  %201 = fmul reassoc ninf nsz float %200, %78
  %202 = fadd reassoc ninf nsz float %201, %199
  %203 = fmul reassoc ninf nsz float %202, %172
  %204 = load float, ptr %150, align 4
  %205 = fmul reassoc ninf nsz float %204, %159
  %206 = load float, ptr %156, align 4
  %207 = fmul reassoc ninf nsz float %206, %78
  %208 = fadd reassoc ninf nsz float %207, %205
  %209 = fmul reassoc ninf nsz float %208, %80
  %210 = fadd reassoc ninf nsz float %209, %203
  %211 = fmul reassoc ninf nsz float %210, %82
  %212 = fadd reassoc ninf nsz float %211, %197
  %213 = fdiv reassoc ninf nsz float %212, %182
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.0 = phi float [ %213, %true_block ], [ %65, %for_loop_body ]
  %214 = load ptr, ptr %41, align 8
  %215 = load i32, ptr %42, align 4
  %216 = sub i32 %215, %47
  %217 = mul i32 %216, %54
  %218 = add i32 %.047, %217
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, ptr %214, i64 %219
  store float %.0, ptr %220, align 4
  %221 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %18, %221
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.7, align 8
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

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #2

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
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
