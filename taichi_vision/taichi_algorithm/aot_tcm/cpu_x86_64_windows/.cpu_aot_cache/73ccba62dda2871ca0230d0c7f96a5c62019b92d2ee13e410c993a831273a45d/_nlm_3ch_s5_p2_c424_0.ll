; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_3ch_s5_p2_c424_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_nlm_3ch_s5_p2_c424_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %29 = add i32 %16, -5
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.06998 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %846, %after_if47 ]
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
  %264 = add i32 %43, -2
  %265 = tail call i32 @llvm.smax.i32(i32 %264, i32 0)
  %266 = tail call i32 @llvm.smin.i32(i32 %49, i32 %265)
  %267 = add i32 %41, -2
  %268 = tail call i32 @llvm.smax.i32(i32 %267, i32 0)
  %269 = tail call i32 @llvm.smin.i32(i32 %46, i32 %268)
  %270 = add i32 %43, 2
  %271 = tail call i32 @llvm.smax.i32(i32 %270, i32 0)
  %272 = tail call i32 @llvm.smin.i32(i32 %49, i32 %271)
  %273 = add i32 %41, 2
  %274 = tail call i32 @llvm.smax.i32(i32 %273, i32 0)
  %275 = tail call i32 @llvm.smin.i32(i32 %46, i32 %274)
  %276 = sub i32 %lsr.iv, %42
  %277 = add i32 %35, -5
  %278 = add i32 %277, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv115 = phi i32 [ %278, %for_loop_body ], [ %lsr.iv.next116, %for_loop_inc10 ]
  %.04797 = phi i32 [ -5, %for_loop_body ], [ %281, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %279 = add i32 %.04797, %41
  %280 = icmp slt i32 %279, 0
  br i1 %280, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %281 = add nsw i32 %.04797, 1
  %lsr.iv.next116 = add i32 %lsr.iv115, 1
  %exitcond101.not = icmp eq i32 %281, 6
  br i1 %exitcond101.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %282 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %282, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %283 = load i32, ptr %44, align 4
  %.not76 = icmp slt i32 %279, %283
  br i1 %.not76, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %284 = tail call i32 @llvm.smax.i32(i32 %279, i32 2)
  %285 = add nsw i32 %284, -2
  %286 = tail call i32 @llvm.smin.i32(i32 %46, i32 %285)
  %287 = tail call i32 @llvm.smax.i32(i32 %279, i32 1)
  %288 = add nsw i32 %287, -1
  %289 = tail call i32 @llvm.smin.i32(i32 %46, i32 %288)
  %290 = tail call i32 @llvm.smin.i32(i32 %46, i32 %279)
  %291 = add nuw i32 %279, 1
  %292 = tail call i32 @llvm.smax.i32(i32 %291, i32 0)
  %293 = tail call i32 @llvm.smin.i32(i32 %46, i32 %292)
  %294 = add nuw i32 %279, 2
  %295 = tail call i32 @llvm.smax.i32(i32 %294, i32 0)
  %296 = tail call i32 @llvm.smin.i32(i32 %46, i32 %295)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv112 = phi i32 [ %276, %for_loop_body16.preheader ], [ %lsr.iv.next113, %for_loop_inc17 ]
  %.04592 = phi i32 [ %301, %for_loop_inc17 ], [ -5, %for_loop_body16.preheader ]
  %.391 = phi float [ %.250, %for_loop_inc17 ], [ %.14996, %for_loop_body16.preheader ]
  %.35490 = phi float [ %.253, %for_loop_inc17 ], [ %.15295, %for_loop_body16.preheader ]
  %.35889 = phi float [ %.257, %for_loop_inc17 ], [ %.15694, %for_loop_body16.preheader ]
  %.36288 = phi float [ %.261, %for_loop_inc17 ], [ %.16093, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv112, i32 1)
  %297 = sub i32 %276, %umin
  %umin114 = call i32 @llvm.umin.i32(i32 %lsr.iv112, i32 2)
  %298 = sub i32 %276, %umin114
  %299 = add i32 %43, %.04592
  %300 = icmp slt i32 %299, 0
  br i1 %300, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %682, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %693, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %699, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %705, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %301 = add nsw i32 %.04592, 1
  %lsr.iv.next113 = add i32 %lsr.iv112, 1
  %exitcond.not = icmp eq i32 %301, 6
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %302 = load i32, ptr %47, align 4
  %.not77 = icmp slt i32 %299, %302
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %303 = or i32 %.04592, %.04797
  %spec.select.not = icmp eq i32 %303, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %304 = load ptr, ptr %26, align 8
  %305 = load i32, ptr %27, align 4
  %306 = load i32, ptr %28, align 4
  %307 = add i32 %.04592, %298
  %308 = add i32 %307, 5
  %309 = tail call i32 @llvm.smin.i32(i32 %49, i32 %308)
  %310 = mul i32 %305, %269
  %311 = mul i32 %305, %286
  %312 = add i32 %310, %266
  %313 = mul i32 %312, %306
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, ptr %304, i64 %314
  %316 = load float, ptr %315, align 4
  %317 = add i32 %311, %309
  %318 = mul i32 %317, %306
  %319 = sext i32 %318 to i64
  %320 = getelementptr float, ptr %304, i64 %319
  %321 = load float, ptr %320, align 4
  %322 = fsub reassoc ninf nsz float %316, %321
  %323 = fmul reassoc ninf nsz float %322, %322
  %324 = add i32 %.04592, %297
  %325 = add i32 %324, 5
  %326 = tail call i32 @llvm.smin.i32(i32 %49, i32 %325)
  %327 = add i32 %310, %55
  %328 = mul i32 %327, %306
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %304, i64 %329
  %331 = load float, ptr %330, align 4
  %332 = add i32 %311, %326
  %333 = mul i32 %332, %306
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, ptr %304, i64 %334
  %336 = load float, ptr %335, align 4
  %337 = fsub reassoc ninf nsz float %331, %336
  %338 = fmul reassoc ninf nsz float %337, %337
  %339 = fadd reassoc ninf nsz float %338, %323
  %340 = tail call i32 @llvm.smin.i32(i32 %49, i32 %299)
  %341 = add i32 %310, %78
  %342 = mul i32 %341, %306
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %304, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = add i32 %311, %340
  %347 = mul i32 %346, %306
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, ptr %304, i64 %348
  %350 = load float, ptr %349, align 4
  %351 = fsub reassoc ninf nsz float %345, %350
  %352 = fmul reassoc ninf nsz float %351, %351
  %353 = fadd reassoc ninf nsz float %352, %339
  %354 = add i32 %299, 1
  %355 = tail call i32 @llvm.smin.i32(i32 %49, i32 %354)
  %356 = add i32 %310, %100
  %357 = mul i32 %356, %306
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, ptr %304, i64 %358
  %360 = load float, ptr %359, align 4
  %361 = add i32 %311, %355
  %362 = mul i32 %361, %306
  %363 = sext i32 %362 to i64
  %364 = getelementptr float, ptr %304, i64 %363
  %365 = load float, ptr %364, align 4
  %366 = fsub reassoc ninf nsz float %360, %365
  %367 = fmul reassoc ninf nsz float %366, %366
  %368 = fadd reassoc ninf nsz float %367, %353
  %369 = add i32 %299, 2
  %370 = tail call i32 @llvm.smax.i32(i32 %369, i32 0)
  %371 = tail call i32 @llvm.smin.i32(i32 %49, i32 %370)
  %372 = add i32 %310, %272
  %373 = mul i32 %372, %306
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %304, i64 %374
  %376 = load float, ptr %375, align 4
  %377 = add i32 %311, %371
  %378 = mul i32 %377, %306
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, ptr %304, i64 %379
  %381 = load float, ptr %380, align 4
  %382 = fsub reassoc ninf nsz float %376, %381
  %383 = fmul reassoc ninf nsz float %382, %382
  %384 = fadd reassoc ninf nsz float %383, %368
  %385 = mul i32 %305, %58
  %386 = mul i32 %305, %289
  %387 = add i32 %385, %266
  %388 = mul i32 %387, %306
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %304, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = add i32 %386, %309
  %393 = mul i32 %392, %306
  %394 = sext i32 %393 to i64
  %395 = getelementptr float, ptr %304, i64 %394
  %396 = load float, ptr %395, align 4
  %397 = fsub reassoc ninf nsz float %391, %396
  %398 = fmul reassoc ninf nsz float %397, %397
  %399 = fadd reassoc ninf nsz float %398, %384
  %400 = add i32 %385, %55
  %401 = mul i32 %400, %306
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %304, i64 %402
  %404 = load float, ptr %403, align 4
  %405 = add i32 %386, %326
  %406 = mul i32 %405, %306
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %304, i64 %407
  %409 = load float, ptr %408, align 4
  %410 = fsub reassoc ninf nsz float %404, %409
  %411 = fmul reassoc ninf nsz float %410, %410
  %412 = fadd reassoc ninf nsz float %411, %399
  %413 = add i32 %385, %78
  %414 = mul i32 %413, %306
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, ptr %304, i64 %415
  %417 = load float, ptr %416, align 4
  %418 = add i32 %386, %340
  %419 = mul i32 %418, %306
  %420 = sext i32 %419 to i64
  %421 = getelementptr float, ptr %304, i64 %420
  %422 = load float, ptr %421, align 4
  %423 = fsub reassoc ninf nsz float %417, %422
  %424 = fmul reassoc ninf nsz float %423, %423
  %425 = fadd reassoc ninf nsz float %424, %412
  %426 = add i32 %385, %100
  %427 = mul i32 %426, %306
  %428 = sext i32 %427 to i64
  %429 = getelementptr float, ptr %304, i64 %428
  %430 = load float, ptr %429, align 4
  %431 = add i32 %386, %355
  %432 = mul i32 %431, %306
  %433 = sext i32 %432 to i64
  %434 = getelementptr float, ptr %304, i64 %433
  %435 = load float, ptr %434, align 4
  %436 = fsub reassoc ninf nsz float %430, %435
  %437 = fmul reassoc ninf nsz float %436, %436
  %438 = fadd reassoc ninf nsz float %437, %425
  %439 = add i32 %385, %272
  %440 = mul i32 %439, %306
  %441 = sext i32 %440 to i64
  %442 = getelementptr float, ptr %304, i64 %441
  %443 = load float, ptr %442, align 4
  %444 = add i32 %386, %371
  %445 = mul i32 %444, %306
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, ptr %304, i64 %446
  %448 = load float, ptr %447, align 4
  %449 = fsub reassoc ninf nsz float %443, %448
  %450 = fmul reassoc ninf nsz float %449, %449
  %451 = fadd reassoc ninf nsz float %450, %438
  %452 = mul i32 %305, %121
  %453 = mul i32 %305, %290
  %454 = add i32 %452, %266
  %455 = mul i32 %454, %306
  %456 = sext i32 %455 to i64
  %457 = getelementptr float, ptr %304, i64 %456
  %458 = load float, ptr %457, align 4
  %459 = add i32 %453, %309
  %460 = mul i32 %459, %306
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %304, i64 %461
  %463 = load float, ptr %462, align 4
  %464 = fsub reassoc ninf nsz float %458, %463
  %465 = fmul reassoc ninf nsz float %464, %464
  %466 = fadd reassoc ninf nsz float %465, %451
  %467 = add i32 %452, %55
  %468 = mul i32 %467, %306
  %469 = sext i32 %468 to i64
  %470 = getelementptr float, ptr %304, i64 %469
  %471 = load float, ptr %470, align 4
  %472 = add i32 %453, %326
  %473 = mul i32 %472, %306
  %474 = sext i32 %473 to i64
  %475 = getelementptr float, ptr %304, i64 %474
  %476 = load float, ptr %475, align 4
  %477 = fsub reassoc ninf nsz float %471, %476
  %478 = fmul reassoc ninf nsz float %477, %477
  %479 = fadd reassoc ninf nsz float %478, %466
  %480 = add i32 %452, %78
  %481 = mul i32 %480, %306
  %482 = sext i32 %481 to i64
  %483 = getelementptr float, ptr %304, i64 %482
  %484 = load float, ptr %483, align 4
  %485 = add i32 %453, %340
  %486 = mul i32 %485, %306
  %487 = sext i32 %486 to i64
  %488 = getelementptr float, ptr %304, i64 %487
  %489 = load float, ptr %488, align 4
  %490 = fsub reassoc ninf nsz float %484, %489
  %491 = fmul reassoc ninf nsz float %490, %490
  %492 = fadd reassoc ninf nsz float %491, %479
  %493 = add i32 %452, %100
  %494 = mul i32 %493, %306
  %495 = sext i32 %494 to i64
  %496 = getelementptr float, ptr %304, i64 %495
  %497 = load float, ptr %496, align 4
  %498 = add i32 %453, %355
  %499 = mul i32 %498, %306
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, ptr %304, i64 %500
  %502 = load float, ptr %501, align 4
  %503 = fsub reassoc ninf nsz float %497, %502
  %504 = fmul reassoc ninf nsz float %503, %503
  %505 = fadd reassoc ninf nsz float %504, %492
  %506 = add i32 %452, %272
  %507 = mul i32 %506, %306
  %508 = sext i32 %507 to i64
  %509 = getelementptr float, ptr %304, i64 %508
  %510 = load float, ptr %509, align 4
  %511 = add i32 %453, %371
  %512 = mul i32 %511, %306
  %513 = sext i32 %512 to i64
  %514 = getelementptr float, ptr %304, i64 %513
  %515 = load float, ptr %514, align 4
  %516 = fsub reassoc ninf nsz float %510, %515
  %517 = fmul reassoc ninf nsz float %516, %516
  %518 = fadd reassoc ninf nsz float %517, %505
  %519 = mul i32 %305, %182
  %520 = mul i32 %305, %293
  %521 = add i32 %519, %266
  %522 = mul i32 %521, %306
  %523 = sext i32 %522 to i64
  %524 = getelementptr float, ptr %304, i64 %523
  %525 = load float, ptr %524, align 4
  %526 = add i32 %520, %309
  %527 = mul i32 %526, %306
  %528 = sext i32 %527 to i64
  %529 = getelementptr float, ptr %304, i64 %528
  %530 = load float, ptr %529, align 4
  %531 = fsub reassoc ninf nsz float %525, %530
  %532 = fmul reassoc ninf nsz float %531, %531
  %533 = fadd reassoc ninf nsz float %532, %518
  %534 = add i32 %519, %55
  %535 = mul i32 %534, %306
  %536 = sext i32 %535 to i64
  %537 = getelementptr float, ptr %304, i64 %536
  %538 = load float, ptr %537, align 4
  %539 = add i32 %520, %326
  %540 = mul i32 %539, %306
  %541 = sext i32 %540 to i64
  %542 = getelementptr float, ptr %304, i64 %541
  %543 = load float, ptr %542, align 4
  %544 = fsub reassoc ninf nsz float %538, %543
  %545 = fmul reassoc ninf nsz float %544, %544
  %546 = fadd reassoc ninf nsz float %545, %533
  %547 = add i32 %519, %78
  %548 = mul i32 %547, %306
  %549 = sext i32 %548 to i64
  %550 = getelementptr float, ptr %304, i64 %549
  %551 = load float, ptr %550, align 4
  %552 = add i32 %520, %340
  %553 = mul i32 %552, %306
  %554 = sext i32 %553 to i64
  %555 = getelementptr float, ptr %304, i64 %554
  %556 = load float, ptr %555, align 4
  %557 = fsub reassoc ninf nsz float %551, %556
  %558 = fmul reassoc ninf nsz float %557, %557
  %559 = fadd reassoc ninf nsz float %558, %546
  %560 = add i32 %519, %100
  %561 = mul i32 %560, %306
  %562 = sext i32 %561 to i64
  %563 = getelementptr float, ptr %304, i64 %562
  %564 = load float, ptr %563, align 4
  %565 = add i32 %520, %355
  %566 = mul i32 %565, %306
  %567 = sext i32 %566 to i64
  %568 = getelementptr float, ptr %304, i64 %567
  %569 = load float, ptr %568, align 4
  %570 = fsub reassoc ninf nsz float %564, %569
  %571 = fmul reassoc ninf nsz float %570, %570
  %572 = fadd reassoc ninf nsz float %571, %559
  %573 = add i32 %519, %272
  %574 = mul i32 %573, %306
  %575 = sext i32 %574 to i64
  %576 = getelementptr float, ptr %304, i64 %575
  %577 = load float, ptr %576, align 4
  %578 = add i32 %520, %371
  %579 = mul i32 %578, %306
  %580 = sext i32 %579 to i64
  %581 = getelementptr float, ptr %304, i64 %580
  %582 = load float, ptr %581, align 4
  %583 = fsub reassoc ninf nsz float %577, %582
  %584 = fmul reassoc ninf nsz float %583, %583
  %585 = fadd reassoc ninf nsz float %584, %572
  %586 = mul i32 %305, %275
  %587 = mul i32 %305, %296
  %588 = add i32 %586, %266
  %589 = mul i32 %588, %306
  %590 = sext i32 %589 to i64
  %591 = getelementptr float, ptr %304, i64 %590
  %592 = load float, ptr %591, align 4
  %593 = add i32 %587, %309
  %594 = mul i32 %593, %306
  %595 = sext i32 %594 to i64
  %596 = getelementptr float, ptr %304, i64 %595
  %597 = load float, ptr %596, align 4
  %598 = fsub reassoc ninf nsz float %592, %597
  %599 = fmul reassoc ninf nsz float %598, %598
  %600 = fadd reassoc ninf nsz float %599, %585
  %601 = add i32 %586, %55
  %602 = mul i32 %601, %306
  %603 = sext i32 %602 to i64
  %604 = getelementptr float, ptr %304, i64 %603
  %605 = load float, ptr %604, align 4
  %606 = add i32 %587, %326
  %607 = mul i32 %606, %306
  %608 = sext i32 %607 to i64
  %609 = getelementptr float, ptr %304, i64 %608
  %610 = load float, ptr %609, align 4
  %611 = fsub reassoc ninf nsz float %605, %610
  %612 = fmul reassoc ninf nsz float %611, %611
  %613 = fadd reassoc ninf nsz float %612, %600
  %614 = add i32 %586, %78
  %615 = mul i32 %614, %306
  %616 = sext i32 %615 to i64
  %617 = getelementptr float, ptr %304, i64 %616
  %618 = load float, ptr %617, align 4
  %619 = add i32 %587, %340
  %620 = mul i32 %619, %306
  %621 = sext i32 %620 to i64
  %622 = getelementptr float, ptr %304, i64 %621
  %623 = load float, ptr %622, align 4
  %624 = fsub reassoc ninf nsz float %618, %623
  %625 = fmul reassoc ninf nsz float %624, %624
  %626 = fadd reassoc ninf nsz float %625, %613
  %627 = add i32 %586, %100
  %628 = mul i32 %627, %306
  %629 = sext i32 %628 to i64
  %630 = getelementptr float, ptr %304, i64 %629
  %631 = load float, ptr %630, align 4
  %632 = add i32 %587, %355
  %633 = mul i32 %632, %306
  %634 = sext i32 %633 to i64
  %635 = getelementptr float, ptr %304, i64 %634
  %636 = load float, ptr %635, align 4
  %637 = fsub reassoc ninf nsz float %631, %636
  %638 = fmul reassoc ninf nsz float %637, %637
  %639 = fadd reassoc ninf nsz float %638, %626
  %640 = add i32 %586, %272
  %641 = mul i32 %640, %306
  %642 = sext i32 %641 to i64
  %643 = getelementptr float, ptr %304, i64 %642
  %644 = load float, ptr %643, align 4
  %645 = add i32 %587, %371
  %646 = mul i32 %645, %306
  %647 = sext i32 %646 to i64
  %648 = getelementptr float, ptr %304, i64 %647
  %649 = load float, ptr %648, align 4
  %650 = fsub reassoc ninf nsz float %644, %649
  %651 = fmul reassoc ninf nsz float %650, %650
  %652 = fadd reassoc ninf nsz float %651, %639
  %653 = fmul reassoc ninf nsz float %652, 0x3FA47AE140000000
  %654 = mul i32 %lsr.iv115, %305
  %655 = add i32 %299, %654
  %656 = mul i32 %655, %306
  %657 = add i32 %656, 1
  %658 = sext i32 %657 to i64
  %659 = getelementptr float, ptr %304, i64 %658
  %660 = load float, ptr %659, align 4
  %661 = add i32 %656, 2
  %662 = sext i32 %661 to i64
  %663 = getelementptr float, ptr %304, i64 %662
  %664 = load float, ptr %663, align 4
  %665 = fsub reassoc ninf nsz float %259, %660
  %666 = fsub reassoc ninf nsz float %263, %664
  %667 = fmul reassoc ninf nsz float %665, %665
  %668 = fmul reassoc ninf nsz float %666, %666
  %669 = fadd reassoc ninf nsz float %668, %667
  %670 = fmul reassoc ninf nsz float %669, 2.500000e-01
  %671 = fadd reassoc ninf nsz float %670, %653
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %671, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %672 = load ptr, ptr %3, align 8
  %673 = getelementptr inbounds nuw i8, ptr %672, i64 32872
  %674 = load ptr, ptr %673, align 8
  %675 = getelementptr inbounds nuw i8, ptr %674, i64 16
  %676 = load float, ptr %675, align 4
  %677 = fcmp reassoc ninf nsz ugt float %.043, %676
  br i1 %677, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %678 = getelementptr inbounds nuw i8, ptr %674, i64 20
  %679 = load float, ptr %678, align 4
  %680 = fmul reassoc ninf nsz float %679, %neg44
  %681 = tail call noundef float @expf(float noundef %680) #8
  %682 = fadd reassoc ninf nsz float %681, %.36288
  %683 = load ptr, ptr %23, align 8
  %684 = load i32, ptr %24, align 4
  %685 = load i32, ptr %25, align 4
  %686 = mul i32 %lsr.iv115, %684
  %687 = add i32 %299, %686
  %688 = mul i32 %687, %685
  %689 = sext i32 %688 to i64
  %690 = getelementptr float, ptr %683, i64 %689
  %691 = load float, ptr %690, align 4
  %692 = fmul reassoc ninf nsz float %691, %681
  %693 = fadd reassoc ninf nsz float %692, %.35889
  %694 = add i32 %688, 1
  %695 = sext i32 %694 to i64
  %696 = getelementptr float, ptr %683, i64 %695
  %697 = load float, ptr %696, align 4
  %698 = fmul reassoc ninf nsz float %697, %681
  %699 = fadd reassoc ninf nsz float %698, %.35490
  %700 = add i32 %688, 2
  %701 = sext i32 %700 to i64
  %702 = getelementptr float, ptr %683, i64 %701
  %703 = load float, ptr %702, align 4
  %704 = fmul reassoc ninf nsz float %703, %681
  %705 = fadd reassoc ninf nsz float %704, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %706 = fmul reassoc ninf nsz float %249, %21
  %707 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %708 = fmul reassoc ninf nsz float %.055, %707
  %709 = fmul reassoc ninf nsz float %.051, %707
  %710 = fmul reassoc ninf nsz float %.048, %707
  %711 = load ptr, ptr %23, align 8
  %712 = load i32, ptr %24, align 4
  %713 = load i32, ptr %25, align 4
  %714 = mul i32 %712, %41
  %715 = add i32 %714, %43
  %716 = mul i32 %715, %713
  %717 = sext i32 %716 to i64
  %718 = getelementptr float, ptr %711, i64 %717
  %719 = load float, ptr %718, align 4
  %720 = fsub reassoc ninf nsz float %719, %708
  %721 = add i32 %716, 1
  %722 = sext i32 %721 to i64
  %723 = getelementptr float, ptr %711, i64 %722
  %724 = load float, ptr %723, align 4
  %725 = fsub reassoc ninf nsz float %724, %709
  %726 = add i32 %716, 2
  %727 = sext i32 %726 to i64
  %728 = getelementptr float, ptr %711, i64 %727
  %729 = load float, ptr %728, align 4
  %730 = fsub reassoc ninf nsz float %729, %710
  %731 = tail call noundef float @llvm.fabs.f32(float %720)
  %732 = load ptr, ptr %3, align 8
  %733 = getelementptr inbounds nuw i8, ptr %732, i64 32872
  %734 = load ptr, ptr %733, align 8
  %735 = getelementptr inbounds nuw i8, ptr %734, i64 24
  %736 = load float, ptr %735, align 4
  %737 = fsub reassoc ninf nsz float %731, %736
  %738 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %737, float 0.000000e+00)
  %739 = fcmp reassoc ninf nsz oge float %720, 0.000000e+00
  %740 = uitofp i1 %739 to float
  %741 = fcmp reassoc ninf nsz ole float %720, 0.000000e+00
  %742 = uitofp i1 %741 to float
  %743 = fsub reassoc ninf nsz float %740, %742
  %744 = tail call noundef float @llvm.fabs.f32(float %725)
  %745 = fsub reassoc ninf nsz float %744, %736
  %746 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %745, float 0.000000e+00)
  %747 = fcmp reassoc ninf nsz oge float %725, 0.000000e+00
  %748 = uitofp i1 %747 to float
  %749 = fcmp reassoc ninf nsz ole float %725, 0.000000e+00
  %750 = uitofp i1 %749 to float
  %751 = fsub reassoc ninf nsz float %748, %750
  %752 = tail call noundef float @llvm.fabs.f32(float %730)
  %753 = fsub reassoc ninf nsz float %752, %736
  %754 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %753, float 0.000000e+00)
  %755 = fcmp reassoc ninf nsz oge float %730, 0.000000e+00
  %756 = uitofp i1 %755 to float
  %757 = fcmp reassoc ninf nsz ole float %730, 0.000000e+00
  %758 = uitofp i1 %757 to float
  %759 = fsub reassoc ninf nsz float %756, %758
  %760 = fmul reassoc ninf nsz float %743, %706
  %761 = fmul reassoc ninf nsz float %760, %738
  %762 = fadd reassoc ninf nsz float %761, %708
  %763 = load ptr, ptr %0, align 8
  %764 = getelementptr i8, ptr %763, i64 64
  %765 = load ptr, ptr %764, align 8
  %766 = getelementptr i8, ptr %763, i64 52
  %767 = load i32, ptr %766, align 4
  %768 = getelementptr i8, ptr %763, i64 56
  %769 = load i32, ptr %768, align 4
  %770 = mul i32 %767, %41
  %771 = add i32 %770, %43
  %772 = mul i32 %771, %769
  %773 = sext i32 %772 to i64
  %774 = getelementptr float, ptr %765, i64 %773
  store float %762, ptr %774, align 4
  %775 = fmul reassoc ninf nsz float %751, %706
  %776 = fmul reassoc ninf nsz float %775, %746
  %777 = fadd reassoc ninf nsz float %776, %709
  %778 = load ptr, ptr %764, align 8
  %779 = load i32, ptr %766, align 4
  %780 = load i32, ptr %768, align 4
  %781 = mul i32 %779, %41
  %782 = add i32 %781, %43
  %783 = mul i32 %782, %780
  %784 = add i32 %783, 1
  %785 = sext i32 %784 to i64
  %786 = getelementptr float, ptr %778, i64 %785
  store float %777, ptr %786, align 4
  %787 = fmul reassoc ninf nsz float %759, %706
  %788 = fmul reassoc ninf nsz float %787, %754
  %789 = fadd reassoc ninf nsz float %788, %710
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %790 = load ptr, ptr %23, align 8
  %791 = load i32, ptr %24, align 4
  %792 = load i32, ptr %25, align 4
  %793 = mul i32 %791, %41
  %794 = add i32 %793, %43
  %795 = mul i32 %794, %792
  %796 = sext i32 %795 to i64
  %797 = getelementptr float, ptr %790, i64 %796
  %798 = load float, ptr %797, align 4
  %799 = load ptr, ptr %0, align 8
  %800 = getelementptr i8, ptr %799, i64 64
  %801 = load ptr, ptr %800, align 8
  %802 = getelementptr i8, ptr %799, i64 52
  %803 = load i32, ptr %802, align 4
  %804 = getelementptr i8, ptr %799, i64 56
  %805 = load i32, ptr %804, align 4
  %806 = mul i32 %803, %41
  %807 = add i32 %806, %43
  %808 = mul i32 %807, %805
  %809 = sext i32 %808 to i64
  %810 = getelementptr float, ptr %801, i64 %809
  store float %798, ptr %810, align 4
  %811 = load ptr, ptr %23, align 8
  %812 = load i32, ptr %24, align 4
  %813 = load i32, ptr %25, align 4
  %814 = mul i32 %812, %41
  %815 = add i32 %814, %43
  %816 = mul i32 %815, %813
  %817 = add i32 %816, 1
  %818 = sext i32 %817 to i64
  %819 = getelementptr float, ptr %811, i64 %818
  %820 = load float, ptr %819, align 4
  %821 = load ptr, ptr %800, align 8
  %822 = load i32, ptr %802, align 4
  %823 = load i32, ptr %804, align 4
  %824 = mul i32 %822, %41
  %825 = add i32 %824, %43
  %826 = mul i32 %825, %823
  %827 = add i32 %826, 1
  %828 = sext i32 %827 to i64
  %829 = getelementptr float, ptr %821, i64 %828
  store float %820, ptr %829, align 4
  %830 = load ptr, ptr %23, align 8
  %831 = load i32, ptr %24, align 4
  %832 = load i32, ptr %25, align 4
  %833 = mul i32 %831, %41
  %834 = add i32 %833, %43
  %835 = mul i32 %834, %832
  %836 = add i32 %835, 2
  %837 = sext i32 %836 to i64
  %838 = getelementptr float, ptr %830, i64 %837
  %839 = load float, ptr %838, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink111.in = phi ptr [ %802, %false_block46 ], [ %766, %true_block45 ]
  %.sink109.in = phi ptr [ %804, %false_block46 ], [ %768, %true_block45 ]
  %.sink104.in = phi ptr [ %800, %false_block46 ], [ %764, %true_block45 ]
  %.sink = phi float [ %839, %false_block46 ], [ %789, %true_block45 ]
  %.sink104 = load ptr, ptr %.sink104.in, align 8
  %.sink109 = load i32, ptr %.sink109.in, align 4
  %.sink111 = load i32, ptr %.sink111.in, align 4
  %840 = mul i32 %.sink111, %41
  %841 = add i32 %840, %43
  %842 = mul i32 %841, %.sink109
  %843 = add i32 %842, 2
  %844 = sext i32 %843 to i64
  %845 = getelementptr float, ptr %.sink104, i64 %844
  store float %.sink, ptr %845, align 4
  %846 = add nsw i32 %.06998, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond102.not = icmp eq i32 %846, %18
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
  %4 = alloca %struct.RuntimeContext.9, align 8
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
