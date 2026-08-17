; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_downsample_2x_kernel_c262_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 8
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 12
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 16
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 20
  %18 = load i32, ptr %17, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %20 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %21 = load ptr, ptr %2, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 4
  store i32 %20, ptr %24, align 4
  %25 = mul i32 %20, %19
  %26 = load ptr, ptr %2, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  store i32 %25, ptr %28, align 4
  ret void
}

define void @_downsample_2x_kernel_c262_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %25, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.023 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %250, %for_loop_body ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.023, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.023
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.023, %32
  %36 = and i1 %34, %35
  %.neg4 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg4
  %38 = shl i32 %37, 1
  %39 = mul i32 %30, -2
  %40 = mul i32 %39, %37
  %41 = add i32 %lsr.iv, %40
  %42 = add i32 %38, -2
  %43 = tail call i32 @llvm.abs.i32(i32 %42, i1 true)
  %44 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %45 = load i32, ptr %44, align 4
  %46 = add i32 %45, -1
  %47 = sub i32 %43, %46
  %48 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %49 = shl nuw i32 %48, 1
  %50 = sub i32 %43, %49
  %51 = tail call i32 @llvm.smax.i32(i32 %50, i32 0)
  %52 = tail call i32 @llvm.smin.i32(i32 %46, i32 %51)
  %53 = add i32 %41, -2
  %54 = tail call i32 @llvm.abs.i32(i32 %53, i1 true)
  %55 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %56 = load i32, ptr %55, align 4
  %57 = add i32 %56, -1
  %58 = sub i32 %54, %57
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = shl nuw i32 %59, 1
  %61 = sub i32 %54, %60
  %62 = tail call i32 @llvm.smax.i32(i32 %61, i32 0)
  %63 = tail call i32 @llvm.smin.i32(i32 %57, i32 %62)
  %64 = load ptr, ptr %21, align 8
  %65 = load i32, ptr %22, align 4
  %66 = mul i32 %52, %65
  %67 = add i32 %63, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %64, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = add i32 %41, -1
  %72 = tail call i32 @llvm.abs.i32(i32 %71, i1 true)
  %73 = sub i32 %72, %57
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = shl nuw i32 %74, 1
  %76 = sub i32 %72, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %57, i32 %77)
  %79 = add i32 %78, %66
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %64, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = tail call i32 @llvm.abs.i32(i32 %41, i1 true)
  %84 = sub i32 %83, %57
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = shl nuw i32 %85, 1
  %87 = sub i32 %83, %86
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %57, i32 %88)
  %90 = add i32 %66, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %64, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = add i32 %41, 1
  %95 = tail call i32 @llvm.abs.i32(i32 %94, i1 true)
  %96 = sub i32 %95, %57
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = shl nuw i32 %97, 1
  %99 = sub i32 %95, %98
  %100 = tail call i32 @llvm.smax.i32(i32 %99, i32 0)
  %101 = tail call i32 @llvm.smin.i32(i32 %57, i32 %100)
  %102 = add i32 %101, %66
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %64, i64 %103
  %105 = load float, ptr %104, align 4
  %106 = add i32 %41, 2
  %107 = tail call i32 @llvm.abs.i32(i32 %106, i1 true)
  %108 = sub i32 %107, %57
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %110 = shl nuw i32 %109, 1
  %111 = sub i32 %107, %110
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = tail call i32 @llvm.smin.i32(i32 %57, i32 %112)
  %114 = add i32 %113, %66
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %64, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %38, -1
  %119 = tail call i32 @llvm.abs.i32(i32 %118, i1 true)
  %120 = sub i32 %119, %46
  %121 = tail call i32 @llvm.smax.i32(i32 %120, i32 0)
  %122 = shl nuw i32 %121, 1
  %123 = sub i32 %119, %122
  %124 = tail call i32 @llvm.smax.i32(i32 %123, i32 0)
  %125 = tail call i32 @llvm.smin.i32(i32 %46, i32 %124)
  %126 = mul i32 %125, %65
  %127 = add i32 %63, %126
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %64, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = add i32 %78, %126
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %64, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = add i32 %126, %89
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %64, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %101, %126
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %64, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %113, %126
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %64, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = tail call i32 @llvm.abs.i32(i32 %38, i1 true)
  %148 = sub i32 %147, %46
  %149 = tail call i32 @llvm.smax.i32(i32 %148, i32 0)
  %150 = shl nuw i32 %149, 1
  %151 = sub i32 %147, %150
  %152 = tail call i32 @llvm.smax.i32(i32 %151, i32 0)
  %153 = tail call i32 @llvm.smin.i32(i32 %46, i32 %152)
  %154 = mul i32 %153, %65
  %155 = add i32 %63, %154
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %64, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %78, %154
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %64, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %89, %154
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %64, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = fmul reassoc ninf nsz float %166, 3.600000e+01
  %168 = add i32 %101, %154
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %64, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = add i32 %113, %154
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, ptr %64, i64 %173
  %175 = load float, ptr %174, align 4
  %176 = or disjoint i32 %38, 1
  %177 = tail call i32 @llvm.abs.i32(i32 %176, i1 true)
  %178 = sub i32 %177, %46
  %179 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %180 = shl nuw i32 %179, 1
  %181 = sub i32 %177, %180
  %182 = tail call i32 @llvm.smax.i32(i32 %181, i32 0)
  %183 = tail call i32 @llvm.smin.i32(i32 %46, i32 %182)
  %184 = mul i32 %183, %65
  %185 = add i32 %63, %184
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %64, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = add i32 %78, %184
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %64, i64 %190
  %192 = load float, ptr %191, align 4
  %193 = add i32 %184, %89
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %64, i64 %194
  %196 = load float, ptr %195, align 4
  %197 = add i32 %101, %184
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %64, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = add i32 %113, %184
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %64, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = add i32 %38, 2
  %206 = tail call i32 @llvm.abs.i32(i32 %205, i1 true)
  %207 = sub i32 %206, %46
  %208 = tail call i32 @llvm.smax.i32(i32 %207, i32 0)
  %209 = shl nuw i32 %208, 1
  %210 = sub i32 %206, %209
  %211 = tail call i32 @llvm.smax.i32(i32 %210, i32 0)
  %212 = tail call i32 @llvm.smin.i32(i32 %46, i32 %211)
  %213 = mul i32 %212, %65
  %214 = add i32 %63, %213
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, ptr %64, i64 %215
  %217 = load float, ptr %216, align 4
  %218 = add i32 %78, %213
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, ptr %64, i64 %219
  %221 = load float, ptr %220, align 4
  %222 = add i32 %213, %89
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %64, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = add i32 %101, %213
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %64, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = add i32 %113, %213
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %64, i64 %231
  %233 = load float, ptr %232, align 4
  %reass.add = fadd reassoc ninf nsz float %105, %82
  %reass.add5 = fadd reassoc ninf nsz float %reass.add, %130
  %reass.add6 = fadd reassoc ninf nsz float %reass.add5, %146
  %reass.add7 = fadd reassoc ninf nsz float %reass.add6, %188
  %reass.add8 = fadd reassoc ninf nsz float %reass.add7, %204
  %reass.add9 = fadd reassoc ninf nsz float %reass.add8, %221
  %reass.add10 = fadd reassoc ninf nsz float %reass.add9, %229
  %reass.mul = fmul reassoc ninf nsz float %reass.add10, 4.000000e+00
  %reass.add11 = fadd reassoc ninf nsz float %162, %138
  %reass.add12 = fadd reassoc ninf nsz float %reass.add11, %171
  %reass.add13 = fadd reassoc ninf nsz float %reass.add12, %196
  %reass.mul14 = fmul reassoc ninf nsz float %reass.add13, 2.400000e+01
  %reass.add15 = fadd reassoc ninf nsz float %142, %134
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %192
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %200
  %reass.mul18 = fmul reassoc ninf nsz float %reass.add17, 1.600000e+01
  %reass.add19 = fadd reassoc ninf nsz float %158, %93
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %175
  %reass.add21 = fadd reassoc ninf nsz float %reass.add20, %225
  %reass.mul22 = fmul reassoc ninf nsz float %reass.add21, 6.000000e+00
  %234 = fadd reassoc ninf nsz float %117, %70
  %235 = fadd reassoc ninf nsz float %234, %167
  %236 = fadd reassoc ninf nsz float %235, %217
  %237 = fadd reassoc ninf nsz float %236, %reass.mul14
  %238 = fadd reassoc ninf nsz float %237, %reass.mul18
  %239 = fadd reassoc ninf nsz float %238, %233
  %240 = fadd reassoc ninf nsz float %239, %reass.mul22
  %241 = fadd reassoc ninf nsz float %240, %reass.mul
  %242 = fmul reassoc ninf nsz float %241, 3.906250e-03
  %243 = load ptr, ptr %23, align 8
  %244 = load i32, ptr %24, align 4
  %245 = sub i32 %244, %30
  %246 = mul i32 %245, %37
  %247 = add i32 %.023, %246
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %243, i64 %248
  store float %242, ptr %249, align 4
  %250 = add nsw i32 %.023, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %250
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.0, align 8
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #4

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
