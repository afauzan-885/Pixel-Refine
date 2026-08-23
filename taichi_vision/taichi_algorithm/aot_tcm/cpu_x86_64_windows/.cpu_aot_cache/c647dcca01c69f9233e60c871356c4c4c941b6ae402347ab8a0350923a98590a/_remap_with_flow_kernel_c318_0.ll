; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.13 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_kernel_c318_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_remap_with_flow_kernel_c318_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 76
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 72
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 80
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 84
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 56
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 60
  %31 = load i32, ptr %30, align 4
  %32 = add i32 %21, -1
  %33 = add i32 %23, -1
  %34 = add i32 %31, -1
  %35 = add i32 %29, -1
  %36 = sitofp i32 %32 to float
  %37 = sitofp i32 %33 to float
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 32
  %40 = getelementptr i8, ptr %19, i64 20
  %41 = getelementptr i8, ptr %19, i64 24
  %42 = getelementptr i8, ptr %19, i64 8
  %43 = getelementptr i8, ptr %19, i64 4
  %44 = getelementptr i8, ptr %19, i64 48
  %45 = getelementptr i8, ptr %19, i64 44
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.06 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %253, %for_loop_body ]
  %46 = load ptr, ptr %3, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 4
  %50 = load i32, ptr %49, align 4
  %51 = sdiv i32 %.06, %50
  %52 = mul i32 %51, %50
  %53 = xor i32 %50, %.06
  %54 = icmp slt i32 %53, 0
  %55 = icmp ne i32 %.06, %52
  %56 = and i1 %54, %55
  %.neg4 = sext i1 %56 to i32
  %57 = add i32 %51, %.neg4
  %58 = mul i32 %50, -1
  %59 = mul i32 %58, %57
  %60 = add i32 %.06, %59
  %61 = sitofp i32 %60 to float
  %62 = fmul reassoc ninf nsz float %61, %36
  %63 = getelementptr inbounds nuw i8, ptr %48, i64 8
  %64 = load i32, ptr %63, align 4
  %65 = add i32 %64, -1
  %66 = sitofp i32 %65 to float
  %67 = fdiv reassoc ninf nsz float %62, %66
  %68 = sitofp i32 %57 to float
  %69 = fmul reassoc ninf nsz float %68, %37
  %70 = getelementptr inbounds nuw i8, ptr %48, i64 12
  %71 = load i32, ptr %70, align 4
  %72 = add i32 %71, -1
  %73 = sitofp i32 %72 to float
  %74 = fdiv reassoc ninf nsz float %69, %73
  %75 = tail call reassoc ninf nsz float @llvm.floor.f32(float %67)
  %76 = fptosi float %75 to i32
  %77 = tail call reassoc ninf nsz float @llvm.floor.f32(float %74)
  %78 = fptosi float %77 to i32
  %79 = sitofp i32 %76 to float
  %80 = fsub reassoc ninf nsz float %67, %79
  %81 = sitofp i32 %78 to float
  %82 = fsub reassoc ninf nsz float %74, %81
  %83 = tail call i32 @llvm.abs.i32(i32 %76, i1 true)
  %84 = sub i32 %83, %32
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = shl nuw i32 %85, 1
  %87 = sub i32 %83, %86
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %32, i32 %88)
  %90 = tail call i32 @llvm.abs.i32(i32 %78, i1 true)
  %91 = sub i32 %90, %33
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %93 = shl nuw i32 %92, 1
  %94 = sub i32 %90, %93
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %33, i32 %95)
  %97 = add i32 %76, 1
  %98 = tail call i32 @llvm.abs.i32(i32 %97, i1 true)
  %99 = sub i32 %98, %32
  %100 = tail call i32 @llvm.smax.i32(i32 %99, i32 0)
  %101 = shl nuw i32 %100, 1
  %102 = sub i32 %98, %101
  %103 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %32, i32 %103)
  %105 = add i32 %78, 1
  %106 = tail call i32 @llvm.abs.i32(i32 %105, i1 true)
  %107 = sub i32 %106, %33
  %108 = tail call i32 @llvm.smax.i32(i32 %107, i32 0)
  %109 = shl nuw i32 %108, 1
  %110 = sub i32 %106, %109
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = tail call i32 @llvm.smin.i32(i32 %33, i32 %111)
  %113 = load ptr, ptr %39, align 8
  %114 = load i32, ptr %40, align 4
  %115 = load i32, ptr %41, align 4
  %116 = mul i32 %96, %114
  %117 = add i32 %89, %116
  %118 = mul i32 %117, %115
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %113, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = add i32 %104, %116
  %123 = mul i32 %122, %115
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %113, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = mul i32 %112, %114
  %128 = add i32 %127, %89
  %129 = mul i32 %128, %115
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %113, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = add i32 %104, %127
  %134 = mul i32 %133, %115
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %113, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %139 = fmul reassoc ninf nsz float %138, %121
  %140 = fmul reassoc ninf nsz float %80, %126
  %141 = fadd reassoc ninf nsz float %139, %140
  %142 = fmul reassoc ninf nsz float %138, %132
  %143 = fmul reassoc ninf nsz float %80, %137
  %144 = fadd reassoc ninf nsz float %142, %143
  %145 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %146 = fmul reassoc ninf nsz float %141, %145
  %147 = fmul reassoc ninf nsz float %144, %82
  %148 = fadd reassoc ninf nsz float %146, %147
  %149 = add i32 %118, 1
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %113, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = add i32 %123, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %113, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = add i32 %129, 1
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %113, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = add i32 %134, 1
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %113, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = fmul reassoc ninf nsz float %138, %152
  %166 = fmul reassoc ninf nsz float %80, %156
  %167 = fadd reassoc ninf nsz float %165, %166
  %168 = fmul reassoc ninf nsz float %138, %160
  %169 = fmul reassoc ninf nsz float %80, %164
  %170 = fadd reassoc ninf nsz float %168, %169
  %171 = fmul reassoc ninf nsz float %167, %145
  %172 = fmul reassoc ninf nsz float %170, %82
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %148, %25
  %175 = fadd reassoc ninf nsz float %174, %61
  %176 = fmul reassoc ninf nsz float %173, %27
  %177 = fadd reassoc ninf nsz float %176, %68
  %178 = tail call reassoc ninf nsz float @llvm.floor.f32(float %175)
  %179 = fptosi float %178 to i32
  %180 = tail call reassoc ninf nsz float @llvm.floor.f32(float %177)
  %181 = fptosi float %180 to i32
  %182 = sitofp i32 %179 to float
  %183 = fsub reassoc ninf nsz float %175, %182
  %184 = sitofp i32 %181 to float
  %185 = fsub reassoc ninf nsz float %177, %184
  %186 = tail call i32 @llvm.abs.i32(i32 %179, i1 true)
  %187 = sub i32 %186, %34
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = shl nuw i32 %188, 1
  %190 = sub i32 %186, %189
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = tail call i32 @llvm.smin.i32(i32 %34, i32 %191)
  %193 = tail call i32 @llvm.abs.i32(i32 %181, i1 true)
  %194 = sub i32 %193, %35
  %195 = tail call i32 @llvm.smax.i32(i32 %194, i32 0)
  %196 = shl nuw i32 %195, 1
  %197 = sub i32 %193, %196
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %35, i32 %198)
  %200 = add i32 %179, 1
  %201 = tail call i32 @llvm.abs.i32(i32 %200, i1 true)
  %202 = sub i32 %201, %34
  %203 = tail call i32 @llvm.smax.i32(i32 %202, i32 0)
  %204 = shl nuw i32 %203, 1
  %205 = sub i32 %201, %204
  %206 = tail call i32 @llvm.smax.i32(i32 %205, i32 0)
  %207 = tail call i32 @llvm.smin.i32(i32 %34, i32 %206)
  %208 = add i32 %181, 1
  %209 = tail call i32 @llvm.abs.i32(i32 %208, i1 true)
  %210 = sub i32 %209, %35
  %211 = tail call i32 @llvm.smax.i32(i32 %210, i32 0)
  %212 = shl nuw i32 %211, 1
  %213 = sub i32 %209, %212
  %214 = tail call i32 @llvm.smax.i32(i32 %213, i32 0)
  %215 = tail call i32 @llvm.smin.i32(i32 %35, i32 %214)
  %216 = load ptr, ptr %42, align 8
  %217 = load i32, ptr %43, align 4
  %218 = mul i32 %199, %217
  %219 = add i32 %218, %192
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, ptr %216, i64 %220
  %222 = load float, ptr %221, align 4
  %223 = add i32 %218, %207
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %216, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = mul i32 %215, %217
  %228 = add i32 %227, %192
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %216, i64 %229
  %231 = load float, ptr %230, align 4
  %232 = add i32 %227, %207
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %216, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fsub reassoc ninf nsz float 1.000000e+00, %183
  %237 = fmul reassoc ninf nsz float %236, %222
  %238 = fmul reassoc ninf nsz float %183, %226
  %239 = fadd reassoc ninf nsz float %237, %238
  %240 = fmul reassoc ninf nsz float %236, %231
  %241 = fmul reassoc ninf nsz float %183, %235
  %242 = fadd reassoc ninf nsz float %240, %241
  %243 = fsub reassoc ninf nsz float %242, %239
  %244 = fmul reassoc ninf nsz float %243, %185
  %245 = fadd reassoc ninf nsz float %244, %239
  %246 = load ptr, ptr %44, align 8
  %247 = load i32, ptr %45, align 4
  %248 = sub i32 %247, %50
  %249 = mul i32 %248, %57
  %250 = add i32 %.06, %249
  %251 = sext i32 %250 to i64
  %252 = getelementptr float, ptr %246, i64 %251
  store float %245, ptr %252, align 4
  %253 = add nsw i32 %.06, 1
  %exitcond.not = icmp eq i32 %18, %253
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
  %4 = alloca %struct.RuntimeContext.13, align 8
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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
