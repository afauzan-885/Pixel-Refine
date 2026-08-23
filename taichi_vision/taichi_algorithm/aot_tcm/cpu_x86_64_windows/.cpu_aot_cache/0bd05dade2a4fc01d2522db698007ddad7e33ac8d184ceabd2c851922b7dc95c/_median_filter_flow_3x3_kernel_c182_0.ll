; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_median_filter_flow_3x3_kernel_c182_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 36
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

define void @_median_filter_flow_3x3_kernel_c182_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = getelementptr i8, ptr %20, i64 8
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 24
  %24 = getelementptr i8, ptr %20, i64 20
  %25 = shl i32 %16, 1
  br label %for_loop_body5.lr.ph

after_for.loopexit:                               ; preds = %for_loop_body5.lr.ph
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.lr.ph:                             ; preds = %for_loop_body5.lr.ph, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %for_loop_body5.lr.ph ], [ %25, %for_loop_body.lr.ph ]
  %.01929 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %208, %for_loop_body5.lr.ph ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.01929, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.01929
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.01929, %32
  %36 = and i1 %34, %35
  %.neg24 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg24
  %38 = mul i32 %30, -1
  %39 = mul i32 %38, %37
  %40 = add i32 %.01929, %39
  %41 = add i32 %37, -1
  %42 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %43 = load i32, ptr %42, align 4
  %44 = add i32 %43, -1
  %45 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %46 = tail call i32 @llvm.smin.i32(i32 %44, i32 %45)
  %47 = add i32 %40, -1
  %48 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %49 = load i32, ptr %48, align 4
  %50 = add i32 %49, -1
  %51 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %52 = tail call i32 @llvm.smin.i32(i32 %50, i32 %51)
  %53 = load ptr, ptr %21, align 8
  %54 = load i32, ptr %22, align 4
  %55 = mul i32 %46, %54
  %56 = add i32 %52, %55
  %57 = shl i32 %56, 1
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, ptr %53, i64 %58
  %60 = load float, ptr %59, align 4
  %61 = getelementptr i8, ptr %59, i64 4
  %62 = load float, ptr %61, align 4
  %63 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %64 = tail call i32 @llvm.smin.i32(i32 %50, i32 %63)
  %65 = add i32 %55, %64
  %66 = shl i32 %65, 1
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %53, i64 %67
  %69 = load float, ptr %68, align 4
  %70 = getelementptr i8, ptr %68, i64 4
  %71 = load float, ptr %70, align 4
  %72 = add i32 %40, 1
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = tail call i32 @llvm.smin.i32(i32 %50, i32 %73)
  %75 = add i32 %74, %55
  %76 = shl i32 %75, 1
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, ptr %53, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = getelementptr i8, ptr %78, i64 4
  %81 = load float, ptr %80, align 4
  %82 = tail call i32 @llvm.smax.i32(i32 %37, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %44, i32 %82)
  %84 = mul i32 %83, %54
  %85 = add i32 %52, %84
  %86 = shl i32 %85, 1
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, ptr %53, i64 %87
  %89 = load float, ptr %88, align 4
  %90 = getelementptr i8, ptr %88, i64 4
  %91 = load float, ptr %90, align 4
  %92 = add i32 %64, %84
  %93 = shl i32 %92, 1
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %53, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = getelementptr i8, ptr %95, i64 4
  %98 = load float, ptr %97, align 4
  %99 = add i32 %74, %84
  %100 = shl i32 %99, 1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %53, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = getelementptr i8, ptr %102, i64 4
  %105 = load float, ptr %104, align 4
  %106 = add i32 %37, 1
  %107 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %44, i32 %107)
  %109 = mul i32 %108, %54
  %110 = add i32 %52, %109
  %111 = shl i32 %110, 1
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %53, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = getelementptr i8, ptr %113, i64 4
  %116 = load float, ptr %115, align 4
  %117 = add i32 %109, %64
  %118 = shl i32 %117, 1
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %53, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = getelementptr i8, ptr %120, i64 4
  %123 = load float, ptr %122, align 4
  %124 = add i32 %74, %109
  %125 = shl i32 %124, 1
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %53, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = getelementptr i8, ptr %127, i64 4
  %130 = load float, ptr %129, align 4
  %131 = fcmp reassoc ninf nsz olt float %69, %60
  %.sroa.17158.0 = select i1 %131, float %60, float %69
  %.sroa.0150.0 = select i1 %131, float %69, float %60
  %132 = fcmp reassoc ninf nsz olt float %79, %.sroa.0150.0
  %.sroa.34166.8 = select i1 %132, float %.sroa.0150.0, float %79
  %.sroa.0150.1 = select i1 %132, float %79, float %.sroa.0150.0
  %133 = fcmp reassoc ninf nsz olt float %89, %.sroa.0150.1
  %.sroa.51174.9 = select i1 %133, float %.sroa.0150.1, float %89
  %.sroa.0150.2 = select i1 %133, float %89, float %.sroa.0150.1
  %134 = fcmp reassoc ninf nsz olt float %96, %.sroa.0150.2
  %.sroa.68182.12 = select i1 %134, float %.sroa.0150.2, float %96
  %.sroa.0150.3 = select i1 %134, float %96, float %.sroa.0150.2
  %135 = fcmp reassoc ninf nsz olt float %103, %.sroa.0150.3
  %.sroa.86191.11 = select i1 %135, float %.sroa.0150.3, float %103
  %.sroa.0150.4 = select i1 %135, float %103, float %.sroa.0150.3
  %136 = fcmp reassoc ninf nsz olt float %114, %.sroa.0150.4
  %.sroa.103199.12 = select i1 %136, float %.sroa.0150.4, float %114
  %.sroa.0150.5 = select i1 %136, float %114, float %.sroa.0150.4
  %137 = fcmp reassoc ninf nsz olt float %121, %.sroa.0150.5
  %.sroa.120207.13 = select i1 %137, float %.sroa.0150.5, float %121
  %.sroa.0150.6 = select i1 %137, float %121, float %.sroa.0150.5
  %138 = fcmp reassoc ninf nsz olt float %128, %.sroa.0150.6
  %.sroa.137215.13 = select i1 %138, float %.sroa.0150.6, float %128
  %139 = fcmp reassoc ninf nsz olt float %.sroa.34166.8, %.sroa.17158.0
  %.sroa.34166.1 = select i1 %139, float %.sroa.17158.0, float %.sroa.34166.8
  %.sroa.17158.2 = select i1 %139, float %.sroa.34166.8, float %.sroa.17158.0
  %140 = fcmp reassoc ninf nsz olt float %.sroa.51174.9, %.sroa.17158.2
  %.sroa.51174.8 = select i1 %140, float %.sroa.17158.2, float %.sroa.51174.9
  %.sroa.17158.3 = select i1 %140, float %.sroa.51174.9, float %.sroa.17158.2
  %141 = fcmp reassoc ninf nsz olt float %.sroa.68182.12, %.sroa.17158.3
  %.sroa.68182.11 = select i1 %141, float %.sroa.17158.3, float %.sroa.68182.12
  %.sroa.17158.4 = select i1 %141, float %.sroa.68182.12, float %.sroa.17158.3
  %142 = fcmp reassoc ninf nsz olt float %.sroa.86191.11, %.sroa.17158.4
  %.sroa.86191.10 = select i1 %142, float %.sroa.17158.4, float %.sroa.86191.11
  %.sroa.17158.5 = select i1 %142, float %.sroa.86191.11, float %.sroa.17158.4
  %143 = fcmp reassoc ninf nsz olt float %.sroa.103199.12, %.sroa.17158.5
  %.sroa.103199.11 = select i1 %143, float %.sroa.17158.5, float %.sroa.103199.12
  %.sroa.17158.6 = select i1 %143, float %.sroa.103199.12, float %.sroa.17158.5
  %144 = fcmp reassoc ninf nsz olt float %.sroa.120207.13, %.sroa.17158.6
  %.sroa.120207.12 = select i1 %144, float %.sroa.17158.6, float %.sroa.120207.13
  %.sroa.17158.7 = select i1 %144, float %.sroa.120207.13, float %.sroa.17158.6
  %145 = fcmp reassoc ninf nsz olt float %.sroa.137215.13, %.sroa.17158.7
  %.sroa.137215.12 = select i1 %145, float %.sroa.17158.7, float %.sroa.137215.13
  %146 = fcmp reassoc ninf nsz olt float %.sroa.51174.8, %.sroa.34166.1
  %.sroa.51174.2 = select i1 %146, float %.sroa.34166.1, float %.sroa.51174.8
  %.sroa.34166.3 = select i1 %146, float %.sroa.51174.8, float %.sroa.34166.1
  %147 = fcmp reassoc ninf nsz olt float %.sroa.68182.11, %.sroa.34166.3
  %.sroa.68182.10 = select i1 %147, float %.sroa.34166.3, float %.sroa.68182.11
  %.sroa.34166.4 = select i1 %147, float %.sroa.68182.11, float %.sroa.34166.3
  %148 = fcmp reassoc ninf nsz olt float %.sroa.86191.10, %.sroa.34166.4
  %.sroa.86191.9 = select i1 %148, float %.sroa.34166.4, float %.sroa.86191.10
  %.sroa.34166.5 = select i1 %148, float %.sroa.86191.10, float %.sroa.34166.4
  %149 = fcmp reassoc ninf nsz olt float %.sroa.103199.11, %.sroa.34166.5
  %.sroa.103199.10 = select i1 %149, float %.sroa.34166.5, float %.sroa.103199.11
  %.sroa.34166.6 = select i1 %149, float %.sroa.103199.11, float %.sroa.34166.5
  %150 = fcmp reassoc ninf nsz olt float %.sroa.120207.12, %.sroa.34166.6
  %.sroa.120207.11 = select i1 %150, float %.sroa.34166.6, float %.sroa.120207.12
  %.sroa.34166.7 = select i1 %150, float %.sroa.120207.12, float %.sroa.34166.6
  %151 = fcmp reassoc ninf nsz olt float %.sroa.137215.12, %.sroa.34166.7
  %.sroa.137215.11 = select i1 %151, float %.sroa.34166.7, float %.sroa.137215.12
  %152 = fcmp reassoc ninf nsz olt float %.sroa.68182.10, %.sroa.51174.2
  %.sroa.68182.3 = select i1 %152, float %.sroa.51174.2, float %.sroa.68182.10
  %.sroa.51174.4 = select i1 %152, float %.sroa.68182.10, float %.sroa.51174.2
  %153 = fcmp reassoc ninf nsz olt float %.sroa.86191.9, %.sroa.51174.4
  %.sroa.86191.8 = select i1 %153, float %.sroa.51174.4, float %.sroa.86191.9
  %.sroa.51174.5 = select i1 %153, float %.sroa.86191.9, float %.sroa.51174.4
  %154 = fcmp reassoc ninf nsz olt float %.sroa.103199.10, %.sroa.51174.5
  %.sroa.103199.9 = select i1 %154, float %.sroa.51174.5, float %.sroa.103199.10
  %.sroa.51174.6 = select i1 %154, float %.sroa.103199.10, float %.sroa.51174.5
  %155 = fcmp reassoc ninf nsz olt float %.sroa.120207.11, %.sroa.51174.6
  %.sroa.120207.10 = select i1 %155, float %.sroa.51174.6, float %.sroa.120207.11
  %.sroa.51174.7 = select i1 %155, float %.sroa.120207.11, float %.sroa.51174.6
  %156 = fcmp reassoc ninf nsz olt float %.sroa.137215.11, %.sroa.51174.7
  %.sroa.137215.10 = select i1 %156, float %.sroa.51174.7, float %.sroa.137215.11
  %157 = fcmp reassoc ninf nsz olt float %.sroa.86191.8, %.sroa.68182.3
  %.sroa.68182.5 = select i1 %157, float %.sroa.86191.8, float %.sroa.68182.3
  %158 = fcmp reassoc ninf nsz olt float %.sroa.103199.9, %.sroa.68182.5
  %.sroa.68182.7 = select i1 %158, float %.sroa.103199.9, float %.sroa.68182.5
  %159 = fcmp reassoc ninf nsz olt float %.sroa.120207.10, %.sroa.68182.7
  %.sroa.68182.8 = select i1 %159, float %.sroa.120207.10, float %.sroa.68182.7
  %160 = fcmp reassoc ninf nsz olt float %.sroa.137215.10, %.sroa.68182.8
  %.sroa.68182.9 = select i1 %160, float %.sroa.137215.10, float %.sroa.68182.8
  %161 = fcmp reassoc ninf nsz olt float %71, %62
  %.sroa.17.0 = select i1 %161, float %62, float %71
  %.sroa.0.0 = select i1 %161, float %71, float %62
  %162 = fcmp reassoc ninf nsz olt float %81, %.sroa.0.0
  %.sroa.34.8 = select i1 %162, float %.sroa.0.0, float %81
  %.sroa.0.1 = select i1 %162, float %81, float %.sroa.0.0
  %163 = fcmp reassoc ninf nsz olt float %91, %.sroa.0.1
  %.sroa.51.9 = select i1 %163, float %.sroa.0.1, float %91
  %.sroa.0.2 = select i1 %163, float %91, float %.sroa.0.1
  %164 = fcmp reassoc ninf nsz olt float %98, %.sroa.0.2
  %.sroa.68.12 = select i1 %164, float %.sroa.0.2, float %98
  %.sroa.0.3 = select i1 %164, float %98, float %.sroa.0.2
  %165 = fcmp reassoc ninf nsz olt float %105, %.sroa.0.3
  %.sroa.86.11 = select i1 %165, float %.sroa.0.3, float %105
  %.sroa.0.4 = select i1 %165, float %105, float %.sroa.0.3
  %166 = fcmp reassoc ninf nsz olt float %116, %.sroa.0.4
  %.sroa.103.12 = select i1 %166, float %.sroa.0.4, float %116
  %.sroa.0.5 = select i1 %166, float %116, float %.sroa.0.4
  %167 = fcmp reassoc ninf nsz olt float %123, %.sroa.0.5
  %.sroa.120.13 = select i1 %167, float %.sroa.0.5, float %123
  %.sroa.0.6 = select i1 %167, float %123, float %.sroa.0.5
  %168 = fcmp reassoc ninf nsz olt float %130, %.sroa.0.6
  %.sroa.137.13 = select i1 %168, float %.sroa.0.6, float %130
  %169 = fcmp reassoc ninf nsz olt float %.sroa.34.8, %.sroa.17.0
  %.sroa.34.1 = select i1 %169, float %.sroa.17.0, float %.sroa.34.8
  %.sroa.17.2 = select i1 %169, float %.sroa.34.8, float %.sroa.17.0
  %170 = fcmp reassoc ninf nsz olt float %.sroa.51.9, %.sroa.17.2
  %.sroa.51.8 = select i1 %170, float %.sroa.17.2, float %.sroa.51.9
  %.sroa.17.3 = select i1 %170, float %.sroa.51.9, float %.sroa.17.2
  %171 = fcmp reassoc ninf nsz olt float %.sroa.68.12, %.sroa.17.3
  %.sroa.68.11 = select i1 %171, float %.sroa.17.3, float %.sroa.68.12
  %.sroa.17.4 = select i1 %171, float %.sroa.68.12, float %.sroa.17.3
  %172 = fcmp reassoc ninf nsz olt float %.sroa.86.11, %.sroa.17.4
  %.sroa.86.10 = select i1 %172, float %.sroa.17.4, float %.sroa.86.11
  %.sroa.17.5 = select i1 %172, float %.sroa.86.11, float %.sroa.17.4
  %173 = fcmp reassoc ninf nsz olt float %.sroa.103.12, %.sroa.17.5
  %.sroa.103.11 = select i1 %173, float %.sroa.17.5, float %.sroa.103.12
  %.sroa.17.6 = select i1 %173, float %.sroa.103.12, float %.sroa.17.5
  %174 = fcmp reassoc ninf nsz olt float %.sroa.120.13, %.sroa.17.6
  %.sroa.120.12 = select i1 %174, float %.sroa.17.6, float %.sroa.120.13
  %.sroa.17.7 = select i1 %174, float %.sroa.120.13, float %.sroa.17.6
  %175 = fcmp reassoc ninf nsz olt float %.sroa.137.13, %.sroa.17.7
  %.sroa.137.12 = select i1 %175, float %.sroa.17.7, float %.sroa.137.13
  %176 = fcmp reassoc ninf nsz olt float %.sroa.51.8, %.sroa.34.1
  %.sroa.51.2 = select i1 %176, float %.sroa.34.1, float %.sroa.51.8
  %.sroa.34.3 = select i1 %176, float %.sroa.51.8, float %.sroa.34.1
  %177 = fcmp reassoc ninf nsz olt float %.sroa.68.11, %.sroa.34.3
  %.sroa.68.10 = select i1 %177, float %.sroa.34.3, float %.sroa.68.11
  %.sroa.34.4 = select i1 %177, float %.sroa.68.11, float %.sroa.34.3
  %178 = fcmp reassoc ninf nsz olt float %.sroa.86.10, %.sroa.34.4
  %.sroa.86.9 = select i1 %178, float %.sroa.34.4, float %.sroa.86.10
  %.sroa.34.5 = select i1 %178, float %.sroa.86.10, float %.sroa.34.4
  %179 = fcmp reassoc ninf nsz olt float %.sroa.103.11, %.sroa.34.5
  %.sroa.103.10 = select i1 %179, float %.sroa.34.5, float %.sroa.103.11
  %.sroa.34.6 = select i1 %179, float %.sroa.103.11, float %.sroa.34.5
  %180 = fcmp reassoc ninf nsz olt float %.sroa.120.12, %.sroa.34.6
  %.sroa.120.11 = select i1 %180, float %.sroa.34.6, float %.sroa.120.12
  %.sroa.34.7 = select i1 %180, float %.sroa.120.12, float %.sroa.34.6
  %181 = fcmp reassoc ninf nsz olt float %.sroa.137.12, %.sroa.34.7
  %.sroa.137.11 = select i1 %181, float %.sroa.34.7, float %.sroa.137.12
  %182 = fcmp reassoc ninf nsz olt float %.sroa.68.10, %.sroa.51.2
  %.sroa.68.3 = select i1 %182, float %.sroa.51.2, float %.sroa.68.10
  %.sroa.51.4 = select i1 %182, float %.sroa.68.10, float %.sroa.51.2
  %183 = fcmp reassoc ninf nsz olt float %.sroa.86.9, %.sroa.51.4
  %.sroa.86.8 = select i1 %183, float %.sroa.51.4, float %.sroa.86.9
  %.sroa.51.5 = select i1 %183, float %.sroa.86.9, float %.sroa.51.4
  %184 = fcmp reassoc ninf nsz olt float %.sroa.103.10, %.sroa.51.5
  %.sroa.103.9 = select i1 %184, float %.sroa.51.5, float %.sroa.103.10
  %.sroa.51.6 = select i1 %184, float %.sroa.103.10, float %.sroa.51.5
  %185 = fcmp reassoc ninf nsz olt float %.sroa.120.11, %.sroa.51.6
  %.sroa.120.10 = select i1 %185, float %.sroa.51.6, float %.sroa.120.11
  %.sroa.51.7 = select i1 %185, float %.sroa.120.11, float %.sroa.51.6
  %186 = fcmp reassoc ninf nsz olt float %.sroa.137.11, %.sroa.51.7
  %.sroa.137.10 = select i1 %186, float %.sroa.51.7, float %.sroa.137.11
  %187 = fcmp reassoc ninf nsz olt float %.sroa.86.8, %.sroa.68.3
  %.sroa.68.5 = select i1 %187, float %.sroa.86.8, float %.sroa.68.3
  %188 = fcmp reassoc ninf nsz olt float %.sroa.103.9, %.sroa.68.5
  %.sroa.68.7 = select i1 %188, float %.sroa.103.9, float %.sroa.68.5
  %189 = fcmp reassoc ninf nsz olt float %.sroa.120.10, %.sroa.68.7
  %.sroa.68.8 = select i1 %189, float %.sroa.120.10, float %.sroa.68.7
  %190 = fcmp reassoc ninf nsz olt float %.sroa.137.10, %.sroa.68.8
  %.sroa.68.9 = select i1 %190, float %.sroa.137.10, float %.sroa.68.8
  %191 = load ptr, ptr %23, align 8
  %192 = load i32, ptr %24, align 4
  %193 = sub i32 %192, %30
  %194 = shl i32 %193, 1
  %195 = mul i32 %194, %37
  %196 = add i32 %lsr.iv, %195
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %191, i64 %197
  store float %.sroa.68182.9, ptr %198, align 4
  %199 = load ptr, ptr %23, align 8
  %200 = load i32, ptr %24, align 4
  %201 = sub i32 %200, %30
  %202 = shl i32 %201, 1
  %203 = mul i32 %202, %37
  %204 = add i32 %lsr.iv, %203
  %205 = add i32 %204, 1
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %199, i64 %206
  store float %.sroa.68.9, ptr %207, align 4
  %208 = add nsw i32 %.01929, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %208
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body5.lr.ph
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
