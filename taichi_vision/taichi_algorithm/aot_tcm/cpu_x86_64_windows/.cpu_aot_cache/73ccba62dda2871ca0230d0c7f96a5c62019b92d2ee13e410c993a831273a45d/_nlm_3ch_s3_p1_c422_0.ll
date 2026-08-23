; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_3ch_s3_p1_c422_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 80
  %2 = load float, ptr %1, align 4
  %3 = fmul reassoc ninf nsz float %2, %2
  %4 = fdiv reassoc ninf nsz float 1.000000e+00, %3
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 20
  store float %4, ptr %9, align 4
  %10 = fmul reassoc ninf nsz float %3, 3.500000e+00
  %11 = fadd reassoc ninf nsz float %10, 0x3F60624DE0000000
  %12 = load ptr, ptr %5, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 16
  store float %11, ptr %15, align 4
  %16 = fmul reassoc ninf nsz float %2, 0x3FE6666660000000
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 88
  %19 = load float, ptr %18, align 4
  %20 = fmul reassoc ninf nsz float %16, %19
  %21 = load ptr, ptr %5, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 24
  store float %20, ptr %24, align 4
  %25 = load ptr, ptr %context, align 8
  %26 = getelementptr i8, ptr %25, i64 72
  %27 = load i32, ptr %26, align 4
  %28 = load ptr, ptr %5, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 8
  store i32 %27, ptr %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %27, i32 0)
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 76
  %35 = load i32, ptr %34, align 4
  %36 = load ptr, ptr %5, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 12
  store i32 %35, ptr %39, align 4
  %40 = tail call i32 @llvm.smax.i32(i32 %35, i32 0)
  %41 = load ptr, ptr %5, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 4
  store i32 %40, ptr %44, align 4
  %45 = mul i32 %40, %32
  %46 = load ptr, ptr %5, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  store i32 %45, ptr %48, align 4
  ret void
}

define void @_nlm_3ch_s3_p1_c422_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #8
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree nounwind memory(readwrite, inaccessiblemem: write)
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
  %20 = getelementptr i8, ptr %19, i64 84
  %21 = load float, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 16
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 8
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = getelementptr i8, ptr %19, i64 28
  %28 = getelementptr i8, ptr %19, i64 32
  %29 = add i32 %16, -3
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.06998 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %609, %after_if47 ]
  %30 = load ptr, ptr %3, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 32872
  %32 = load ptr, ptr %31, align 8
  %33 = getelementptr inbounds nuw i8, ptr %32, i64 4
  %34 = load i32, ptr %33, align 4
  %35 = sdiv i32 %.06998, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.06998
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %36, %.06998
  %40 = and i1 %38, %39
  %.neg75 = sext i1 %40 to i32
  %41 = add i32 %35, %.neg75
  %42 = mul i32 %41, %34
  %43 = sub i32 %.06998, %42
  %44 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %45 = load i32, ptr %44, align 4
  %46 = add i32 %45, -1
  %47 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %48 = load i32, ptr %47, align 4
  %49 = add i32 %48, -1
  %50 = load ptr, ptr %23, align 8
  %51 = load i32, ptr %24, align 4
  %52 = load i32, ptr %25, align 4
  %53 = add i32 %43, -1
  %54 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %55 = tail call i32 @llvm.smin.i32(i32 %49, i32 %54)
  %56 = add i32 %41, -1
  %57 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %58 = tail call i32 @llvm.smin.i32(i32 %46, i32 %57)
  %59 = mul i32 %51, %58
  %60 = add i32 %59, %55
  %61 = mul i32 %60, %52
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %50, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = add i32 %61, 1
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %50, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = fadd reassoc ninf nsz float %68, %64
  %70 = add i32 %61, 2
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, ptr %50, i64 %71
  %73 = load float, ptr %72, align 4
  %74 = fadd reassoc ninf nsz float %69, %73
  %75 = fmul reassoc ninf nsz float %74, 0x3FD5555560000000
  %76 = fmul reassoc ninf nsz float %75, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %43, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %49, i32 %77)
  %79 = add i32 %59, %78
  %80 = mul i32 %79, %52
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %50, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = add i32 %80, 1
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %50, i64 %85
  %87 = load float, ptr %86, align 4
  %88 = fadd reassoc ninf nsz float %87, %83
  %89 = add i32 %80, 2
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %50, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = fadd reassoc ninf nsz float %88, %92
  %94 = fmul reassoc ninf nsz float %93, 0x3FD5555560000000
  %95 = fadd reassoc ninf nsz float %94, %75
  %96 = fmul reassoc ninf nsz float %94, %94
  %97 = fadd reassoc ninf nsz float %96, %76
  %98 = add i32 %43, 1
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %100 = tail call i32 @llvm.smin.i32(i32 %49, i32 %99)
  %101 = add i32 %59, %100
  %102 = mul i32 %101, %52
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %50, i64 %103
  %105 = load float, ptr %104, align 4
  %106 = add i32 %102, 1
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %50, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = fadd reassoc ninf nsz float %109, %105
  %111 = add i32 %102, 2
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %50, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = fadd reassoc ninf nsz float %110, %114
  %116 = fmul reassoc ninf nsz float %115, 0x3FD5555560000000
  %117 = fadd reassoc ninf nsz float %116, %95
  %118 = fmul reassoc ninf nsz float %116, %116
  %119 = fadd reassoc ninf nsz float %118, %97
  %120 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %46, i32 %120)
  %122 = mul i32 %51, %121
  %123 = add i32 %122, %55
  %124 = mul i32 %123, %52
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %50, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %124, 1
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %50, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = fadd reassoc ninf nsz float %131, %127
  %133 = add i32 %124, 2
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %50, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = fadd reassoc ninf nsz float %132, %136
  %138 = fmul reassoc ninf nsz float %137, 0x3FD5555560000000
  %139 = fadd reassoc ninf nsz float %138, %117
  %140 = fmul reassoc ninf nsz float %138, %138
  %141 = fadd reassoc ninf nsz float %140, %119
  %142 = add i32 %122, %78
  %143 = mul i32 %142, %52
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %50, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %143, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %50, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fadd reassoc ninf nsz float %150, %146
  %152 = add i32 %143, 2
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %50, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = fadd reassoc ninf nsz float %151, %155
  %157 = fmul reassoc ninf nsz float %156, 0x3FD5555560000000
  %158 = fadd reassoc ninf nsz float %157, %139
  %159 = fmul reassoc ninf nsz float %157, %157
  %160 = fadd reassoc ninf nsz float %159, %141
  %161 = add i32 %122, %100
  %162 = mul i32 %161, %52
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %50, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = add i32 %162, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %50, i64 %167
  %169 = load float, ptr %168, align 4
  %170 = fadd reassoc ninf nsz float %169, %165
  %171 = add i32 %162, 2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %50, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fadd reassoc ninf nsz float %170, %174
  %176 = fmul reassoc ninf nsz float %175, 0x3FD5555560000000
  %177 = fadd reassoc ninf nsz float %176, %158
  %178 = fmul reassoc ninf nsz float %176, %176
  %179 = fadd reassoc ninf nsz float %178, %160
  %180 = add i32 %41, 1
  %181 = tail call i32 @llvm.smax.i32(i32 %180, i32 0)
  %182 = tail call i32 @llvm.smin.i32(i32 %46, i32 %181)
  %183 = mul i32 %51, %182
  %184 = add i32 %183, %55
  %185 = mul i32 %184, %52
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %50, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = add i32 %185, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %50, i64 %190
  %192 = load float, ptr %191, align 4
  %193 = fadd reassoc ninf nsz float %192, %188
  %194 = add i32 %185, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %50, i64 %195
  %197 = load float, ptr %196, align 4
  %198 = fadd reassoc ninf nsz float %193, %197
  %199 = fmul reassoc ninf nsz float %198, 0x3FD5555560000000
  %200 = fadd reassoc ninf nsz float %199, %177
  %201 = fmul reassoc ninf nsz float %199, %199
  %202 = fadd reassoc ninf nsz float %201, %179
  %203 = add i32 %183, %78
  %204 = mul i32 %203, %52
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, ptr %50, i64 %205
  %207 = load float, ptr %206, align 4
  %208 = add i32 %204, 1
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, ptr %50, i64 %209
  %211 = load float, ptr %210, align 4
  %212 = fadd reassoc ninf nsz float %211, %207
  %213 = add i32 %204, 2
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %50, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = fadd reassoc ninf nsz float %212, %216
  %218 = fmul reassoc ninf nsz float %217, 0x3FD5555560000000
  %219 = fadd reassoc ninf nsz float %218, %200
  %220 = fmul reassoc ninf nsz float %218, %218
  %221 = fadd reassoc ninf nsz float %220, %202
  %222 = add i32 %183, %100
  %223 = mul i32 %222, %52
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %50, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = add i32 %223, 1
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, ptr %50, i64 %228
  %230 = load float, ptr %229, align 4
  %231 = fadd reassoc ninf nsz float %230, %226
  %232 = add i32 %223, 2
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %50, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fadd reassoc ninf nsz float %231, %235
  %237 = fmul reassoc ninf nsz float %236, 0x3FD5555560000000
  %238 = fadd reassoc ninf nsz float %237, %219
  %239 = fmul reassoc ninf nsz float %237, %237
  %240 = fadd reassoc ninf nsz float %239, %221
  %241 = fmul reassoc ninf nsz float %238, 0x3FBC71C720000000
  %242 = fmul reassoc ninf nsz float %240, 0x3FBC71C720000000
  %243 = fmul reassoc ninf nsz float %241, %241
  %244 = fsub reassoc ninf nsz float %242, %243
  %245 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %244, float 0.000000e+00)
  %246 = fmul reassoc ninf nsz float %245, -3.500000e+02
  %247 = tail call noundef float @expf(float noundef %246) #8
  %248 = fsub reassoc ninf nsz float 1.000000e+00, %247
  %249 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %248, float 0x3FE6666660000000)
  %250 = load ptr, ptr %26, align 8
  %251 = load i32, ptr %27, align 4
  %252 = load i32, ptr %28, align 4
  %253 = mul i32 %251, %41
  %254 = add i32 %253, %43
  %255 = mul i32 %254, %252
  %256 = add i32 %255, 1
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, ptr %250, i64 %257
  %259 = load float, ptr %258, align 4
  %260 = add i32 %255, 2
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, ptr %250, i64 %261
  %263 = load float, ptr %262, align 4
  %264 = sub i32 %lsr.iv, %42
  %265 = add i32 %35, -3
  %266 = add i32 %265, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv114 = phi i32 [ %266, %for_loop_body ], [ %lsr.iv.next115, %for_loop_inc10 ]
  %.04797 = phi i32 [ -3, %for_loop_body ], [ %269, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %267 = add i32 %.04797, %41
  %268 = icmp slt i32 %267, 0
  br i1 %268, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %269 = add nsw i32 %.04797, 1
  %lsr.iv.next115 = add i32 %lsr.iv114, 1
  %exitcond101.not = icmp eq i32 %269, 4
  br i1 %exitcond101.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %270 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %270, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %271 = load i32, ptr %44, align 4
  %.not76 = icmp slt i32 %267, %271
  br i1 %.not76, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %272 = tail call i32 @llvm.smax.i32(i32 %267, i32 1)
  %273 = add nsw i32 %272, -1
  %274 = tail call i32 @llvm.smin.i32(i32 %46, i32 %273)
  %275 = tail call i32 @llvm.smin.i32(i32 %46, i32 %267)
  %276 = add nuw i32 %267, 1
  %277 = tail call i32 @llvm.smax.i32(i32 %276, i32 0)
  %278 = tail call i32 @llvm.smin.i32(i32 %46, i32 %277)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv112 = phi i32 [ %264, %for_loop_body16.preheader ], [ %lsr.iv.next113, %for_loop_inc17 ]
  %.04592 = phi i32 [ %282, %for_loop_inc17 ], [ -3, %for_loop_body16.preheader ]
  %.391 = phi float [ %.250, %for_loop_inc17 ], [ %.14996, %for_loop_body16.preheader ]
  %.35490 = phi float [ %.253, %for_loop_inc17 ], [ %.15295, %for_loop_body16.preheader ]
  %.35889 = phi float [ %.257, %for_loop_inc17 ], [ %.15694, %for_loop_body16.preheader ]
  %.36288 = phi float [ %.261, %for_loop_inc17 ], [ %.16093, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv112, i32 1)
  %279 = sub i32 %264, %umin
  %280 = add i32 %43, %.04592
  %281 = icmp slt i32 %280, 0
  br i1 %281, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %445, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %456, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %462, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %468, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %282 = add nsw i32 %.04592, 1
  %lsr.iv.next113 = add i32 %lsr.iv112, 1
  %exitcond.not = icmp eq i32 %282, 4
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %283 = load i32, ptr %47, align 4
  %.not77 = icmp slt i32 %280, %283
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %284 = or i32 %.04592, %.04797
  %spec.select.not = icmp eq i32 %284, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %285 = load ptr, ptr %26, align 8
  %286 = load i32, ptr %27, align 4
  %287 = load i32, ptr %28, align 4
  %288 = add i32 %.04592, %279
  %289 = add i32 %288, 3
  %290 = tail call i32 @llvm.smin.i32(i32 %49, i32 %289)
  %291 = mul i32 %286, %58
  %292 = mul i32 %286, %274
  %293 = add i32 %291, %55
  %294 = mul i32 %293, %287
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %285, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = add i32 %292, %290
  %299 = mul i32 %298, %287
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %285, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = fsub reassoc ninf nsz float %297, %302
  %304 = fmul reassoc ninf nsz float %303, %303
  %305 = tail call i32 @llvm.smin.i32(i32 %49, i32 %280)
  %306 = add i32 %291, %78
  %307 = mul i32 %306, %287
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %285, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = add i32 %292, %305
  %312 = mul i32 %311, %287
  %313 = sext i32 %312 to i64
  %314 = getelementptr float, ptr %285, i64 %313
  %315 = load float, ptr %314, align 4
  %316 = fsub reassoc ninf nsz float %310, %315
  %317 = fmul reassoc ninf nsz float %316, %316
  %318 = fadd reassoc ninf nsz float %317, %304
  %319 = add i32 %280, 1
  %320 = tail call i32 @llvm.smin.i32(i32 %49, i32 %319)
  %321 = add i32 %291, %100
  %322 = mul i32 %321, %287
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, ptr %285, i64 %323
  %325 = load float, ptr %324, align 4
  %326 = add i32 %292, %320
  %327 = mul i32 %326, %287
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %285, i64 %328
  %330 = load float, ptr %329, align 4
  %331 = fsub reassoc ninf nsz float %325, %330
  %332 = fmul reassoc ninf nsz float %331, %331
  %333 = fadd reassoc ninf nsz float %332, %318
  %334 = mul i32 %286, %121
  %335 = mul i32 %286, %275
  %336 = add i32 %334, %55
  %337 = mul i32 %336, %287
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %285, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = add i32 %335, %290
  %342 = mul i32 %341, %287
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %285, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = fsub reassoc ninf nsz float %340, %345
  %347 = fmul reassoc ninf nsz float %346, %346
  %348 = fadd reassoc ninf nsz float %347, %333
  %349 = add i32 %334, %78
  %350 = mul i32 %349, %287
  %351 = sext i32 %350 to i64
  %352 = getelementptr float, ptr %285, i64 %351
  %353 = load float, ptr %352, align 4
  %354 = add i32 %335, %305
  %355 = mul i32 %354, %287
  %356 = sext i32 %355 to i64
  %357 = getelementptr float, ptr %285, i64 %356
  %358 = load float, ptr %357, align 4
  %359 = fsub reassoc ninf nsz float %353, %358
  %360 = fmul reassoc ninf nsz float %359, %359
  %361 = fadd reassoc ninf nsz float %360, %348
  %362 = add i32 %334, %100
  %363 = mul i32 %362, %287
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %285, i64 %364
  %366 = load float, ptr %365, align 4
  %367 = add i32 %335, %320
  %368 = mul i32 %367, %287
  %369 = sext i32 %368 to i64
  %370 = getelementptr float, ptr %285, i64 %369
  %371 = load float, ptr %370, align 4
  %372 = fsub reassoc ninf nsz float %366, %371
  %373 = fmul reassoc ninf nsz float %372, %372
  %374 = fadd reassoc ninf nsz float %373, %361
  %375 = mul i32 %286, %182
  %376 = mul i32 %286, %278
  %377 = add i32 %375, %55
  %378 = mul i32 %377, %287
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, ptr %285, i64 %379
  %381 = load float, ptr %380, align 4
  %382 = add i32 %376, %290
  %383 = mul i32 %382, %287
  %384 = sext i32 %383 to i64
  %385 = getelementptr float, ptr %285, i64 %384
  %386 = load float, ptr %385, align 4
  %387 = fsub reassoc ninf nsz float %381, %386
  %388 = fmul reassoc ninf nsz float %387, %387
  %389 = fadd reassoc ninf nsz float %388, %374
  %390 = add i32 %375, %78
  %391 = mul i32 %390, %287
  %392 = sext i32 %391 to i64
  %393 = getelementptr float, ptr %285, i64 %392
  %394 = load float, ptr %393, align 4
  %395 = add i32 %376, %305
  %396 = mul i32 %395, %287
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %285, i64 %397
  %399 = load float, ptr %398, align 4
  %400 = fsub reassoc ninf nsz float %394, %399
  %401 = fmul reassoc ninf nsz float %400, %400
  %402 = fadd reassoc ninf nsz float %401, %389
  %403 = add i32 %375, %100
  %404 = mul i32 %403, %287
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, ptr %285, i64 %405
  %407 = load float, ptr %406, align 4
  %408 = add i32 %376, %320
  %409 = mul i32 %408, %287
  %410 = sext i32 %409 to i64
  %411 = getelementptr float, ptr %285, i64 %410
  %412 = load float, ptr %411, align 4
  %413 = fsub reassoc ninf nsz float %407, %412
  %414 = fmul reassoc ninf nsz float %413, %413
  %415 = fadd reassoc ninf nsz float %414, %402
  %416 = fmul reassoc ninf nsz float %415, 0x3FBC71C720000000
  %417 = mul i32 %lsr.iv114, %286
  %418 = add i32 %280, %417
  %419 = mul i32 %418, %287
  %420 = add i32 %419, 1
  %421 = sext i32 %420 to i64
  %422 = getelementptr float, ptr %285, i64 %421
  %423 = load float, ptr %422, align 4
  %424 = add i32 %419, 2
  %425 = sext i32 %424 to i64
  %426 = getelementptr float, ptr %285, i64 %425
  %427 = load float, ptr %426, align 4
  %428 = fsub reassoc ninf nsz float %259, %423
  %429 = fsub reassoc ninf nsz float %263, %427
  %430 = fmul reassoc ninf nsz float %428, %428
  %431 = fmul reassoc ninf nsz float %429, %429
  %432 = fadd reassoc ninf nsz float %431, %430
  %433 = fmul reassoc ninf nsz float %432, 2.500000e-01
  %434 = fadd reassoc ninf nsz float %433, %416
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %434, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %435 = load ptr, ptr %3, align 8
  %436 = getelementptr inbounds nuw i8, ptr %435, i64 32872
  %437 = load ptr, ptr %436, align 8
  %438 = getelementptr inbounds nuw i8, ptr %437, i64 16
  %439 = load float, ptr %438, align 4
  %440 = fcmp reassoc ninf nsz ugt float %.043, %439
  br i1 %440, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %441 = getelementptr inbounds nuw i8, ptr %437, i64 20
  %442 = load float, ptr %441, align 4
  %443 = fmul reassoc ninf nsz float %442, %neg44
  %444 = tail call noundef float @expf(float noundef %443) #8
  %445 = fadd reassoc ninf nsz float %444, %.36288
  %446 = load ptr, ptr %23, align 8
  %447 = load i32, ptr %24, align 4
  %448 = load i32, ptr %25, align 4
  %449 = mul i32 %lsr.iv114, %447
  %450 = add i32 %280, %449
  %451 = mul i32 %450, %448
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, ptr %446, i64 %452
  %454 = load float, ptr %453, align 4
  %455 = fmul reassoc ninf nsz float %454, %444
  %456 = fadd reassoc ninf nsz float %455, %.35889
  %457 = add i32 %451, 1
  %458 = sext i32 %457 to i64
  %459 = getelementptr float, ptr %446, i64 %458
  %460 = load float, ptr %459, align 4
  %461 = fmul reassoc ninf nsz float %460, %444
  %462 = fadd reassoc ninf nsz float %461, %.35490
  %463 = add i32 %451, 2
  %464 = sext i32 %463 to i64
  %465 = getelementptr float, ptr %446, i64 %464
  %466 = load float, ptr %465, align 4
  %467 = fmul reassoc ninf nsz float %466, %444
  %468 = fadd reassoc ninf nsz float %467, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %469 = fmul reassoc ninf nsz float %249, %21
  %470 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %471 = fmul reassoc ninf nsz float %.055, %470
  %472 = fmul reassoc ninf nsz float %.051, %470
  %473 = fmul reassoc ninf nsz float %.048, %470
  %474 = load ptr, ptr %23, align 8
  %475 = load i32, ptr %24, align 4
  %476 = load i32, ptr %25, align 4
  %477 = mul i32 %475, %41
  %478 = add i32 %477, %43
  %479 = mul i32 %478, %476
  %480 = sext i32 %479 to i64
  %481 = getelementptr float, ptr %474, i64 %480
  %482 = load float, ptr %481, align 4
  %483 = fsub reassoc ninf nsz float %482, %471
  %484 = add i32 %479, 1
  %485 = sext i32 %484 to i64
  %486 = getelementptr float, ptr %474, i64 %485
  %487 = load float, ptr %486, align 4
  %488 = fsub reassoc ninf nsz float %487, %472
  %489 = add i32 %479, 2
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, ptr %474, i64 %490
  %492 = load float, ptr %491, align 4
  %493 = fsub reassoc ninf nsz float %492, %473
  %494 = tail call noundef float @llvm.fabs.f32(float %483)
  %495 = load ptr, ptr %3, align 8
  %496 = getelementptr inbounds nuw i8, ptr %495, i64 32872
  %497 = load ptr, ptr %496, align 8
  %498 = getelementptr inbounds nuw i8, ptr %497, i64 24
  %499 = load float, ptr %498, align 4
  %500 = fsub reassoc ninf nsz float %494, %499
  %501 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %500, float 0.000000e+00)
  %502 = fcmp reassoc ninf nsz oge float %483, 0.000000e+00
  %503 = uitofp i1 %502 to float
  %504 = fcmp reassoc ninf nsz ole float %483, 0.000000e+00
  %505 = uitofp i1 %504 to float
  %506 = fsub reassoc ninf nsz float %503, %505
  %507 = tail call noundef float @llvm.fabs.f32(float %488)
  %508 = fsub reassoc ninf nsz float %507, %499
  %509 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %508, float 0.000000e+00)
  %510 = fcmp reassoc ninf nsz oge float %488, 0.000000e+00
  %511 = uitofp i1 %510 to float
  %512 = fcmp reassoc ninf nsz ole float %488, 0.000000e+00
  %513 = uitofp i1 %512 to float
  %514 = fsub reassoc ninf nsz float %511, %513
  %515 = tail call noundef float @llvm.fabs.f32(float %493)
  %516 = fsub reassoc ninf nsz float %515, %499
  %517 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %516, float 0.000000e+00)
  %518 = fcmp reassoc ninf nsz oge float %493, 0.000000e+00
  %519 = uitofp i1 %518 to float
  %520 = fcmp reassoc ninf nsz ole float %493, 0.000000e+00
  %521 = uitofp i1 %520 to float
  %522 = fsub reassoc ninf nsz float %519, %521
  %523 = fmul reassoc ninf nsz float %506, %469
  %524 = fmul reassoc ninf nsz float %523, %501
  %525 = fadd reassoc ninf nsz float %524, %471
  %526 = load ptr, ptr %0, align 8
  %527 = getelementptr i8, ptr %526, i64 64
  %528 = load ptr, ptr %527, align 8
  %529 = getelementptr i8, ptr %526, i64 52
  %530 = load i32, ptr %529, align 4
  %531 = getelementptr i8, ptr %526, i64 56
  %532 = load i32, ptr %531, align 4
  %533 = mul i32 %530, %41
  %534 = add i32 %533, %43
  %535 = mul i32 %534, %532
  %536 = sext i32 %535 to i64
  %537 = getelementptr float, ptr %528, i64 %536
  store float %525, ptr %537, align 4
  %538 = fmul reassoc ninf nsz float %514, %469
  %539 = fmul reassoc ninf nsz float %538, %509
  %540 = fadd reassoc ninf nsz float %539, %472
  %541 = load ptr, ptr %527, align 8
  %542 = load i32, ptr %529, align 4
  %543 = load i32, ptr %531, align 4
  %544 = mul i32 %542, %41
  %545 = add i32 %544, %43
  %546 = mul i32 %545, %543
  %547 = add i32 %546, 1
  %548 = sext i32 %547 to i64
  %549 = getelementptr float, ptr %541, i64 %548
  store float %540, ptr %549, align 4
  %550 = fmul reassoc ninf nsz float %522, %469
  %551 = fmul reassoc ninf nsz float %550, %517
  %552 = fadd reassoc ninf nsz float %551, %473
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %553 = load ptr, ptr %23, align 8
  %554 = load i32, ptr %24, align 4
  %555 = load i32, ptr %25, align 4
  %556 = mul i32 %554, %41
  %557 = add i32 %556, %43
  %558 = mul i32 %557, %555
  %559 = sext i32 %558 to i64
  %560 = getelementptr float, ptr %553, i64 %559
  %561 = load float, ptr %560, align 4
  %562 = load ptr, ptr %0, align 8
  %563 = getelementptr i8, ptr %562, i64 64
  %564 = load ptr, ptr %563, align 8
  %565 = getelementptr i8, ptr %562, i64 52
  %566 = load i32, ptr %565, align 4
  %567 = getelementptr i8, ptr %562, i64 56
  %568 = load i32, ptr %567, align 4
  %569 = mul i32 %566, %41
  %570 = add i32 %569, %43
  %571 = mul i32 %570, %568
  %572 = sext i32 %571 to i64
  %573 = getelementptr float, ptr %564, i64 %572
  store float %561, ptr %573, align 4
  %574 = load ptr, ptr %23, align 8
  %575 = load i32, ptr %24, align 4
  %576 = load i32, ptr %25, align 4
  %577 = mul i32 %575, %41
  %578 = add i32 %577, %43
  %579 = mul i32 %578, %576
  %580 = add i32 %579, 1
  %581 = sext i32 %580 to i64
  %582 = getelementptr float, ptr %574, i64 %581
  %583 = load float, ptr %582, align 4
  %584 = load ptr, ptr %563, align 8
  %585 = load i32, ptr %565, align 4
  %586 = load i32, ptr %567, align 4
  %587 = mul i32 %585, %41
  %588 = add i32 %587, %43
  %589 = mul i32 %588, %586
  %590 = add i32 %589, 1
  %591 = sext i32 %590 to i64
  %592 = getelementptr float, ptr %584, i64 %591
  store float %583, ptr %592, align 4
  %593 = load ptr, ptr %23, align 8
  %594 = load i32, ptr %24, align 4
  %595 = load i32, ptr %25, align 4
  %596 = mul i32 %594, %41
  %597 = add i32 %596, %43
  %598 = mul i32 %597, %595
  %599 = add i32 %598, 2
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %593, i64 %600
  %602 = load float, ptr %601, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink111.in = phi ptr [ %565, %false_block46 ], [ %529, %true_block45 ]
  %.sink109.in = phi ptr [ %567, %false_block46 ], [ %531, %true_block45 ]
  %.sink104.in = phi ptr [ %563, %false_block46 ], [ %527, %true_block45 ]
  %.sink = phi float [ %602, %false_block46 ], [ %552, %true_block45 ]
  %.sink104 = load ptr, ptr %.sink104.in, align 8
  %.sink109 = load i32, ptr %.sink109.in, align 4
  %.sink111 = load i32, ptr %.sink111.in, align 4
  %603 = mul i32 %.sink111, %41
  %604 = add i32 %603, %43
  %605 = mul i32 %604, %.sink109
  %606 = add i32 %605, 2
  %607 = sext i32 %606 to i64
  %608 = getelementptr float, ptr %.sink104, i64 %607
  store float %.sink, ptr %608, align 4
  %609 = add nsw i32 %.06998, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond102.not = icmp eq i32 %609, %18
  br i1 %exitcond102.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.usub.sat.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #6

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
