; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.32 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @remap_accumulate_average_sum_tile_kernel_c766_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 92
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
  %11 = getelementptr i8, ptr %10, i64 84
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
  %25 = getelementptr i8, ptr %24, i64 88
  %26 = load i32, ptr %25, align 4
  %27 = add i32 %26, -1
  %28 = load ptr, ptr %4, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 28
  store i32 %27, ptr %31, align 4
  %32 = sitofp i32 %27 to float
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 80
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
  %48 = getelementptr i8, ptr %47, i64 104
  %49 = load i32, ptr %48, align 4
  %50 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %51 = getelementptr i8, ptr %47, i64 108
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

define void @remap_accumulate_average_sum_tile_kernel_c766_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 116
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %25 = sub i32 %18, %16
  %26 = add i32 %23, %16
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %lsr.iv14 = phi i32 [ %26, %for_loop_body.preheader ], [ %lsr.iv.next15, %after_if3 ]
  %lsr.iv = phi i32 [ %25, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if3 ]
  %.01013 = phi i32 [ %272, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.01013, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.01013
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.01013, %33
  %37 = and i1 %35, %36
  %.neg12 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg12
  %39 = mul i32 %38, %31
  %40 = add i32 %38, %21
  %41 = mul i32 %31, -1
  %42 = mul i32 %41, %38
  %43 = add i32 %lsr.iv14, %42
  %44 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %45 = load i32, ptr %44, align 4
  %46 = icmp slt i32 %40, %45
  br i1 %46, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %47 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %48 = load i32, ptr %47, align 4
  %49 = icmp slt i32 %43, %48
  br i1 %49, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %50 = sitofp i32 %43 to float
  %51 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %52 = load float, ptr %51, align 4
  %53 = fmul reassoc ninf nsz float %52, %50
  %54 = sitofp i32 %40 to float
  %55 = getelementptr inbounds nuw i8, ptr %29, i64 20
  %56 = load float, ptr %55, align 4
  %57 = fmul reassoc ninf nsz float %56, %54
  %58 = tail call reassoc ninf nsz float @llvm.floor.f32(float %53)
  %59 = fptosi float %58 to i32
  %60 = tail call reassoc ninf nsz float @llvm.floor.f32(float %57)
  %61 = fptosi float %60 to i32
  %62 = sitofp i32 %59 to float
  %63 = fsub reassoc ninf nsz float %53, %62
  %64 = sitofp i32 %61 to float
  %65 = fsub reassoc ninf nsz float %57, %64
  %66 = tail call i32 @llvm.abs.i32(i32 %59, i1 true)
  %67 = getelementptr inbounds nuw i8, ptr %29, i64 24
  %68 = load i32, ptr %67, align 4
  %69 = sub i32 %66, %68
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = shl nuw i32 %70, 1
  %72 = sub i32 %66, %71
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = tail call i32 @llvm.smin.i32(i32 %68, i32 %73)
  %75 = tail call i32 @llvm.abs.i32(i32 %61, i1 true)
  %76 = getelementptr inbounds nuw i8, ptr %29, i64 28
  %77 = load i32, ptr %76, align 4
  %78 = sub i32 %75, %77
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %80 = shl nuw i32 %79, 1
  %81 = sub i32 %75, %80
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %77, i32 %82)
  %84 = add i32 %59, 1
  %85 = tail call i32 @llvm.abs.i32(i32 %84, i1 true)
  %86 = sub i32 %85, %68
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = shl nuw i32 %87, 1
  %89 = sub i32 %85, %88
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %68, i32 %90)
  %92 = add i32 %61, 1
  %93 = tail call i32 @llvm.abs.i32(i32 %92, i1 true)
  %94 = sub i32 %93, %77
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = shl nuw i32 %95, 1
  %97 = sub i32 %93, %96
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = tail call i32 @llvm.smin.i32(i32 %77, i32 %98)
  %100 = load ptr, ptr %0, align 8
  %101 = getelementptr i8, ptr %100, i64 40
  %102 = load ptr, ptr %101, align 8
  %103 = getelementptr i8, ptr %100, i64 28
  %104 = load i32, ptr %103, align 4
  %105 = getelementptr i8, ptr %100, i64 32
  %106 = load i32, ptr %105, align 4
  %107 = mul i32 %83, %104
  %108 = add i32 %107, %74
  %109 = mul i32 %108, %106
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %102, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = add i32 %107, %91
  %114 = mul i32 %113, %106
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %102, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = mul i32 %99, %104
  %119 = add i32 %118, %74
  %120 = mul i32 %119, %106
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %102, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %118, %91
  %125 = mul i32 %124, %106
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %102, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fsub reassoc ninf nsz float 1.000000e+00, %63
  %130 = fmul reassoc ninf nsz float %112, %129
  %131 = fmul reassoc ninf nsz float %117, %63
  %132 = fadd reassoc ninf nsz float %131, %130
  %133 = fmul reassoc ninf nsz float %123, %129
  %134 = fmul reassoc ninf nsz float %128, %63
  %135 = fadd reassoc ninf nsz float %134, %133
  %136 = fsub reassoc ninf nsz float 1.000000e+00, %65
  %137 = fmul reassoc ninf nsz float %132, %136
  %138 = fmul reassoc ninf nsz float %135, %65
  %139 = fadd reassoc ninf nsz float %138, %137
  %140 = add i32 %109, 1
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %102, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = add i32 %114, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %102, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = add i32 %120, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %102, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = add i32 %125, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %102, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = fmul reassoc ninf nsz float %143, %129
  %157 = fmul reassoc ninf nsz float %147, %63
  %158 = fadd reassoc ninf nsz float %157, %156
  %159 = fmul reassoc ninf nsz float %151, %129
  %160 = fmul reassoc ninf nsz float %155, %63
  %161 = fadd reassoc ninf nsz float %160, %159
  %162 = fmul reassoc ninf nsz float %158, %136
  %163 = fmul reassoc ninf nsz float %161, %65
  %164 = fadd reassoc ninf nsz float %163, %162
  %165 = getelementptr i8, ptr %100, i64 96
  %166 = load float, ptr %165, align 4
  %167 = fmul reassoc ninf nsz float %166, %139
  %168 = fadd reassoc ninf nsz float %167, %50
  %169 = getelementptr i8, ptr %100, i64 100
  %170 = load float, ptr %169, align 4
  %171 = fmul reassoc ninf nsz float %164, %170
  %172 = fadd reassoc ninf nsz float %171, %54
  %173 = getelementptr i8, ptr %100, i64 72
  %174 = load i32, ptr %173, align 4
  %175 = getelementptr i8, ptr %100, i64 76
  %176 = load i32, ptr %175, align 4
  %177 = tail call reassoc ninf nsz float @llvm.floor.f32(float %168)
  %178 = fptosi float %177 to i32
  %179 = tail call reassoc ninf nsz float @llvm.floor.f32(float %172)
  %180 = fptosi float %179 to i32
  %181 = sitofp i32 %178 to float
  %182 = fsub reassoc ninf nsz float %168, %181
  %183 = sitofp i32 %180 to float
  %184 = fsub reassoc ninf nsz float %172, %183
  %185 = tail call i32 @llvm.abs.i32(i32 %178, i1 true)
  %186 = add i32 %176, -1
  %187 = sub i32 %185, %186
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = shl nuw i32 %188, 1
  %190 = sub i32 %185, %189
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = tail call i32 @llvm.smin.i32(i32 %186, i32 %191)
  %193 = tail call i32 @llvm.abs.i32(i32 %180, i1 true)
  %194 = add i32 %174, -1
  %195 = sub i32 %193, %194
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = shl nuw i32 %196, 1
  %198 = sub i32 %193, %197
  %199 = tail call i32 @llvm.smax.i32(i32 %198, i32 0)
  %200 = tail call i32 @llvm.smin.i32(i32 %194, i32 %199)
  %201 = add i32 %178, 1
  %202 = tail call i32 @llvm.abs.i32(i32 %201, i1 true)
  %203 = sub i32 %202, %186
  %204 = tail call i32 @llvm.smax.i32(i32 %203, i32 0)
  %205 = shl nuw i32 %204, 1
  %206 = sub i32 %202, %205
  %207 = tail call i32 @llvm.smax.i32(i32 %206, i32 0)
  %208 = tail call i32 @llvm.smin.i32(i32 %186, i32 %207)
  %209 = add i32 %180, 1
  %210 = tail call i32 @llvm.abs.i32(i32 %209, i1 true)
  %211 = sub i32 %210, %194
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = shl nuw i32 %212, 1
  %214 = sub i32 %210, %213
  %215 = tail call i32 @llvm.smax.i32(i32 %214, i32 0)
  %216 = tail call i32 @llvm.smin.i32(i32 %194, i32 %215)
  %217 = getelementptr i8, ptr %100, i64 16
  %218 = load ptr, ptr %217, align 8
  %219 = getelementptr i8, ptr %100, i64 4
  %220 = load i32, ptr %219, align 4
  %221 = getelementptr i8, ptr %100, i64 8
  %222 = load i32, ptr %221, align 4
  %223 = mul i32 %200, %220
  %224 = add i32 %223, %192
  %225 = mul i32 %224, %222
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %218, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = add i32 %223, %208
  %230 = mul i32 %229, %222
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %218, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = mul i32 %216, %220
  %235 = add i32 %234, %192
  %236 = mul i32 %235, %222
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, ptr %218, i64 %237
  %239 = load float, ptr %238, align 4
  %240 = add i32 %234, %208
  %241 = mul i32 %240, %222
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %218, i64 %242
  %244 = load float, ptr %243, align 4
  %245 = fsub reassoc ninf nsz float 1.000000e+00, %182
  %246 = fmul reassoc ninf nsz float %228, %245
  %247 = fmul reassoc ninf nsz float %233, %182
  %248 = fadd reassoc ninf nsz float %247, %246
  %249 = fmul reassoc ninf nsz float %239, %245
  %250 = fmul reassoc ninf nsz float %244, %182
  %251 = fadd reassoc ninf nsz float %250, %249
  %252 = getelementptr i8, ptr %100, i64 64
  %253 = load ptr, ptr %252, align 8
  %254 = getelementptr i8, ptr %100, i64 52
  %255 = load i32, ptr %254, align 4
  %256 = getelementptr i8, ptr %100, i64 56
  %257 = load i32, ptr %256, align 4
  %258 = mul i32 %255, %40
  %259 = sub i32 %258, %39
  %260 = add i32 %lsr.iv14, %259
  %261 = mul i32 %260, %257
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %253, i64 %262
  %264 = load float, ptr %263, align 4
  %265 = fsub reassoc ninf nsz float 1.000000e+00, %184
  %266 = fmul reassoc ninf nsz float %248, %265
  %267 = fmul reassoc ninf nsz float %251, %184
  %268 = fadd reassoc ninf nsz float %267, %266
  %269 = fadd reassoc ninf nsz float %268, %264
  %270 = getelementptr i8, ptr %100, i64 120
  %271 = load i32, ptr %270, align 4
  %.not = icmp eq i32 %271, 0
  br i1 %.not, label %after_if6, label %true_block4

after_if3:                                        ; preds = %after_if12, %true_block, %for_loop_body
  %272 = add nsw i32 %.01013, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %lsr.iv.next15 = add i32 %lsr.iv14, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %273 = getelementptr i8, ptr %100, i64 124
  %274 = load float, ptr %273, align 4
  %275 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %274, float 0x3E45798EE0000000)
  %276 = fdiv reassoc ninf nsz float %269, %275
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.08 = phi float [ %276, %true_block4 ], [ %269, %true_block1 ]
  store float %.08, ptr %263, align 4
  %277 = load ptr, ptr %217, align 8
  %278 = load i32, ptr %219, align 4
  %279 = load i32, ptr %221, align 4
  %280 = mul i32 %278, %200
  %281 = add i32 %280, %192
  %282 = mul i32 %281, %279
  %283 = add i32 %282, 1
  %284 = sext i32 %283 to i64
  %285 = getelementptr float, ptr %277, i64 %284
  %286 = load float, ptr %285, align 4
  %287 = add i32 %280, %208
  %288 = mul i32 %287, %279
  %289 = add i32 %288, 1
  %290 = sext i32 %289 to i64
  %291 = getelementptr float, ptr %277, i64 %290
  %292 = load float, ptr %291, align 4
  %293 = mul i32 %278, %216
  %294 = add i32 %293, %192
  %295 = mul i32 %294, %279
  %296 = add i32 %295, 1
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %277, i64 %297
  %299 = load float, ptr %298, align 4
  %300 = add i32 %293, %208
  %301 = mul i32 %300, %279
  %302 = add i32 %301, 1
  %303 = sext i32 %302 to i64
  %304 = getelementptr float, ptr %277, i64 %303
  %305 = load float, ptr %304, align 4
  %306 = fmul reassoc ninf nsz float %286, %245
  %307 = fmul reassoc ninf nsz float %292, %182
  %308 = fadd reassoc ninf nsz float %307, %306
  %309 = fmul reassoc ninf nsz float %299, %245
  %310 = fmul reassoc ninf nsz float %305, %182
  %311 = fadd reassoc ninf nsz float %310, %309
  %312 = load ptr, ptr %252, align 8
  %313 = load i32, ptr %254, align 4
  %314 = load i32, ptr %256, align 4
  %315 = mul i32 %313, %40
  %316 = sub i32 %315, %39
  %317 = add i32 %lsr.iv14, %316
  %318 = mul i32 %317, %314
  %319 = add i32 %318, 1
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, ptr %312, i64 %320
  %322 = load float, ptr %321, align 4
  %323 = fmul reassoc ninf nsz float %308, %265
  %324 = fmul reassoc ninf nsz float %311, %184
  %325 = fadd reassoc ninf nsz float %324, %323
  %326 = fadd reassoc ninf nsz float %325, %322
  br i1 %.not, label %after_if9, label %true_block7

true_block7:                                      ; preds = %after_if6
  %327 = load ptr, ptr %0, align 8
  %328 = getelementptr i8, ptr %327, i64 124
  %329 = load float, ptr %328, align 4
  %330 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %329, float 0x3E45798EE0000000)
  %331 = fdiv reassoc ninf nsz float %326, %330
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.07 = phi float [ %331, %true_block7 ], [ %326, %after_if6 ]
  store float %.07, ptr %321, align 4
  %332 = load ptr, ptr %217, align 8
  %333 = load i32, ptr %219, align 4
  %334 = load i32, ptr %221, align 4
  %335 = mul i32 %333, %200
  %336 = add i32 %335, %192
  %337 = mul i32 %336, %334
  %338 = add i32 %337, 2
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, ptr %332, i64 %339
  %341 = load float, ptr %340, align 4
  %342 = add i32 %335, %208
  %343 = mul i32 %342, %334
  %344 = add i32 %343, 2
  %345 = sext i32 %344 to i64
  %346 = getelementptr float, ptr %332, i64 %345
  %347 = load float, ptr %346, align 4
  %348 = mul i32 %333, %216
  %349 = add i32 %348, %192
  %350 = mul i32 %349, %334
  %351 = add i32 %350, 2
  %352 = sext i32 %351 to i64
  %353 = getelementptr float, ptr %332, i64 %352
  %354 = load float, ptr %353, align 4
  %355 = add i32 %348, %208
  %356 = mul i32 %355, %334
  %357 = add i32 %356, 2
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, ptr %332, i64 %358
  %360 = load float, ptr %359, align 4
  %361 = fmul reassoc ninf nsz float %341, %245
  %362 = fmul reassoc ninf nsz float %347, %182
  %363 = fadd reassoc ninf nsz float %362, %361
  %364 = fmul reassoc ninf nsz float %354, %245
  %365 = fmul reassoc ninf nsz float %360, %182
  %366 = fadd reassoc ninf nsz float %365, %364
  %367 = load ptr, ptr %252, align 8
  %368 = load i32, ptr %254, align 4
  %369 = load i32, ptr %256, align 4
  %370 = mul i32 %368, %40
  %371 = sub i32 %370, %39
  %372 = add i32 %lsr.iv14, %371
  %373 = mul i32 %372, %369
  %374 = add i32 %373, 2
  %375 = sext i32 %374 to i64
  %376 = getelementptr float, ptr %367, i64 %375
  %377 = load float, ptr %376, align 4
  %378 = fmul reassoc ninf nsz float %363, %265
  %379 = fmul reassoc ninf nsz float %366, %184
  %380 = fadd reassoc ninf nsz float %379, %378
  %381 = fadd reassoc ninf nsz float %380, %377
  br i1 %.not, label %after_if12, label %true_block10

true_block10:                                     ; preds = %after_if9
  %382 = load ptr, ptr %0, align 8
  %383 = getelementptr i8, ptr %382, i64 124
  %384 = load float, ptr %383, align 4
  %385 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %384, float 0x3E45798EE0000000)
  %386 = fdiv reassoc ninf nsz float %381, %385
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %.0 = phi float [ %386, %true_block10 ], [ %381, %after_if9 ]
  store float %.0, ptr %376, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.32, align 8
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
