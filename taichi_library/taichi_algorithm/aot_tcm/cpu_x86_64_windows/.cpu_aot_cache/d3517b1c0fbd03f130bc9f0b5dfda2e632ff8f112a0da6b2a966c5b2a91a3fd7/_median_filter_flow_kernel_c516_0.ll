; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.15 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_median_filter_flow_kernel_c516_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_median_filter_flow_kernel_c516_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  br label %for_loop_body5.preheader

after_for.loopexit:                               ; preds = %for_loop_body5.preheader
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.preheader:                         ; preds = %for_loop_body5.preheader, %for_loop_body.lr.ph
  %.01929 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %259, %for_loop_body5.preheader ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.01929, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.01929
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.01929, %33
  %37 = and i1 %35, %36
  %.neg24 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg24
  %39 = mul i32 %38, %31
  %40 = add i32 %38, -1
  %41 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %42 = load i32, ptr %41, align 4
  %43 = add i32 %42, -1
  %44 = tail call i32 @llvm.smin.i32(i32 %40, i32 %43)
  %45 = tail call i32 @llvm.smax.i32(i32 %44, i32 0)
  %46 = mul i32 %31, -1
  %47 = mul i32 %46, %38
  %48 = add i32 %.01929, %47
  %49 = add i32 %48, -1
  %50 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %51 = load i32, ptr %50, align 4
  %52 = add i32 %51, -1
  %53 = tail call i32 @llvm.smin.i32(i32 %49, i32 %52)
  %54 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %55 = load ptr, ptr %21, align 8
  %56 = load i32, ptr %22, align 4
  %57 = load i32, ptr %23, align 4
  %58 = mul i32 %45, %56
  %59 = add i32 %54, %58
  %60 = mul i32 %59, %57
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, ptr %55, i64 %61
  %63 = load float, ptr %62, align 4
  %64 = sub i32 %58, %39
  %65 = add i32 %.01929, %64
  %66 = mul i32 %65, %57
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %55, i64 %67
  %69 = load float, ptr %68, align 4
  %70 = add i32 %48, 1
  %71 = tail call i32 @llvm.smin.i32(i32 %70, i32 %52)
  %72 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %73 = add i32 %72, %58
  %74 = mul i32 %73, %57
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, ptr %55, i64 %75
  %77 = load float, ptr %76, align 4
  %78 = mul i32 %38, %56
  %79 = add i32 %54, %78
  %80 = mul i32 %79, %57
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %55, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = sub i32 %56, %31
  %85 = mul i32 %84, %38
  %86 = add i32 %.01929, %85
  %87 = mul i32 %86, %57
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %55, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = add i32 %72, %78
  %92 = mul i32 %91, %57
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %55, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = add i32 %38, 1
  %97 = tail call i32 @llvm.smin.i32(i32 %96, i32 %43)
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = mul i32 %98, %56
  %100 = add i32 %54, %99
  %101 = mul i32 %100, %57
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %55, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = sub i32 %99, %39
  %106 = add i32 %.01929, %105
  %107 = mul i32 %106, %57
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %55, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = add i32 %72, %99
  %112 = mul i32 %111, %57
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %55, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = fcmp reassoc ninf nsz ogt float %63, %69
  %.sroa.17159.1 = select i1 %116, float %63, float %69
  %.sroa.0151.1 = select i1 %116, float %69, float %63
  %117 = fcmp reassoc ninf nsz ogt float %.sroa.17159.1, %77
  %.sroa.48174.16 = select i1 %117, float %.sroa.17159.1, float %77
  %.sroa.17159.20 = select i1 %117, float %77, float %.sroa.17159.1
  %118 = fcmp reassoc ninf nsz ogt float %.sroa.48174.16, %83
  %.sroa.75187.13 = select i1 %118, float %.sroa.48174.16, float %83
  %.sroa.48174.17 = select i1 %118, float %83, float %.sroa.48174.16
  %119 = fcmp reassoc ninf nsz ogt float %.sroa.75187.13, %90
  %.sroa.98198.12 = select i1 %119, float %.sroa.75187.13, float %90
  %.sroa.75187.14 = select i1 %119, float %90, float %.sroa.75187.13
  %120 = fcmp reassoc ninf nsz ogt float %.sroa.98198.12, %95
  %.sroa.118208.7 = select i1 %120, float %.sroa.98198.12, float %95
  %.sroa.98198.13 = select i1 %120, float %95, float %.sroa.98198.12
  %121 = fcmp reassoc ninf nsz ogt float %.sroa.118208.7, %104
  %.sroa.133215.4 = select i1 %121, float %.sroa.118208.7, float %104
  %.sroa.118208.8 = select i1 %121, float %104, float %.sroa.118208.7
  %122 = fcmp reassoc ninf nsz ogt float %.sroa.133215.4, %110
  %.sroa.144220.1 = select i1 %122, float %.sroa.133215.4, float %110
  %.sroa.133215.5 = select i1 %122, float %110, float %.sroa.133215.4
  %123 = fcmp reassoc ninf nsz ogt float %.sroa.144220.1, %115
  %.sroa.144220.2 = select i1 %123, float %115, float %.sroa.144220.1
  %124 = fcmp reassoc ninf nsz ogt float %.sroa.0151.1, %.sroa.17159.20
  %.sroa.17159.2 = select i1 %124, float %.sroa.0151.1, float %.sroa.17159.20
  %.sroa.0151.2 = select i1 %124, float %.sroa.17159.20, float %.sroa.0151.1
  %125 = fcmp reassoc ninf nsz ogt float %.sroa.17159.2, %.sroa.48174.17
  %.sroa.48174.14 = select i1 %125, float %.sroa.17159.2, float %.sroa.48174.17
  %.sroa.17159.19 = select i1 %125, float %.sroa.48174.17, float %.sroa.17159.2
  %126 = fcmp reassoc ninf nsz ogt float %.sroa.48174.14, %.sroa.75187.14
  %.sroa.75187.11 = select i1 %126, float %.sroa.48174.14, float %.sroa.75187.14
  %.sroa.48174.15 = select i1 %126, float %.sroa.75187.14, float %.sroa.48174.14
  %127 = fcmp reassoc ninf nsz ogt float %.sroa.75187.11, %.sroa.98198.13
  %.sroa.98198.10 = select i1 %127, float %.sroa.75187.11, float %.sroa.98198.13
  %.sroa.75187.12 = select i1 %127, float %.sroa.98198.13, float %.sroa.75187.11
  %128 = fcmp reassoc ninf nsz ogt float %.sroa.98198.10, %.sroa.118208.8
  %.sroa.118208.5 = select i1 %128, float %.sroa.98198.10, float %.sroa.118208.8
  %.sroa.98198.11 = select i1 %128, float %.sroa.118208.8, float %.sroa.98198.10
  %129 = fcmp reassoc ninf nsz ogt float %.sroa.118208.5, %.sroa.133215.5
  %.sroa.133215.2 = select i1 %129, float %.sroa.118208.5, float %.sroa.133215.5
  %.sroa.118208.6 = select i1 %129, float %.sroa.133215.5, float %.sroa.118208.5
  %130 = fcmp reassoc ninf nsz ogt float %.sroa.133215.2, %.sroa.144220.2
  %.sroa.133215.3 = select i1 %130, float %.sroa.144220.2, float %.sroa.133215.2
  %131 = fcmp reassoc ninf nsz ogt float %.sroa.0151.2, %.sroa.17159.19
  %.sroa.17159.4 = select i1 %131, float %.sroa.0151.2, float %.sroa.17159.19
  %.sroa.0151.4 = select i1 %131, float %.sroa.17159.19, float %.sroa.0151.2
  %132 = fcmp reassoc ninf nsz ogt float %.sroa.17159.4, %.sroa.48174.15
  %.sroa.48174.12 = select i1 %132, float %.sroa.17159.4, float %.sroa.48174.15
  %.sroa.17159.18 = select i1 %132, float %.sroa.48174.15, float %.sroa.17159.4
  %133 = fcmp reassoc ninf nsz ogt float %.sroa.48174.12, %.sroa.75187.12
  %.sroa.75187.9 = select i1 %133, float %.sroa.48174.12, float %.sroa.75187.12
  %.sroa.48174.13 = select i1 %133, float %.sroa.75187.12, float %.sroa.48174.12
  %134 = fcmp reassoc ninf nsz ogt float %.sroa.75187.9, %.sroa.98198.11
  %.sroa.98198.8 = select i1 %134, float %.sroa.75187.9, float %.sroa.98198.11
  %.sroa.75187.10 = select i1 %134, float %.sroa.98198.11, float %.sroa.75187.9
  %135 = fcmp reassoc ninf nsz ogt float %.sroa.98198.8, %.sroa.118208.6
  %.sroa.118208.3 = select i1 %135, float %.sroa.98198.8, float %.sroa.118208.6
  %.sroa.98198.9 = select i1 %135, float %.sroa.118208.6, float %.sroa.98198.8
  %136 = fcmp reassoc ninf nsz ogt float %.sroa.118208.3, %.sroa.133215.3
  %.sroa.118208.4 = select i1 %136, float %.sroa.133215.3, float %.sroa.118208.3
  %137 = fcmp reassoc ninf nsz ogt float %.sroa.0151.4, %.sroa.17159.18
  %.sroa.17159.6 = select i1 %137, float %.sroa.0151.4, float %.sroa.17159.18
  %.sroa.0151.6 = select i1 %137, float %.sroa.17159.18, float %.sroa.0151.4
  %138 = fcmp reassoc ninf nsz ogt float %.sroa.17159.6, %.sroa.48174.13
  %.sroa.48174.10 = select i1 %138, float %.sroa.17159.6, float %.sroa.48174.13
  %.sroa.17159.17 = select i1 %138, float %.sroa.48174.13, float %.sroa.17159.6
  %139 = fcmp reassoc ninf nsz ogt float %.sroa.48174.10, %.sroa.75187.10
  %.sroa.75187.7 = select i1 %139, float %.sroa.48174.10, float %.sroa.75187.10
  %.sroa.48174.11 = select i1 %139, float %.sroa.75187.10, float %.sroa.48174.10
  %140 = fcmp reassoc ninf nsz ogt float %.sroa.75187.7, %.sroa.98198.9
  %.sroa.98198.6 = select i1 %140, float %.sroa.75187.7, float %.sroa.98198.9
  %.sroa.75187.8 = select i1 %140, float %.sroa.98198.9, float %.sroa.75187.7
  %141 = fcmp reassoc ninf nsz ogt float %.sroa.98198.6, %.sroa.118208.4
  %.sroa.98198.7 = select i1 %141, float %.sroa.118208.4, float %.sroa.98198.6
  %142 = fcmp reassoc ninf nsz ogt float %.sroa.0151.6, %.sroa.17159.17
  %.sroa.17159.8 = select i1 %142, float %.sroa.0151.6, float %.sroa.17159.17
  %143 = fcmp reassoc ninf nsz ogt float %.sroa.17159.8, %.sroa.48174.11
  %.sroa.48174.8 = select i1 %143, float %.sroa.17159.8, float %.sroa.48174.11
  %144 = fcmp reassoc ninf nsz ogt float %.sroa.48174.8, %.sroa.75187.8
  %.sroa.75187.5 = select i1 %144, float %.sroa.48174.8, float %.sroa.75187.8
  %145 = fcmp reassoc ninf nsz ogt float %.sroa.75187.5, %.sroa.98198.7
  %.sroa.98198.5 = select i1 %145, float %.sroa.75187.5, float %.sroa.98198.7
  %146 = load ptr, ptr %24, align 8
  %147 = load i32, ptr %25, align 4
  %148 = load i32, ptr %26, align 4
  %149 = sub i32 %147, %31
  %150 = mul i32 %149, %38
  %151 = add i32 %.01929, %150
  %152 = mul i32 %151, %148
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %146, i64 %153
  store float %.sroa.98198.5, ptr %154, align 4
  %155 = load ptr, ptr %21, align 8
  %156 = load i32, ptr %22, align 4
  %157 = load i32, ptr %23, align 4
  %158 = mul i32 %156, %45
  %159 = add i32 %158, %54
  %160 = mul i32 %159, %157
  %161 = add i32 %160, 1
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %155, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = sub i32 %158, %39
  %166 = add i32 %.01929, %165
  %167 = mul i32 %166, %157
  %168 = add i32 %167, 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %155, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = add i32 %158, %72
  %173 = mul i32 %172, %157
  %174 = add i32 %173, 1
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %155, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = mul i32 %156, %38
  %179 = add i32 %178, %54
  %180 = mul i32 %179, %157
  %181 = add i32 %180, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %155, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = sub i32 %156, %31
  %186 = mul i32 %185, %38
  %187 = add i32 %.01929, %186
  %188 = mul i32 %187, %157
  %189 = add i32 %188, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %155, i64 %190
  %192 = load float, ptr %191, align 4
  %193 = add i32 %178, %72
  %194 = mul i32 %193, %157
  %195 = add i32 %194, 1
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %155, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = mul i32 %156, %98
  %200 = add i32 %199, %54
  %201 = mul i32 %200, %157
  %202 = add i32 %201, 1
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %155, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = sub i32 %199, %39
  %207 = add i32 %.01929, %206
  %208 = mul i32 %207, %157
  %209 = add i32 %208, 1
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, ptr %155, i64 %210
  %212 = load float, ptr %211, align 4
  %213 = add i32 %199, %72
  %214 = mul i32 %213, %157
  %215 = add i32 %214, 1
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %155, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = fcmp reassoc ninf nsz ogt float %164, %171
  %.sroa.17.1 = select i1 %219, float %164, float %171
  %.sroa.0.1 = select i1 %219, float %171, float %164
  %220 = fcmp reassoc ninf nsz ogt float %.sroa.17.1, %177
  %.sroa.48.16 = select i1 %220, float %.sroa.17.1, float %177
  %.sroa.17.20 = select i1 %220, float %177, float %.sroa.17.1
  %221 = fcmp reassoc ninf nsz ogt float %.sroa.48.16, %184
  %.sroa.75.13 = select i1 %221, float %.sroa.48.16, float %184
  %.sroa.48.17 = select i1 %221, float %184, float %.sroa.48.16
  %222 = fcmp reassoc ninf nsz ogt float %.sroa.75.13, %192
  %.sroa.98.12 = select i1 %222, float %.sroa.75.13, float %192
  %.sroa.75.14 = select i1 %222, float %192, float %.sroa.75.13
  %223 = fcmp reassoc ninf nsz ogt float %.sroa.98.12, %198
  %.sroa.118.7 = select i1 %223, float %.sroa.98.12, float %198
  %.sroa.98.13 = select i1 %223, float %198, float %.sroa.98.12
  %224 = fcmp reassoc ninf nsz ogt float %.sroa.118.7, %205
  %.sroa.133.4 = select i1 %224, float %.sroa.118.7, float %205
  %.sroa.118.8 = select i1 %224, float %205, float %.sroa.118.7
  %225 = fcmp reassoc ninf nsz ogt float %.sroa.133.4, %212
  %.sroa.144.1 = select i1 %225, float %.sroa.133.4, float %212
  %.sroa.133.5 = select i1 %225, float %212, float %.sroa.133.4
  %226 = fcmp reassoc ninf nsz ogt float %.sroa.144.1, %218
  %.sroa.144.2 = select i1 %226, float %218, float %.sroa.144.1
  %227 = fcmp reassoc ninf nsz ogt float %.sroa.0.1, %.sroa.17.20
  %.sroa.17.2 = select i1 %227, float %.sroa.0.1, float %.sroa.17.20
  %.sroa.0.2 = select i1 %227, float %.sroa.17.20, float %.sroa.0.1
  %228 = fcmp reassoc ninf nsz ogt float %.sroa.17.2, %.sroa.48.17
  %.sroa.48.14 = select i1 %228, float %.sroa.17.2, float %.sroa.48.17
  %.sroa.17.19 = select i1 %228, float %.sroa.48.17, float %.sroa.17.2
  %229 = fcmp reassoc ninf nsz ogt float %.sroa.48.14, %.sroa.75.14
  %.sroa.75.11 = select i1 %229, float %.sroa.48.14, float %.sroa.75.14
  %.sroa.48.15 = select i1 %229, float %.sroa.75.14, float %.sroa.48.14
  %230 = fcmp reassoc ninf nsz ogt float %.sroa.75.11, %.sroa.98.13
  %.sroa.98.10 = select i1 %230, float %.sroa.75.11, float %.sroa.98.13
  %.sroa.75.12 = select i1 %230, float %.sroa.98.13, float %.sroa.75.11
  %231 = fcmp reassoc ninf nsz ogt float %.sroa.98.10, %.sroa.118.8
  %.sroa.118.5 = select i1 %231, float %.sroa.98.10, float %.sroa.118.8
  %.sroa.98.11 = select i1 %231, float %.sroa.118.8, float %.sroa.98.10
  %232 = fcmp reassoc ninf nsz ogt float %.sroa.118.5, %.sroa.133.5
  %.sroa.133.2 = select i1 %232, float %.sroa.118.5, float %.sroa.133.5
  %.sroa.118.6 = select i1 %232, float %.sroa.133.5, float %.sroa.118.5
  %233 = fcmp reassoc ninf nsz ogt float %.sroa.133.2, %.sroa.144.2
  %.sroa.133.3 = select i1 %233, float %.sroa.144.2, float %.sroa.133.2
  %234 = fcmp reassoc ninf nsz ogt float %.sroa.0.2, %.sroa.17.19
  %.sroa.17.4 = select i1 %234, float %.sroa.0.2, float %.sroa.17.19
  %.sroa.0.4 = select i1 %234, float %.sroa.17.19, float %.sroa.0.2
  %235 = fcmp reassoc ninf nsz ogt float %.sroa.17.4, %.sroa.48.15
  %.sroa.48.12 = select i1 %235, float %.sroa.17.4, float %.sroa.48.15
  %.sroa.17.18 = select i1 %235, float %.sroa.48.15, float %.sroa.17.4
  %236 = fcmp reassoc ninf nsz ogt float %.sroa.48.12, %.sroa.75.12
  %.sroa.75.9 = select i1 %236, float %.sroa.48.12, float %.sroa.75.12
  %.sroa.48.13 = select i1 %236, float %.sroa.75.12, float %.sroa.48.12
  %237 = fcmp reassoc ninf nsz ogt float %.sroa.75.9, %.sroa.98.11
  %.sroa.98.8 = select i1 %237, float %.sroa.75.9, float %.sroa.98.11
  %.sroa.75.10 = select i1 %237, float %.sroa.98.11, float %.sroa.75.9
  %238 = fcmp reassoc ninf nsz ogt float %.sroa.98.8, %.sroa.118.6
  %.sroa.118.3 = select i1 %238, float %.sroa.98.8, float %.sroa.118.6
  %.sroa.98.9 = select i1 %238, float %.sroa.118.6, float %.sroa.98.8
  %239 = fcmp reassoc ninf nsz ogt float %.sroa.118.3, %.sroa.133.3
  %.sroa.118.4 = select i1 %239, float %.sroa.133.3, float %.sroa.118.3
  %240 = fcmp reassoc ninf nsz ogt float %.sroa.0.4, %.sroa.17.18
  %.sroa.17.6 = select i1 %240, float %.sroa.0.4, float %.sroa.17.18
  %.sroa.0.6 = select i1 %240, float %.sroa.17.18, float %.sroa.0.4
  %241 = fcmp reassoc ninf nsz ogt float %.sroa.17.6, %.sroa.48.13
  %.sroa.48.10 = select i1 %241, float %.sroa.17.6, float %.sroa.48.13
  %.sroa.17.17 = select i1 %241, float %.sroa.48.13, float %.sroa.17.6
  %242 = fcmp reassoc ninf nsz ogt float %.sroa.48.10, %.sroa.75.10
  %.sroa.75.7 = select i1 %242, float %.sroa.48.10, float %.sroa.75.10
  %.sroa.48.11 = select i1 %242, float %.sroa.75.10, float %.sroa.48.10
  %243 = fcmp reassoc ninf nsz ogt float %.sroa.75.7, %.sroa.98.9
  %.sroa.98.6 = select i1 %243, float %.sroa.75.7, float %.sroa.98.9
  %.sroa.75.8 = select i1 %243, float %.sroa.98.9, float %.sroa.75.7
  %244 = fcmp reassoc ninf nsz ogt float %.sroa.98.6, %.sroa.118.4
  %.sroa.98.7 = select i1 %244, float %.sroa.118.4, float %.sroa.98.6
  %245 = fcmp reassoc ninf nsz ogt float %.sroa.0.6, %.sroa.17.17
  %.sroa.17.8 = select i1 %245, float %.sroa.0.6, float %.sroa.17.17
  %246 = fcmp reassoc ninf nsz ogt float %.sroa.17.8, %.sroa.48.11
  %.sroa.48.8 = select i1 %246, float %.sroa.17.8, float %.sroa.48.11
  %247 = fcmp reassoc ninf nsz ogt float %.sroa.48.8, %.sroa.75.8
  %.sroa.75.5 = select i1 %247, float %.sroa.48.8, float %.sroa.75.8
  %248 = fcmp reassoc ninf nsz ogt float %.sroa.75.5, %.sroa.98.7
  %.sroa.98.5 = select i1 %248, float %.sroa.75.5, float %.sroa.98.7
  %249 = load ptr, ptr %24, align 8
  %250 = load i32, ptr %25, align 4
  %251 = load i32, ptr %26, align 4
  %252 = sub i32 %250, %31
  %253 = mul i32 %252, %38
  %254 = add i32 %.01929, %253
  %255 = mul i32 %254, %251
  %256 = add i32 %255, 1
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, ptr %249, i64 %257
  store float %.sroa.98.5, ptr %258, align 4
  %259 = add nsw i32 %.01929, 1
  %exitcond.not = icmp eq i32 %18, %259
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body5.preheader
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.15, align 8
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
