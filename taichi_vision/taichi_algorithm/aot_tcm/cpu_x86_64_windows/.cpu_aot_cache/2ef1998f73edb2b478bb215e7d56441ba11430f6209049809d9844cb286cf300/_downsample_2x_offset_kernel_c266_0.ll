; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_downsample_2x_offset_kernel_c266_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
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

define void @_downsample_2x_offset_kernel_c266_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 32
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 36
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 8
  %26 = getelementptr i8, ptr %19, i64 4
  %27 = getelementptr i8, ptr %19, i64 24
  %28 = getelementptr i8, ptr %19, i64 20
  %29 = add i32 %23, %16
  %30 = shl i32 %29, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %30, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.023 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %256, %for_loop_body ]
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 4
  %35 = load i32, ptr %34, align 4
  %36 = sdiv i32 %.023, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.023
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.023, %37
  %41 = and i1 %39, %40
  %.neg4 = sext i1 %41 to i32
  %42 = add i32 %36, %.neg4
  %43 = add i32 %42, %21
  %44 = shl i32 %43, 1
  %45 = mul i32 %35, -2
  %46 = mul i32 %45, %42
  %47 = add i32 %lsr.iv, %46
  %48 = add i32 %44, -2
  %49 = load ptr, ptr %0, align 8
  %50 = load i32, ptr %49, align 4
  %51 = tail call i32 @llvm.abs.i32(i32 %48, i1 true)
  %52 = add i32 %50, -1
  %53 = sub i32 %51, %52
  %54 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %55 = shl nuw i32 %54, 1
  %56 = sub i32 %51, %55
  %57 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %58 = tail call i32 @llvm.smin.i32(i32 %52, i32 %57)
  %59 = add i32 %47, -2
  %60 = getelementptr i8, ptr %49, i64 4
  %61 = load i32, ptr %60, align 4
  %62 = tail call i32 @llvm.abs.i32(i32 %59, i1 true)
  %63 = add i32 %61, -1
  %64 = sub i32 %62, %63
  %65 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %66 = shl nuw i32 %65, 1
  %67 = sub i32 %62, %66
  %68 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %69 = tail call i32 @llvm.smin.i32(i32 %63, i32 %68)
  %70 = load ptr, ptr %25, align 8
  %71 = load i32, ptr %26, align 4
  %72 = mul i32 %58, %71
  %73 = add i32 %69, %72
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %70, i64 %74
  %76 = load float, ptr %75, align 4
  %77 = add i32 %47, -1
  %78 = tail call i32 @llvm.abs.i32(i32 %77, i1 true)
  %79 = sub i32 %78, %63
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = shl nuw i32 %80, 1
  %82 = sub i32 %78, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %63, i32 %83)
  %85 = add i32 %84, %72
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %70, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = tail call i32 @llvm.abs.i32(i32 %47, i1 true)
  %90 = sub i32 %89, %63
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %92 = shl nuw i32 %91, 1
  %93 = sub i32 %89, %92
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %63, i32 %94)
  %96 = add i32 %72, %95
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %70, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = add i32 %47, 1
  %101 = tail call i32 @llvm.abs.i32(i32 %100, i1 true)
  %102 = sub i32 %101, %63
  %103 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %104 = shl nuw i32 %103, 1
  %105 = sub i32 %101, %104
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  %107 = tail call i32 @llvm.smin.i32(i32 %63, i32 %106)
  %108 = add i32 %107, %72
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %70, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = add i32 %47, 2
  %113 = tail call i32 @llvm.abs.i32(i32 %112, i1 true)
  %114 = sub i32 %113, %63
  %115 = tail call i32 @llvm.smax.i32(i32 %114, i32 0)
  %116 = shl nuw i32 %115, 1
  %117 = sub i32 %113, %116
  %118 = tail call i32 @llvm.smax.i32(i32 %117, i32 0)
  %119 = tail call i32 @llvm.smin.i32(i32 %63, i32 %118)
  %120 = add i32 %119, %72
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %70, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %44, -1
  %125 = tail call i32 @llvm.abs.i32(i32 %124, i1 true)
  %126 = sub i32 %125, %52
  %127 = tail call i32 @llvm.smax.i32(i32 %126, i32 0)
  %128 = shl nuw i32 %127, 1
  %129 = sub i32 %125, %128
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %131 = tail call i32 @llvm.smin.i32(i32 %52, i32 %130)
  %132 = mul i32 %131, %71
  %133 = add i32 %69, %132
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %70, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %84, %132
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %70, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %132, %95
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %70, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = add i32 %107, %132
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, ptr %70, i64 %146
  %148 = load float, ptr %147, align 4
  %149 = add i32 %119, %132
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %70, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = tail call i32 @llvm.abs.i32(i32 %44, i1 true)
  %154 = sub i32 %153, %52
  %155 = tail call i32 @llvm.smax.i32(i32 %154, i32 0)
  %156 = shl nuw i32 %155, 1
  %157 = sub i32 %153, %156
  %158 = tail call i32 @llvm.smax.i32(i32 %157, i32 0)
  %159 = tail call i32 @llvm.smin.i32(i32 %52, i32 %158)
  %160 = mul i32 %159, %71
  %161 = add i32 %69, %160
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %70, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = add i32 %84, %160
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %70, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = add i32 %95, %160
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %70, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = fmul reassoc ninf nsz float %172, 3.600000e+01
  %174 = add i32 %107, %160
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %70, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = add i32 %119, %160
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, ptr %70, i64 %179
  %181 = load float, ptr %180, align 4
  %182 = or disjoint i32 %44, 1
  %183 = tail call i32 @llvm.abs.i32(i32 %182, i1 true)
  %184 = sub i32 %183, %52
  %185 = tail call i32 @llvm.smax.i32(i32 %184, i32 0)
  %186 = shl nuw i32 %185, 1
  %187 = sub i32 %183, %186
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = tail call i32 @llvm.smin.i32(i32 %52, i32 %188)
  %190 = mul i32 %189, %71
  %191 = add i32 %69, %190
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %70, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = add i32 %84, %190
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %70, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = add i32 %190, %95
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, ptr %70, i64 %200
  %202 = load float, ptr %201, align 4
  %203 = add i32 %107, %190
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %70, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = add i32 %119, %190
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %70, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i32 %44, 2
  %212 = tail call i32 @llvm.abs.i32(i32 %211, i1 true)
  %213 = sub i32 %212, %52
  %214 = tail call i32 @llvm.smax.i32(i32 %213, i32 0)
  %215 = shl nuw i32 %214, 1
  %216 = sub i32 %212, %215
  %217 = tail call i32 @llvm.smax.i32(i32 %216, i32 0)
  %218 = tail call i32 @llvm.smin.i32(i32 %52, i32 %217)
  %219 = mul i32 %218, %71
  %220 = add i32 %69, %219
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, ptr %70, i64 %221
  %223 = load float, ptr %222, align 4
  %224 = add i32 %84, %219
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, ptr %70, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = add i32 %219, %95
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %70, i64 %229
  %231 = load float, ptr %230, align 4
  %232 = add i32 %107, %219
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %70, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = add i32 %119, %219
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, ptr %70, i64 %237
  %239 = load float, ptr %238, align 4
  %reass.add = fadd reassoc ninf nsz float %111, %88
  %reass.add5 = fadd reassoc ninf nsz float %reass.add, %136
  %reass.add6 = fadd reassoc ninf nsz float %reass.add5, %152
  %reass.add7 = fadd reassoc ninf nsz float %reass.add6, %194
  %reass.add8 = fadd reassoc ninf nsz float %reass.add7, %210
  %reass.add9 = fadd reassoc ninf nsz float %reass.add8, %227
  %reass.add10 = fadd reassoc ninf nsz float %reass.add9, %235
  %reass.mul = fmul reassoc ninf nsz float %reass.add10, 4.000000e+00
  %reass.add11 = fadd reassoc ninf nsz float %168, %144
  %reass.add12 = fadd reassoc ninf nsz float %reass.add11, %177
  %reass.add13 = fadd reassoc ninf nsz float %reass.add12, %202
  %reass.mul14 = fmul reassoc ninf nsz float %reass.add13, 2.400000e+01
  %reass.add15 = fadd reassoc ninf nsz float %148, %140
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %198
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %206
  %reass.mul18 = fmul reassoc ninf nsz float %reass.add17, 1.600000e+01
  %reass.add19 = fadd reassoc ninf nsz float %164, %99
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %181
  %reass.add21 = fadd reassoc ninf nsz float %reass.add20, %231
  %reass.mul22 = fmul reassoc ninf nsz float %reass.add21, 6.000000e+00
  %240 = fadd reassoc ninf nsz float %123, %76
  %241 = fadd reassoc ninf nsz float %240, %173
  %242 = fadd reassoc ninf nsz float %241, %223
  %243 = fadd reassoc ninf nsz float %242, %reass.mul14
  %244 = fadd reassoc ninf nsz float %243, %reass.mul18
  %245 = fadd reassoc ninf nsz float %244, %239
  %246 = fadd reassoc ninf nsz float %245, %reass.mul22
  %247 = fadd reassoc ninf nsz float %246, %reass.mul
  %248 = fmul reassoc ninf nsz float %247, 3.906250e-03
  %249 = load ptr, ptr %27, align 8
  %250 = load i32, ptr %28, align 4
  %251 = sub i32 %250, %35
  %252 = mul i32 %251, %42
  %253 = add i32 %.023, %252
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, ptr %249, i64 %254
  store float %248, ptr %255, align 4
  %256 = add nsw i32 %.023, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %256
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
