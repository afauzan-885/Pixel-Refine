; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

@switch.table.function_body.13 = private unnamed_addr constant [5 x float] [float 0x3FC1EB8520000000, float 0x3FC1EB8520000000, float 0x3FDC9EECC0000000, float 0x3FDC9EECC0000000, float 0x3FDC9EECC0000000], align 4

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_compute_tensors_kernel_c506_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 96
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 100
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

define void @_compute_tensors_kernel_c506_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 64
  %22 = getelementptr i8, ptr %20, i64 52
  %23 = getelementptr i8, ptr %20, i64 56
  %24 = getelementptr i8, ptr %20, i64 40
  %25 = getelementptr i8, ptr %20, i64 28
  %26 = getelementptr i8, ptr %20, i64 32
  %27 = getelementptr i8, ptr %20, i64 16
  %28 = getelementptr i8, ptr %20, i64 4
  %29 = getelementptr i8, ptr %20, i64 8
  %30 = getelementptr i8, ptr %20, i64 88
  %31 = getelementptr i8, ptr %20, i64 76
  %32 = getelementptr i8, ptr %20, i64 80
  %33 = sub i32 -1, %16
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if18, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if18 ]
  %.01034 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %349, %after_if18 ]
  %34 = load ptr, ptr %3, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 4
  %38 = load i32, ptr %37, align 4
  %39 = sdiv i32 %.01034, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.01034
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.01034, %40
  %44 = and i1 %42, %43
  %.neg13 = sext i1 %44 to i32
  %45 = add i32 %39, %.neg13
  %46 = mul i32 %45, %38
  %47 = mul i32 %38, -1
  %48 = mul i32 %47, %45
  %49 = add i32 %.01034, %48
  %50 = load ptr, ptr %21, align 8
  %51 = load i32, ptr %22, align 4
  %52 = load i32, ptr %23, align 4
  %53 = sub i32 %51, %38
  %54 = mul i32 %53, %45
  %55 = add i32 %.01034, %54
  %56 = mul i32 %55, %52
  %57 = sext i32 %56 to i64
  %58 = getelementptr float, ptr %50, i64 %57
  %59 = load float, ptr %58, align 4
  %60 = add i32 %56, 1
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, ptr %50, i64 %61
  %63 = load float, ptr %62, align 4
  %64 = sitofp i32 %49 to float
  %65 = fadd reassoc ninf nsz float %59, %64
  %66 = sitofp i32 %45 to float
  %67 = fadd reassoc ninf nsz float %63, %66
  %68 = tail call reassoc ninf nsz float @llvm.floor.f32(float %65)
  %69 = fptosi float %68 to i32
  %70 = tail call reassoc ninf nsz float @llvm.floor.f32(float %67)
  %71 = fptosi float %70 to i32
  %72 = sitofp i32 %69 to float
  %73 = fsub reassoc ninf nsz float %65, %72
  %74 = sitofp i32 %71 to float
  %75 = fsub reassoc ninf nsz float %67, %74
  %76 = tail call i32 @llvm.abs.i32(i32 %69, i1 true)
  %77 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %78 = load i32, ptr %77, align 4
  %79 = add i32 %78, -1
  %80 = sub i32 %76, %79
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = shl nuw i32 %81, 1
  %83 = sub i32 %76, %82
  %84 = tail call i32 @llvm.smax.i32(i32 %83, i32 0)
  %85 = tail call i32 @llvm.smin.i32(i32 %79, i32 %84)
  %86 = tail call i32 @llvm.abs.i32(i32 %71, i1 true)
  %87 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %88 = load i32, ptr %87, align 4
  %89 = add i32 %88, -1
  %90 = sub i32 %86, %89
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %92 = shl nuw i32 %91, 1
  %93 = sub i32 %86, %92
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %89, i32 %94)
  %96 = add i32 %69, 1
  %97 = tail call i32 @llvm.abs.i32(i32 %96, i1 true)
  %98 = sub i32 %97, %79
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %100 = shl nuw i32 %99, 1
  %101 = sub i32 %97, %100
  %102 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %103 = tail call i32 @llvm.smin.i32(i32 %79, i32 %102)
  %104 = add i32 %71, 1
  %105 = tail call i32 @llvm.abs.i32(i32 %104, i1 true)
  %106 = sub i32 %105, %89
  %107 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %108 = shl nuw i32 %107, 1
  %109 = sub i32 %105, %108
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = tail call i32 @llvm.smin.i32(i32 %89, i32 %110)
  %112 = fsub reassoc ninf nsz float 1.000000e+00, %73
  %113 = fsub reassoc ninf nsz float 1.000000e+00, %75
  %114 = fmul reassoc ninf nsz float %112, %113
  %115 = fmul reassoc ninf nsz float %73, %113
  %116 = fmul reassoc ninf nsz float %112, %75
  %117 = fmul reassoc ninf nsz float %73, %75
  %118 = load ptr, ptr %24, align 8
  %119 = load i32, ptr %25, align 4
  %120 = load i32, ptr %26, align 4
  %121 = mul i32 %95, %119
  %122 = add i32 %85, %121
  %123 = mul i32 %122, %120
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %118, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %103, %121
  %128 = mul i32 %127, %120
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %118, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = mul i32 %111, %119
  %133 = add i32 %132, %85
  %134 = mul i32 %133, %120
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %118, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = add i32 %103, %132
  %139 = mul i32 %138, %120
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %118, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %123, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %118, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %128, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %118, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %134, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %118, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %139, 1
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %118, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %123, 2
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %118, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = fmul reassoc ninf nsz float %162, %114
  %164 = add i32 %128, 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %118, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = fmul reassoc ninf nsz float %167, %115
  %169 = fadd reassoc ninf nsz float %168, %163
  %170 = add i32 %134, 2
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %118, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fmul reassoc ninf nsz float %173, %116
  %175 = fadd reassoc ninf nsz float %169, %174
  %176 = add i32 %139, 2
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %118, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = fmul reassoc ninf nsz float %179, %117
  %181 = fadd reassoc ninf nsz float %175, %180
  %182 = add i32 %123, 3
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %118, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = fmul reassoc ninf nsz float %185, %114
  %187 = add i32 %128, 3
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, ptr %118, i64 %188
  %190 = load float, ptr %189, align 4
  %191 = fmul reassoc ninf nsz float %190, %115
  %192 = fadd reassoc ninf nsz float %191, %186
  %193 = add i32 %134, 3
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %118, i64 %194
  %196 = load float, ptr %195, align 4
  %197 = fmul reassoc ninf nsz float %196, %116
  %198 = fadd reassoc ninf nsz float %192, %197
  %199 = add i32 %139, 3
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, ptr %118, i64 %200
  %202 = load float, ptr %201, align 4
  %203 = fmul reassoc ninf nsz float %202, %117
  %204 = fadd reassoc ninf nsz float %198, %203
  %205 = add i32 %123, 4
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %118, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = fmul reassoc ninf nsz float %208, %114
  %210 = add i32 %128, 4
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %118, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fmul reassoc ninf nsz float %213, %115
  %215 = fadd reassoc ninf nsz float %214, %209
  %216 = add i32 %134, 4
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %118, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %219, %116
  %221 = fadd reassoc ninf nsz float %215, %220
  %222 = add i32 %139, 4
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %118, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = fmul reassoc ninf nsz float %225, %117
  %227 = fadd reassoc ninf nsz float %221, %226
  %228 = load ptr, ptr %27, align 8
  %229 = load i32, ptr %28, align 4
  %230 = load i32, ptr %29, align 4
  %231 = sub i32 %229, %38
  %232 = mul i32 %231, %45
  %233 = add i32 %.01034, %232
  %234 = mul i32 %233, %230
  %235 = add i32 %234, 2
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %228, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = fadd reassoc ninf nsz float %181, %238
  %240 = fmul reassoc ninf nsz float %239, 5.000000e-01
  %241 = add i32 %234, 3
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %228, i64 %242
  %244 = load float, ptr %243, align 4
  %245 = fadd reassoc ninf nsz float %204, %244
  %246 = fmul reassoc ninf nsz float %245, 5.000000e-01
  %247 = add i32 %234, 4
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %228, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = fadd reassoc ninf nsz float %227, %250
  %252 = fmul reassoc ninf nsz float %251, 2.500000e-01
  %253 = sext i32 %234 to i64
  %254 = getelementptr float, ptr %228, i64 %253
  %255 = load float, ptr %254, align 4
  %.neg14 = fmul reassoc ninf nsz float %142, %117
  %.neg15 = fmul reassoc ninf nsz float %116, %137
  %.neg16 = fmul reassoc ninf nsz float %115, %131
  %.neg17 = fmul reassoc ninf nsz float %114, %126
  %reass.add = fadd reassoc ninf nsz float %.neg16, %.neg14
  %reass.add28 = fadd reassoc ninf nsz float %reass.add, %.neg17
  %reass.add29 = fadd reassoc ninf nsz float %reass.add28, %.neg15
  %256 = fsub reassoc ninf nsz float %255, %reass.add29
  %257 = fmul reassoc ninf nsz float %256, 5.000000e-01
  %258 = add i32 %234, 1
  %259 = sext i32 %258 to i64
  %260 = getelementptr float, ptr %228, i64 %259
  %261 = load float, ptr %260, align 4
  %.neg21 = fmul reassoc ninf nsz float %146, %114
  %.neg22 = fmul reassoc ninf nsz float %150, %115
  %.neg24 = fmul reassoc ninf nsz float %154, %116
  %.neg26 = fmul reassoc ninf nsz float %158, %117
  %reass.add30 = fadd reassoc ninf nsz float %.neg22, %.neg21
  %reass.add31 = fadd reassoc ninf nsz float %reass.add30, %.neg24
  %reass.add32 = fadd reassoc ninf nsz float %reass.add31, %.neg26
  %262 = fsub reassoc ninf nsz float %261, %reass.add32
  %263 = fmul reassoc ninf nsz float %262, 5.000000e-01
  %264 = fmul reassoc ninf nsz float %240, %63
  %265 = fmul reassoc ninf nsz float %252, %59
  %266 = fadd reassoc ninf nsz float %265, %264
  %267 = fadd reassoc ninf nsz float %266, %257
  %268 = fmul reassoc ninf nsz float %252, %63
  %269 = fmul reassoc ninf nsz float %246, %59
  %270 = fadd reassoc ninf nsz float %268, %269
  %271 = fadd reassoc ninf nsz float %270, %263
  %272 = sub i32 %89, %45
  %273 = tail call i32 @llvm.smin.i32(i32 %45, i32 %272)
  %274 = add i32 %78, %46
  %275 = add i32 %lsr.iv, %274
  %276 = tail call i32 @llvm.smin.i32(i32 %49, i32 %275)
  %277 = icmp ult i32 %273, 5
  br i1 %277, label %switch.lookup, label %after_if

after_for.loopexit:                               ; preds = %after_if18
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

switch.lookup:                                    ; preds = %for_loop_body
  %278 = zext nneg i32 %273 to i64
  %switch.gep = getelementptr inbounds nuw [5 x float], ptr @switch.table.function_body.13, i64 0, i64 %278
  %switch.load = load float, ptr %switch.gep, align 4
  br label %after_if

after_if:                                         ; preds = %switch.lookup, %for_loop_body
  %.09 = phi float [ 1.000000e+00, %for_loop_body ], [ %switch.load, %switch.lookup ]
  %279 = icmp ult i32 %276, 5
  br i1 %279, label %switch.lookup35, label %after_if18

switch.lookup35:                                  ; preds = %after_if
  %280 = zext nneg i32 %276 to i64
  %switch.gep36 = getelementptr inbounds nuw [5 x float], ptr @switch.table.function_body.13, i64 0, i64 %280
  %switch.load37 = load float, ptr %switch.gep36, align 4
  br label %after_if18

after_if18:                                       ; preds = %switch.lookup35, %after_if
  %.08 = phi float [ 1.000000e+00, %after_if ], [ %switch.load37, %switch.lookup35 ]
  %281 = fmul reassoc ninf nsz float %.08, %.09
  %282 = fmul reassoc ninf nsz float %281, %267
  %283 = fmul reassoc ninf nsz float %281, %271
  %284 = fmul reassoc ninf nsz float %281, %240
  %285 = fmul reassoc ninf nsz float %281, %246
  %286 = fmul reassoc ninf nsz float %281, %252
  %287 = fmul reassoc ninf nsz float %284, %284
  %288 = fmul reassoc ninf nsz float %286, %286
  %289 = fadd reassoc ninf nsz float %287, %288
  %290 = load ptr, ptr %30, align 8
  %291 = load i32, ptr %31, align 4
  %292 = load i32, ptr %32, align 4
  %293 = sub i32 %291, %38
  %294 = mul i32 %293, %45
  %295 = add i32 %.01034, %294
  %296 = mul i32 %295, %292
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %290, i64 %297
  store float %289, ptr %298, align 4
  %299 = fadd reassoc ninf nsz float %284, %285
  %300 = fmul reassoc ninf nsz float %299, %286
  %301 = load ptr, ptr %30, align 8
  %302 = load i32, ptr %31, align 4
  %303 = load i32, ptr %32, align 4
  %304 = sub i32 %302, %38
  %305 = mul i32 %304, %45
  %306 = add i32 %.01034, %305
  %307 = mul i32 %306, %303
  %308 = add i32 %307, 1
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, ptr %301, i64 %309
  store float %300, ptr %310, align 4
  %311 = fmul reassoc ninf nsz float %285, %285
  %312 = fadd reassoc ninf nsz float %311, %288
  %313 = load ptr, ptr %30, align 8
  %314 = load i32, ptr %31, align 4
  %315 = load i32, ptr %32, align 4
  %316 = sub i32 %314, %38
  %317 = mul i32 %316, %45
  %318 = add i32 %.01034, %317
  %319 = mul i32 %318, %315
  %320 = add i32 %319, 2
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %313, i64 %321
  store float %312, ptr %322, align 4
  %323 = fmul reassoc ninf nsz float %284, %282
  %324 = fmul reassoc ninf nsz float %286, %283
  %325 = fadd reassoc ninf nsz float %323, %324
  %326 = load ptr, ptr %30, align 8
  %327 = load i32, ptr %31, align 4
  %328 = load i32, ptr %32, align 4
  %329 = sub i32 %327, %38
  %330 = mul i32 %329, %45
  %331 = add i32 %.01034, %330
  %332 = mul i32 %331, %328
  %333 = add i32 %332, 3
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, ptr %326, i64 %334
  store float %325, ptr %335, align 4
  %336 = fmul reassoc ninf nsz float %286, %282
  %337 = fmul reassoc ninf nsz float %285, %283
  %338 = fadd reassoc ninf nsz float %336, %337
  %339 = load ptr, ptr %30, align 8
  %340 = load i32, ptr %31, align 4
  %341 = load i32, ptr %32, align 4
  %342 = sub i32 %340, %38
  %343 = mul i32 %342, %45
  %344 = add i32 %.01034, %343
  %345 = mul i32 %344, %341
  %346 = add i32 %345, 4
  %347 = sext i32 %346 to i64
  %348 = getelementptr float, ptr %339, i64 %347
  store float %338, ptr %348, align 4
  %349 = add nsw i32 %.01034, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %18, %349
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
