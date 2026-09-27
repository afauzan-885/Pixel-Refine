; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.30 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @remap_accumulate_average_tile_kernel_c764_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 116
  %2 = load i32, ptr %1, align 4
  %3 = add i32 %2, -1
  %4 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 32872
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 24
  store i32 %3, ptr %8, align 4
  %9 = sitofp i32 %3 to float
  %10 = load ptr, ptr %context, align 8
  %11 = getelementptr i8, ptr %10, i64 108
  %12 = load i32, ptr %11, align 4
  %13 = load ptr, ptr %4, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 12
  store i32 %12, ptr %16, align 4
  %17 = add i32 %12, -1
  %18 = sitofp i32 %17 to float
  %19 = fdiv reassoc ninf nsz float %9, %18
  %20 = load ptr, ptr %4, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 16
  store float %19, ptr %23, align 4
  %24 = load ptr, ptr %context, align 8
  %25 = getelementptr i8, ptr %24, i64 112
  %26 = load i32, ptr %25, align 4
  %27 = add i32 %26, -1
  %28 = load ptr, ptr %4, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 28
  store i32 %27, ptr %31, align 4
  %32 = sitofp i32 %27 to float
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 104
  %35 = load i32, ptr %34, align 4
  %36 = load ptr, ptr %4, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 8
  store i32 %35, ptr %39, align 4
  %40 = add i32 %35, -1
  %41 = sitofp i32 %40 to float
  %42 = fdiv reassoc ninf nsz float %32, %41
  %43 = load ptr, ptr %4, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 20
  store float %42, ptr %46, align 4
  %47 = load ptr, ptr %context, align 8
  %48 = getelementptr i8, ptr %47, i64 128
  %49 = load i32, ptr %48, align 4
  %50 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %51 = getelementptr i8, ptr %47, i64 132
  %52 = load i32, ptr %51, align 4
  %53 = tail call i32 @llvm.smax.i32(i32 %52, i32 0)
  %54 = load ptr, ptr %4, align 8
  %55 = getelementptr inbounds nuw i8, ptr %54, i64 32872
  %56 = load ptr, ptr %55, align 8
  %57 = getelementptr inbounds nuw i8, ptr %56, i64 4
  store i32 %53, ptr %57, align 4
  %58 = mul i32 %53, %50
  %59 = load ptr, ptr %4, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 32872
  %61 = load ptr, ptr %60, align 8
  store i32 %58, ptr %61, align 4
  ret void
}

define void @remap_accumulate_average_tile_kernel_c764_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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

; Function Attrs: nofree norecurse nounwind memory(readwrite, inaccessiblemem: none)
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
  %20 = getelementptr i8, ptr %19, i64 136
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 140
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.047 = phi i32 [ %402, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  %29 = load i32, ptr %28, align 4
  %30 = sdiv i32 %.047, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.047
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.047, %31
  %35 = and i1 %33, %34
  %.neg6 = sext i1 %35 to i32
  %36 = add i32 %30, %.neg6
  %37 = mul i32 %36, %29
  %38 = add i32 %36, %21
  %39 = mul i32 %29, -1
  %40 = mul i32 %39, %36
  %41 = add i32 %23, %.047
  %42 = add i32 %41, %40
  %43 = getelementptr inbounds nuw i8, ptr %27, i64 8
  %44 = load i32, ptr %43, align 4
  %45 = icmp slt i32 %38, %44
  br i1 %45, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = getelementptr inbounds nuw i8, ptr %27, i64 12
  %47 = load i32, ptr %46, align 4
  %48 = icmp slt i32 %42, %47
  br i1 %48, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %49 = sitofp i32 %42 to float
  %50 = getelementptr inbounds nuw i8, ptr %27, i64 16
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sitofp i32 %38 to float
  %54 = getelementptr inbounds nuw i8, ptr %27, i64 20
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %58 = fptosi float %57 to i32
  %59 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %60 = fptosi float %59 to i32
  %61 = sitofp i32 %58 to float
  %62 = fsub reassoc ninf nsz float %52, %61
  %63 = sitofp i32 %60 to float
  %64 = fsub reassoc ninf nsz float %56, %63
  %65 = tail call i32 @llvm.abs.i32(i32 %58, i1 true)
  %66 = getelementptr inbounds nuw i8, ptr %27, i64 24
  %67 = load i32, ptr %66, align 4
  %68 = sub i32 %65, %67
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = shl nuw i32 %69, 1
  %71 = sub i32 %65, %70
  %72 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %73 = tail call i32 @llvm.smin.i32(i32 %67, i32 %72)
  %74 = tail call i32 @llvm.abs.i32(i32 %60, i1 true)
  %75 = getelementptr inbounds nuw i8, ptr %27, i64 28
  %76 = load i32, ptr %75, align 4
  %77 = sub i32 %74, %76
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = shl nuw i32 %78, 1
  %80 = sub i32 %74, %79
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = tail call i32 @llvm.smin.i32(i32 %76, i32 %81)
  %83 = add i32 %58, 1
  %84 = tail call i32 @llvm.abs.i32(i32 %83, i1 true)
  %85 = sub i32 %84, %67
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = shl nuw i32 %86, 1
  %88 = sub i32 %84, %87
  %89 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %67, i32 %89)
  %91 = add i32 %60, 1
  %92 = tail call i32 @llvm.abs.i32(i32 %91, i1 true)
  %93 = sub i32 %92, %76
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = shl nuw i32 %94, 1
  %96 = sub i32 %92, %95
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = tail call i32 @llvm.smin.i32(i32 %76, i32 %97)
  %99 = load ptr, ptr %0, align 8
  %100 = getelementptr i8, ptr %99, i64 40
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr i8, ptr %99, i64 28
  %103 = load i32, ptr %102, align 4
  %104 = getelementptr i8, ptr %99, i64 32
  %105 = load i32, ptr %104, align 4
  %106 = mul i32 %82, %103
  %107 = add i32 %106, %73
  %108 = mul i32 %107, %105
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %101, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = add i32 %106, %90
  %113 = mul i32 %112, %105
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %101, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = mul i32 %98, %103
  %118 = add i32 %117, %73
  %119 = mul i32 %118, %105
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %101, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %117, %90
  %124 = mul i32 %123, %105
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %101, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = fsub reassoc ninf nsz float 1.000000e+00, %62
  %129 = fmul reassoc ninf nsz float %111, %128
  %130 = fmul reassoc ninf nsz float %116, %62
  %131 = fadd reassoc ninf nsz float %130, %129
  %132 = fmul reassoc ninf nsz float %122, %128
  %133 = fmul reassoc ninf nsz float %127, %62
  %134 = fadd reassoc ninf nsz float %133, %132
  %135 = fsub reassoc ninf nsz float 1.000000e+00, %64
  %136 = fmul reassoc ninf nsz float %131, %135
  %137 = fmul reassoc ninf nsz float %134, %64
  %138 = fadd reassoc ninf nsz float %137, %136
  %139 = add i32 %108, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %101, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %113, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %101, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %119, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %101, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %124, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %101, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %142, %128
  %156 = fmul reassoc ninf nsz float %146, %62
  %157 = fadd reassoc ninf nsz float %156, %155
  %158 = fmul reassoc ninf nsz float %150, %128
  %159 = fmul reassoc ninf nsz float %154, %62
  %160 = fadd reassoc ninf nsz float %159, %158
  %161 = fmul reassoc ninf nsz float %157, %135
  %162 = fmul reassoc ninf nsz float %160, %64
  %163 = fadd reassoc ninf nsz float %162, %161
  %164 = getelementptr i8, ptr %99, i64 120
  %165 = load float, ptr %164, align 4
  %166 = fmul reassoc ninf nsz float %165, %138
  %167 = fadd reassoc ninf nsz float %166, %49
  %168 = getelementptr i8, ptr %99, i64 124
  %169 = load float, ptr %168, align 4
  %170 = fmul reassoc ninf nsz float %163, %169
  %171 = fadd reassoc ninf nsz float %170, %53
  %172 = getelementptr i8, ptr %99, i64 96
  %173 = load i32, ptr %172, align 4
  %174 = getelementptr i8, ptr %99, i64 100
  %175 = load i32, ptr %174, align 4
  %176 = tail call reassoc ninf nsz float @llvm.floor.f32(float %167)
  %177 = fptosi float %176 to i32
  %178 = tail call reassoc ninf nsz float @llvm.floor.f32(float %171)
  %179 = fptosi float %178 to i32
  %180 = sitofp i32 %177 to float
  %181 = fsub reassoc ninf nsz float %167, %180
  %182 = sitofp i32 %179 to float
  %183 = fsub reassoc ninf nsz float %171, %182
  %184 = tail call i32 @llvm.abs.i32(i32 %177, i1 true)
  %185 = add i32 %175, -1
  %186 = sub i32 %184, %185
  %187 = tail call i32 @llvm.smax.i32(i32 %186, i32 0)
  %188 = shl nuw i32 %187, 1
  %189 = sub i32 %184, %188
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %191 = tail call i32 @llvm.smin.i32(i32 %185, i32 %190)
  %192 = tail call i32 @llvm.abs.i32(i32 %179, i1 true)
  %193 = add i32 %173, -1
  %194 = sub i32 %192, %193
  %195 = tail call i32 @llvm.smax.i32(i32 %194, i32 0)
  %196 = shl nuw i32 %195, 1
  %197 = sub i32 %192, %196
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %193, i32 %198)
  %200 = add i32 %177, 1
  %201 = tail call i32 @llvm.abs.i32(i32 %200, i1 true)
  %202 = sub i32 %201, %185
  %203 = tail call i32 @llvm.smax.i32(i32 %202, i32 0)
  %204 = shl nuw i32 %203, 1
  %205 = sub i32 %201, %204
  %206 = tail call i32 @llvm.smax.i32(i32 %205, i32 0)
  %207 = tail call i32 @llvm.smin.i32(i32 %185, i32 %206)
  %208 = add i32 %179, 1
  %209 = tail call i32 @llvm.abs.i32(i32 %208, i1 true)
  %210 = sub i32 %209, %193
  %211 = tail call i32 @llvm.smax.i32(i32 %210, i32 0)
  %212 = shl nuw i32 %211, 1
  %213 = sub i32 %209, %212
  %214 = tail call i32 @llvm.smax.i32(i32 %213, i32 0)
  %215 = tail call i32 @llvm.smin.i32(i32 %193, i32 %214)
  %216 = getelementptr i8, ptr %99, i64 16
  %217 = load ptr, ptr %216, align 8
  %218 = getelementptr i8, ptr %99, i64 4
  %219 = load i32, ptr %218, align 4
  %220 = getelementptr i8, ptr %99, i64 8
  %221 = load i32, ptr %220, align 4
  %222 = mul i32 %199, %219
  %223 = add i32 %222, %191
  %224 = mul i32 %223, %221
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, ptr %217, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = add i32 %222, %207
  %229 = mul i32 %228, %221
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %217, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = mul i32 %215, %219
  %234 = add i32 %233, %191
  %235 = mul i32 %234, %221
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %217, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = add i32 %233, %207
  %240 = mul i32 %239, %221
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %217, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = fsub reassoc ninf nsz float 1.000000e+00, %181
  %245 = fmul reassoc ninf nsz float %227, %244
  %246 = fmul reassoc ninf nsz float %232, %181
  %247 = fadd reassoc ninf nsz float %246, %245
  %248 = fmul reassoc ninf nsz float %238, %244
  %249 = fmul reassoc ninf nsz float %243, %181
  %250 = fadd reassoc ninf nsz float %249, %248
  %251 = fsub reassoc ninf nsz float 1.000000e+00, %183
  %252 = fmul reassoc ninf nsz float %247, %251
  %253 = fmul reassoc ninf nsz float %250, %183
  %254 = fadd reassoc ninf nsz float %253, %252
  %255 = getelementptr i8, ptr %99, i64 64
  %256 = load ptr, ptr %255, align 8
  %257 = getelementptr i8, ptr %99, i64 52
  %258 = load i32, ptr %257, align 4
  %259 = getelementptr i8, ptr %99, i64 56
  %260 = load i32, ptr %259, align 4
  %261 = mul i32 %258, %38
  %262 = sub i32 %261, %37
  %263 = add i32 %41, %262
  %264 = mul i32 %263, %260
  %265 = sext i32 %264 to i64
  %266 = getelementptr float, ptr %256, i64 %265
  %267 = atomicrmw fadd ptr %266, float %254 seq_cst, align 4
  %268 = load ptr, ptr %0, align 8
  %269 = getelementptr i8, ptr %268, i64 88
  %270 = load ptr, ptr %269, align 8
  %271 = getelementptr i8, ptr %268, i64 76
  %272 = load i32, ptr %271, align 4
  %273 = getelementptr i8, ptr %268, i64 80
  %274 = load i32, ptr %273, align 4
  %275 = mul i32 %272, %38
  %276 = sub i32 %275, %37
  %277 = add i32 %41, %276
  %278 = mul i32 %277, %274
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %270, i64 %279
  %281 = atomicrmw fadd ptr %280, float 1.000000e+00 seq_cst, align 4
  %282 = load ptr, ptr %216, align 8
  %283 = load i32, ptr %218, align 4
  %284 = load i32, ptr %220, align 4
  %285 = mul i32 %283, %199
  %286 = add i32 %285, %191
  %287 = mul i32 %286, %284
  %288 = add i32 %287, 1
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %282, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = add i32 %285, %207
  %293 = mul i32 %292, %284
  %294 = add i32 %293, 1
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %282, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = mul i32 %283, %215
  %299 = add i32 %298, %191
  %300 = mul i32 %299, %284
  %301 = add i32 %300, 1
  %302 = sext i32 %301 to i64
  %303 = getelementptr float, ptr %282, i64 %302
  %304 = load float, ptr %303, align 4
  %305 = add i32 %298, %207
  %306 = mul i32 %305, %284
  %307 = add i32 %306, 1
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %282, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = fmul reassoc ninf nsz float %291, %244
  %312 = fmul reassoc ninf nsz float %297, %181
  %313 = fadd reassoc ninf nsz float %312, %311
  %314 = fmul reassoc ninf nsz float %304, %244
  %315 = fmul reassoc ninf nsz float %310, %181
  %316 = fadd reassoc ninf nsz float %315, %314
  %317 = fmul reassoc ninf nsz float %313, %251
  %318 = fmul reassoc ninf nsz float %316, %183
  %319 = fadd reassoc ninf nsz float %318, %317
  %320 = load ptr, ptr %255, align 8
  %321 = load i32, ptr %257, align 4
  %322 = load i32, ptr %259, align 4
  %323 = mul i32 %321, %38
  %324 = sub i32 %323, %37
  %325 = add i32 %41, %324
  %326 = mul i32 %325, %322
  %327 = add i32 %326, 1
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %320, i64 %328
  %330 = atomicrmw fadd ptr %329, float %319 seq_cst, align 4
  %331 = load ptr, ptr %269, align 8
  %332 = load i32, ptr %271, align 4
  %333 = load i32, ptr %273, align 4
  %334 = mul i32 %332, %38
  %335 = sub i32 %334, %37
  %336 = add i32 %41, %335
  %337 = mul i32 %336, %333
  %338 = add i32 %337, 1
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, ptr %331, i64 %339
  %341 = atomicrmw fadd ptr %340, float 1.000000e+00 seq_cst, align 4
  %342 = load ptr, ptr %216, align 8
  %343 = load i32, ptr %218, align 4
  %344 = load i32, ptr %220, align 4
  %345 = mul i32 %343, %199
  %346 = add i32 %345, %191
  %347 = mul i32 %346, %344
  %348 = add i32 %347, 2
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, ptr %342, i64 %349
  %351 = load float, ptr %350, align 4
  %352 = add i32 %345, %207
  %353 = mul i32 %352, %344
  %354 = add i32 %353, 2
  %355 = sext i32 %354 to i64
  %356 = getelementptr float, ptr %342, i64 %355
  %357 = load float, ptr %356, align 4
  %358 = mul i32 %343, %215
  %359 = add i32 %358, %191
  %360 = mul i32 %359, %344
  %361 = add i32 %360, 2
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %342, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = add i32 %358, %207
  %366 = mul i32 %365, %344
  %367 = add i32 %366, 2
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, ptr %342, i64 %368
  %370 = load float, ptr %369, align 4
  %371 = fmul reassoc ninf nsz float %351, %244
  %372 = fmul reassoc ninf nsz float %357, %181
  %373 = fadd reassoc ninf nsz float %372, %371
  %374 = fmul reassoc ninf nsz float %364, %244
  %375 = fmul reassoc ninf nsz float %370, %181
  %376 = fadd reassoc ninf nsz float %375, %374
  %377 = fmul reassoc ninf nsz float %373, %251
  %378 = fmul reassoc ninf nsz float %376, %183
  %379 = fadd reassoc ninf nsz float %378, %377
  %380 = load ptr, ptr %255, align 8
  %381 = load i32, ptr %257, align 4
  %382 = load i32, ptr %259, align 4
  %383 = mul i32 %381, %38
  %384 = sub i32 %383, %37
  %385 = add i32 %41, %384
  %386 = mul i32 %385, %382
  %387 = add i32 %386, 2
  %388 = sext i32 %387 to i64
  %389 = getelementptr float, ptr %380, i64 %388
  %390 = atomicrmw fadd ptr %389, float %379 seq_cst, align 4
  %391 = load ptr, ptr %269, align 8
  %392 = load i32, ptr %271, align 4
  %393 = load i32, ptr %273, align 4
  %394 = mul i32 %392, %38
  %395 = sub i32 %394, %37
  %396 = add i32 %41, %395
  %397 = mul i32 %396, %393
  %398 = add i32 %397, 2
  %399 = sext i32 %398 to i64
  %400 = getelementptr float, ptr %391, i64 %399
  %401 = atomicrmw fadd ptr %400, float 1.000000e+00 seq_cst, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %true_block, %for_loop_body
  %402 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %18, %402
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.30, align 8
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
attributes #1 = { nofree norecurse nounwind memory(readwrite, inaccessiblemem: none) }
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
