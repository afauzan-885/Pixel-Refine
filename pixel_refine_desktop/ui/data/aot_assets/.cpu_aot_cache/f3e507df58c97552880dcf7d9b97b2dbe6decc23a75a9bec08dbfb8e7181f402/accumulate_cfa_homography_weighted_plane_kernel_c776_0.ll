; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.42 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_cfa_homography_weighted_plane_kernel_c776_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 100
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 92
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 12
  store i32 %11, ptr %15, align 4
  %16 = sitofp i32 %11 to float
  %17 = fdiv reassoc ninf nsz float %8, %16
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 24
  store float %17, ptr %21, align 4
  %22 = load ptr, ptr %context, align 8
  %23 = getelementptr i8, ptr %22, i64 96
  %24 = load i32, ptr %23, align 4
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 36
  store i32 %24, ptr %28, align 4
  %29 = sitofp i32 %24 to float
  %30 = load ptr, ptr %context, align 8
  %31 = getelementptr i8, ptr %30, i64 88
  %32 = load i32, ptr %31, align 4
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 8
  store i32 %32, ptr %36, align 4
  %37 = sitofp i32 %32 to float
  %38 = fdiv reassoc ninf nsz float %29, %37
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 28
  store float %38, ptr %42, align 4
  %43 = load ptr, ptr %context, align 8
  %44 = getelementptr i8, ptr %43, i64 104
  %45 = load i32, ptr %44, align 4
  %46 = load ptr, ptr %3, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 20
  store i32 %45, ptr %49, align 4
  %50 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %51 = load ptr, ptr %context, align 8
  %52 = getelementptr i8, ptr %51, i64 108
  %53 = load i32, ptr %52, align 4
  %54 = load ptr, ptr %3, align 8
  %55 = getelementptr inbounds nuw i8, ptr %54, i64 32872
  %56 = load ptr, ptr %55, align 8
  %57 = getelementptr inbounds nuw i8, ptr %56, i64 16
  store i32 %53, ptr %57, align 4
  %58 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %59 = load ptr, ptr %3, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 32872
  %61 = load ptr, ptr %60, align 8
  %62 = getelementptr inbounds nuw i8, ptr %61, i64 4
  store i32 %58, ptr %62, align 4
  %63 = mul i32 %58, %50
  %64 = load ptr, ptr %3, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 32872
  %66 = load ptr, ptr %65, align 8
  store i32 %63, ptr %66, align 4
  ret void
}

define void @accumulate_cfa_homography_weighted_plane_kernel_c776_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 116
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = sitofp i32 %23 to float
  %26 = sitofp i32 %21 to float
  %27 = shl i32 %16, 1
  %28 = add i32 %23, %27
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %28, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if3 ]
  %.01024 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %75, %after_if3 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.01024, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.01024
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.01024, %35
  %39 = and i1 %37, %38
  %.neg16 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg16
  %41 = shl i32 %40, 1
  %42 = add i32 %41, %21
  %43 = mul i32 %33, -2
  %44 = mul i32 %43, %40
  %45 = add i32 %lsr.iv, %44
  %46 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %47 = load i32, ptr %46, align 4
  %48 = icmp slt i32 %42, %47
  br i1 %48, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %49 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %50 = load i32, ptr %49, align 4
  %51 = icmp slt i32 %45, %50
  br i1 %51, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %52 = load ptr, ptr %0, align 8
  %53 = getelementptr i8, ptr %52, i64 24
  %54 = load ptr, ptr %53, align 8
  %55 = getelementptr i8, ptr %52, i64 20
  %56 = load i32, ptr %55, align 4
  %57 = sitofp i32 %45 to float
  %58 = sitofp i32 %42 to float
  %59 = shl i32 %56, 1
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %54, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = fmul reassoc ninf nsz float %62, %57
  %64 = getelementptr i8, ptr %61, i64 4
  %65 = load float, ptr %64, align 4
  %66 = fmul reassoc ninf nsz float %65, %58
  %67 = fadd reassoc ninf nsz float %66, %63
  %68 = add i32 %59, 2
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, ptr %54, i64 %69
  %71 = load float, ptr %70, align 4
  %72 = fadd reassoc ninf nsz float %67, %71
  %73 = tail call noundef float @llvm.fabs.f32(float %72)
  %74 = fcmp reassoc ninf nsz ogt float %73, 0x3E45798EE0000000
  br i1 %74, label %true_block4, label %after_if3

after_if3:                                        ; preds = %true_block16, %true_block13, %true_block7, %true_block4, %true_block1, %true_block, %for_loop_body
  %75 = add nsw i32 %.01024, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %75
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %76 = add i32 %56, 2
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, ptr %54, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = add i32 %56, 1
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %54, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = sext i32 %56 to i64
  %85 = getelementptr float, ptr %54, i64 %84
  %86 = load float, ptr %85, align 4
  %87 = getelementptr i8, ptr %54, i64 8
  %88 = load float, ptr %87, align 4
  %89 = getelementptr i8, ptr %54, i64 4
  %90 = load float, ptr %89, align 4
  %91 = load float, ptr %54, align 4
  %92 = fmul reassoc ninf nsz float %86, %57
  %93 = fmul reassoc ninf nsz float %83, %58
  %94 = fadd reassoc ninf nsz float %93, %79
  %95 = fadd reassoc ninf nsz float %94, %92
  %96 = fmul reassoc ninf nsz float %91, %57
  %97 = fmul reassoc ninf nsz float %90, %58
  %98 = fadd reassoc ninf nsz float %97, %88
  %99 = fadd reassoc ninf nsz float %98, %96
  %100 = fdiv reassoc ninf nsz float %99, %72
  %101 = fdiv reassoc ninf nsz float %95, %72
  %102 = fsub reassoc ninf nsz float %100, %25
  %103 = fmul reassoc ninf nsz float %102, 5.000000e-01
  %104 = fsub reassoc ninf nsz float %101, %26
  %105 = fmul reassoc ninf nsz float %104, 5.000000e-01
  %106 = fcmp reassoc ninf nsz ult float %103, 0.000000e+00
  br i1 %106, label %after_if3, label %true_block7

true_block7:                                      ; preds = %true_block4
  %107 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %108 = load i32, ptr %107, align 4
  %109 = add i32 %108, -1
  %110 = sitofp i32 %109 to float
  %111 = fcmp reassoc ninf nsz ugt float %103, %110
  %112 = fcmp reassoc ninf nsz ult float %105, 0.000000e+00
  %or.cond = select i1 %111, i1 true, i1 %112
  br i1 %or.cond, label %after_if3, label %true_block13

true_block13:                                     ; preds = %true_block7
  %113 = getelementptr inbounds nuw i8, ptr %31, i64 20
  %114 = load i32, ptr %113, align 4
  %115 = add i32 %114, -1
  %116 = sitofp i32 %115 to float
  %117 = fcmp reassoc ninf nsz ugt float %105, %116
  br i1 %117, label %after_if3, label %true_block16

true_block16:                                     ; preds = %true_block13
  %118 = tail call reassoc ninf nsz float @llvm.floor.f32(float %103)
  %119 = fptosi float %118 to i32
  %120 = tail call reassoc ninf nsz float @llvm.floor.f32(float %105)
  %121 = fptosi float %120 to i32
  %122 = add i32 %119, 1
  %123 = tail call i32 @llvm.smin.i32(i32 %122, i32 %109)
  %124 = add i32 %121, 1
  %125 = tail call i32 @llvm.smin.i32(i32 %124, i32 %115)
  %126 = sitofp i32 %119 to float
  %127 = fsub reassoc ninf nsz float %103, %126
  %128 = sitofp i32 %121 to float
  %129 = fsub reassoc ninf nsz float %105, %128
  %130 = fsub reassoc ninf nsz float 1.000000e+00, %127
  %131 = getelementptr i8, ptr %52, i64 8
  %132 = load ptr, ptr %131, align 8
  %133 = getelementptr i8, ptr %52, i64 4
  %134 = load i32, ptr %133, align 4
  %135 = mul i32 %134, %121
  %136 = add i32 %135, %119
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %132, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = fmul reassoc ninf nsz float %139, %130
  %141 = add i32 %135, %123
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %132, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = fmul reassoc ninf nsz float %144, %127
  %146 = mul i32 %134, %125
  %147 = add i32 %146, %119
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %132, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fmul reassoc ninf nsz float %150, %130
  %152 = add i32 %146, %123
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %132, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = fmul reassoc ninf nsz float %155, %127
  %reass.add = fadd reassoc ninf nsz float %156, %151
  %reass.add18 = fadd reassoc ninf nsz float %145, %140
  %157 = fsub reassoc ninf nsz float %reass.add, %reass.add18
  %158 = fmul reassoc ninf nsz float %129, %157
  %159 = fadd reassoc ninf nsz float %reass.add18, %158
  %160 = getelementptr inbounds nuw i8, ptr %31, i64 24
  %161 = load float, ptr %160, align 4
  %162 = fmul reassoc ninf nsz float %161, %57
  %163 = getelementptr inbounds nuw i8, ptr %31, i64 28
  %164 = load float, ptr %163, align 4
  %165 = fmul reassoc ninf nsz float %164, %58
  %166 = tail call reassoc ninf nsz float @llvm.floor.f32(float %162)
  %167 = fptosi float %166 to i32
  %168 = tail call i32 @llvm.smax.i32(i32 %167, i32 0)
  %169 = tail call reassoc ninf nsz float @llvm.floor.f32(float %165)
  %170 = fptosi float %169 to i32
  %171 = tail call i32 @llvm.smax.i32(i32 %170, i32 0)
  %172 = add nuw i32 %168, 1
  %173 = getelementptr inbounds nuw i8, ptr %31, i64 32
  %174 = load i32, ptr %173, align 4
  %175 = add i32 %174, -1
  %176 = tail call i32 @llvm.smin.i32(i32 %172, i32 %175)
  %177 = add nuw i32 %171, 1
  %178 = getelementptr inbounds nuw i8, ptr %31, i64 36
  %179 = load i32, ptr %178, align 4
  %180 = add i32 %179, -1
  %181 = tail call i32 @llvm.smin.i32(i32 %177, i32 %180)
  %182 = uitofp nneg i32 %168 to float
  %183 = fsub reassoc ninf nsz float %162, %182
  %184 = uitofp nneg i32 %171 to float
  %185 = fsub reassoc ninf nsz float %165, %184
  %186 = fsub reassoc ninf nsz float 1.000000e+00, %183
  %187 = getelementptr i8, ptr %52, i64 120
  %188 = load i32, ptr %187, align 4
  %189 = getelementptr i8, ptr %52, i64 48
  %190 = load ptr, ptr %189, align 8
  %191 = getelementptr i8, ptr %52, i64 36
  %192 = load i32, ptr %191, align 4
  %193 = getelementptr i8, ptr %52, i64 40
  %194 = load i32, ptr %193, align 4
  %195 = mul i32 %192, %171
  %196 = add i32 %195, %168
  %197 = mul i32 %196, %194
  %198 = add i32 %197, %188
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, ptr %190, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = fmul reassoc ninf nsz float %201, %186
  %203 = add i32 %195, %176
  %204 = mul i32 %203, %194
  %205 = add i32 %204, %188
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %190, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = fmul reassoc ninf nsz float %208, %183
  %210 = mul i32 %181, %192
  %211 = add i32 %210, %168
  %212 = mul i32 %211, %194
  %213 = add i32 %212, %188
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %190, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = fmul reassoc ninf nsz float %216, %186
  %218 = add i32 %210, %176
  %219 = mul i32 %218, %194
  %220 = add i32 %219, %188
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, ptr %190, i64 %221
  %223 = load float, ptr %222, align 4
  %224 = fmul reassoc ninf nsz float %223, %183
  %reass.add20 = fadd reassoc ninf nsz float %224, %217
  %reass.add22 = fadd reassoc ninf nsz float %202, %209
  %225 = fsub reassoc ninf nsz float %reass.add20, %reass.add22
  %226 = fmul reassoc ninf nsz float %185, %225
  %227 = fadd reassoc ninf nsz float %reass.add22, %226
  %228 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %227, float 1.000000e+00)
  %229 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %228, float 0.000000e+00)
  %230 = fmul reassoc ninf nsz float %229, %159
  %231 = getelementptr i8, ptr %52, i64 64
  %232 = load ptr, ptr %231, align 8
  %233 = getelementptr i8, ptr %52, i64 60
  %234 = load i32, ptr %233, align 4
  %235 = mul i32 %234, %42
  %236 = shl i32 %33, 1
  %237 = mul i32 %236, %40
  %238 = sub i32 %235, %237
  %239 = add i32 %lsr.iv, %238
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, ptr %232, i64 %240
  %242 = atomicrmw fadd ptr %241, float %230 seq_cst, align 4
  %243 = load ptr, ptr %0, align 8
  %244 = getelementptr i8, ptr %243, i64 80
  %245 = load ptr, ptr %244, align 8
  %246 = getelementptr i8, ptr %243, i64 76
  %247 = load i32, ptr %246, align 4
  %248 = mul i32 %247, %42
  %249 = sub i32 %248, %237
  %250 = add i32 %lsr.iv, %249
  %251 = sext i32 %250 to i64
  %252 = getelementptr float, ptr %245, i64 %251
  %253 = atomicrmw fadd ptr %252, float %229 seq_cst, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.42, align 8
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
