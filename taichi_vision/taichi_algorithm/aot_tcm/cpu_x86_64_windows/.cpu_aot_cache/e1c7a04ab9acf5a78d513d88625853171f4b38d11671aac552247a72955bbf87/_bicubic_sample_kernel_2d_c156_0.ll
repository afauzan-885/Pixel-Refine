; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_sample_kernel_2d_c156_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_bicubic_sample_kernel_2d_c156_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 52
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 56
  %23 = load i32, ptr %22, align 4
  %24 = add i32 %21, -1
  %25 = add i32 %23, -1
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr i8, ptr %19, i64 24
  %28 = getelementptr i8, ptr %19, i64 20
  %29 = getelementptr i8, ptr %19, i64 8
  %30 = getelementptr i8, ptr %19, i64 4
  %31 = getelementptr i8, ptr %19, i64 40
  %32 = sext i32 %16 to i64
  %wide.trip.count = sext i32 %18 to i64
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %indvars.iv = phi i64 [ %32, %for_loop_body.lr.ph ], [ %indvars.iv.next, %for_loop_body ]
  %lsr51 = trunc i64 %indvars.iv to i32
  %33 = load ptr, ptr %27, align 8
  %34 = load i32, ptr %28, align 4
  %35 = mul i32 %34, %lsr51
  %36 = sext i32 %35 to i64
  %37 = getelementptr float, ptr %33, i64 %36
  %38 = load float, ptr %37, align 4
  %39 = add i32 %35, 1
  %40 = sext i32 %39 to i64
  %41 = getelementptr float, ptr %33, i64 %40
  %42 = load float, ptr %41, align 4
  %43 = tail call reassoc ninf nsz float @llvm.floor.f32(float %38)
  %44 = fptosi float %43 to i32
  %45 = tail call reassoc ninf nsz float @llvm.floor.f32(float %42)
  %46 = fptosi float %45 to i32
  %47 = sitofp i32 %44 to float
  %48 = fsub reassoc ninf nsz float %38, %47
  %49 = sitofp i32 %46 to float
  %50 = load ptr, ptr %29, align 8
  %51 = load i32, ptr %30, align 4
  %52 = add i32 %44, -1
  %53 = tail call i32 @llvm.smax.i32(i32 %52, i32 0)
  %54 = tail call i32 @llvm.smin.i32(i32 %25, i32 %53)
  %55 = add i32 %46, -1
  %56 = tail call i32 @llvm.smax.i32(i32 %55, i32 0)
  %57 = tail call i32 @llvm.smin.i32(i32 %24, i32 %56)
  %58 = mul i32 %51, %57
  %59 = add i32 %58, %54
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %50, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = tail call i32 @llvm.smax.i32(i32 %44, i32 0)
  %64 = tail call i32 @llvm.smin.i32(i32 %25, i32 %63)
  %65 = add i32 %58, %64
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %50, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = add i32 %44, 1
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = tail call i32 @llvm.smin.i32(i32 %25, i32 %70)
  %72 = add i32 %58, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %50, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = add i32 %44, 2
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %25, i32 %77)
  %79 = add i32 %58, %78
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %50, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = fmul reassoc ninf nsz float %62, -5.000000e-01
  %84 = fmul reassoc ninf nsz float %82, 5.000000e-01
  %reass.add28 = fsub reassoc ninf nsz float %68, %75
  %reass.mul29 = fmul reassoc ninf nsz float %reass.add28, 1.500000e+00
  %85 = fadd reassoc ninf nsz float %84, %83
  %86 = fadd reassoc ninf nsz float %85, %reass.mul29
  %.neg21 = fmul reassoc ninf nsz float %68, -2.500000e+00
  %factor24 = fmul reassoc ninf nsz float %75, 2.000000e+00
  %87 = fadd reassoc ninf nsz float %.neg21, %62
  %88 = fmul reassoc ninf nsz float %75, 5.000000e-01
  %89 = fadd reassoc ninf nsz float %88, %83
  %90 = fmul reassoc ninf nsz float %86, %48
  %91 = fadd reassoc ninf nsz float %87, %factor24
  %92 = fsub reassoc ninf nsz float %91, %84
  %reass.add25 = fadd reassoc ninf nsz float %92, %90
  %reass.mul26 = fmul reassoc ninf nsz float %reass.add25, %48
  %reass.add30 = fadd reassoc ninf nsz float %89, %reass.mul26
  %reass.mul31 = fmul reassoc ninf nsz float %reass.add30, %48
  %93 = fadd reassoc ninf nsz float %reass.mul31, %68
  %94 = tail call i32 @llvm.smax.i32(i32 %46, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %24, i32 %94)
  %96 = mul i32 %51, %95
  %97 = add i32 %96, %54
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %50, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = add i32 %96, %64
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %50, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = add i32 %96, %71
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %50, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = add i32 %96, %78
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %50, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fmul reassoc ninf nsz float %100, -5.000000e-01
  %114 = fmul reassoc ninf nsz float %112, 5.000000e-01
  %reass.add28.1 = fsub reassoc ninf nsz float %104, %108
  %reass.mul29.1 = fmul reassoc ninf nsz float %reass.add28.1, 1.500000e+00
  %115 = fadd reassoc ninf nsz float %114, %113
  %116 = fadd reassoc ninf nsz float %115, %reass.mul29.1
  %.neg21.1 = fmul reassoc ninf nsz float %104, -2.500000e+00
  %factor24.1 = fmul reassoc ninf nsz float %108, 2.000000e+00
  %117 = fadd reassoc ninf nsz float %.neg21.1, %100
  %118 = fmul reassoc ninf nsz float %108, 5.000000e-01
  %119 = fadd reassoc ninf nsz float %118, %113
  %120 = fmul reassoc ninf nsz float %116, %48
  %121 = fadd reassoc ninf nsz float %117, %factor24.1
  %122 = fsub reassoc ninf nsz float %121, %114
  %reass.add25.1 = fadd reassoc ninf nsz float %122, %120
  %reass.mul26.1 = fmul reassoc ninf nsz float %reass.add25.1, %48
  %reass.add30.1 = fadd reassoc ninf nsz float %119, %reass.mul26.1
  %reass.mul31.1 = fmul reassoc ninf nsz float %reass.add30.1, %48
  %123 = fadd reassoc ninf nsz float %reass.mul31.1, %104
  %124 = add i32 %46, 1
  %125 = tail call i32 @llvm.smax.i32(i32 %124, i32 0)
  %126 = tail call i32 @llvm.smin.i32(i32 %24, i32 %125)
  %127 = mul i32 %51, %126
  %128 = add i32 %127, %54
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %50, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = add i32 %127, %64
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %50, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = add i32 %127, %71
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %50, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = add i32 %127, %78
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %50, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = fmul reassoc ninf nsz float %131, -5.000000e-01
  %145 = fmul reassoc ninf nsz float %143, 5.000000e-01
  %reass.add28.2 = fsub reassoc ninf nsz float %135, %139
  %reass.mul29.2 = fmul reassoc ninf nsz float %reass.add28.2, 1.500000e+00
  %146 = fadd reassoc ninf nsz float %145, %144
  %147 = fadd reassoc ninf nsz float %146, %reass.mul29.2
  %.neg21.2 = fmul reassoc ninf nsz float %135, -2.500000e+00
  %factor24.2 = fmul reassoc ninf nsz float %139, 2.000000e+00
  %148 = fadd reassoc ninf nsz float %.neg21.2, %131
  %149 = fmul reassoc ninf nsz float %139, 5.000000e-01
  %150 = fadd reassoc ninf nsz float %149, %144
  %151 = fmul reassoc ninf nsz float %147, %48
  %152 = fadd reassoc ninf nsz float %148, %factor24.2
  %153 = fsub reassoc ninf nsz float %152, %145
  %reass.add25.2 = fadd reassoc ninf nsz float %153, %151
  %reass.mul26.2 = fmul reassoc ninf nsz float %reass.add25.2, %48
  %reass.add30.2 = fadd reassoc ninf nsz float %150, %reass.mul26.2
  %reass.mul31.2 = fmul reassoc ninf nsz float %reass.add30.2, %48
  %154 = fadd reassoc ninf nsz float %reass.mul31.2, %135
  %155 = add i32 %46, 2
  %156 = tail call i32 @llvm.smax.i32(i32 %155, i32 0)
  %157 = tail call i32 @llvm.smin.i32(i32 %24, i32 %156)
  %158 = mul i32 %51, %157
  %159 = add i32 %158, %54
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %50, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %158, %64
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %50, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = add i32 %158, %71
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, ptr %50, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = add i32 %158, %78
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %50, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fmul reassoc ninf nsz float %162, -5.000000e-01
  %176 = fmul reassoc ninf nsz float %174, 5.000000e-01
  %reass.add28.3 = fsub reassoc ninf nsz float %166, %170
  %reass.mul29.3 = fmul reassoc ninf nsz float %reass.add28.3, 1.500000e+00
  %177 = fadd reassoc ninf nsz float %176, %175
  %178 = fadd reassoc ninf nsz float %177, %reass.mul29.3
  %.neg21.3 = fmul reassoc ninf nsz float %166, -2.500000e+00
  %factor24.3 = fmul reassoc ninf nsz float %170, 2.000000e+00
  %179 = fadd reassoc ninf nsz float %.neg21.3, %162
  %180 = fmul reassoc ninf nsz float %170, 5.000000e-01
  %181 = fadd reassoc ninf nsz float %180, %175
  %182 = fmul reassoc ninf nsz float %178, %48
  %183 = fadd reassoc ninf nsz float %179, %factor24.3
  %184 = fsub reassoc ninf nsz float %183, %176
  %reass.add25.3 = fadd reassoc ninf nsz float %184, %182
  %reass.mul26.3 = fmul reassoc ninf nsz float %reass.add25.3, %48
  %reass.add30.3 = fadd reassoc ninf nsz float %181, %reass.mul26.3
  %reass.mul31.3 = fmul reassoc ninf nsz float %reass.add30.3, %48
  %185 = fadd reassoc ninf nsz float %reass.mul31.3, %166
  %186 = fsub reassoc ninf nsz float %42, %49
  %187 = fmul reassoc ninf nsz float %93, -5.000000e-01
  %188 = fmul reassoc ninf nsz float %185, 5.000000e-01
  %reass.add16 = fsub reassoc ninf nsz float %123, %154
  %reass.mul17 = fmul reassoc ninf nsz float %reass.add16, 1.500000e+00
  %189 = fadd reassoc ninf nsz float %188, %187
  %190 = fadd reassoc ninf nsz float %189, %reass.mul17
  %.neg13 = fmul reassoc ninf nsz float %123, -2.500000e+00
  %factor = fmul reassoc ninf nsz float %154, 2.000000e+00
  %191 = fadd reassoc ninf nsz float %.neg13, %93
  %192 = fmul reassoc ninf nsz float %154, 5.000000e-01
  %193 = fadd reassoc ninf nsz float %192, %187
  %194 = fmul reassoc ninf nsz float %190, %186
  %195 = fadd reassoc ninf nsz float %191, %factor
  %196 = fsub reassoc ninf nsz float %195, %188
  %reass.add = fadd reassoc ninf nsz float %196, %194
  %reass.mul = fmul reassoc ninf nsz float %reass.add, %186
  %reass.add18 = fadd reassoc ninf nsz float %193, %reass.mul
  %reass.mul19 = fmul reassoc ninf nsz float %reass.add18, %186
  %197 = fadd reassoc ninf nsz float %reass.mul19, %123
  %198 = load ptr, ptr %31, align 8
  %199 = shl i64 %indvars.iv, 2
  %scevgep = getelementptr i8, ptr %198, i64 %199
  store float %197, ptr %scevgep, align 4
  %indvars.iv.next = add nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %wide.trip.count, %indvars.iv.next
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

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
