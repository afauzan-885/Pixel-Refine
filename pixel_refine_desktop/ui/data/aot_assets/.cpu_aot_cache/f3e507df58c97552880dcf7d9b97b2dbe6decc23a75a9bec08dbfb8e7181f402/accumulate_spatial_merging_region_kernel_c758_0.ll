; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.16 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_region_kernel_c758_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 88
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 24
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 80
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
  store i32 %11, ptr %15, align 4
  %16 = sitofp i32 %11 to float
  %17 = fdiv reassoc ninf nsz float %8, %16
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 16
  store float %17, ptr %21, align 4
  %22 = load ptr, ptr %context, align 8
  %23 = getelementptr i8, ptr %22, i64 92
  %24 = load i32, ptr %23, align 4
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 28
  store i32 %24, ptr %28, align 4
  %29 = sitofp i32 %24 to float
  %30 = load ptr, ptr %context, align 8
  %31 = getelementptr i8, ptr %30, i64 84
  %32 = load i32, ptr %31, align 4
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 12
  store i32 %32, ptr %36, align 4
  %37 = sitofp i32 %32 to float
  %38 = fdiv reassoc ninf nsz float %29, %37
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 20
  store float %38, ptr %42, align 4
  %43 = load ptr, ptr %context, align 8
  %44 = getelementptr i8, ptr %43, i64 96
  %45 = load i32, ptr %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = getelementptr i8, ptr %43, i64 100
  %48 = load i32, ptr %47, align 4
  %49 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %50 = load ptr, ptr %3, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 4
  store i32 %49, ptr %53, align 4
  %54 = mul i32 %49, %46
  %55 = load ptr, ptr %3, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 32872
  %57 = load ptr, ptr %56, align 8
  store i32 %54, ptr %57, align 4
  ret void
}

define void @accumulate_spatial_merging_region_kernel_c758_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 104
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 108
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.01015 = phi i32 [ %150, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  %29 = load i32, ptr %28, align 4
  %30 = sdiv i32 %.01015, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.01015
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.01015, %31
  %35 = and i1 %33, %34
  %.neg12 = sext i1 %35 to i32
  %36 = add i32 %30, %.neg12
  %37 = mul i32 %36, %29
  %38 = add i32 %36, %21
  %39 = mul i32 %29, -1
  %40 = mul i32 %39, %36
  %41 = add i32 %23, %.01015
  %42 = add i32 %41, %40
  %43 = getelementptr inbounds nuw i8, ptr %27, i64 8
  %44 = load i32, ptr %43, align 4
  %45 = icmp slt i32 %38, %44
  br i1 %45, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = getelementptr inbounds nuw i8, ptr %27, i64 12
  %47 = load i32, ptr %46, align 4
  %48 = icmp slt i32 %42, %47
  br i1 %48, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %49 = sitofp i32 %38 to float
  %50 = getelementptr inbounds nuw i8, ptr %27, i64 16
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sitofp i32 %42 to float
  %54 = getelementptr inbounds nuw i8, ptr %27, i64 20
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %58 = fptosi float %57 to i32
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %61 = fptosi float %60 to i32
  %62 = tail call i32 @llvm.smax.i32(i32 %61, i32 0)
  %63 = add nuw i32 %59, 1
  %64 = getelementptr inbounds nuw i8, ptr %27, i64 24
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = tail call i32 @llvm.smin.i32(i32 %63, i32 %66)
  %68 = add nuw i32 %62, 1
  %69 = getelementptr inbounds nuw i8, ptr %27, i64 28
  %70 = load i32, ptr %69, align 4
  %71 = add i32 %70, -1
  %72 = tail call i32 @llvm.smin.i32(i32 %68, i32 %71)
  %73 = uitofp nneg i32 %59 to float
  %74 = fsub reassoc ninf nsz float %52, %73
  %75 = uitofp nneg i32 %62 to float
  %76 = fsub reassoc ninf nsz float %56, %75
  %77 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %78 = load ptr, ptr %0, align 8
  %79 = getelementptr i8, ptr %78, i64 32
  %80 = load ptr, ptr %79, align 8
  %81 = getelementptr i8, ptr %78, i64 28
  %82 = load i32, ptr %81, align 4
  %83 = mul i32 %82, %59
  %84 = add i32 %83, %62
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %80, i64 %85
  %87 = load float, ptr %86, align 4
  %88 = fmul reassoc ninf nsz float %77, %87
  %89 = add i32 %83, %72
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %80, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = fmul reassoc ninf nsz float %92, %76
  %94 = mul i32 %67, %82
  %95 = add i32 %94, %62
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %80, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = fmul reassoc ninf nsz float %98, %77
  %100 = add i32 %94, %72
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %80, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = fmul reassoc ninf nsz float %103, %76
  %reass.add = fadd reassoc ninf nsz float %104, %99
  %reass.add13 = fadd reassoc ninf nsz float %88, %93
  %105 = fsub reassoc ninf nsz float %reass.add, %reass.add13
  %106 = fmul reassoc ninf nsz float %74, %105
  %107 = fadd reassoc ninf nsz float %reass.add13, %106
  %108 = getelementptr i8, ptr %78, i64 72
  %109 = load ptr, ptr %108, align 8
  %110 = getelementptr i8, ptr %78, i64 68
  %111 = load i32, ptr %110, align 4
  %112 = mul i32 %111, %38
  %113 = sub i32 %112, %37
  %114 = add i32 %41, %113
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %109, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = fadd reassoc ninf nsz float %107, %117
  store float %118, ptr %116, align 4
  %119 = load ptr, ptr %0, align 8
  %120 = getelementptr i8, ptr %119, i64 56
  %121 = load ptr, ptr %120, align 8
  %122 = getelementptr i8, ptr %119, i64 44
  %123 = load i32, ptr %122, align 4
  %124 = getelementptr i8, ptr %119, i64 48
  %125 = load i32, ptr %124, align 4
  %126 = mul i32 %123, %38
  %127 = sub i32 %126, %37
  %128 = add i32 %41, %127
  %129 = mul i32 %128, %125
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %121, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = getelementptr i8, ptr %119, i64 16
  %134 = load ptr, ptr %133, align 8
  %135 = getelementptr i8, ptr %119, i64 4
  %136 = load i32, ptr %135, align 4
  %137 = getelementptr i8, ptr %119, i64 8
  %138 = load i32, ptr %137, align 4
  %139 = mul i32 %136, %38
  %140 = sub i32 %139, %37
  %141 = add i32 %41, %140
  %142 = mul i32 %141, %138
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %134, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = fmul reassoc ninf nsz float %145, %107
  %147 = fadd reassoc ninf nsz float %146, %132
  %148 = getelementptr i8, ptr %119, i64 112
  %149 = load i32, ptr %148, align 4
  %.not = icmp eq i32 %149, 0
  br i1 %.not, label %after_if6, label %true_block4

after_if3:                                        ; preds = %after_if12, %true_block, %for_loop_body
  %150 = add nsw i32 %.01015, 1
  %exitcond.not = icmp eq i32 %18, %150
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %151 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0x3EB0C6F7A0000000)
  %152 = fdiv reassoc ninf nsz float %147, %151
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.08 = phi float [ %152, %true_block4 ], [ %147, %true_block1 ]
  store float %.08, ptr %131, align 4
  %153 = load ptr, ptr %120, align 8
  %154 = load i32, ptr %122, align 4
  %155 = load i32, ptr %124, align 4
  %156 = mul i32 %154, %38
  %157 = sub i32 %156, %37
  %158 = add i32 %41, %157
  %159 = mul i32 %158, %155
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %153, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = load ptr, ptr %133, align 8
  %165 = load i32, ptr %135, align 4
  %166 = load i32, ptr %137, align 4
  %167 = mul i32 %165, %38
  %168 = sub i32 %167, %37
  %169 = add i32 %41, %168
  %170 = mul i32 %169, %166
  %171 = add i32 %170, 1
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %164, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fmul reassoc ninf nsz float %174, %107
  %176 = fadd reassoc ninf nsz float %175, %163
  br i1 %.not, label %after_if9, label %true_block7

true_block7:                                      ; preds = %after_if6
  %177 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0x3EB0C6F7A0000000)
  %178 = fdiv reassoc ninf nsz float %176, %177
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.07 = phi float [ %178, %true_block7 ], [ %176, %after_if6 ]
  store float %.07, ptr %162, align 4
  %179 = load ptr, ptr %120, align 8
  %180 = load i32, ptr %122, align 4
  %181 = load i32, ptr %124, align 4
  %182 = mul i32 %180, %38
  %183 = sub i32 %182, %37
  %184 = add i32 %41, %183
  %185 = mul i32 %184, %181
  %186 = add i32 %185, 2
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, ptr %179, i64 %187
  %189 = load float, ptr %188, align 4
  %190 = load ptr, ptr %133, align 8
  %191 = load i32, ptr %135, align 4
  %192 = load i32, ptr %137, align 4
  %193 = mul i32 %191, %38
  %194 = sub i32 %193, %37
  %195 = add i32 %41, %194
  %196 = mul i32 %195, %192
  %197 = add i32 %196, 2
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %190, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = fmul reassoc ninf nsz float %200, %107
  %202 = fadd reassoc ninf nsz float %201, %189
  br i1 %.not, label %after_if12, label %true_block10

true_block10:                                     ; preds = %after_if9
  %203 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0x3EB0C6F7A0000000)
  %204 = fdiv reassoc ninf nsz float %202, %203
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %.0 = phi float [ %204, %true_block10 ], [ %202, %after_if9 ]
  store float %.0, ptr %188, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.16, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
