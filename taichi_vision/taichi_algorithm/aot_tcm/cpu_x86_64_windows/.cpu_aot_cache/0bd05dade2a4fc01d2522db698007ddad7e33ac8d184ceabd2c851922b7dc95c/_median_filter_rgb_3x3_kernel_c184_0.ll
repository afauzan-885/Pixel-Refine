; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_median_filter_rgb_3x3_kernel_c184_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 52
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

define void @_median_filter_rgb_3x3_kernel_c184_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = getelementptr i8, ptr %20, i64 16
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 8
  %24 = getelementptr i8, ptr %20, i64 40
  %25 = getelementptr i8, ptr %20, i64 28
  %26 = getelementptr i8, ptr %20, i64 32
  br label %for_loop_body5.lr.ph

after_for.loopexit:                               ; preds = %for_loop_body5.lr.ph
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.lr.ph:                             ; preds = %for_loop_body5.lr.ph, %for_loop_body.lr.ph
  %.02741 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %354, %for_loop_body5.lr.ph ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.02741, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.02741
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.02741, %33
  %37 = and i1 %35, %36
  %.neg34 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg34
  %39 = mul i32 %31, -1
  %40 = mul i32 %39, %38
  %41 = add i32 %.02741, %40
  %42 = add i32 %38, -1
  %43 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %44 = load i32, ptr %43, align 4
  %45 = add i32 %44, -1
  %46 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %47 = tail call i32 @llvm.smin.i32(i32 %45, i32 %46)
  %48 = add i32 %41, -1
  %49 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %50 = load i32, ptr %49, align 4
  %51 = add i32 %50, -1
  %52 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %53 = tail call i32 @llvm.smin.i32(i32 %51, i32 %52)
  %54 = load ptr, ptr %21, align 8
  %55 = load i32, ptr %22, align 4
  %56 = load i32, ptr %23, align 4
  %57 = mul i32 %47, %55
  %58 = add i32 %53, %57
  %59 = mul i32 %58, %56
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %54, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %64 = tail call i32 @llvm.smin.i32(i32 %51, i32 %63)
  %65 = add i32 %57, %64
  %66 = mul i32 %65, %56
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %54, i64 %67
  %69 = load float, ptr %68, align 4
  %70 = add i32 %41, 1
  %71 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %72 = tail call i32 @llvm.smin.i32(i32 %51, i32 %71)
  %73 = add i32 %72, %57
  %74 = mul i32 %73, %56
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, ptr %54, i64 %75
  %77 = load float, ptr %76, align 4
  %78 = tail call i32 @llvm.smax.i32(i32 %38, i32 0)
  %79 = tail call i32 @llvm.smin.i32(i32 %45, i32 %78)
  %80 = mul i32 %79, %55
  %81 = add i32 %53, %80
  %82 = mul i32 %81, %56
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %54, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = add i32 %64, %80
  %87 = mul i32 %86, %56
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %54, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = add i32 %72, %80
  %92 = mul i32 %91, %56
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %54, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = add i32 %38, 1
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = tail call i32 @llvm.smin.i32(i32 %45, i32 %97)
  %99 = mul i32 %98, %55
  %100 = add i32 %53, %99
  %101 = mul i32 %100, %56
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %54, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = add i32 %99, %64
  %106 = mul i32 %105, %56
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %54, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = add i32 %72, %99
  %111 = mul i32 %110, %56
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %54, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = fcmp reassoc ninf nsz olt float %69, %62
  %.sroa.17271.0 = select i1 %115, float %62, float %69
  %.sroa.0263.0 = select i1 %115, float %69, float %62
  %116 = fcmp reassoc ninf nsz olt float %77, %.sroa.0263.0
  %.sroa.34279.8 = select i1 %116, float %.sroa.0263.0, float %77
  %.sroa.0263.1 = select i1 %116, float %77, float %.sroa.0263.0
  %117 = fcmp reassoc ninf nsz olt float %85, %.sroa.0263.1
  %.sroa.51287.9 = select i1 %117, float %.sroa.0263.1, float %85
  %.sroa.0263.2 = select i1 %117, float %85, float %.sroa.0263.1
  %118 = fcmp reassoc ninf nsz olt float %90, %.sroa.0263.2
  %.sroa.68295.12 = select i1 %118, float %.sroa.0263.2, float %90
  %.sroa.0263.3 = select i1 %118, float %90, float %.sroa.0263.2
  %119 = fcmp reassoc ninf nsz olt float %95, %.sroa.0263.3
  %.sroa.86304.11 = select i1 %119, float %.sroa.0263.3, float %95
  %.sroa.0263.4 = select i1 %119, float %95, float %.sroa.0263.3
  %120 = fcmp reassoc ninf nsz olt float %104, %.sroa.0263.4
  %.sroa.103312.12 = select i1 %120, float %.sroa.0263.4, float %104
  %.sroa.0263.5 = select i1 %120, float %104, float %.sroa.0263.4
  %121 = fcmp reassoc ninf nsz olt float %109, %.sroa.0263.5
  %.sroa.120320.13 = select i1 %121, float %.sroa.0263.5, float %109
  %.sroa.0263.6 = select i1 %121, float %109, float %.sroa.0263.5
  %122 = fcmp reassoc ninf nsz olt float %114, %.sroa.0263.6
  %.sroa.137328.13 = select i1 %122, float %.sroa.0263.6, float %114
  %123 = fcmp reassoc ninf nsz olt float %.sroa.34279.8, %.sroa.17271.0
  %.sroa.34279.1 = select i1 %123, float %.sroa.17271.0, float %.sroa.34279.8
  %.sroa.17271.2 = select i1 %123, float %.sroa.34279.8, float %.sroa.17271.0
  %124 = fcmp reassoc ninf nsz olt float %.sroa.51287.9, %.sroa.17271.2
  %.sroa.51287.8 = select i1 %124, float %.sroa.17271.2, float %.sroa.51287.9
  %.sroa.17271.3 = select i1 %124, float %.sroa.51287.9, float %.sroa.17271.2
  %125 = fcmp reassoc ninf nsz olt float %.sroa.68295.12, %.sroa.17271.3
  %.sroa.68295.11 = select i1 %125, float %.sroa.17271.3, float %.sroa.68295.12
  %.sroa.17271.4 = select i1 %125, float %.sroa.68295.12, float %.sroa.17271.3
  %126 = fcmp reassoc ninf nsz olt float %.sroa.86304.11, %.sroa.17271.4
  %.sroa.86304.10 = select i1 %126, float %.sroa.17271.4, float %.sroa.86304.11
  %.sroa.17271.5 = select i1 %126, float %.sroa.86304.11, float %.sroa.17271.4
  %127 = fcmp reassoc ninf nsz olt float %.sroa.103312.12, %.sroa.17271.5
  %.sroa.103312.11 = select i1 %127, float %.sroa.17271.5, float %.sroa.103312.12
  %.sroa.17271.6 = select i1 %127, float %.sroa.103312.12, float %.sroa.17271.5
  %128 = fcmp reassoc ninf nsz olt float %.sroa.120320.13, %.sroa.17271.6
  %.sroa.120320.12 = select i1 %128, float %.sroa.17271.6, float %.sroa.120320.13
  %.sroa.17271.7 = select i1 %128, float %.sroa.120320.13, float %.sroa.17271.6
  %129 = fcmp reassoc ninf nsz olt float %.sroa.137328.13, %.sroa.17271.7
  %.sroa.137328.12 = select i1 %129, float %.sroa.17271.7, float %.sroa.137328.13
  %130 = fcmp reassoc ninf nsz olt float %.sroa.51287.8, %.sroa.34279.1
  %.sroa.51287.2 = select i1 %130, float %.sroa.34279.1, float %.sroa.51287.8
  %.sroa.34279.3 = select i1 %130, float %.sroa.51287.8, float %.sroa.34279.1
  %131 = fcmp reassoc ninf nsz olt float %.sroa.68295.11, %.sroa.34279.3
  %.sroa.68295.10 = select i1 %131, float %.sroa.34279.3, float %.sroa.68295.11
  %.sroa.34279.4 = select i1 %131, float %.sroa.68295.11, float %.sroa.34279.3
  %132 = fcmp reassoc ninf nsz olt float %.sroa.86304.10, %.sroa.34279.4
  %.sroa.86304.9 = select i1 %132, float %.sroa.34279.4, float %.sroa.86304.10
  %.sroa.34279.5 = select i1 %132, float %.sroa.86304.10, float %.sroa.34279.4
  %133 = fcmp reassoc ninf nsz olt float %.sroa.103312.11, %.sroa.34279.5
  %.sroa.103312.10 = select i1 %133, float %.sroa.34279.5, float %.sroa.103312.11
  %.sroa.34279.6 = select i1 %133, float %.sroa.103312.11, float %.sroa.34279.5
  %134 = fcmp reassoc ninf nsz olt float %.sroa.120320.12, %.sroa.34279.6
  %.sroa.120320.11 = select i1 %134, float %.sroa.34279.6, float %.sroa.120320.12
  %.sroa.34279.7 = select i1 %134, float %.sroa.120320.12, float %.sroa.34279.6
  %135 = fcmp reassoc ninf nsz olt float %.sroa.137328.12, %.sroa.34279.7
  %.sroa.137328.11 = select i1 %135, float %.sroa.34279.7, float %.sroa.137328.12
  %136 = fcmp reassoc ninf nsz olt float %.sroa.68295.10, %.sroa.51287.2
  %.sroa.68295.3 = select i1 %136, float %.sroa.51287.2, float %.sroa.68295.10
  %.sroa.51287.4 = select i1 %136, float %.sroa.68295.10, float %.sroa.51287.2
  %137 = fcmp reassoc ninf nsz olt float %.sroa.86304.9, %.sroa.51287.4
  %.sroa.86304.8 = select i1 %137, float %.sroa.51287.4, float %.sroa.86304.9
  %.sroa.51287.5 = select i1 %137, float %.sroa.86304.9, float %.sroa.51287.4
  %138 = fcmp reassoc ninf nsz olt float %.sroa.103312.10, %.sroa.51287.5
  %.sroa.103312.9 = select i1 %138, float %.sroa.51287.5, float %.sroa.103312.10
  %.sroa.51287.6 = select i1 %138, float %.sroa.103312.10, float %.sroa.51287.5
  %139 = fcmp reassoc ninf nsz olt float %.sroa.120320.11, %.sroa.51287.6
  %.sroa.120320.10 = select i1 %139, float %.sroa.51287.6, float %.sroa.120320.11
  %.sroa.51287.7 = select i1 %139, float %.sroa.120320.11, float %.sroa.51287.6
  %140 = fcmp reassoc ninf nsz olt float %.sroa.137328.11, %.sroa.51287.7
  %.sroa.137328.10 = select i1 %140, float %.sroa.51287.7, float %.sroa.137328.11
  %141 = fcmp reassoc ninf nsz olt float %.sroa.86304.8, %.sroa.68295.3
  %.sroa.68295.5 = select i1 %141, float %.sroa.86304.8, float %.sroa.68295.3
  %142 = fcmp reassoc ninf nsz olt float %.sroa.103312.9, %.sroa.68295.5
  %.sroa.68295.7 = select i1 %142, float %.sroa.103312.9, float %.sroa.68295.5
  %143 = fcmp reassoc ninf nsz olt float %.sroa.120320.10, %.sroa.68295.7
  %.sroa.68295.8 = select i1 %143, float %.sroa.120320.10, float %.sroa.68295.7
  %144 = fcmp reassoc ninf nsz olt float %.sroa.137328.10, %.sroa.68295.8
  %.sroa.68295.9 = select i1 %144, float %.sroa.137328.10, float %.sroa.68295.8
  %145 = load ptr, ptr %24, align 8
  %146 = load i32, ptr %25, align 4
  %147 = load i32, ptr %26, align 4
  %148 = sub i32 %146, %31
  %149 = mul i32 %148, %38
  %150 = add i32 %.02741, %149
  %151 = mul i32 %150, %147
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %145, i64 %152
  store float %.sroa.68295.9, ptr %153, align 4
  %154 = load ptr, ptr %21, align 8
  %155 = load i32, ptr %22, align 4
  %156 = load i32, ptr %23, align 4
  %157 = mul i32 %155, %47
  %158 = add i32 %157, %53
  %159 = mul i32 %158, %156
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %154, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = add i32 %157, %64
  %165 = mul i32 %164, %156
  %166 = add i32 %165, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %154, i64 %167
  %169 = load float, ptr %168, align 4
  %170 = add i32 %157, %72
  %171 = mul i32 %170, %156
  %172 = add i32 %171, 1
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, ptr %154, i64 %173
  %175 = load float, ptr %174, align 4
  %176 = mul i32 %155, %79
  %177 = add i32 %176, %53
  %178 = mul i32 %177, %156
  %179 = add i32 %178, 1
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %154, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = add i32 %176, %64
  %184 = mul i32 %183, %156
  %185 = add i32 %184, 1
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %154, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = add i32 %176, %72
  %190 = mul i32 %189, %156
  %191 = add i32 %190, 1
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %154, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = mul i32 %155, %98
  %196 = add i32 %195, %53
  %197 = mul i32 %196, %156
  %198 = add i32 %197, 1
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, ptr %154, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = add i32 %195, %64
  %203 = mul i32 %202, %156
  %204 = add i32 %203, 1
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, ptr %154, i64 %205
  %207 = load float, ptr %206, align 4
  %208 = add i32 %195, %72
  %209 = mul i32 %208, %156
  %210 = add i32 %209, 1
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %154, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fcmp reassoc ninf nsz olt float %169, %163
  %.sroa.17198.0 = select i1 %214, float %163, float %169
  %.sroa.0190.0 = select i1 %214, float %169, float %163
  %215 = fcmp reassoc ninf nsz olt float %175, %.sroa.0190.0
  %.sroa.34206.8 = select i1 %215, float %.sroa.0190.0, float %175
  %.sroa.0190.1 = select i1 %215, float %175, float %.sroa.0190.0
  %216 = fcmp reassoc ninf nsz olt float %182, %.sroa.0190.1
  %.sroa.51214.9 = select i1 %216, float %.sroa.0190.1, float %182
  %.sroa.0190.2 = select i1 %216, float %182, float %.sroa.0190.1
  %217 = fcmp reassoc ninf nsz olt float %188, %.sroa.0190.2
  %.sroa.68222.12 = select i1 %217, float %.sroa.0190.2, float %188
  %.sroa.0190.3 = select i1 %217, float %188, float %.sroa.0190.2
  %218 = fcmp reassoc ninf nsz olt float %194, %.sroa.0190.3
  %.sroa.86231.11 = select i1 %218, float %.sroa.0190.3, float %194
  %.sroa.0190.4 = select i1 %218, float %194, float %.sroa.0190.3
  %219 = fcmp reassoc ninf nsz olt float %201, %.sroa.0190.4
  %.sroa.103239.12 = select i1 %219, float %.sroa.0190.4, float %201
  %.sroa.0190.5 = select i1 %219, float %201, float %.sroa.0190.4
  %220 = fcmp reassoc ninf nsz olt float %207, %.sroa.0190.5
  %.sroa.120247.13 = select i1 %220, float %.sroa.0190.5, float %207
  %.sroa.0190.6 = select i1 %220, float %207, float %.sroa.0190.5
  %221 = fcmp reassoc ninf nsz olt float %213, %.sroa.0190.6
  %.sroa.137255.13 = select i1 %221, float %.sroa.0190.6, float %213
  %222 = fcmp reassoc ninf nsz olt float %.sroa.34206.8, %.sroa.17198.0
  %.sroa.34206.1 = select i1 %222, float %.sroa.17198.0, float %.sroa.34206.8
  %.sroa.17198.2 = select i1 %222, float %.sroa.34206.8, float %.sroa.17198.0
  %223 = fcmp reassoc ninf nsz olt float %.sroa.51214.9, %.sroa.17198.2
  %.sroa.51214.8 = select i1 %223, float %.sroa.17198.2, float %.sroa.51214.9
  %.sroa.17198.3 = select i1 %223, float %.sroa.51214.9, float %.sroa.17198.2
  %224 = fcmp reassoc ninf nsz olt float %.sroa.68222.12, %.sroa.17198.3
  %.sroa.68222.11 = select i1 %224, float %.sroa.17198.3, float %.sroa.68222.12
  %.sroa.17198.4 = select i1 %224, float %.sroa.68222.12, float %.sroa.17198.3
  %225 = fcmp reassoc ninf nsz olt float %.sroa.86231.11, %.sroa.17198.4
  %.sroa.86231.10 = select i1 %225, float %.sroa.17198.4, float %.sroa.86231.11
  %.sroa.17198.5 = select i1 %225, float %.sroa.86231.11, float %.sroa.17198.4
  %226 = fcmp reassoc ninf nsz olt float %.sroa.103239.12, %.sroa.17198.5
  %.sroa.103239.11 = select i1 %226, float %.sroa.17198.5, float %.sroa.103239.12
  %.sroa.17198.6 = select i1 %226, float %.sroa.103239.12, float %.sroa.17198.5
  %227 = fcmp reassoc ninf nsz olt float %.sroa.120247.13, %.sroa.17198.6
  %.sroa.120247.12 = select i1 %227, float %.sroa.17198.6, float %.sroa.120247.13
  %.sroa.17198.7 = select i1 %227, float %.sroa.120247.13, float %.sroa.17198.6
  %228 = fcmp reassoc ninf nsz olt float %.sroa.137255.13, %.sroa.17198.7
  %.sroa.137255.12 = select i1 %228, float %.sroa.17198.7, float %.sroa.137255.13
  %229 = fcmp reassoc ninf nsz olt float %.sroa.51214.8, %.sroa.34206.1
  %.sroa.51214.2 = select i1 %229, float %.sroa.34206.1, float %.sroa.51214.8
  %.sroa.34206.3 = select i1 %229, float %.sroa.51214.8, float %.sroa.34206.1
  %230 = fcmp reassoc ninf nsz olt float %.sroa.68222.11, %.sroa.34206.3
  %.sroa.68222.10 = select i1 %230, float %.sroa.34206.3, float %.sroa.68222.11
  %.sroa.34206.4 = select i1 %230, float %.sroa.68222.11, float %.sroa.34206.3
  %231 = fcmp reassoc ninf nsz olt float %.sroa.86231.10, %.sroa.34206.4
  %.sroa.86231.9 = select i1 %231, float %.sroa.34206.4, float %.sroa.86231.10
  %.sroa.34206.5 = select i1 %231, float %.sroa.86231.10, float %.sroa.34206.4
  %232 = fcmp reassoc ninf nsz olt float %.sroa.103239.11, %.sroa.34206.5
  %.sroa.103239.10 = select i1 %232, float %.sroa.34206.5, float %.sroa.103239.11
  %.sroa.34206.6 = select i1 %232, float %.sroa.103239.11, float %.sroa.34206.5
  %233 = fcmp reassoc ninf nsz olt float %.sroa.120247.12, %.sroa.34206.6
  %.sroa.120247.11 = select i1 %233, float %.sroa.34206.6, float %.sroa.120247.12
  %.sroa.34206.7 = select i1 %233, float %.sroa.120247.12, float %.sroa.34206.6
  %234 = fcmp reassoc ninf nsz olt float %.sroa.137255.12, %.sroa.34206.7
  %.sroa.137255.11 = select i1 %234, float %.sroa.34206.7, float %.sroa.137255.12
  %235 = fcmp reassoc ninf nsz olt float %.sroa.68222.10, %.sroa.51214.2
  %.sroa.68222.3 = select i1 %235, float %.sroa.51214.2, float %.sroa.68222.10
  %.sroa.51214.4 = select i1 %235, float %.sroa.68222.10, float %.sroa.51214.2
  %236 = fcmp reassoc ninf nsz olt float %.sroa.86231.9, %.sroa.51214.4
  %.sroa.86231.8 = select i1 %236, float %.sroa.51214.4, float %.sroa.86231.9
  %.sroa.51214.5 = select i1 %236, float %.sroa.86231.9, float %.sroa.51214.4
  %237 = fcmp reassoc ninf nsz olt float %.sroa.103239.10, %.sroa.51214.5
  %.sroa.103239.9 = select i1 %237, float %.sroa.51214.5, float %.sroa.103239.10
  %.sroa.51214.6 = select i1 %237, float %.sroa.103239.10, float %.sroa.51214.5
  %238 = fcmp reassoc ninf nsz olt float %.sroa.120247.11, %.sroa.51214.6
  %.sroa.120247.10 = select i1 %238, float %.sroa.51214.6, float %.sroa.120247.11
  %.sroa.51214.7 = select i1 %238, float %.sroa.120247.11, float %.sroa.51214.6
  %239 = fcmp reassoc ninf nsz olt float %.sroa.137255.11, %.sroa.51214.7
  %.sroa.137255.10 = select i1 %239, float %.sroa.51214.7, float %.sroa.137255.11
  %240 = fcmp reassoc ninf nsz olt float %.sroa.86231.8, %.sroa.68222.3
  %.sroa.68222.5 = select i1 %240, float %.sroa.86231.8, float %.sroa.68222.3
  %241 = fcmp reassoc ninf nsz olt float %.sroa.103239.9, %.sroa.68222.5
  %.sroa.68222.7 = select i1 %241, float %.sroa.103239.9, float %.sroa.68222.5
  %242 = fcmp reassoc ninf nsz olt float %.sroa.120247.10, %.sroa.68222.7
  %.sroa.68222.8 = select i1 %242, float %.sroa.120247.10, float %.sroa.68222.7
  %243 = fcmp reassoc ninf nsz olt float %.sroa.137255.10, %.sroa.68222.8
  %.sroa.68222.9 = select i1 %243, float %.sroa.137255.10, float %.sroa.68222.8
  %244 = load ptr, ptr %24, align 8
  %245 = load i32, ptr %25, align 4
  %246 = load i32, ptr %26, align 4
  %247 = sub i32 %245, %31
  %248 = mul i32 %247, %38
  %249 = add i32 %.02741, %248
  %250 = mul i32 %249, %246
  %251 = add i32 %250, 1
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, ptr %244, i64 %252
  store float %.sroa.68222.9, ptr %253, align 4
  %254 = load ptr, ptr %21, align 8
  %255 = load i32, ptr %22, align 4
  %256 = load i32, ptr %23, align 4
  %257 = mul i32 %255, %47
  %258 = add i32 %257, %53
  %259 = mul i32 %258, %256
  %260 = add i32 %259, 2
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, ptr %254, i64 %261
  %263 = load float, ptr %262, align 4
  %264 = add i32 %257, %64
  %265 = mul i32 %264, %256
  %266 = add i32 %265, 2
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %254, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %257, %72
  %271 = mul i32 %270, %256
  %272 = add i32 %271, 2
  %273 = sext i32 %272 to i64
  %274 = getelementptr float, ptr %254, i64 %273
  %275 = load float, ptr %274, align 4
  %276 = mul i32 %255, %79
  %277 = add i32 %276, %53
  %278 = mul i32 %277, %256
  %279 = add i32 %278, 2
  %280 = sext i32 %279 to i64
  %281 = getelementptr float, ptr %254, i64 %280
  %282 = load float, ptr %281, align 4
  %283 = add i32 %276, %64
  %284 = mul i32 %283, %256
  %285 = add i32 %284, 2
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, ptr %254, i64 %286
  %288 = load float, ptr %287, align 4
  %289 = add i32 %276, %72
  %290 = mul i32 %289, %256
  %291 = add i32 %290, 2
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, ptr %254, i64 %292
  %294 = load float, ptr %293, align 4
  %295 = mul i32 %255, %98
  %296 = add i32 %295, %53
  %297 = mul i32 %296, %256
  %298 = add i32 %297, 2
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, ptr %254, i64 %299
  %301 = load float, ptr %300, align 4
  %302 = add i32 %295, %64
  %303 = mul i32 %302, %256
  %304 = add i32 %303, 2
  %305 = sext i32 %304 to i64
  %306 = getelementptr float, ptr %254, i64 %305
  %307 = load float, ptr %306, align 4
  %308 = add i32 %295, %72
  %309 = mul i32 %308, %256
  %310 = add i32 %309, 2
  %311 = sext i32 %310 to i64
  %312 = getelementptr float, ptr %254, i64 %311
  %313 = load float, ptr %312, align 4
  %314 = fcmp reassoc ninf nsz olt float %269, %263
  %.sroa.17.0 = select i1 %314, float %263, float %269
  %.sroa.0.0 = select i1 %314, float %269, float %263
  %315 = fcmp reassoc ninf nsz olt float %275, %.sroa.0.0
  %.sroa.34.8 = select i1 %315, float %.sroa.0.0, float %275
  %.sroa.0.1 = select i1 %315, float %275, float %.sroa.0.0
  %316 = fcmp reassoc ninf nsz olt float %282, %.sroa.0.1
  %.sroa.51.9 = select i1 %316, float %.sroa.0.1, float %282
  %.sroa.0.2 = select i1 %316, float %282, float %.sroa.0.1
  %317 = fcmp reassoc ninf nsz olt float %288, %.sroa.0.2
  %.sroa.68.12 = select i1 %317, float %.sroa.0.2, float %288
  %.sroa.0.3 = select i1 %317, float %288, float %.sroa.0.2
  %318 = fcmp reassoc ninf nsz olt float %294, %.sroa.0.3
  %.sroa.86.11 = select i1 %318, float %.sroa.0.3, float %294
  %.sroa.0.4 = select i1 %318, float %294, float %.sroa.0.3
  %319 = fcmp reassoc ninf nsz olt float %301, %.sroa.0.4
  %.sroa.103.12 = select i1 %319, float %.sroa.0.4, float %301
  %.sroa.0.5 = select i1 %319, float %301, float %.sroa.0.4
  %320 = fcmp reassoc ninf nsz olt float %307, %.sroa.0.5
  %.sroa.120.13 = select i1 %320, float %.sroa.0.5, float %307
  %.sroa.0.6 = select i1 %320, float %307, float %.sroa.0.5
  %321 = fcmp reassoc ninf nsz olt float %313, %.sroa.0.6
  %.sroa.137.13 = select i1 %321, float %.sroa.0.6, float %313
  %322 = fcmp reassoc ninf nsz olt float %.sroa.34.8, %.sroa.17.0
  %.sroa.34.1 = select i1 %322, float %.sroa.17.0, float %.sroa.34.8
  %.sroa.17.2 = select i1 %322, float %.sroa.34.8, float %.sroa.17.0
  %323 = fcmp reassoc ninf nsz olt float %.sroa.51.9, %.sroa.17.2
  %.sroa.51.8 = select i1 %323, float %.sroa.17.2, float %.sroa.51.9
  %.sroa.17.3 = select i1 %323, float %.sroa.51.9, float %.sroa.17.2
  %324 = fcmp reassoc ninf nsz olt float %.sroa.68.12, %.sroa.17.3
  %.sroa.68.11 = select i1 %324, float %.sroa.17.3, float %.sroa.68.12
  %.sroa.17.4 = select i1 %324, float %.sroa.68.12, float %.sroa.17.3
  %325 = fcmp reassoc ninf nsz olt float %.sroa.86.11, %.sroa.17.4
  %.sroa.86.10 = select i1 %325, float %.sroa.17.4, float %.sroa.86.11
  %.sroa.17.5 = select i1 %325, float %.sroa.86.11, float %.sroa.17.4
  %326 = fcmp reassoc ninf nsz olt float %.sroa.103.12, %.sroa.17.5
  %.sroa.103.11 = select i1 %326, float %.sroa.17.5, float %.sroa.103.12
  %.sroa.17.6 = select i1 %326, float %.sroa.103.12, float %.sroa.17.5
  %327 = fcmp reassoc ninf nsz olt float %.sroa.120.13, %.sroa.17.6
  %.sroa.120.12 = select i1 %327, float %.sroa.17.6, float %.sroa.120.13
  %.sroa.17.7 = select i1 %327, float %.sroa.120.13, float %.sroa.17.6
  %328 = fcmp reassoc ninf nsz olt float %.sroa.137.13, %.sroa.17.7
  %.sroa.137.12 = select i1 %328, float %.sroa.17.7, float %.sroa.137.13
  %329 = fcmp reassoc ninf nsz olt float %.sroa.51.8, %.sroa.34.1
  %.sroa.51.2 = select i1 %329, float %.sroa.34.1, float %.sroa.51.8
  %.sroa.34.3 = select i1 %329, float %.sroa.51.8, float %.sroa.34.1
  %330 = fcmp reassoc ninf nsz olt float %.sroa.68.11, %.sroa.34.3
  %.sroa.68.10 = select i1 %330, float %.sroa.34.3, float %.sroa.68.11
  %.sroa.34.4 = select i1 %330, float %.sroa.68.11, float %.sroa.34.3
  %331 = fcmp reassoc ninf nsz olt float %.sroa.86.10, %.sroa.34.4
  %.sroa.86.9 = select i1 %331, float %.sroa.34.4, float %.sroa.86.10
  %.sroa.34.5 = select i1 %331, float %.sroa.86.10, float %.sroa.34.4
  %332 = fcmp reassoc ninf nsz olt float %.sroa.103.11, %.sroa.34.5
  %.sroa.103.10 = select i1 %332, float %.sroa.34.5, float %.sroa.103.11
  %.sroa.34.6 = select i1 %332, float %.sroa.103.11, float %.sroa.34.5
  %333 = fcmp reassoc ninf nsz olt float %.sroa.120.12, %.sroa.34.6
  %.sroa.120.11 = select i1 %333, float %.sroa.34.6, float %.sroa.120.12
  %.sroa.34.7 = select i1 %333, float %.sroa.120.12, float %.sroa.34.6
  %334 = fcmp reassoc ninf nsz olt float %.sroa.137.12, %.sroa.34.7
  %.sroa.137.11 = select i1 %334, float %.sroa.34.7, float %.sroa.137.12
  %335 = fcmp reassoc ninf nsz olt float %.sroa.68.10, %.sroa.51.2
  %.sroa.68.3 = select i1 %335, float %.sroa.51.2, float %.sroa.68.10
  %.sroa.51.4 = select i1 %335, float %.sroa.68.10, float %.sroa.51.2
  %336 = fcmp reassoc ninf nsz olt float %.sroa.86.9, %.sroa.51.4
  %.sroa.86.8 = select i1 %336, float %.sroa.51.4, float %.sroa.86.9
  %.sroa.51.5 = select i1 %336, float %.sroa.86.9, float %.sroa.51.4
  %337 = fcmp reassoc ninf nsz olt float %.sroa.103.10, %.sroa.51.5
  %.sroa.103.9 = select i1 %337, float %.sroa.51.5, float %.sroa.103.10
  %.sroa.51.6 = select i1 %337, float %.sroa.103.10, float %.sroa.51.5
  %338 = fcmp reassoc ninf nsz olt float %.sroa.120.11, %.sroa.51.6
  %.sroa.120.10 = select i1 %338, float %.sroa.51.6, float %.sroa.120.11
  %.sroa.51.7 = select i1 %338, float %.sroa.120.11, float %.sroa.51.6
  %339 = fcmp reassoc ninf nsz olt float %.sroa.137.11, %.sroa.51.7
  %.sroa.137.10 = select i1 %339, float %.sroa.51.7, float %.sroa.137.11
  %340 = fcmp reassoc ninf nsz olt float %.sroa.86.8, %.sroa.68.3
  %.sroa.68.5 = select i1 %340, float %.sroa.86.8, float %.sroa.68.3
  %341 = fcmp reassoc ninf nsz olt float %.sroa.103.9, %.sroa.68.5
  %.sroa.68.7 = select i1 %341, float %.sroa.103.9, float %.sroa.68.5
  %342 = fcmp reassoc ninf nsz olt float %.sroa.120.10, %.sroa.68.7
  %.sroa.68.8 = select i1 %342, float %.sroa.120.10, float %.sroa.68.7
  %343 = fcmp reassoc ninf nsz olt float %.sroa.137.10, %.sroa.68.8
  %.sroa.68.9 = select i1 %343, float %.sroa.137.10, float %.sroa.68.8
  %344 = load ptr, ptr %24, align 8
  %345 = load i32, ptr %25, align 4
  %346 = load i32, ptr %26, align 4
  %347 = sub i32 %345, %31
  %348 = mul i32 %347, %38
  %349 = add i32 %.02741, %348
  %350 = mul i32 %349, %346
  %351 = add i32 %350, 2
  %352 = sext i32 %351 to i64
  %353 = getelementptr float, ptr %344, i64 %352
  store float %.sroa.68.9, ptr %353, align 4
  %354 = add nsw i32 %.02741, 1
  %exitcond.not = icmp eq i32 %18, %354
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body5.lr.ph
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
