; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @search_coarse_level_kernel_c86_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 12
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 24
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 56
  %16 = load i32, ptr %15, align 4
  %17 = load ptr, ptr %2, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 40
  store i32 %16, ptr %20, align 4
  %21 = load ptr, ptr %context, align 8
  %22 = getelementptr i8, ptr %21, i64 60
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %2, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 44
  store i32 %23, ptr %27, align 4
  %28 = load ptr, ptr %context, align 8
  %29 = getelementptr i8, ptr %28, i64 104
  %30 = load i32, ptr %29, align 4
  %31 = load ptr, ptr %2, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 16
  store i32 %30, ptr %34, align 4
  %35 = sdiv i32 %30, 2
  %36 = icmp slt i32 %30, 0
  %37 = shl nsw i32 %35, 1
  %38 = icmp ne i32 %37, %30
  %39 = and i1 %36, %38
  %.neg = sext i1 %39 to i32
  %40 = add nsw i32 %35, %.neg
  %41 = load ptr, ptr %2, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32
  store i32 %40, ptr %44, align 4
  %45 = tail call i32 @llvm.smax.i32(i32 %40, i32 1)
  %46 = load ptr, ptr %2, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 8
  store i32 %45, ptr %49, align 4
  %50 = load ptr, ptr %context, align 8
  %51 = getelementptr i8, ptr %50, i64 108
  %52 = load i32, ptr %51, align 4
  %53 = load ptr, ptr %2, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 32872
  %55 = load ptr, ptr %54, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 28
  store i32 %52, ptr %56, align 4
  %57 = sdiv i32 %52, 2
  %58 = icmp slt i32 %52, 0
  %59 = shl nsw i32 %57, 1
  %60 = icmp ne i32 %59, %52
  %61 = and i1 %58, %60
  %.neg1 = sext i1 %61 to i32
  %62 = add nsw i32 %57, %.neg1
  %63 = load ptr, ptr %2, align 8
  %64 = getelementptr inbounds nuw i8, ptr %63, i64 32872
  %65 = load ptr, ptr %64, align 8
  %66 = getelementptr inbounds nuw i8, ptr %65, i64 36
  store i32 %62, ptr %66, align 4
  %67 = tail call i32 @llvm.smax.i32(i32 %62, i32 1)
  %68 = load ptr, ptr %2, align 8
  %69 = getelementptr inbounds nuw i8, ptr %68, i64 32872
  %70 = load ptr, ptr %69, align 8
  %71 = getelementptr inbounds nuw i8, ptr %70, i64 20
  store i32 %67, ptr %71, align 4
  %72 = mul i32 %52, %30
  %73 = sitofp i32 %72 to float
  %74 = fdiv reassoc ninf nsz float 1.000000e+00, %73
  %75 = load ptr, ptr %2, align 8
  %76 = getelementptr inbounds nuw i8, ptr %75, i64 32872
  %77 = load ptr, ptr %76, align 8
  %78 = getelementptr inbounds nuw i8, ptr %77, i64 48
  store float %74, ptr %78, align 4
  %79 = add i32 %1, -1
  %80 = add i32 %79, %45
  %81 = sdiv i32 %80, %45
  %82 = mul i32 %81, %45
  %83 = icmp slt i32 %80, 0
  %84 = icmp ne i32 %82, %80
  %85 = and i1 %83, %84
  %.neg2 = sext i1 %85 to i32
  %86 = add i32 %81, %.neg2
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = add i32 %9, -1
  %89 = add i32 %88, %67
  %90 = sdiv i32 %89, %67
  %91 = mul i32 %90, %67
  %92 = icmp slt i32 %89, 0
  %93 = icmp ne i32 %91, %89
  %94 = and i1 %92, %93
  %.neg3 = sext i1 %94 to i32
  %95 = add i32 %90, %.neg3
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = load ptr, ptr %2, align 8
  %98 = getelementptr inbounds nuw i8, ptr %97, i64 32872
  %99 = load ptr, ptr %98, align 8
  %100 = getelementptr inbounds nuw i8, ptr %99, i64 4
  store i32 %96, ptr %100, align 4
  %101 = mul i32 %96, %87
  %102 = load ptr, ptr %2, align 8
  %103 = getelementptr inbounds nuw i8, ptr %102, i64 32872
  %104 = load ptr, ptr %103, align 8
  store i32 %101, ptr %104, align 4
  ret void
}

define void @search_coarse_level_kernel_c86_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = sdiv i32 %21, 2
  %23 = icmp slt i32 %21, 0
  %24 = shl nsw i32 %22, 1
  %25 = icmp ne i32 %24, %21
  %26 = and i1 %23, %25
  %.neg320 = sext i1 %26 to i32
  %27 = add nsw i32 %22, %.neg320
  %28 = tail call i32 @llvm.smax.i32(i32 %27, i32 1)
  %29 = icmp slt i32 %16, %18
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr i8, ptr %19, i64 48
  %31 = getelementptr i8, ptr %19, i64 36
  %32 = getelementptr i8, ptr %19, i64 40
  %reass.add = shl nuw i32 %28, 1
  %33 = or disjoint i32 %reass.add, 1
  %34 = mul i32 %33, %33
  %35 = icmp sgt i32 %34, 0
  br label %after_if7

after_for.loopexit:                               ; preds = %after_for338
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if7.1:                                      ; preds = %true_block17, %true_block11, %after_if7
  %.0231 = phi float [ %228, %true_block17 ], [ 0.000000e+00, %true_block11 ], [ 0.000000e+00, %after_if7 ]
  %.0229 = phi float [ %232, %true_block17 ], [ 0.000000e+00, %true_block11 ], [ 0.000000e+00, %after_if7 ]
  %.0227 = phi float [ 1.000000e+00, %true_block17 ], [ 0.000000e+00, %true_block11 ], [ 0.000000e+00, %after_if7 ]
  br i1 %spec.select333, label %true_block11.1, label %after_if7.2

true_block11.1:                                   ; preds = %after_if7.1
  %36 = icmp sgt i32 %208, -1
  %37 = icmp slt i32 %208, %213
  %spec.select334.1 = select i1 %36, i1 %37, i1 false
  br i1 %spec.select334.1, label %true_block17.1, label %after_if7.2

true_block17.1:                                   ; preds = %true_block11.1
  %38 = load ptr, ptr %30, align 8
  %39 = load i32, ptr %31, align 4
  %40 = load i32, ptr %32, align 4
  %41 = mul i32 %39, %214
  %42 = add i32 %41, %208
  %43 = mul i32 %42, %40
  %44 = sext i32 %43 to i64
  %45 = getelementptr float, ptr %38, i64 %44
  %46 = load float, ptr %45, align 4
  %47 = fadd reassoc ninf nsz float %46, %.0231
  %48 = add i32 %43, 1
  %49 = sext i32 %48 to i64
  %50 = getelementptr float, ptr %38, i64 %49
  %51 = load float, ptr %50, align 4
  %52 = fadd reassoc ninf nsz float %51, %.0229
  %53 = fadd reassoc ninf nsz float %.0227, 1.000000e+00
  br label %after_if7.2

after_if7.2:                                      ; preds = %true_block17.1, %true_block11.1, %after_if7.1
  %.0231.1 = phi float [ %47, %true_block17.1 ], [ %.0231, %true_block11.1 ], [ %.0231, %after_if7.1 ]
  %.0229.1 = phi float [ %52, %true_block17.1 ], [ %.0229, %true_block11.1 ], [ %.0229, %after_if7.1 ]
  %.0227.1 = phi float [ %53, %true_block17.1 ], [ %.0227, %true_block11.1 ], [ %.0227, %after_if7.1 ]
  %54 = add i32 %199, %208
  br i1 %spec.select333, label %true_block11.2, label %after_if7.3

true_block11.2:                                   ; preds = %after_if7.2
  %55 = icmp sgt i32 %54, -1
  %56 = icmp slt i32 %54, %213
  %spec.select334.2 = select i1 %55, i1 %56, i1 false
  br i1 %spec.select334.2, label %true_block17.2, label %after_if7.3

true_block17.2:                                   ; preds = %true_block11.2
  %57 = load ptr, ptr %30, align 8
  %58 = load i32, ptr %31, align 4
  %59 = load i32, ptr %32, align 4
  %60 = mul i32 %58, %214
  %61 = add i32 %60, %54
  %62 = mul i32 %61, %59
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, ptr %57, i64 %63
  %65 = load float, ptr %64, align 4
  %66 = fadd reassoc ninf nsz float %65, %.0231.1
  %67 = add i32 %62, 1
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %57, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = fadd reassoc ninf nsz float %70, %.0229.1
  %72 = fadd reassoc ninf nsz float %.0227.1, 1.000000e+00
  br label %after_if7.3

after_if7.3:                                      ; preds = %true_block17.2, %true_block11.2, %after_if7.2
  %.0231.2 = phi float [ %66, %true_block17.2 ], [ %.0231.1, %true_block11.2 ], [ %.0231.1, %after_if7.2 ]
  %.0229.2 = phi float [ %71, %true_block17.2 ], [ %.0229.1, %true_block11.2 ], [ %.0229.1, %after_if7.2 ]
  %.0227.2 = phi float [ %72, %true_block17.2 ], [ %.0227.1, %true_block11.2 ], [ %.0227.1, %after_if7.2 ]
  %73 = icmp sgt i32 %205, -1
  %74 = icmp slt i32 %205, %211
  %spec.select333.3 = select i1 %73, i1 %74, i1 false
  br i1 %spec.select333.3, label %true_block11.3, label %after_if7.5

true_block11.3:                                   ; preds = %after_if7.3
  %75 = icmp sgt i32 %215, -1
  %76 = icmp slt i32 %215, %213
  %spec.select334.3 = select i1 %75, i1 %76, i1 false
  br i1 %spec.select334.3, label %true_block17.3, label %after_if7.5

true_block17.3:                                   ; preds = %true_block11.3
  %77 = load ptr, ptr %30, align 8
  %78 = load i32, ptr %31, align 4
  %79 = load i32, ptr %32, align 4
  %80 = mul i32 %78, %205
  %81 = add i32 %80, %215
  %82 = mul i32 %81, %79
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %77, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fadd reassoc ninf nsz float %85, %.0231.2
  %87 = add i32 %82, 1
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %77, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = fadd reassoc ninf nsz float %90, %.0229.2
  %92 = fadd reassoc ninf nsz float %.0227.2, 1.000000e+00
  br label %after_if7.5

after_if7.5:                                      ; preds = %true_block17.3, %true_block11.3, %after_if7.3
  %.0231.3 = phi float [ %86, %true_block17.3 ], [ %.0231.2, %true_block11.3 ], [ %.0231.2, %after_if7.3 ]
  %.0229.3 = phi float [ %91, %true_block17.3 ], [ %.0229.2, %true_block11.3 ], [ %.0229.2, %after_if7.3 ]
  %.0227.3 = phi float [ %92, %true_block17.3 ], [ %.0227.2, %true_block11.3 ], [ %.0227.2, %after_if7.3 ]
  br i1 %spec.select333.3, label %true_block11.5, label %after_if7.6

true_block11.5:                                   ; preds = %after_if7.5
  %93 = icmp sgt i32 %54, -1
  %94 = icmp slt i32 %54, %213
  %spec.select334.5 = select i1 %93, i1 %94, i1 false
  br i1 %spec.select334.5, label %true_block17.5, label %after_if7.6

true_block17.5:                                   ; preds = %true_block11.5
  %95 = load ptr, ptr %30, align 8
  %96 = load i32, ptr %31, align 4
  %97 = load i32, ptr %32, align 4
  %98 = mul i32 %96, %205
  %99 = add i32 %98, %54
  %100 = mul i32 %99, %97
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %95, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = fadd reassoc ninf nsz float %103, %.0231.3
  %105 = add i32 %100, 1
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %95, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = fadd reassoc ninf nsz float %108, %.0229.3
  %110 = fadd reassoc ninf nsz float %.0227.3, 1.000000e+00
  br label %after_if7.6

after_if7.6:                                      ; preds = %true_block17.5, %true_block11.5, %after_if7.5
  %.0231.5 = phi float [ %104, %true_block17.5 ], [ %.0231.3, %true_block11.5 ], [ %.0231.3, %after_if7.5 ]
  %.0229.5 = phi float [ %109, %true_block17.5 ], [ %.0229.3, %true_block11.5 ], [ %.0229.3, %after_if7.5 ]
  %.0227.5 = phi float [ %110, %true_block17.5 ], [ %.0227.3, %true_block11.5 ], [ %.0227.3, %after_if7.5 ]
  %111 = add i32 %189, %205
  %112 = icmp sgt i32 %111, -1
  %113 = icmp slt i32 %111, %211
  %spec.select333.6 = select i1 %112, i1 %113, i1 false
  br i1 %spec.select333.6, label %true_block11.6, label %after_if7.7

true_block11.6:                                   ; preds = %after_if7.6
  %114 = icmp sgt i32 %215, -1
  %115 = icmp slt i32 %215, %213
  %spec.select334.6 = select i1 %114, i1 %115, i1 false
  br i1 %spec.select334.6, label %true_block17.6, label %after_if7.7

true_block17.6:                                   ; preds = %true_block11.6
  %116 = load ptr, ptr %30, align 8
  %117 = load i32, ptr %31, align 4
  %118 = load i32, ptr %32, align 4
  %119 = mul i32 %117, %111
  %120 = add i32 %119, %215
  %121 = mul i32 %120, %118
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %116, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fadd reassoc ninf nsz float %124, %.0231.5
  %126 = add i32 %121, 1
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %116, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fadd reassoc ninf nsz float %129, %.0229.5
  %131 = fadd reassoc ninf nsz float %.0227.5, 1.000000e+00
  br label %after_if7.7

after_if7.7:                                      ; preds = %true_block17.6, %true_block11.6, %after_if7.6
  %.0231.6 = phi float [ %125, %true_block17.6 ], [ %.0231.5, %true_block11.6 ], [ %.0231.5, %after_if7.6 ]
  %.0229.6 = phi float [ %130, %true_block17.6 ], [ %.0229.5, %true_block11.6 ], [ %.0229.5, %after_if7.6 ]
  %.0227.6 = phi float [ %131, %true_block17.6 ], [ %.0227.5, %true_block11.6 ], [ %.0227.5, %after_if7.6 ]
  br i1 %spec.select333.6, label %true_block11.7, label %after_if7.8

true_block11.7:                                   ; preds = %after_if7.7
  %132 = icmp sgt i32 %208, -1
  %133 = icmp slt i32 %208, %213
  %spec.select334.7 = select i1 %132, i1 %133, i1 false
  br i1 %spec.select334.7, label %true_block17.7, label %after_if7.8

true_block17.7:                                   ; preds = %true_block11.7
  %134 = load ptr, ptr %30, align 8
  %135 = load i32, ptr %31, align 4
  %136 = load i32, ptr %32, align 4
  %137 = mul i32 %135, %111
  %138 = add i32 %137, %208
  %139 = mul i32 %138, %136
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %134, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = fadd reassoc ninf nsz float %142, %.0231.6
  %144 = add i32 %139, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %134, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = fadd reassoc ninf nsz float %147, %.0229.6
  %149 = fadd reassoc ninf nsz float %.0227.6, 1.000000e+00
  br label %after_if7.8

after_if7.8:                                      ; preds = %true_block17.7, %true_block11.7, %after_if7.7
  %.0231.7 = phi float [ %143, %true_block17.7 ], [ %.0231.6, %true_block11.7 ], [ %.0231.6, %after_if7.7 ]
  %.0229.7 = phi float [ %148, %true_block17.7 ], [ %.0229.6, %true_block11.7 ], [ %.0229.6, %after_if7.7 ]
  %.0227.7 = phi float [ %149, %true_block17.7 ], [ %.0227.6, %true_block11.7 ], [ %.0227.6, %after_if7.7 ]
  br i1 %spec.select333.6, label %true_block11.8, label %for_loop_inc2.8

true_block11.8:                                   ; preds = %after_if7.8
  %150 = icmp sgt i32 %54, -1
  %151 = icmp slt i32 %54, %213
  %spec.select334.8 = select i1 %150, i1 %151, i1 false
  br i1 %spec.select334.8, label %true_block17.8, label %for_loop_inc2.8

true_block17.8:                                   ; preds = %true_block11.8
  %152 = load ptr, ptr %30, align 8
  %153 = load i32, ptr %31, align 4
  %154 = load i32, ptr %32, align 4
  %155 = mul i32 %153, %111
  %156 = add i32 %155, %54
  %157 = mul i32 %156, %154
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %152, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = fadd reassoc ninf nsz float %160, %.0231.7
  %162 = add i32 %157, 1
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %152, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = fadd reassoc ninf nsz float %165, %.0229.7
  %167 = fadd reassoc ninf nsz float %.0227.7, 1.000000e+00
  br label %for_loop_inc2.8

for_loop_inc2.8:                                  ; preds = %true_block17.8, %true_block11.8, %after_if7.8
  %.0231.8 = phi float [ %161, %true_block17.8 ], [ %.0231.7, %true_block11.8 ], [ %.0231.7, %after_if7.8 ]
  %.0229.8 = phi float [ %166, %true_block17.8 ], [ %.0229.7, %true_block11.8 ], [ %.0229.7, %after_if7.8 ]
  %.0227.8 = phi float [ %167, %true_block17.8 ], [ %.0227.7, %true_block11.8 ], [ %.0227.7, %after_if7.8 ]
  %168 = fcmp reassoc ninf nsz ogt float %.0227.8, 0.000000e+00
  br i1 %168, label %true_block20, label %false_block21

after_if7:                                        ; preds = %after_for338, %for_loop_body.lr.ph
  %.0233454 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %750, %after_for338 ]
  %169 = load ptr, ptr %3, align 8
  %170 = getelementptr inbounds nuw i8, ptr %169, i64 32872
  %171 = load ptr, ptr %170, align 8
  %172 = getelementptr inbounds nuw i8, ptr %171, i64 4
  %173 = load i32, ptr %172, align 4
  %174 = sdiv i32 %.0233454, %173
  %175 = mul i32 %174, %173
  %176 = xor i32 %173, %.0233454
  %177 = icmp slt i32 %176, 0
  %178 = icmp ne i32 %175, %.0233454
  %179 = and i1 %177, %178
  %.neg321 = sext i1 %179 to i32
  %180 = add i32 %174, %.neg321
  %181 = mul i32 %180, %173
  %182 = sub i32 %.0233454, %181
  %183 = getelementptr inbounds nuw i8, ptr %171, i64 8
  %184 = load i32, ptr %183, align 4
  %185 = mul i32 %180, %184
  %186 = getelementptr inbounds nuw i8, ptr %171, i64 12
  %187 = load i32, ptr %186, align 4
  %188 = getelementptr inbounds nuw i8, ptr %171, i64 16
  %189 = load i32, ptr %188, align 4
  %190 = sub i32 %187, %189
  %191 = tail call i32 @llvm.smin.i32(i32 %185, i32 %190)
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = getelementptr inbounds nuw i8, ptr %171, i64 20
  %194 = load i32, ptr %193, align 4
  %195 = mul i32 %182, %194
  %196 = getelementptr inbounds nuw i8, ptr %171, i64 24
  %197 = load i32, ptr %196, align 4
  %198 = getelementptr inbounds nuw i8, ptr %171, i64 28
  %199 = load i32, ptr %198, align 4
  %200 = sub i32 %197, %199
  %201 = tail call i32 @llvm.smin.i32(i32 %195, i32 %200)
  %202 = tail call i32 @llvm.smax.i32(i32 %201, i32 0)
  %203 = getelementptr inbounds nuw i8, ptr %171, i64 32
  %204 = load i32, ptr %203, align 4
  %205 = add i32 %192, %204
  %206 = getelementptr inbounds nuw i8, ptr %171, i64 36
  %207 = load i32, ptr %206, align 4
  %208 = add i32 %202, %207
  %209 = load ptr, ptr %0, align 8
  %210 = getelementptr i8, ptr %209, i64 32
  %211 = load i32, ptr %210, align 4
  %212 = getelementptr i8, ptr %209, i64 36
  %213 = load i32, ptr %212, align 4
  %214 = sub i32 %205, %189
  %215 = sub i32 %208, %199
  %216 = icmp sgt i32 %214, -1
  %217 = icmp slt i32 %214, %211
  %spec.select333 = select i1 %216, i1 %217, i1 false
  br i1 %spec.select333, label %true_block11, label %after_if7.1

true_block11:                                     ; preds = %after_if7
  %218 = icmp sgt i32 %215, -1
  %219 = icmp slt i32 %215, %213
  %spec.select334 = select i1 %218, i1 %219, i1 false
  br i1 %spec.select334, label %true_block17, label %after_if7.1

true_block17:                                     ; preds = %true_block11
  %220 = load ptr, ptr %30, align 8
  %221 = load i32, ptr %31, align 4
  %222 = load i32, ptr %32, align 4
  %223 = mul i32 %221, %214
  %224 = add i32 %223, %215
  %225 = mul i32 %224, %222
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %220, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = add i32 %225, 1
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %220, i64 %230
  %232 = load float, ptr %231, align 4
  br label %after_if7.1

true_block20:                                     ; preds = %for_loop_inc2.8
  %233 = fdiv reassoc ninf nsz float %.0231.8, %.0227.8
  %234 = fdiv reassoc ninf nsz float %.0229.8, %.0227.8
  %235 = load ptr, ptr %30, align 8
  %236 = load i32, ptr %31, align 4
  %237 = load i32, ptr %32, align 4
  %238 = mul i32 %236, %205
  %239 = add i32 %238, %208
  %240 = mul i32 %239, %237
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %235, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = add i32 %240, 1
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, ptr %235, i64 %245
  %247 = load float, ptr %246, align 4
  %248 = fsub reassoc ninf nsz float %243, %233
  %249 = fmul reassoc ninf nsz float %248, %248
  %250 = fsub reassoc ninf nsz float %247, %234
  %251 = fmul reassoc ninf nsz float %250, %250
  %252 = fadd reassoc ninf nsz float %251, %249
  %253 = fcmp reassoc ninf nsz ogt float %252, 9.000000e+00
  br i1 %253, label %true_block23, label %after_if22

false_block21:                                    ; preds = %for_loop_inc2.8
  %254 = load ptr, ptr %30, align 8
  %255 = load i32, ptr %31, align 4
  %256 = load i32, ptr %32, align 4
  %257 = mul i32 %255, %205
  %258 = add i32 %257, %208
  %259 = mul i32 %258, %256
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, ptr %254, i64 %260
  %262 = load float, ptr %261, align 4
  %263 = add i32 %259, 1
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %254, i64 %264
  %266 = load float, ptr %265, align 4
  br label %after_if22

after_if22:                                       ; preds = %true_block23, %false_block21, %true_block20
  %.pre-phi575 = phi i32 [ %238, %true_block23 ], [ %238, %true_block20 ], [ %257, %false_block21 ]
  %267 = phi float [ %247, %true_block23 ], [ %247, %true_block20 ], [ %266, %false_block21 ]
  %268 = phi float [ %243, %true_block23 ], [ %243, %true_block20 ], [ %262, %false_block21 ]
  %269 = phi i32 [ %237, %true_block23 ], [ %237, %true_block20 ], [ %256, %false_block21 ]
  %270 = phi i32 [ %236, %true_block23 ], [ %236, %true_block20 ], [ %255, %false_block21 ]
  %271 = phi ptr [ %235, %true_block23 ], [ %235, %true_block20 ], [ %254, %false_block21 ]
  %.0221 = phi float [ %233, %true_block23 ], [ %233, %true_block20 ], [ %262, %false_block21 ]
  %.0220 = phi float [ %234, %true_block23 ], [ %234, %true_block20 ], [ %266, %false_block21 ]
  %.0219 = phi float [ 4.000000e+00, %true_block23 ], [ 1.000000e+00, %true_block20 ], [ 1.000000e+00, %false_block21 ]
  %272 = tail call reassoc ninf nsz float @llvm.round.f32(float %268)
  %273 = fptosi float %272 to i32
  %274 = tail call reassoc ninf nsz float @llvm.round.f32(float %267)
  %275 = fptosi float %274 to i32
  %276 = getelementptr i8, ptr %209, i64 20
  %277 = load i32, ptr %276, align 4
  %278 = getelementptr inbounds nuw i8, ptr %171, i64 48
  %279 = load float, ptr %278, align 4
  %280 = getelementptr inbounds nuw i8, ptr %171, i64 40
  %281 = getelementptr inbounds nuw i8, ptr %171, i64 44
  %282 = getelementptr i8, ptr %209, i64 116
  %283 = getelementptr i8, ptr %209, i64 72
  %284 = getelementptr i8, ptr %209, i64 60
  %285 = getelementptr i8, ptr %209, i64 64
  %286 = shl i32 %199, 1
  %287 = add i32 %208, %286
  %288 = shl i32 %189, 1
  %289 = sub i32 %205, %288
  %290 = icmp slt i32 %289, 0
  %291 = icmp sge i32 %289, %187
  %292 = icmp slt i32 %287, 0
  %293 = icmp sge i32 %287, %197
  %294 = mul i32 %270, %289
  %295 = add i32 %294, %287
  %296 = mul i32 %295, %269
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %271, i64 %297
  %299 = add i32 %296, 1
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %271, i64 %300
  %302 = sub i32 %208, %286
  %303 = icmp slt i32 %302, 0
  %304 = icmp sge i32 %302, %197
  %305 = add i32 %294, %302
  %306 = mul i32 %305, %269
  %307 = sext i32 %306 to i64
  %308 = getelementptr float, ptr %271, i64 %307
  %309 = add i32 %306, 1
  %310 = sext i32 %309 to i64
  %311 = getelementptr float, ptr %271, i64 %310
  %312 = add i32 %205, %288
  %313 = icmp slt i32 %312, 0
  %314 = icmp sge i32 %312, %187
  %315 = icmp slt i32 %208, 0
  %316 = icmp sge i32 %208, %197
  %317 = mul i32 %270, %312
  %318 = add i32 %317, %208
  %319 = mul i32 %318, %269
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, ptr %271, i64 %320
  %322 = add i32 %319, 1
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, ptr %271, i64 %323
  %325 = add i32 %294, %208
  %326 = mul i32 %325, %269
  %327 = sext i32 %326 to i64
  %328 = getelementptr float, ptr %271, i64 %327
  %329 = add i32 %326, 1
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, ptr %271, i64 %330
  %332 = icmp slt i32 %205, 0
  %333 = icmp sge i32 %205, %187
  %334 = add i32 %.pre-phi575, %287
  %335 = mul i32 %334, %269
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, ptr %271, i64 %336
  %338 = add i32 %335, 1
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, ptr %271, i64 %339
  %341 = add i32 %.pre-phi575, %302
  %342 = mul i32 %341, %269
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %271, i64 %343
  %345 = add i32 %342, 1
  %346 = sext i32 %345 to i64
  %347 = getelementptr float, ptr %271, i64 %346
  %348 = icmp slt i32 %111, 0
  %349 = icmp sge i32 %111, %187
  %350 = icmp slt i32 %54, 0
  %351 = icmp sge i32 %54, %197
  %352 = mul i32 %270, %111
  %353 = add i32 %352, %54
  %354 = mul i32 %353, %269
  %355 = sext i32 %354 to i64
  %356 = getelementptr float, ptr %271, i64 %355
  %357 = add i32 %354, 1
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, ptr %271, i64 %358
  %360 = icmp slt i32 %215, 0
  %361 = icmp sge i32 %215, %197
  %362 = add i32 %352, %215
  %363 = mul i32 %362, %269
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %271, i64 %364
  %366 = add i32 %363, 1
  %367 = sext i32 %366 to i64
  %368 = getelementptr float, ptr %271, i64 %367
  %369 = icmp slt i32 %214, 0
  %370 = icmp sge i32 %214, %187
  %371 = mul i32 %270, %214
  %372 = add i32 %371, %54
  %373 = mul i32 %372, %269
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %271, i64 %374
  %376 = add i32 %373, 1
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, ptr %271, i64 %377
  %379 = add i32 %371, %215
  %380 = mul i32 %379, %269
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, ptr %271, i64 %381
  %383 = add i32 %380, 1
  %384 = sext i32 %383 to i64
  %385 = getelementptr float, ptr %271, i64 %384
  %386 = add i32 %352, %208
  %387 = mul i32 %386, %269
  %388 = sext i32 %387 to i64
  %389 = getelementptr float, ptr %271, i64 %388
  %390 = add i32 %387, 1
  %391 = sext i32 %390 to i64
  %392 = getelementptr float, ptr %271, i64 %391
  %393 = add i32 %371, %208
  %394 = mul i32 %393, %269
  %395 = sext i32 %394 to i64
  %396 = getelementptr float, ptr %271, i64 %395
  %397 = add i32 %394, 1
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %271, i64 %398
  %400 = add i32 %.pre-phi575, %54
  %401 = mul i32 %400, %269
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %271, i64 %402
  %404 = add i32 %401, 1
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, ptr %271, i64 %405
  %407 = add i32 %.pre-phi575, %215
  %408 = mul i32 %407, %269
  %409 = sext i32 %408 to i64
  %410 = getelementptr float, ptr %271, i64 %409
  %411 = add i32 %408, 1
  %412 = sext i32 %411 to i64
  %413 = getelementptr float, ptr %271, i64 %412
  %414 = add i32 %317, %302
  %415 = mul i32 %414, %269
  %416 = sext i32 %415 to i64
  %417 = getelementptr float, ptr %271, i64 %416
  %418 = add i32 %415, 1
  %419 = sext i32 %418 to i64
  %420 = getelementptr float, ptr %271, i64 %419
  %421 = add i32 %317, %287
  %422 = mul i32 %421, %269
  %423 = sext i32 %422 to i64
  %424 = getelementptr float, ptr %271, i64 %423
  %425 = add i32 %422, 1
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, ptr %271, i64 %426
  %428 = getelementptr i8, ptr %209, i64 16
  %429 = add i32 %189, 1
  %430 = sdiv i32 %429, 2
  %431 = icmp slt i32 %429, 0
  %432 = shl nsw i32 %430, 1
  %433 = icmp ne i32 %432, %429
  %434 = and i1 %431, %433
  %.neg329 = sext i1 %434 to i32
  %435 = add i32 %430, %.neg329
  %436 = tail call i32 @llvm.smax.i32(i32 %435, i32 0)
  %437 = add i32 %199, 1
  %438 = sdiv i32 %437, 2
  %439 = icmp slt i32 %437, 0
  %440 = shl nsw i32 %438, 1
  %441 = icmp ne i32 %440, %437
  %442 = and i1 %439, %441
  %.neg330 = sext i1 %442 to i32
  %443 = add i32 %438, %.neg330
  %444 = tail call i32 @llvm.smax.i32(i32 %443, i32 0)
  %445 = mul i32 %444, %436
  %446 = icmp slt i32 %445, 1
  %447 = getelementptr i8, ptr %209, i64 8
  %448 = getelementptr i8, ptr %209, i64 4
  %449 = getelementptr i8, ptr %209, i64 24
  %450 = select i1 %290, i1 true, i1 %291
  %451 = select i1 %450, i1 true, i1 %292
  %brmerge481 = select i1 %451, i1 true, i1 %293
  %452 = select i1 %450, i1 true, i1 %303
  %brmerge479 = select i1 %452, i1 true, i1 %304
  %453 = select i1 %313, i1 true, i1 %314
  %454 = select i1 %453, i1 true, i1 %315
  %brmerge477 = select i1 %454, i1 true, i1 %316
  %455 = select i1 %450, i1 true, i1 %315
  %brmerge475 = select i1 %455, i1 true, i1 %316
  %456 = select i1 %332, i1 true, i1 %333
  %457 = select i1 %456, i1 true, i1 %292
  %brmerge473 = select i1 %457, i1 true, i1 %293
  %458 = select i1 %456, i1 true, i1 %303
  %brmerge471 = select i1 %458, i1 true, i1 %304
  %459 = select i1 %348, i1 true, i1 %349
  %460 = select i1 %459, i1 true, i1 %350
  %brmerge469 = select i1 %460, i1 true, i1 %351
  %461 = select i1 %459, i1 true, i1 %360
  %brmerge467 = select i1 %461, i1 true, i1 %361
  %462 = select i1 %369, i1 true, i1 %370
  %463 = select i1 %462, i1 true, i1 %350
  %brmerge465 = select i1 %463, i1 true, i1 %351
  %464 = select i1 %462, i1 true, i1 %360
  %brmerge463 = select i1 %464, i1 true, i1 %361
  %465 = select i1 %459, i1 true, i1 %315
  %brmerge461 = select i1 %465, i1 true, i1 %316
  %466 = select i1 %462, i1 true, i1 %315
  %brmerge459 = select i1 %466, i1 true, i1 %316
  %467 = select i1 %456, i1 true, i1 %350
  %brmerge457 = select i1 %467, i1 true, i1 %351
  %468 = select i1 %456, i1 true, i1 %360
  %brmerge = select i1 %468, i1 true, i1 %361
  %469 = select i1 %453, i1 true, i1 %303
  %brmerge483 = select i1 %469, i1 true, i1 %304
  %470 = select i1 %453, i1 true, i1 %292
  %brmerge485 = select i1 %470, i1 true, i1 %293
  br label %for_loop_body26

true_block23:                                     ; preds = %true_block20
  br label %after_if22

for_loop_body26:                                  ; preds = %after_if302, %after_if22
  %.0212440 = phi i32 [ 0, %after_if22 ], [ %625, %after_if302 ]
  %.0213439 = phi float [ 1.000000e+10, %after_if22 ], [ %.1214, %after_if302 ]
  %.0215438 = phi i32 [ %275, %after_if22 ], [ %.1216, %after_if302 ]
  %.0217437 = phi i32 [ %273, %after_if22 ], [ %.1218, %after_if302 ]
  switch i32 %.0212440, label %after_if35 [
    i32 16, label %true_block261
    i32 15, label %true_block246
    i32 1, label %true_block36
    i32 2, label %true_block51
    i32 3, label %true_block66
    i32 4, label %true_block81
    i32 5, label %true_block96
    i32 6, label %true_block111
    i32 7, label %true_block126
    i32 8, label %true_block141
    i32 9, label %true_block156
    i32 10, label %true_block171
    i32 11, label %true_block186
    i32 12, label %true_block201
    i32 13, label %true_block216
    i32 14, label %true_block231
    i32 17, label %true_block276
  ]

after_for28:                                      ; preds = %after_if302
  %471 = sitofp i32 %.1218 to float
  %472 = sitofp i32 %.1216 to float
  %473 = fcmp reassoc ninf nsz ult float %.1214, 0x3F689374C0000000
  br i1 %473, label %after_if312, label %true_block310

after_if35:                                       ; preds = %true_block288, %true_block282, %true_block279, %true_block276, %true_block273, %true_block261, %true_block258, %true_block246, %true_block243, %true_block231, %true_block228, %true_block216, %true_block213, %true_block201, %true_block198, %true_block186, %true_block183, %true_block171, %true_block168, %true_block156, %true_block153, %true_block141, %true_block138, %true_block126, %true_block123, %true_block111, %true_block108, %true_block96, %true_block93, %true_block81, %true_block78, %true_block66, %true_block63, %true_block51, %true_block48, %true_block36, %for_loop_body26
  %.0196 = phi i32 [ %569, %true_block273 ], [ %606, %true_block288 ], [ %.0217437, %true_block279 ], [ %.0217437, %true_block261 ], [ %.0217437, %true_block276 ], [ %.0217437, %true_block282 ], [ %.0217437, %true_block246 ], [ %563, %true_block258 ], [ %.0217437, %true_block231 ], [ %557, %true_block243 ], [ %.0217437, %true_block216 ], [ %551, %true_block228 ], [ %.0217437, %true_block201 ], [ %545, %true_block213 ], [ %.0217437, %true_block186 ], [ %539, %true_block198 ], [ %.0217437, %true_block171 ], [ %533, %true_block183 ], [ %.0217437, %true_block156 ], [ %527, %true_block168 ], [ %.0217437, %true_block141 ], [ %521, %true_block153 ], [ %.0217437, %true_block126 ], [ %515, %true_block138 ], [ %.0217437, %true_block111 ], [ %509, %true_block123 ], [ %.0217437, %true_block96 ], [ %503, %true_block108 ], [ %.0217437, %true_block81 ], [ %497, %true_block93 ], [ %.0217437, %true_block66 ], [ %491, %true_block78 ], [ %.0217437, %true_block51 ], [ %485, %true_block63 ], [ %.0217437, %true_block36 ], [ %479, %true_block48 ], [ %.0217437, %for_loop_body26 ]
  %.0193 = phi i32 [ %572, %true_block273 ], [ %613, %true_block288 ], [ %.0215438, %true_block279 ], [ %.0215438, %true_block261 ], [ %.0215438, %true_block276 ], [ %.0215438, %true_block282 ], [ %.0215438, %true_block246 ], [ %566, %true_block258 ], [ %.0215438, %true_block231 ], [ %560, %true_block243 ], [ %.0215438, %true_block216 ], [ %554, %true_block228 ], [ %.0215438, %true_block201 ], [ %548, %true_block213 ], [ %.0215438, %true_block186 ], [ %542, %true_block198 ], [ %.0215438, %true_block171 ], [ %536, %true_block183 ], [ %.0215438, %true_block156 ], [ %530, %true_block168 ], [ %.0215438, %true_block141 ], [ %524, %true_block153 ], [ %.0215438, %true_block126 ], [ %518, %true_block138 ], [ %.0215438, %true_block111 ], [ %512, %true_block123 ], [ %.0215438, %true_block96 ], [ %506, %true_block108 ], [ %.0215438, %true_block81 ], [ %500, %true_block93 ], [ %.0215438, %true_block66 ], [ %494, %true_block78 ], [ %.0215438, %true_block51 ], [ %488, %true_block63 ], [ %.0215438, %true_block36 ], [ %482, %true_block48 ], [ %.0215438, %for_loop_body26 ]
  %474 = add i32 %.0193, %192
  %475 = add i32 %.0196, %202
  %476 = icmp sgt i32 %474, -1
  br i1 %476, label %true_block291, label %after_if302

true_block36:                                     ; preds = %for_loop_body26
  br i1 %brmerge, label %after_if35, label %true_block48

true_block48:                                     ; preds = %true_block36
  %477 = load float, ptr %410, align 4
  %478 = tail call reassoc ninf nsz float @llvm.round.f32(float %477)
  %479 = fptosi float %478 to i32
  %480 = load float, ptr %413, align 4
  %481 = tail call reassoc ninf nsz float @llvm.round.f32(float %480)
  %482 = fptosi float %481 to i32
  br label %after_if35

true_block51:                                     ; preds = %for_loop_body26
  br i1 %brmerge457, label %after_if35, label %true_block63

true_block63:                                     ; preds = %true_block51
  %483 = load float, ptr %403, align 4
  %484 = tail call reassoc ninf nsz float @llvm.round.f32(float %483)
  %485 = fptosi float %484 to i32
  %486 = load float, ptr %406, align 4
  %487 = tail call reassoc ninf nsz float @llvm.round.f32(float %486)
  %488 = fptosi float %487 to i32
  br label %after_if35

true_block66:                                     ; preds = %for_loop_body26
  br i1 %brmerge459, label %after_if35, label %true_block78

true_block78:                                     ; preds = %true_block66
  %489 = load float, ptr %396, align 4
  %490 = tail call reassoc ninf nsz float @llvm.round.f32(float %489)
  %491 = fptosi float %490 to i32
  %492 = load float, ptr %399, align 4
  %493 = tail call reassoc ninf nsz float @llvm.round.f32(float %492)
  %494 = fptosi float %493 to i32
  br label %after_if35

true_block81:                                     ; preds = %for_loop_body26
  br i1 %brmerge461, label %after_if35, label %true_block93

true_block93:                                     ; preds = %true_block81
  %495 = load float, ptr %389, align 4
  %496 = tail call reassoc ninf nsz float @llvm.round.f32(float %495)
  %497 = fptosi float %496 to i32
  %498 = load float, ptr %392, align 4
  %499 = tail call reassoc ninf nsz float @llvm.round.f32(float %498)
  %500 = fptosi float %499 to i32
  br label %after_if35

true_block96:                                     ; preds = %for_loop_body26
  br i1 %brmerge463, label %after_if35, label %true_block108

true_block108:                                    ; preds = %true_block96
  %501 = load float, ptr %382, align 4
  %502 = tail call reassoc ninf nsz float @llvm.round.f32(float %501)
  %503 = fptosi float %502 to i32
  %504 = load float, ptr %385, align 4
  %505 = tail call reassoc ninf nsz float @llvm.round.f32(float %504)
  %506 = fptosi float %505 to i32
  br label %after_if35

true_block111:                                    ; preds = %for_loop_body26
  br i1 %brmerge465, label %after_if35, label %true_block123

true_block123:                                    ; preds = %true_block111
  %507 = load float, ptr %375, align 4
  %508 = tail call reassoc ninf nsz float @llvm.round.f32(float %507)
  %509 = fptosi float %508 to i32
  %510 = load float, ptr %378, align 4
  %511 = tail call reassoc ninf nsz float @llvm.round.f32(float %510)
  %512 = fptosi float %511 to i32
  br label %after_if35

true_block126:                                    ; preds = %for_loop_body26
  br i1 %brmerge467, label %after_if35, label %true_block138

true_block138:                                    ; preds = %true_block126
  %513 = load float, ptr %365, align 4
  %514 = tail call reassoc ninf nsz float @llvm.round.f32(float %513)
  %515 = fptosi float %514 to i32
  %516 = load float, ptr %368, align 4
  %517 = tail call reassoc ninf nsz float @llvm.round.f32(float %516)
  %518 = fptosi float %517 to i32
  br label %after_if35

true_block141:                                    ; preds = %for_loop_body26
  br i1 %brmerge469, label %after_if35, label %true_block153

true_block153:                                    ; preds = %true_block141
  %519 = load float, ptr %356, align 4
  %520 = tail call reassoc ninf nsz float @llvm.round.f32(float %519)
  %521 = fptosi float %520 to i32
  %522 = load float, ptr %359, align 4
  %523 = tail call reassoc ninf nsz float @llvm.round.f32(float %522)
  %524 = fptosi float %523 to i32
  br label %after_if35

true_block156:                                    ; preds = %for_loop_body26
  br i1 %brmerge471, label %after_if35, label %true_block168

true_block168:                                    ; preds = %true_block156
  %525 = load float, ptr %344, align 4
  %526 = tail call reassoc ninf nsz float @llvm.round.f32(float %525)
  %527 = fptosi float %526 to i32
  %528 = load float, ptr %347, align 4
  %529 = tail call reassoc ninf nsz float @llvm.round.f32(float %528)
  %530 = fptosi float %529 to i32
  br label %after_if35

true_block171:                                    ; preds = %for_loop_body26
  br i1 %brmerge473, label %after_if35, label %true_block183

true_block183:                                    ; preds = %true_block171
  %531 = load float, ptr %337, align 4
  %532 = tail call reassoc ninf nsz float @llvm.round.f32(float %531)
  %533 = fptosi float %532 to i32
  %534 = load float, ptr %340, align 4
  %535 = tail call reassoc ninf nsz float @llvm.round.f32(float %534)
  %536 = fptosi float %535 to i32
  br label %after_if35

true_block186:                                    ; preds = %for_loop_body26
  br i1 %brmerge475, label %after_if35, label %true_block198

true_block198:                                    ; preds = %true_block186
  %537 = load float, ptr %328, align 4
  %538 = tail call reassoc ninf nsz float @llvm.round.f32(float %537)
  %539 = fptosi float %538 to i32
  %540 = load float, ptr %331, align 4
  %541 = tail call reassoc ninf nsz float @llvm.round.f32(float %540)
  %542 = fptosi float %541 to i32
  br label %after_if35

true_block201:                                    ; preds = %for_loop_body26
  br i1 %brmerge477, label %after_if35, label %true_block213

true_block213:                                    ; preds = %true_block201
  %543 = load float, ptr %321, align 4
  %544 = tail call reassoc ninf nsz float @llvm.round.f32(float %543)
  %545 = fptosi float %544 to i32
  %546 = load float, ptr %324, align 4
  %547 = tail call reassoc ninf nsz float @llvm.round.f32(float %546)
  %548 = fptosi float %547 to i32
  br label %after_if35

true_block216:                                    ; preds = %for_loop_body26
  br i1 %brmerge479, label %after_if35, label %true_block228

true_block228:                                    ; preds = %true_block216
  %549 = load float, ptr %308, align 4
  %550 = tail call reassoc ninf nsz float @llvm.round.f32(float %549)
  %551 = fptosi float %550 to i32
  %552 = load float, ptr %311, align 4
  %553 = tail call reassoc ninf nsz float @llvm.round.f32(float %552)
  %554 = fptosi float %553 to i32
  br label %after_if35

true_block231:                                    ; preds = %for_loop_body26
  br i1 %brmerge481, label %after_if35, label %true_block243

true_block243:                                    ; preds = %true_block231
  %555 = load float, ptr %298, align 4
  %556 = tail call reassoc ninf nsz float @llvm.round.f32(float %555)
  %557 = fptosi float %556 to i32
  %558 = load float, ptr %301, align 4
  %559 = tail call reassoc ninf nsz float @llvm.round.f32(float %558)
  %560 = fptosi float %559 to i32
  br label %after_if35

true_block246:                                    ; preds = %for_loop_body26
  br i1 %brmerge483, label %after_if35, label %true_block258

true_block258:                                    ; preds = %true_block246
  %561 = load float, ptr %417, align 4
  %562 = tail call reassoc ninf nsz float @llvm.round.f32(float %561)
  %563 = fptosi float %562 to i32
  %564 = load float, ptr %420, align 4
  %565 = tail call reassoc ninf nsz float @llvm.round.f32(float %564)
  %566 = fptosi float %565 to i32
  br label %after_if35

true_block261:                                    ; preds = %for_loop_body26
  br i1 %brmerge485, label %after_if35, label %true_block273

true_block273:                                    ; preds = %true_block261
  %567 = load float, ptr %424, align 4
  %568 = tail call reassoc ninf nsz float @llvm.round.f32(float %567)
  %569 = fptosi float %568 to i32
  %570 = load float, ptr %427, align 4
  %571 = tail call reassoc ninf nsz float @llvm.round.f32(float %570)
  %572 = fptosi float %571 to i32
  br label %after_if35

true_block276:                                    ; preds = %for_loop_body26
  %573 = load i32, ptr %280, align 4
  %574 = icmp sgt i32 %573, 1
  br i1 %574, label %true_block279, label %after_if35

true_block279:                                    ; preds = %true_block276
  %575 = load i32, ptr %281, align 4
  %576 = icmp sgt i32 %575, 1
  br i1 %576, label %true_block282, label %after_if35

true_block282:                                    ; preds = %true_block279
  %577 = load i32, ptr %282, align 4
  %578 = sdiv i32 %205, %577
  %579 = mul i32 %578, %577
  %580 = xor i32 %577, %205
  %581 = icmp slt i32 %580, 0
  %582 = icmp ne i32 %579, %205
  %583 = and i1 %581, %582
  %.neg326 = sext i1 %583 to i32
  %584 = add i32 %578, %.neg326
  %585 = sdiv i32 %208, %577
  %586 = mul i32 %585, %577
  %587 = xor i32 %577, %208
  %588 = icmp slt i32 %587, 0
  %589 = icmp ne i32 %586, %208
  %590 = and i1 %588, %589
  %.neg327 = sext i1 %590 to i32
  %591 = add i32 %585, %.neg327
  %592 = icmp slt i32 %584, %573
  %593 = icmp slt i32 %591, %575
  %or.cond422 = select i1 %592, i1 %593, i1 false
  br i1 %or.cond422, label %true_block288, label %after_if35

true_block288:                                    ; preds = %true_block282
  %594 = load ptr, ptr %283, align 8
  %595 = load i32, ptr %284, align 4
  %596 = load i32, ptr %285, align 4
  %597 = mul i32 %595, %584
  %598 = add i32 %597, %591
  %599 = mul i32 %598, %596
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %594, i64 %600
  %602 = load float, ptr %601, align 4
  %603 = sitofp i32 %577 to float
  %604 = fmul reassoc ninf nsz float %602, %603
  %605 = tail call reassoc ninf nsz float @llvm.round.f32(float %604)
  %606 = fptosi float %605 to i32
  %607 = add i32 %599, 1
  %608 = sext i32 %607 to i64
  %609 = getelementptr float, ptr %594, i64 %608
  %610 = load float, ptr %609, align 4
  %611 = fmul reassoc ninf nsz float %610, %603
  %612 = tail call reassoc ninf nsz float @llvm.round.f32(float %611)
  %613 = fptosi float %612 to i32
  br label %after_if35

true_block291:                                    ; preds = %after_if35
  %614 = load i32, ptr %428, align 4
  %615 = add i32 %474, %189
  %.not328 = icmp sgt i32 %615, %614
  %616 = icmp slt i32 %475, 0
  %or.cond374.not590 = select i1 %.not328, i1 true, i1 %616
  %617 = add i32 %475, %199
  %618 = icmp sgt i32 %617, %277
  %or.cond424.not588 = select i1 %or.cond374.not590, i1 true, i1 %618
  %brmerge583 = select i1 %or.cond424.not588, i1 true, i1 %446
  %.mux = select i1 %or.cond424.not588, float 1.000000e+10, float 0x7FF8000000000000
  br i1 %brmerge583, label %after_if302, label %for_loop_body303.lr.ph

for_loop_body303.lr.ph:                           ; preds = %true_block291
  %619 = load ptr, ptr %447, align 8
  %620 = load i32, ptr %448, align 4
  %621 = load ptr, ptr %449, align 8
  br label %for_loop_body303

after_if302:                                      ; preds = %after_for305.loopexit, %true_block291, %after_if35
  %.0139 = phi float [ 1.000000e+10, %after_if35 ], [ %.mux, %true_block291 ], [ %648, %after_for305.loopexit ]
  %622 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0139, float 0.000000e+00)
  %623 = fmul reassoc ninf nsz float %622, %279
  %624 = fcmp reassoc ninf nsz olt float %623, %.0213439
  %.1218 = select i1 %624, i32 %.0196, i32 %.0217437
  %.1216 = select i1 %624, i32 %.0193, i32 %.0215438
  %.1214 = select i1 %624, float %623, float %.0213439
  %625 = add nuw nsw i32 %.0212440, 1
  %exitcond569.not = icmp eq i32 %625, 18
  br i1 %exitcond569.not, label %after_for28, label %for_loop_body26

for_loop_body303:                                 ; preds = %for_loop_body303, %for_loop_body303.lr.ph
  %.0134435 = phi i32 [ 0, %for_loop_body303.lr.ph ], [ %647, %for_loop_body303 ]
  %.0135434 = phi float [ 0.000000e+00, %for_loop_body303.lr.ph ], [ %646, %for_loop_body303 ]
  %.0140433 = phi float [ 0.000000e+00, %for_loop_body303.lr.ph ], [ %645, %for_loop_body303 ]
  %626 = udiv i32 %.0134435, %444
  %.recomposed = urem i32 %.0134435, %444
  %627 = shl nuw i32 %626, 1
  %628 = add i32 %627, %192
  %629 = shl nuw i32 %.recomposed, 1
  %630 = add i32 %629, %202
  %631 = mul i32 %628, %620
  %632 = add i32 %630, %631
  %633 = sext i32 %632 to i64
  %634 = getelementptr float, ptr %619, i64 %633
  %635 = load float, ptr %634, align 4
  %636 = add i32 %627, %474
  %637 = add i32 %629, %475
  %638 = mul i32 %636, %277
  %639 = add i32 %637, %638
  %640 = sext i32 %639 to i64
  %641 = getelementptr float, ptr %621, i64 %640
  %642 = load float, ptr %641, align 4
  %643 = fsub reassoc ninf nsz float %635, %642
  %644 = tail call noundef float @llvm.fabs.f32(float %643)
  %645 = fadd reassoc ninf nsz float %644, %.0140433
  %646 = fadd reassoc ninf nsz float %.0135434, 1.000000e+00
  %647 = add nuw nsw i32 %.0134435, 1
  %exitcond.not = icmp eq i32 %445, %647
  br i1 %exitcond.not, label %after_for305.loopexit, label %for_loop_body303

after_for305.loopexit:                            ; preds = %for_loop_body303
  %648 = fdiv reassoc ninf nsz float %645, %646
  br label %after_if302

true_block310:                                    ; preds = %after_for28
  %invariant.op = add i32 %.1216, %192
  br i1 %35, label %for_loop_body313.lr.ph, label %after_if312

for_loop_body313.lr.ph:                           ; preds = %true_block310
  %649 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %650 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %651 = mul i32 %650, %649
  %652 = icmp slt i32 %651, 1
  %xtraiter = and i32 %651, 1
  %653 = icmp eq i32 %651, 1
  %unroll_iter = and i32 %651, 2147483646
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body313

after_if312.loopexit:                             ; preds = %after_if328
  br label %after_if312

after_if312:                                      ; preds = %after_if312.loopexit, %true_block310, %after_for28
  %.0129 = phi float [ %471, %after_for28 ], [ %471, %true_block310 ], [ %.2131, %after_if312.loopexit ]
  %.0128 = phi float [ %472, %after_for28 ], [ %472, %true_block310 ], [ %.2, %after_if312.loopexit ]
  %654 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %655 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %656 = mul i32 %655, %654
  %657 = icmp sgt i32 %656, 0
  br i1 %657, label %for_loop_body336.lr.ph, label %after_for338

for_loop_body336.lr.ph:                           ; preds = %after_if312
  %neg346 = fneg reassoc ninf nsz float %.0129
  br label %for_loop_body336

for_loop_body313:                                 ; preds = %after_if328, %for_loop_body313.lr.ph
  %.0127450 = phi i32 [ 0, %for_loop_body313.lr.ph ], [ %686, %after_if328 ]
  %.1449 = phi float [ %472, %for_loop_body313.lr.ph ], [ %.2, %after_if328 ]
  %.1130448 = phi float [ %471, %for_loop_body313.lr.ph ], [ %.2131, %after_if328 ]
  %.0132447 = phi float [ 1.000000e+10, %for_loop_body313.lr.ph ], [ %.1133, %after_if328 ]
  %.udiv = udiv i32 %.0127450, %33
  %658 = sub nsw i32 %.udiv, %28
  %659 = mul i32 %33, %.udiv
  %660 = add i32 %.1218, %.0127450
  %661 = add i32 %28, %659
  %662 = sub i32 %660, %661
  %663 = add i32 %658, %.1216
  %.reass446 = add i32 %658, %invariant.op
  %664 = add i32 %662, %202
  %665 = icmp sgt i32 %.reass446, -1
  br i1 %665, label %true_block317, label %after_if328

true_block317:                                    ; preds = %for_loop_body313
  %666 = load i32, ptr %428, align 4
  %667 = add i32 %.reass446, %189
  %.not = icmp sgt i32 %667, %666
  %668 = icmp slt i32 %664, 0
  %or.cond375.not594 = select i1 %.not, i1 true, i1 %668
  %669 = add i32 %664, %199
  %670 = icmp sgt i32 %669, %277
  %or.cond426.not592 = select i1 %or.cond375.not594, i1 true, i1 %670
  %brmerge585 = select i1 %or.cond426.not592, i1 true, i1 %652
  %.mux586 = select i1 %or.cond426.not592, float 1.000000e+10, float 0x7FF8000000000000
  br i1 %brmerge585, label %after_if328, label %for_loop_body329.lr.ph

for_loop_body329.lr.ph:                           ; preds = %true_block317
  %671 = load ptr, ptr %447, align 8
  %672 = load i32, ptr %448, align 4
  %673 = load ptr, ptr %449, align 8
  br i1 %653, label %after_for331.loopexit.unr-lcssa, label %for_loop_body329.preheader

for_loop_body329.preheader:                       ; preds = %for_loop_body329.lr.ph
  br label %for_loop_body329

after_if328:                                      ; preds = %after_for331.loopexit, %true_block317, %for_loop_body313
  %.0125 = phi float [ 1.000000e+10, %for_loop_body313 ], [ %.mux586, %true_block317 ], [ %745, %after_for331.loopexit ]
  %674 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.0125, float 0.000000e+00)
  %675 = fmul reassoc ninf nsz float %674, %279
  %676 = sitofp i32 %662 to float
  %677 = fsub reassoc ninf nsz float %676, %.0221
  %678 = fmul reassoc ninf nsz float %677, %677
  %679 = sitofp i32 %663 to float
  %680 = fsub reassoc ninf nsz float %679, %.0220
  %681 = fmul reassoc ninf nsz float %680, %680
  %682 = fadd reassoc ninf nsz float %678, %681
  %683 = fmul reassoc ninf nsz float %.0219, %682
  %684 = fadd reassoc ninf nsz float %675, %683
  %685 = fcmp reassoc ninf nsz olt float %684, %.0132447
  %.1133 = select i1 %685, float %684, float %.0132447
  %.2131 = select i1 %685, float %676, float %.1130448
  %.2 = select i1 %685, float %679, float %.1449
  %686 = add nuw nsw i32 %.0127450, 1
  %exitcond571.not = icmp eq i32 %686, %34
  br i1 %exitcond571.not, label %after_if312.loopexit, label %for_loop_body313

for_loop_body329:                                 ; preds = %for_loop_body329, %for_loop_body329.preheader
  %.0120443 = phi i32 [ %725, %for_loop_body329 ], [ 0, %for_loop_body329.preheader ]
  %.0121442 = phi float [ %724, %for_loop_body329 ], [ 0.000000e+00, %for_loop_body329.preheader ]
  %.0126441 = phi float [ %723, %for_loop_body329 ], [ 0.000000e+00, %for_loop_body329.preheader ]
  %687 = udiv i32 %.0120443, %650
  %.recomposed607 = urem i32 %.0120443, %650
  %688 = add nuw i32 %687, %192
  %689 = add nuw i32 %.recomposed607, %202
  %690 = mul i32 %672, %688
  %691 = add i32 %689, %690
  %692 = sext i32 %691 to i64
  %693 = getelementptr float, ptr %671, i64 %692
  %694 = load float, ptr %693, align 4
  %695 = add nuw i32 %687, %.reass446
  %696 = add nuw i32 %.recomposed607, %664
  %697 = mul i32 %695, %277
  %698 = add i32 %696, %697
  %699 = sext i32 %698 to i64
  %700 = getelementptr float, ptr %673, i64 %699
  %701 = load float, ptr %700, align 4
  %702 = fsub reassoc ninf nsz float %694, %701
  %703 = tail call noundef float @llvm.fabs.f32(float %702)
  %704 = fadd reassoc ninf nsz float %703, %.0126441
  %705 = add i32 %.0120443, 1
  %706 = udiv i32 %705, %650
  %.recomposed608 = urem i32 %705, %650
  %707 = add nuw i32 %706, %192
  %708 = add nuw i32 %.recomposed608, %202
  %709 = mul i32 %672, %707
  %710 = add i32 %708, %709
  %711 = sext i32 %710 to i64
  %712 = getelementptr float, ptr %671, i64 %711
  %713 = load float, ptr %712, align 4
  %714 = add nuw i32 %706, %.reass446
  %715 = add nuw i32 %.recomposed608, %664
  %716 = mul i32 %714, %277
  %717 = add i32 %715, %716
  %718 = sext i32 %717 to i64
  %719 = getelementptr float, ptr %673, i64 %718
  %720 = load float, ptr %719, align 4
  %721 = fsub reassoc ninf nsz float %713, %720
  %722 = tail call noundef float @llvm.fabs.f32(float %721)
  %723 = fadd reassoc ninf nsz float %722, %704
  %724 = fadd reassoc ninf nsz float %.0121442, 2.000000e+00
  %725 = add nuw i32 %.0120443, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %725
  br i1 %niter.ncmp.1, label %after_for331.loopexit.unr-lcssa.loopexit, label %for_loop_body329

after_for331.loopexit.unr-lcssa.loopexit:         ; preds = %for_loop_body329
  %726 = fadd reassoc ninf nsz float %.0121442, 3.000000e+00
  br label %after_for331.loopexit.unr-lcssa

after_for331.loopexit.unr-lcssa:                  ; preds = %after_for331.loopexit.unr-lcssa.loopexit, %for_loop_body329.lr.ph
  %.lcssa600.ph = phi float [ poison, %for_loop_body329.lr.ph ], [ %723, %after_for331.loopexit.unr-lcssa.loopexit ]
  %.lcssa599.ph = phi float [ poison, %for_loop_body329.lr.ph ], [ %724, %after_for331.loopexit.unr-lcssa.loopexit ]
  %.0120443.unr = phi i32 [ 0, %for_loop_body329.lr.ph ], [ %725, %after_for331.loopexit.unr-lcssa.loopexit ]
  %.0121442.unr = phi float [ 1.000000e+00, %for_loop_body329.lr.ph ], [ %726, %after_for331.loopexit.unr-lcssa.loopexit ]
  %.0126441.unr = phi float [ 0.000000e+00, %for_loop_body329.lr.ph ], [ %723, %after_for331.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for331.loopexit, label %for_loop_body329.epil

for_loop_body329.epil:                            ; preds = %after_for331.loopexit.unr-lcssa
  %727 = udiv i32 %.0120443.unr, %650
  %.recomposed609 = urem i32 %.0120443.unr, %650
  %728 = add nuw i32 %727, %192
  %729 = add nuw i32 %.recomposed609, %202
  %730 = mul i32 %672, %728
  %731 = add i32 %729, %730
  %732 = sext i32 %731 to i64
  %733 = getelementptr float, ptr %671, i64 %732
  %734 = load float, ptr %733, align 4
  %735 = add nuw i32 %727, %.reass446
  %736 = add nuw i32 %.recomposed609, %664
  %737 = mul i32 %735, %277
  %738 = add i32 %736, %737
  %739 = sext i32 %738 to i64
  %740 = getelementptr float, ptr %673, i64 %739
  %741 = load float, ptr %740, align 4
  %742 = fsub reassoc ninf nsz float %734, %741
  %743 = tail call noundef float @llvm.fabs.f32(float %742)
  %744 = fadd reassoc ninf nsz float %743, %.0126441.unr
  br label %after_for331.loopexit

after_for331.loopexit:                            ; preds = %for_loop_body329.epil, %after_for331.loopexit.unr-lcssa
  %.lcssa600 = phi float [ %.lcssa600.ph, %after_for331.loopexit.unr-lcssa ], [ %744, %for_loop_body329.epil ]
  %.lcssa599 = phi float [ %.lcssa599.ph, %after_for331.loopexit.unr-lcssa ], [ %.0121442.unr, %for_loop_body329.epil ]
  %745 = fdiv reassoc ninf nsz float %.lcssa600, %.lcssa599
  br label %after_if328

for_loop_body336:                                 ; preds = %after_if345, %for_loop_body336.lr.ph
  %.0119453 = phi i32 [ 0, %for_loop_body336.lr.ph ], [ %775, %after_if345 ]
  %746 = udiv i32 %.0119453, %655
  %.recomposed610 = urem i32 %.0119453, %655
  %747 = add nuw i32 %746, %192
  %748 = load i32, ptr %186, align 4
  %749 = icmp slt i32 %747, %748
  br i1 %749, label %true_block340, label %after_if345

after_for338.loopexit:                            ; preds = %after_if345
  br label %after_for338

after_for338:                                     ; preds = %after_for338.loopexit, %after_if312
  %750 = add nsw i32 %.0233454, 1
  %exitcond573.not = icmp eq i32 %750, %18
  br i1 %exitcond573.not, label %after_for.loopexit, label %after_if7

true_block340:                                    ; preds = %for_loop_body336
  %751 = add nuw i32 %.recomposed610, %202
  %752 = load i32, ptr %196, align 4
  %753 = icmp slt i32 %751, %752
  br i1 %753, label %true_block343, label %after_if345

true_block343:                                    ; preds = %true_block340
  %754 = load ptr, ptr %0, align 8
  %755 = getelementptr i8, ptr %754, i64 96
  %756 = load ptr, ptr %755, align 8
  %757 = getelementptr i8, ptr %754, i64 84
  %758 = load i32, ptr %757, align 4
  %759 = getelementptr i8, ptr %754, i64 88
  %760 = load i32, ptr %759, align 4
  %761 = mul i32 %758, %747
  %762 = add i32 %761, %751
  %763 = mul i32 %762, %760
  %764 = sext i32 %763 to i64
  %765 = getelementptr float, ptr %756, i64 %764
  store float %neg346, ptr %765, align 4
  %766 = load ptr, ptr %755, align 8
  %767 = load i32, ptr %757, align 4
  %768 = load i32, ptr %759, align 4
  %769 = mul i32 %767, %747
  %770 = add i32 %769, %751
  %771 = mul i32 %770, %768
  %772 = add i32 %771, 1
  %773 = sext i32 %772 to i64
  %774 = getelementptr float, ptr %766, i64 %773
  store float %.0128, ptr %774, align 4
  br label %after_if345

after_if345:                                      ; preds = %true_block343, %true_block340, %for_loop_body336
  %775 = add nuw nsw i32 %.0119453, 1
  %exitcond572.not = icmp eq i32 %656, %775
  br i1 %exitcond572.not, label %after_for338.loopexit, label %for_loop_body336
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.round.f32(float) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
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
