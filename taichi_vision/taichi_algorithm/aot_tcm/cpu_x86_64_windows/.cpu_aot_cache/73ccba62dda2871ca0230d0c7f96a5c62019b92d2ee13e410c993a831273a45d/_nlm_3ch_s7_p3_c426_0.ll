; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.11 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_nlm_3ch_s7_p3_c426_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_nlm_3ch_s7_p3_c426_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #9
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
  %29 = add i32 %16, -7
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if47 ]
  %.06998 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %591, %after_if47 ]
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
  %247 = tail call noundef float @expf(float noundef %246) #9
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
  %264 = add i32 %43, -3
  %265 = tail call i32 @llvm.smax.i32(i32 %264, i32 0)
  %266 = tail call i32 @llvm.smin.i32(i32 %49, i32 %265)
  %267 = add i32 %43, -2
  %268 = tail call i32 @llvm.smax.i32(i32 %267, i32 0)
  %269 = tail call i32 @llvm.smin.i32(i32 %49, i32 %268)
  %270 = add i32 %43, 2
  %271 = tail call i32 @llvm.smax.i32(i32 %270, i32 0)
  %272 = tail call i32 @llvm.smin.i32(i32 %49, i32 %271)
  %273 = add i32 %43, 3
  %274 = tail call i32 @llvm.smax.i32(i32 %273, i32 0)
  %275 = tail call i32 @llvm.smin.i32(i32 %49, i32 %274)
  %broadcast.splatinsert113 = insertelement <8 x i32> poison, i32 %41, i64 0
  %broadcast.splat114 = shufflevector <8 x i32> %broadcast.splatinsert113, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert115 = insertelement <8 x i32> poison, i32 %46, i64 0
  %broadcast.splat116 = shufflevector <8 x i32> %broadcast.splatinsert115, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert121 = insertelement <8 x i32> poison, i32 %266, i64 0
  %broadcast.splat122 = shufflevector <8 x i32> %broadcast.splatinsert121, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert128 = insertelement <8 x i32> poison, i32 %269, i64 0
  %broadcast.splat129 = shufflevector <8 x i32> %broadcast.splatinsert128, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert134 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat135 = shufflevector <8 x i32> %broadcast.splatinsert134, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert140 = insertelement <8 x i32> poison, i32 %78, i64 0
  %broadcast.splat141 = shufflevector <8 x i32> %broadcast.splatinsert140, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert146 = insertelement <8 x i32> poison, i32 %100, i64 0
  %broadcast.splat147 = shufflevector <8 x i32> %broadcast.splatinsert146, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert152 = insertelement <8 x i32> poison, i32 %272, i64 0
  %broadcast.splat153 = shufflevector <8 x i32> %broadcast.splatinsert152, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert158 = insertelement <8 x i32> poison, i32 %275, i64 0
  %broadcast.splat159 = shufflevector <8 x i32> %broadcast.splatinsert158, <8 x i32> poison, <8 x i32> zeroinitializer
  %276 = add <8 x i32> %broadcast.splat114, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %277 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %276, <8 x i32> zeroinitializer)
  %278 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat116, <8 x i32> %277)
  %279 = sub i32 %lsr.iv, %42
  %280 = add i32 %35, -7
  %281 = add i32 %280, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv166 = phi i32 [ %281, %for_loop_body ], [ %lsr.iv.next167, %for_loop_inc10 ]
  %.04797 = phi i32 [ -7, %for_loop_body ], [ %284, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %282 = add i32 %.04797, %41
  %283 = icmp slt i32 %282, 0
  br i1 %283, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %284 = add nsw i32 %.04797, 1
  %lsr.iv.next167 = add i32 %lsr.iv166, 1
  %exitcond102.not = icmp eq i32 %284, 8
  br i1 %exitcond102.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %285 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %285, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %286 = load i32, ptr %44, align 4
  %.not76 = icmp slt i32 %282, %286
  br i1 %.not76, label %for_loop_body16.preheader, label %for_loop_inc10

for_loop_body16.preheader:                        ; preds = %false_block
  %broadcast.splatinsert117 = insertelement <8 x i32> poison, i32 %282, i64 0
  %broadcast.splat118 = shufflevector <8 x i32> %broadcast.splatinsert117, <8 x i32> poison, <8 x i32> zeroinitializer
  %287 = add <8 x i32> %broadcast.splat118, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %288 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %287, <8 x i32> zeroinitializer)
  %289 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat116, <8 x i32> %288)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %for_loop_body16.preheader
  %lsr.iv164 = phi i32 [ %279, %for_loop_body16.preheader ], [ %lsr.iv.next165, %for_loop_inc17 ]
  %.04592 = phi i32 [ %293, %for_loop_inc17 ], [ -7, %for_loop_body16.preheader ]
  %.391 = phi float [ %.250, %for_loop_inc17 ], [ %.14996, %for_loop_body16.preheader ]
  %.35490 = phi float [ %.253, %for_loop_inc17 ], [ %.15295, %for_loop_body16.preheader ]
  %.35889 = phi float [ %.257, %for_loop_inc17 ], [ %.15694, %for_loop_body16.preheader ]
  %.36288 = phi float [ %.261, %for_loop_inc17 ], [ %.16093, %for_loop_body16.preheader ]
  %umin = call i32 @llvm.umin.i32(i32 %lsr.iv164, i32 3)
  %290 = sub i32 %279, %umin
  %291 = add i32 %43, %.04592
  %292 = icmp slt i32 %291, 0
  br i1 %292, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %427, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %438, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %444, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %450, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %293 = add nsw i32 %.04592, 1
  %lsr.iv.next165 = add i32 %lsr.iv164, 1
  %exitcond101.not = icmp eq i32 %293, 8
  br i1 %exitcond101.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %294 = load i32, ptr %47, align 4
  %.not77 = icmp slt i32 %291, %294
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %295 = or i32 %.04592, %.04797
  %spec.select.not = icmp eq i32 %295, 0
  br i1 %spec.select.not, label %after_if32, label %for_loop_test36.preheader

for_loop_test36.preheader:                        ; preds = %after_if25
  %296 = load ptr, ptr %26, align 8
  %297 = add i32 %291, 3
  %298 = tail call i32 @llvm.smax.i32(i32 %297, i32 0)
  %299 = tail call i32 @llvm.smin.i32(i32 %49, i32 %298)
  %300 = add i32 %291, 2
  %301 = tail call i32 @llvm.smax.i32(i32 %300, i32 0)
  %302 = tail call i32 @llvm.smin.i32(i32 %49, i32 %301)
  %303 = add i32 %291, 1
  %304 = tail call i32 @llvm.smax.i32(i32 %303, i32 0)
  %305 = tail call i32 @llvm.smin.i32(i32 %49, i32 %304)
  %306 = tail call i32 @llvm.smin.i32(i32 %49, i32 %291)
  %307 = tail call i32 @llvm.smax.i32(i32 %291, i32 1)
  %308 = add nsw i32 %307, -1
  %309 = tail call i32 @llvm.smin.i32(i32 %49, i32 %308)
  %310 = tail call i32 @llvm.smax.i32(i32 %291, i32 2)
  %311 = add nsw i32 %310, -2
  %312 = tail call i32 @llvm.smin.i32(i32 %49, i32 %311)
  %313 = add i32 %.04592, %290
  %314 = add i32 %313, 7
  %315 = tail call i32 @llvm.smin.i32(i32 %49, i32 %314)
  %316 = load i32, ptr %28, align 4
  %317 = load i32, ptr %27, align 4
  %broadcast.splatinsert119 = insertelement <8 x i32> poison, i32 %317, i64 0
  %broadcast.splat120 = shufflevector <8 x i32> %broadcast.splatinsert119, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert123 = insertelement <8 x i32> poison, i32 %316, i64 0
  %broadcast.splat124 = shufflevector <8 x i32> %broadcast.splatinsert123, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert125 = insertelement <8 x i32> poison, i32 %315, i64 0
  %broadcast.splat126 = shufflevector <8 x i32> %broadcast.splatinsert125, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert131 = insertelement <8 x i32> poison, i32 %312, i64 0
  %broadcast.splat132 = shufflevector <8 x i32> %broadcast.splatinsert131, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert137 = insertelement <8 x i32> poison, i32 %309, i64 0
  %broadcast.splat138 = shufflevector <8 x i32> %broadcast.splatinsert137, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert143 = insertelement <8 x i32> poison, i32 %306, i64 0
  %broadcast.splat144 = shufflevector <8 x i32> %broadcast.splatinsert143, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert149 = insertelement <8 x i32> poison, i32 %305, i64 0
  %broadcast.splat150 = shufflevector <8 x i32> %broadcast.splatinsert149, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert155 = insertelement <8 x i32> poison, i32 %302, i64 0
  %broadcast.splat156 = shufflevector <8 x i32> %broadcast.splatinsert155, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert161 = insertelement <8 x i32> poison, i32 %299, i64 0
  %broadcast.splat162 = shufflevector <8 x i32> %broadcast.splatinsert161, <8 x i32> poison, <8 x i32> zeroinitializer
  %318 = mul <8 x i32> %broadcast.splat120, %278
  %319 = add <8 x i32> %318, %broadcast.splat159
  %320 = mul <8 x i32> %319, %broadcast.splat124
  %321 = sext <8 x i32> %320 to <8 x i64>
  %322 = getelementptr float, ptr %296, <8 x i64> %321
  %wide.masked.gather160 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %322, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %323 = mul <8 x i32> %broadcast.splat120, %289
  %324 = add <8 x i32> %323, %broadcast.splat162
  %325 = mul <8 x i32> %324, %broadcast.splat124
  %326 = sext <8 x i32> %325 to <8 x i64>
  %327 = getelementptr float, ptr %296, <8 x i64> %326
  %wide.masked.gather163 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %327, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %328 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather160, %wide.masked.gather163
  %329 = fmul reassoc ninf nsz <8 x float> %328, %328
  %330 = add <8 x i32> %318, %broadcast.splat153
  %331 = mul <8 x i32> %330, %broadcast.splat124
  %332 = sext <8 x i32> %331 to <8 x i64>
  %333 = getelementptr float, ptr %296, <8 x i64> %332
  %wide.masked.gather154 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %333, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %334 = add <8 x i32> %323, %broadcast.splat156
  %335 = mul <8 x i32> %334, %broadcast.splat124
  %336 = sext <8 x i32> %335 to <8 x i64>
  %337 = getelementptr float, ptr %296, <8 x i64> %336
  %wide.masked.gather157 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %337, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %338 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather154, %wide.masked.gather157
  %339 = fmul reassoc ninf nsz <8 x float> %338, %338
  %340 = add <8 x i32> %318, %broadcast.splat147
  %341 = mul <8 x i32> %340, %broadcast.splat124
  %342 = sext <8 x i32> %341 to <8 x i64>
  %343 = getelementptr float, ptr %296, <8 x i64> %342
  %wide.masked.gather148 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %343, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %344 = add <8 x i32> %323, %broadcast.splat150
  %345 = mul <8 x i32> %344, %broadcast.splat124
  %346 = sext <8 x i32> %345 to <8 x i64>
  %347 = getelementptr float, ptr %296, <8 x i64> %346
  %wide.masked.gather151 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %347, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %348 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather148, %wide.masked.gather151
  %349 = fmul reassoc ninf nsz <8 x float> %348, %348
  %350 = add <8 x i32> %318, %broadcast.splat141
  %351 = mul <8 x i32> %350, %broadcast.splat124
  %352 = sext <8 x i32> %351 to <8 x i64>
  %353 = getelementptr float, ptr %296, <8 x i64> %352
  %wide.masked.gather142 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %353, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %354 = add <8 x i32> %323, %broadcast.splat144
  %355 = mul <8 x i32> %354, %broadcast.splat124
  %356 = sext <8 x i32> %355 to <8 x i64>
  %357 = getelementptr float, ptr %296, <8 x i64> %356
  %wide.masked.gather145 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %357, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %358 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather142, %wide.masked.gather145
  %359 = fmul reassoc ninf nsz <8 x float> %358, %358
  %360 = add <8 x i32> %318, %broadcast.splat135
  %361 = mul <8 x i32> %360, %broadcast.splat124
  %362 = sext <8 x i32> %361 to <8 x i64>
  %363 = getelementptr float, ptr %296, <8 x i64> %362
  %wide.masked.gather136 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %363, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %364 = add <8 x i32> %323, %broadcast.splat138
  %365 = mul <8 x i32> %364, %broadcast.splat124
  %366 = sext <8 x i32> %365 to <8 x i64>
  %367 = getelementptr float, ptr %296, <8 x i64> %366
  %wide.masked.gather139 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %367, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %368 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather136, %wide.masked.gather139
  %369 = fmul reassoc ninf nsz <8 x float> %368, %368
  %370 = add <8 x i32> %318, %broadcast.splat129
  %371 = mul <8 x i32> %370, %broadcast.splat124
  %372 = sext <8 x i32> %371 to <8 x i64>
  %373 = getelementptr float, ptr %296, <8 x i64> %372
  %wide.masked.gather130 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %373, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %374 = add <8 x i32> %323, %broadcast.splat132
  %375 = mul <8 x i32> %374, %broadcast.splat124
  %376 = sext <8 x i32> %375 to <8 x i64>
  %377 = getelementptr float, ptr %296, <8 x i64> %376
  %wide.masked.gather133 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %377, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %378 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather130, %wide.masked.gather133
  %379 = fmul reassoc ninf nsz <8 x float> %378, %378
  %380 = add <8 x i32> %318, %broadcast.splat122
  %381 = mul <8 x i32> %380, %broadcast.splat124
  %382 = sext <8 x i32> %381 to <8 x i64>
  %383 = getelementptr float, ptr %296, <8 x i64> %382
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %383, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %384 = add <8 x i32> %323, %broadcast.splat126
  %385 = mul <8 x i32> %384, %broadcast.splat124
  %386 = sext <8 x i32> %385 to <8 x i64>
  %387 = getelementptr float, ptr %296, <8 x i64> %386
  %wide.masked.gather127 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %387, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> poison)
  %388 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather127
  %389 = fmul reassoc ninf nsz <8 x float> %388, %388
  %390 = fadd reassoc ninf nsz <8 x float> %379, %389
  %391 = fadd reassoc ninf nsz <8 x float> %369, %390
  %392 = fadd reassoc ninf nsz <8 x float> %359, %391
  %393 = fadd reassoc ninf nsz <8 x float> %349, %392
  %394 = fadd reassoc ninf nsz <8 x float> %339, %393
  %395 = fadd reassoc ninf nsz <8 x float> %329, %394
  %396 = insertelement <8 x float> %395, float 0.000000e+00, i64 7
  %397 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %396)
  %398 = fmul reassoc ninf nsz float %397, 0x3F94E5E0A0000000
  %399 = mul i32 %lsr.iv166, %317
  %400 = add i32 %291, %399
  %401 = mul i32 %400, %316
  %402 = add i32 %401, 1
  %403 = sext i32 %402 to i64
  %404 = getelementptr float, ptr %296, i64 %403
  %405 = load float, ptr %404, align 4
  %406 = add i32 %401, 2
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %296, i64 %407
  %409 = load float, ptr %408, align 4
  %410 = fsub reassoc ninf nsz float %259, %405
  %411 = fsub reassoc ninf nsz float %263, %409
  %412 = fmul reassoc ninf nsz float %410, %410
  %413 = fmul reassoc ninf nsz float %411, %411
  %414 = fadd reassoc ninf nsz float %413, %412
  %415 = fmul reassoc ninf nsz float %414, 2.500000e-01
  %416 = fadd reassoc ninf nsz float %415, %398
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %416, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %417 = load ptr, ptr %3, align 8
  %418 = getelementptr inbounds nuw i8, ptr %417, i64 32872
  %419 = load ptr, ptr %418, align 8
  %420 = getelementptr inbounds nuw i8, ptr %419, i64 16
  %421 = load float, ptr %420, align 4
  %422 = fcmp reassoc ninf nsz ugt float %.043, %421
  br i1 %422, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %423 = getelementptr inbounds nuw i8, ptr %419, i64 20
  %424 = load float, ptr %423, align 4
  %425 = fmul reassoc ninf nsz float %424, %neg44
  %426 = tail call noundef float @expf(float noundef %425) #9
  %427 = fadd reassoc ninf nsz float %426, %.36288
  %428 = load ptr, ptr %23, align 8
  %429 = load i32, ptr %24, align 4
  %430 = load i32, ptr %25, align 4
  %431 = mul i32 %lsr.iv166, %429
  %432 = add i32 %291, %431
  %433 = mul i32 %432, %430
  %434 = sext i32 %433 to i64
  %435 = getelementptr float, ptr %428, i64 %434
  %436 = load float, ptr %435, align 4
  %437 = fmul reassoc ninf nsz float %436, %426
  %438 = fadd reassoc ninf nsz float %437, %.35889
  %439 = add i32 %433, 1
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, ptr %428, i64 %440
  %442 = load float, ptr %441, align 4
  %443 = fmul reassoc ninf nsz float %442, %426
  %444 = fadd reassoc ninf nsz float %443, %.35490
  %445 = add i32 %433, 2
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, ptr %428, i64 %446
  %448 = load float, ptr %447, align 4
  %449 = fmul reassoc ninf nsz float %448, %426
  %450 = fadd reassoc ninf nsz float %449, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %451 = fmul reassoc ninf nsz float %249, %21
  %452 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %453 = fmul reassoc ninf nsz float %.055, %452
  %454 = fmul reassoc ninf nsz float %.051, %452
  %455 = fmul reassoc ninf nsz float %.048, %452
  %456 = load ptr, ptr %23, align 8
  %457 = load i32, ptr %24, align 4
  %458 = load i32, ptr %25, align 4
  %459 = mul i32 %457, %41
  %460 = add i32 %459, %43
  %461 = mul i32 %460, %458
  %462 = sext i32 %461 to i64
  %463 = getelementptr float, ptr %456, i64 %462
  %464 = load float, ptr %463, align 4
  %465 = fsub reassoc ninf nsz float %464, %453
  %466 = add i32 %461, 1
  %467 = sext i32 %466 to i64
  %468 = getelementptr float, ptr %456, i64 %467
  %469 = load float, ptr %468, align 4
  %470 = fsub reassoc ninf nsz float %469, %454
  %471 = add i32 %461, 2
  %472 = sext i32 %471 to i64
  %473 = getelementptr float, ptr %456, i64 %472
  %474 = load float, ptr %473, align 4
  %475 = fsub reassoc ninf nsz float %474, %455
  %476 = tail call noundef float @llvm.fabs.f32(float %465)
  %477 = load ptr, ptr %3, align 8
  %478 = getelementptr inbounds nuw i8, ptr %477, i64 32872
  %479 = load ptr, ptr %478, align 8
  %480 = getelementptr inbounds nuw i8, ptr %479, i64 24
  %481 = load float, ptr %480, align 4
  %482 = fsub reassoc ninf nsz float %476, %481
  %483 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %482, float 0.000000e+00)
  %484 = fcmp reassoc ninf nsz oge float %465, 0.000000e+00
  %485 = uitofp i1 %484 to float
  %486 = fcmp reassoc ninf nsz ole float %465, 0.000000e+00
  %487 = uitofp i1 %486 to float
  %488 = fsub reassoc ninf nsz float %485, %487
  %489 = tail call noundef float @llvm.fabs.f32(float %470)
  %490 = fsub reassoc ninf nsz float %489, %481
  %491 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %490, float 0.000000e+00)
  %492 = fcmp reassoc ninf nsz oge float %470, 0.000000e+00
  %493 = uitofp i1 %492 to float
  %494 = fcmp reassoc ninf nsz ole float %470, 0.000000e+00
  %495 = uitofp i1 %494 to float
  %496 = fsub reassoc ninf nsz float %493, %495
  %497 = tail call noundef float @llvm.fabs.f32(float %475)
  %498 = fsub reassoc ninf nsz float %497, %481
  %499 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %498, float 0.000000e+00)
  %500 = fcmp reassoc ninf nsz oge float %475, 0.000000e+00
  %501 = uitofp i1 %500 to float
  %502 = fcmp reassoc ninf nsz ole float %475, 0.000000e+00
  %503 = uitofp i1 %502 to float
  %504 = fsub reassoc ninf nsz float %501, %503
  %505 = fmul reassoc ninf nsz float %488, %451
  %506 = fmul reassoc ninf nsz float %505, %483
  %507 = fadd reassoc ninf nsz float %506, %453
  %508 = load ptr, ptr %0, align 8
  %509 = getelementptr i8, ptr %508, i64 64
  %510 = load ptr, ptr %509, align 8
  %511 = getelementptr i8, ptr %508, i64 52
  %512 = load i32, ptr %511, align 4
  %513 = getelementptr i8, ptr %508, i64 56
  %514 = load i32, ptr %513, align 4
  %515 = mul i32 %512, %41
  %516 = add i32 %515, %43
  %517 = mul i32 %516, %514
  %518 = sext i32 %517 to i64
  %519 = getelementptr float, ptr %510, i64 %518
  store float %507, ptr %519, align 4
  %520 = fmul reassoc ninf nsz float %496, %451
  %521 = fmul reassoc ninf nsz float %520, %491
  %522 = fadd reassoc ninf nsz float %521, %454
  %523 = load ptr, ptr %509, align 8
  %524 = load i32, ptr %511, align 4
  %525 = load i32, ptr %513, align 4
  %526 = mul i32 %524, %41
  %527 = add i32 %526, %43
  %528 = mul i32 %527, %525
  %529 = add i32 %528, 1
  %530 = sext i32 %529 to i64
  %531 = getelementptr float, ptr %523, i64 %530
  store float %522, ptr %531, align 4
  %532 = fmul reassoc ninf nsz float %504, %451
  %533 = fmul reassoc ninf nsz float %532, %499
  %534 = fadd reassoc ninf nsz float %533, %455
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %535 = load ptr, ptr %23, align 8
  %536 = load i32, ptr %24, align 4
  %537 = load i32, ptr %25, align 4
  %538 = mul i32 %536, %41
  %539 = add i32 %538, %43
  %540 = mul i32 %539, %537
  %541 = sext i32 %540 to i64
  %542 = getelementptr float, ptr %535, i64 %541
  %543 = load float, ptr %542, align 4
  %544 = load ptr, ptr %0, align 8
  %545 = getelementptr i8, ptr %544, i64 64
  %546 = load ptr, ptr %545, align 8
  %547 = getelementptr i8, ptr %544, i64 52
  %548 = load i32, ptr %547, align 4
  %549 = getelementptr i8, ptr %544, i64 56
  %550 = load i32, ptr %549, align 4
  %551 = mul i32 %548, %41
  %552 = add i32 %551, %43
  %553 = mul i32 %552, %550
  %554 = sext i32 %553 to i64
  %555 = getelementptr float, ptr %546, i64 %554
  store float %543, ptr %555, align 4
  %556 = load ptr, ptr %23, align 8
  %557 = load i32, ptr %24, align 4
  %558 = load i32, ptr %25, align 4
  %559 = mul i32 %557, %41
  %560 = add i32 %559, %43
  %561 = mul i32 %560, %558
  %562 = add i32 %561, 1
  %563 = sext i32 %562 to i64
  %564 = getelementptr float, ptr %556, i64 %563
  %565 = load float, ptr %564, align 4
  %566 = load ptr, ptr %545, align 8
  %567 = load i32, ptr %547, align 4
  %568 = load i32, ptr %549, align 4
  %569 = mul i32 %567, %41
  %570 = add i32 %569, %43
  %571 = mul i32 %570, %568
  %572 = add i32 %571, 1
  %573 = sext i32 %572 to i64
  %574 = getelementptr float, ptr %566, i64 %573
  store float %565, ptr %574, align 4
  %575 = load ptr, ptr %23, align 8
  %576 = load i32, ptr %24, align 4
  %577 = load i32, ptr %25, align 4
  %578 = mul i32 %576, %41
  %579 = add i32 %578, %43
  %580 = mul i32 %579, %577
  %581 = add i32 %580, 2
  %582 = sext i32 %581 to i64
  %583 = getelementptr float, ptr %575, i64 %582
  %584 = load float, ptr %583, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink112.in = phi ptr [ %547, %false_block46 ], [ %511, %true_block45 ]
  %.sink110.in = phi ptr [ %549, %false_block46 ], [ %513, %true_block45 ]
  %.sink105.in = phi ptr [ %545, %false_block46 ], [ %509, %true_block45 ]
  %.sink = phi float [ %584, %false_block46 ], [ %534, %true_block45 ]
  %.sink105 = load ptr, ptr %.sink105.in, align 8
  %.sink110 = load i32, ptr %.sink110.in, align 4
  %.sink112 = load i32, ptr %.sink112.in, align 4
  %585 = mul i32 %.sink112, %41
  %586 = add i32 %585, %43
  %587 = mul i32 %586, %.sink110
  %588 = add i32 %587, 2
  %589 = sext i32 %588 to i64
  %590 = getelementptr float, ptr %.sink105, i64 %589
  store float %.sink, ptr %590, align 4
  %591 = add nsw i32 %.06998, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond103.not = icmp eq i32 %591, %18
  br i1 %exitcond103.not, label %after_for.loopexit, label %for_loop_body
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
  %4 = alloca %struct.RuntimeContext.11, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #9
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #9
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
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
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #6

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
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #9 = { nounwind }

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
