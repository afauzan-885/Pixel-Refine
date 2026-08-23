; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_lk_grid_track_kernel_c490_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 12
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 8
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 56
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 60
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

define void @_lk_grid_track_kernel_c490_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 108
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 104
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 112
  %25 = load i32, ptr %24, align 4
  %26 = tail call i32 @llvm.smax.i32(i32 %23, i32 2)
  %27 = add i32 %25, %23
  %28 = shl i32 %27, 1
  %29 = uitofp nneg i32 %26 to float
  %30 = sitofp i32 %28 to float
  %invariant.op = sub i32 %21, %25
  %31 = icmp slt i32 %16, %18
  br i1 %31, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %neg = sub i32 0, %25
  %32 = shl i32 %25, 1
  %33 = getelementptr i8, ptr %19, i64 72
  %34 = getelementptr i8, ptr %19, i64 60
  %35 = getelementptr i8, ptr %19, i64 64
  %36 = getelementptr i8, ptr %19, i64 96
  %37 = getelementptr i8, ptr %19, i64 84
  %38 = getelementptr i8, ptr %19, i64 88
  %39 = add i32 %25, 1
  %40 = tail call i32 @llvm.smax.i32(i32 %neg, i32 %39)
  %41 = add i32 %40, %25
  %42 = mul i32 %41, %41
  %43 = icmp sgt i32 %42, 0
  %44 = icmp slt i32 %41, 0
  %45 = or disjoint i32 %32, 1
  %46 = mul i32 %45, %45
  %47 = sitofp i32 %46 to float
  %neg19 = fneg reassoc ninf nsz float %29
  %neg20 = fneg reassoc ninf nsz float %30
  %48 = mul i32 %23, %23
  %49 = sitofp i32 %48 to float
  %50 = fmul reassoc ninf nsz float %49, 0x3FC99999A0000000
  %51 = fmul reassoc ninf nsz float %49, 0x3FA47AE140000000
  %min.iters.check = icmp ult i32 %42, 8
  %n.vec = and i32 %42, 2147483640
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %41, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert168 = insertelement <8 x i1> poison, i1 %44, i64 0
  %broadcast.splat169 = shufflevector <8 x i1> %broadcast.splatinsert168, <8 x i1> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert170 = insertelement <8 x i32> poison, i32 %25, i64 0
  %broadcast.splat171 = shufflevector <8 x i32> %broadcast.splatinsert170, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %42, %n.vec
  %52 = sub i32 0, %41
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.065104 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %238, %after_if3 ]
  %53 = load ptr, ptr %3, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 32872
  %55 = load ptr, ptr %54, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 4
  %57 = load i32, ptr %56, align 4
  %58 = sdiv i32 %.065104, %57
  %59 = mul i32 %58, %57
  %60 = xor i32 %57, %.065104
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %59, %.065104
  %63 = and i1 %61, %62
  %.neg72 = sext i1 %63 to i32
  %64 = add i32 %58, %.neg72
  %65 = mul i32 %64, %57
  %66 = sub i32 %.065104, %65
  %67 = mul i32 %66, %23
  %68 = add i32 %67, %21
  %69 = sitofp i32 %68 to float
  %70 = mul i32 %64, %23
  %71 = add i32 %70, %21
  %72 = sitofp i32 %71 to float
  %73 = load ptr, ptr %33, align 8
  %74 = load i32, ptr %34, align 4
  %75 = load i32, ptr %35, align 4
  %76 = mul i32 %64, %74
  %77 = add i32 %66, %76
  %78 = mul i32 %77, %75
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, ptr %73, i64 %79
  store float 0.000000e+00, ptr %80, align 4
  %81 = load ptr, ptr %33, align 8
  %82 = load i32, ptr %34, align 4
  %83 = load i32, ptr %35, align 4
  %84 = mul i32 %82, %64
  %85 = add i32 %84, %66
  %86 = mul i32 %85, %83
  %87 = add i32 %86, 1
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %81, i64 %88
  store float 0.000000e+00, ptr %89, align 4
  %90 = load ptr, ptr %33, align 8
  %91 = load i32, ptr %34, align 4
  %92 = load i32, ptr %35, align 4
  %93 = mul i32 %91, %64
  %94 = add i32 %93, %66
  %95 = mul i32 %94, %92
  %96 = add i32 %95, 2
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %90, i64 %97
  store float 0.000000e+00, ptr %98, align 4
  %99 = load ptr, ptr %36, align 8
  %100 = load i32, ptr %37, align 4
  %101 = load i32, ptr %38, align 4
  %102 = mul i32 %100, %64
  %103 = add i32 %102, %66
  %104 = mul i32 %103, %101
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %99, i64 %105
  store float 0.000000e+00, ptr %106, align 4
  %107 = load ptr, ptr %36, align 8
  %108 = load i32, ptr %37, align 4
  %109 = load i32, ptr %38, align 4
  %110 = mul i32 %108, %64
  %111 = add i32 %110, %66
  %112 = mul i32 %111, %109
  %113 = add i32 %112, 1
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %107, i64 %114
  store float 0.000000e+00, ptr %115, align 4
  %116 = load ptr, ptr %36, align 8
  %117 = load i32, ptr %37, align 4
  %118 = load i32, ptr %38, align 4
  %119 = mul i32 %117, %64
  %120 = add i32 %119, %66
  %121 = mul i32 %120, %118
  %122 = add i32 %121, 2
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, ptr %116, i64 %123
  store float 2.000000e+00, ptr %124, align 4
  %125 = load ptr, ptr %36, align 8
  %126 = load i32, ptr %37, align 4
  %127 = load i32, ptr %38, align 4
  %128 = mul i32 %126, %64
  %129 = add i32 %128, %66
  %130 = mul i32 %129, %127
  %131 = add i32 %130, 3
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %125, i64 %132
  store float 0.000000e+00, ptr %133, align 4
  %134 = load ptr, ptr %3, align 8
  %135 = getelementptr inbounds nuw i8, ptr %134, i64 32872
  %136 = load ptr, ptr %135, align 8
  %137 = getelementptr inbounds nuw i8, ptr %136, i64 8
  %138 = load i32, ptr %137, align 4
  %139 = sub i32 %138, %21
  %140 = sitofp i32 %139 to float
  %141 = fcmp reassoc ninf nsz olt float %69, %140
  br i1 %141, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %142 = getelementptr inbounds nuw i8, ptr %136, i64 12
  %143 = load i32, ptr %142, align 4
  %144 = sub i32 %143, %21
  %145 = sitofp i32 %144 to float
  %146 = fcmp reassoc ninf nsz olt float %72, %145
  br i1 %146, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %147 = fptosi float %69 to i32
  %148 = add i32 %138, -1
  %149 = tail call i32 @llvm.smin.i32(i32 %147, i32 %148)
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = fptosi float %72 to i32
  %152 = add i32 %143, -1
  %153 = tail call i32 @llvm.smin.i32(i32 %151, i32 %152)
  %154 = tail call i32 @llvm.smax.i32(i32 %153, i32 0)
  %155 = add nuw i32 %150, 1
  %156 = tail call i32 @llvm.smin.i32(i32 %155, i32 %148)
  %157 = tail call i32 @llvm.smax.i32(i32 %156, i32 0)
  %158 = add nuw i32 %154, 1
  %159 = tail call i32 @llvm.smin.i32(i32 %158, i32 %152)
  %160 = tail call i32 @llvm.smax.i32(i32 %159, i32 0)
  %161 = uitofp nneg i32 %150 to float
  %162 = fsub reassoc ninf nsz float %69, %161
  %163 = uitofp nneg i32 %154 to float
  %164 = fsub reassoc ninf nsz float %72, %163
  %165 = load ptr, ptr %0, align 8
  %166 = getelementptr i8, ptr %165, i64 48
  %167 = load ptr, ptr %166, align 8
  %168 = getelementptr i8, ptr %165, i64 36
  %169 = load i32, ptr %168, align 4
  %170 = getelementptr i8, ptr %165, i64 40
  %171 = load i32, ptr %170, align 4
  %172 = mul i32 %169, %154
  %173 = add i32 %172, %150
  %174 = mul i32 %173, %171
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %167, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = add i32 %172, %157
  %179 = mul i32 %178, %171
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %167, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = mul i32 %169, %160
  %184 = add i32 %183, %150
  %185 = mul i32 %184, %171
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %167, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = add i32 %183, %157
  %190 = mul i32 %189, %171
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %167, i64 %191
  %193 = load float, ptr %192, align 4
  %194 = fsub reassoc ninf nsz float 1.000000e+00, %164
  %195 = fsub reassoc ninf nsz float 1.000000e+00, %162
  %196 = fmul reassoc ninf nsz float %177, %195
  %197 = fmul reassoc ninf nsz float %182, %162
  %198 = fadd reassoc ninf nsz float %197, %196
  %199 = fmul reassoc ninf nsz float %198, %194
  %200 = fmul reassoc ninf nsz float %188, %195
  %201 = fmul reassoc ninf nsz float %193, %162
  %202 = fadd reassoc ninf nsz float %201, %200
  %203 = fmul reassoc ninf nsz float %202, %164
  %204 = fadd reassoc ninf nsz float %203, %199
  %205 = add i32 %174, 1
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %167, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = add i32 %179, 1
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, ptr %167, i64 %210
  %212 = load float, ptr %211, align 4
  %213 = add i32 %185, 1
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %167, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = add i32 %190, 1
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %167, i64 %218
  %220 = load float, ptr %219, align 4
  %221 = fmul reassoc ninf nsz float %208, %195
  %222 = fmul reassoc ninf nsz float %212, %162
  %223 = fadd reassoc ninf nsz float %222, %221
  %224 = fmul reassoc ninf nsz float %223, %194
  %225 = fmul reassoc ninf nsz float %216, %195
  %226 = fmul reassoc ninf nsz float %220, %162
  %227 = fadd reassoc ninf nsz float %226, %225
  %228 = fmul reassoc ninf nsz float %227, %164
  %229 = fadd reassoc ninf nsz float %228, %224
  %230 = getelementptr i8, ptr %165, i64 116
  %231 = load i32, ptr %230, align 4
  %232 = icmp sgt i32 %231, 0
  br i1 %232, label %for_loop_body4.lr.ph, label %true_block24

for_loop_body4.lr.ph:                             ; preds = %true_block1
  %.neg77.reass = add i32 %67, %invariant.op
  %233 = getelementptr i8, ptr %165, i64 8
  %234 = getelementptr i8, ptr %165, i64 4
  %235 = getelementptr i8, ptr %165, i64 24
  %236 = getelementptr i8, ptr %165, i64 20
  %237 = getelementptr i8, ptr %165, i64 120
  %broadcast.splatinsert172 = insertelement <8 x i32> poison, i32 %71, i64 0
  %broadcast.splat173 = shufflevector <8 x i32> %broadcast.splatinsert172, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert174 = insertelement <8 x i32> poison, i32 %.neg77.reass, i64 0
  %broadcast.splat175 = shufflevector <8 x i32> %broadcast.splatinsert174, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert180 = insertelement <8 x i32> poison, i32 %152, i64 0
  %broadcast.splat181 = shufflevector <8 x i32> %broadcast.splatinsert180, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert182 = insertelement <8 x i32> poison, i32 %148, i64 0
  %broadcast.splat183 = shufflevector <8 x i32> %broadcast.splatinsert182, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %for_loop_body4.outer

after_if3.loopexit:                               ; preds = %after_if10.thread
  br label %after_if3

after_if3:                                        ; preds = %517, %after_for6, %after_if3.loopexit, %true_block, %for_loop_body
  %238 = add nsw i32 %.065104, 1
  %exitcond111.not = icmp eq i32 %238, %18
  br i1 %exitcond111.not, label %after_for.loopexit, label %for_loop_body

for_loop_body4:                                   ; preds = %for_loop_body4.outer, %after_if10
  %.05198 = phi i32 [ %359, %after_if10 ], [ %.05198.ph, %for_loop_body4.outer ]
  %.05297 = phi float [ %.153, %after_if10 ], [ %.05297.ph, %for_loop_body4.outer ]
  %.05496 = phi float [ %.155, %after_if10 ], [ %.05496.ph, %for_loop_body4.outer ]
  %.05695 = phi i32 [ %.157, %after_if10 ], [ %.05695.ph, %for_loop_body4.outer ]
  %.06093 = phi float [ %.161, %after_if10 ], [ %.06093.ph, %for_loop_body4.outer ]
  %.06292 = phi float [ %.163, %after_if10 ], [ %.06292.ph, %for_loop_body4.outer ]
  %239 = icmp eq i32 %.05695, 1
  br i1 %239, label %true_block8, label %after_if10

after_for6:                                       ; preds = %after_if10
  br i1 %.not, label %after_if3, label %true_block24

true_block8:                                      ; preds = %for_loop_body4
  br i1 %43, label %for_loop_body11.lr.ph, label %after_for13

for_loop_body11.lr.ph:                            ; preds = %true_block8
  %240 = load ptr, ptr %233, align 8
  %241 = load i32, ptr %234, align 4
  %242 = load ptr, ptr %235, align 8
  %243 = load i32, ptr %236, align 4
  br i1 %min.iters.check, label %for_loop_body11.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body11.lr.ph
  %broadcast.splatinsert176 = insertelement <8 x float> poison, float %.06292, i64 0
  %broadcast.splat177 = shufflevector <8 x float> %broadcast.splatinsert176, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert178 = insertelement <8 x float> poison, float %.06093, i64 0
  %broadcast.splat179 = shufflevector <8 x float> %broadcast.splatinsert178, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert184 = insertelement <8 x i32> poison, i32 %241, i64 0
  %broadcast.splat185 = shufflevector <8 x i32> %broadcast.splatinsert184, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert189 = insertelement <8 x i32> poison, i32 %243, i64 0
  %broadcast.splat190 = shufflevector <8 x i32> %broadcast.splatinsert189, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %351, %vector.body ]
  %vec.phi163 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %349, %vector.body ]
  %vec.phi164 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %347, %vector.body ]
  %vec.phi165 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %345, %vector.body ]
  %vec.phi166 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %343, %vector.body ]
  %vec.phi167 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %341, %vector.body ]
  %244 = sdiv <8 x i32> %vec.ind, %broadcast.splat
  %245 = mul <8 x i32> %244, %broadcast.splat
  %246 = icmp ne <8 x i32> %245, %vec.ind
  %247 = and <8 x i1> %broadcast.splat169, %246
  %248 = sext <8 x i1> %247 to <8 x i32>
  %249 = add <8 x i32> %244, %248
  %250 = sub <8 x i32> %249, %broadcast.splat171
  %251 = mul <8 x i32> %broadcast.splat, %249
  %252 = add <8 x i32> %250, %broadcast.splat173
  %253 = add <8 x i32> %broadcast.splat175, %vec.ind
  %254 = sub <8 x i32> %253, %251
  %255 = sitofp <8 x i32> %252 to <8 x float>
  %256 = sitofp <8 x i32> %254 to <8 x float>
  %257 = fadd reassoc ninf nsz <8 x float> %broadcast.splat177, %256
  %258 = fadd reassoc ninf nsz <8 x float> %broadcast.splat179, %255
  %259 = add <8 x i32> %254, splat (i32 1)
  %260 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %252, <8 x i32> %broadcast.splat181)
  %261 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %260, <8 x i32> zeroinitializer)
  %262 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %259, <8 x i32> %broadcast.splat183)
  %263 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %262, <8 x i32> zeroinitializer)
  %264 = add <8 x i32> %254, splat (i32 -1)
  %265 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %264, <8 x i32> %broadcast.splat183)
  %266 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %265, <8 x i32> zeroinitializer)
  %267 = mul <8 x i32> %261, %broadcast.splat185
  %268 = add <8 x i32> %263, %267
  %269 = sext <8 x i32> %268 to <8 x i64>
  %270 = getelementptr float, ptr %240, <8 x i64> %269
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %270, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %271 = add <8 x i32> %266, %267
  %272 = sext <8 x i32> %271 to <8 x i64>
  %273 = getelementptr float, ptr %240, <8 x i64> %272
  %wide.masked.gather186 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %273, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %274 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather186
  %275 = fmul reassoc ninf nsz <8 x float> %274, splat (float 5.000000e-01)
  %276 = add <8 x i32> %252, splat (i32 1)
  %277 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %276, <8 x i32> %broadcast.splat181)
  %278 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %277, <8 x i32> zeroinitializer)
  %279 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %254, <8 x i32> %broadcast.splat183)
  %280 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %279, <8 x i32> zeroinitializer)
  %281 = add <8 x i32> %252, splat (i32 -1)
  %282 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %281, <8 x i32> %broadcast.splat181)
  %283 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %282, <8 x i32> zeroinitializer)
  %284 = mul <8 x i32> %278, %broadcast.splat185
  %285 = add <8 x i32> %284, %280
  %286 = sext <8 x i32> %285 to <8 x i64>
  %287 = getelementptr float, ptr %240, <8 x i64> %286
  %wide.masked.gather187 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %287, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %288 = mul <8 x i32> %283, %broadcast.splat185
  %289 = add <8 x i32> %288, %280
  %290 = sext <8 x i32> %289 to <8 x i64>
  %291 = getelementptr float, ptr %240, <8 x i64> %290
  %wide.masked.gather188 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %291, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %292 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather187, %wide.masked.gather188
  %293 = fmul reassoc ninf nsz <8 x float> %292, splat (float 5.000000e-01)
  %294 = tail call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %257)
  %295 = fptosi <8 x float> %294 to <8 x i32>
  %296 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %295, <8 x i32> %broadcast.splat183)
  %297 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %296, <8 x i32> zeroinitializer)
  %298 = tail call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %258)
  %299 = fptosi <8 x float> %298 to <8 x i32>
  %300 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %299, <8 x i32> %broadcast.splat181)
  %301 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %300, <8 x i32> zeroinitializer)
  %302 = add nuw <8 x i32> %297, splat (i32 1)
  %303 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %302, <8 x i32> %broadcast.splat183)
  %304 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %303, <8 x i32> zeroinitializer)
  %305 = add nuw <8 x i32> %301, splat (i32 1)
  %306 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %305, <8 x i32> %broadcast.splat181)
  %307 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %306, <8 x i32> zeroinitializer)
  %308 = uitofp nneg <8 x i32> %297 to <8 x float>
  %309 = fsub reassoc ninf nsz <8 x float> %257, %308
  %310 = uitofp nneg <8 x i32> %301 to <8 x float>
  %311 = fsub reassoc ninf nsz <8 x float> %258, %310
  %312 = mul <8 x i32> %301, %broadcast.splat190
  %313 = add <8 x i32> %297, %312
  %314 = sext <8 x i32> %313 to <8 x i64>
  %315 = getelementptr float, ptr %242, <8 x i64> %314
  %wide.masked.gather191 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %315, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %316 = add <8 x i32> %304, %312
  %317 = sext <8 x i32> %316 to <8 x i64>
  %318 = getelementptr float, ptr %242, <8 x i64> %317
  %wide.masked.gather192 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %318, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %319 = mul <8 x i32> %307, %broadcast.splat190
  %320 = add <8 x i32> %319, %297
  %321 = sext <8 x i32> %320 to <8 x i64>
  %322 = getelementptr float, ptr %242, <8 x i64> %321
  %wide.masked.gather193 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %322, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %323 = add <8 x i32> %304, %319
  %324 = sext <8 x i32> %323 to <8 x i64>
  %325 = getelementptr float, ptr %242, <8 x i64> %324
  %wide.masked.gather194 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %325, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %326 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %309
  %327 = fmul reassoc ninf nsz <8 x float> %326, %wide.masked.gather191
  %328 = fmul reassoc ninf nsz <8 x float> %309, %wide.masked.gather192
  %329 = fadd reassoc ninf nsz <8 x float> %327, %328
  %330 = fmul reassoc ninf nsz <8 x float> %326, %wide.masked.gather193
  %331 = fmul reassoc ninf nsz <8 x float> %309, %wide.masked.gather194
  %332 = fadd reassoc ninf nsz <8 x float> %330, %331
  %333 = fsub reassoc ninf nsz <8 x float> %332, %329
  %334 = fmul reassoc ninf nsz <8 x float> %333, %311
  %335 = add <8 x i32> %280, %267
  %336 = sext <8 x i32> %335 to <8 x i64>
  %337 = getelementptr float, ptr %240, <8 x i64> %336
  %wide.masked.gather195 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %337, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %338 = fsub reassoc ninf nsz <8 x float> %329, %wide.masked.gather195
  %339 = fadd reassoc ninf nsz <8 x float> %338, %334
  %340 = fmul reassoc ninf nsz <8 x float> %275, %275
  %341 = fadd reassoc ninf nsz <8 x float> %340, %vec.phi167
  %342 = fmul reassoc ninf nsz <8 x float> %293, %275
  %343 = fadd reassoc ninf nsz <8 x float> %342, %vec.phi166
  %344 = fmul reassoc ninf nsz <8 x float> %293, %293
  %345 = fadd reassoc ninf nsz <8 x float> %344, %vec.phi165
  %346 = fmul reassoc ninf nsz <8 x float> %339, %275
  %347 = fadd reassoc ninf nsz <8 x float> %346, %vec.phi164
  %348 = fmul reassoc ninf nsz <8 x float> %339, %293
  %349 = fadd reassoc ninf nsz <8 x float> %348, %vec.phi163
  %350 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %339)
  %351 = fadd reassoc ninf nsz <8 x float> %350, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %352 = icmp eq i32 %lsr.iv.next, 0
  br i1 %352, label %middle.block, label %vector.body, !llvm.loop !10

middle.block:                                     ; preds = %vector.body
  %353 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %351)
  %354 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %349)
  %355 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %347)
  %356 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %345)
  %357 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %343)
  %358 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %341)
  br i1 %cmp.n, label %after_for13, label %for_loop_body11.preheader

for_loop_body11.preheader:                        ; preds = %middle.block, %for_loop_body11.lr.ph
  %.04486.ph = phi i32 [ 0, %for_loop_body11.lr.ph ], [ %n.vec, %middle.block ]
  %.04585.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %353, %middle.block ]
  %.04684.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %354, %middle.block ]
  %.04783.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %355, %middle.block ]
  %.04882.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %356, %middle.block ]
  %.04981.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %357, %middle.block ]
  %.05080.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %358, %middle.block ]
  br label %for_loop_body11

after_if10:                                       ; preds = %true_block21, %false_block16, %for_loop_body4
  %.163 = phi float [ %500, %true_block21 ], [ %500, %false_block16 ], [ %.06292, %for_loop_body4 ]
  %.161 = phi float [ %502, %true_block21 ], [ %502, %false_block16 ], [ %.06093, %for_loop_body4 ]
  %.157 = phi i32 [ 0, %true_block21 ], [ 1, %false_block16 ], [ 0, %for_loop_body4 ]
  %.155 = phi float [ %482, %true_block21 ], [ %482, %false_block16 ], [ %.05496, %for_loop_body4 ]
  %.153 = phi float [ %481, %true_block21 ], [ %481, %false_block16 ], [ %.05297, %for_loop_body4 ]
  %359 = add nuw nsw i32 %.05198, 1
  %exitcond110.not = icmp eq i32 %359, %231
  br i1 %exitcond110.not, label %after_for6, label %for_loop_body4

after_if10.thread:                                ; preds = %after_for13
  %360 = add nuw nsw i32 %.05198, 1
  %exitcond110.not129 = icmp eq i32 %360, %231
  br i1 %exitcond110.not129, label %after_if3.loopexit, label %for_loop_body4.outer

for_loop_body4.outer:                             ; preds = %after_if10.thread, %for_loop_body4.lr.ph
  %.05198.ph = phi i32 [ %360, %after_if10.thread ], [ 0, %for_loop_body4.lr.ph ]
  %.05297.ph = phi float [ %481, %after_if10.thread ], [ 0.000000e+00, %for_loop_body4.lr.ph ]
  %.05496.ph = phi float [ %482, %after_if10.thread ], [ 0.000000e+00, %for_loop_body4.lr.ph ]
  %.not = phi i1 [ true, %after_if10.thread ], [ false, %for_loop_body4.lr.ph ]
  %.05695.ph = phi i32 [ 0, %after_if10.thread ], [ 1, %for_loop_body4.lr.ph ]
  %.06093.ph = phi float [ %.06093, %after_if10.thread ], [ %229, %for_loop_body4.lr.ph ]
  %.06292.ph = phi float [ %.06292, %after_if10.thread ], [ %204, %for_loop_body4.lr.ph ]
  br label %for_loop_body4

for_loop_body11:                                  ; preds = %for_loop_body11, %for_loop_body11.preheader
  %.04486 = phi i32 [ %477, %for_loop_body11 ], [ %.04486.ph, %for_loop_body11.preheader ]
  %.04585 = phi float [ %476, %for_loop_body11 ], [ %.04585.ph, %for_loop_body11.preheader ]
  %.04684 = phi float [ %474, %for_loop_body11 ], [ %.04684.ph, %for_loop_body11.preheader ]
  %.04783 = phi float [ %472, %for_loop_body11 ], [ %.04783.ph, %for_loop_body11.preheader ]
  %.04882 = phi float [ %470, %for_loop_body11 ], [ %.04882.ph, %for_loop_body11.preheader ]
  %.04981 = phi float [ %468, %for_loop_body11 ], [ %.04981.ph, %for_loop_body11.preheader ]
  %.05080 = phi float [ %466, %for_loop_body11 ], [ %.05080.ph, %for_loop_body11.preheader ]
  %361 = sdiv i32 %.04486, %41
  %362 = mul i32 %361, %41
  %363 = icmp ne i32 %.04486, %362
  %364 = and i1 %44, %363
  %.neg73 = sext i1 %364 to i32
  %365 = add i32 %361, %.neg73
  %366 = sub i32 %365, %25
  %367 = add i32 %366, %71
  %368 = mul i32 %52, %365
  %369 = add i32 %.neg77.reass, %.04486
  %370 = add i32 %369, %368
  %371 = sitofp i32 %367 to float
  %372 = sitofp i32 %370 to float
  %373 = fadd reassoc ninf nsz float %.06292, %372
  %374 = fadd reassoc ninf nsz float %.06093, %371
  %375 = add i32 %370, 1
  %376 = tail call i32 @llvm.smin.i32(i32 %367, i32 %152)
  %377 = tail call i32 @llvm.smax.i32(i32 %376, i32 0)
  %378 = tail call i32 @llvm.smin.i32(i32 %375, i32 %148)
  %379 = tail call i32 @llvm.smax.i32(i32 %378, i32 0)
  %380 = add i32 %370, -1
  %381 = tail call i32 @llvm.smin.i32(i32 %380, i32 %148)
  %382 = tail call i32 @llvm.smax.i32(i32 %381, i32 0)
  %383 = mul i32 %377, %241
  %384 = add i32 %379, %383
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, ptr %240, i64 %385
  %387 = load float, ptr %386, align 4
  %388 = add i32 %382, %383
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %240, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = fsub reassoc ninf nsz float %387, %391
  %393 = fmul reassoc ninf nsz float %392, 5.000000e-01
  %394 = add i32 %367, 1
  %395 = tail call i32 @llvm.smin.i32(i32 %394, i32 %152)
  %396 = tail call i32 @llvm.smax.i32(i32 %395, i32 0)
  %397 = tail call i32 @llvm.smin.i32(i32 %370, i32 %148)
  %398 = tail call i32 @llvm.smax.i32(i32 %397, i32 0)
  %399 = add i32 %367, -1
  %400 = tail call i32 @llvm.smin.i32(i32 %399, i32 %152)
  %401 = tail call i32 @llvm.smax.i32(i32 %400, i32 0)
  %402 = mul i32 %396, %241
  %403 = add i32 %402, %398
  %404 = sext i32 %403 to i64
  %405 = getelementptr float, ptr %240, i64 %404
  %406 = load float, ptr %405, align 4
  %407 = mul i32 %401, %241
  %408 = add i32 %407, %398
  %409 = sext i32 %408 to i64
  %410 = getelementptr float, ptr %240, i64 %409
  %411 = load float, ptr %410, align 4
  %412 = fsub reassoc ninf nsz float %406, %411
  %413 = fmul reassoc ninf nsz float %412, 5.000000e-01
  %414 = tail call reassoc ninf nsz float @llvm.floor.f32(float %373)
  %415 = fptosi float %414 to i32
  %416 = tail call i32 @llvm.smin.i32(i32 %415, i32 %148)
  %417 = tail call i32 @llvm.smax.i32(i32 %416, i32 0)
  %418 = tail call reassoc ninf nsz float @llvm.floor.f32(float %374)
  %419 = fptosi float %418 to i32
  %420 = tail call i32 @llvm.smin.i32(i32 %419, i32 %152)
  %421 = tail call i32 @llvm.smax.i32(i32 %420, i32 0)
  %422 = add nuw i32 %417, 1
  %423 = tail call i32 @llvm.smin.i32(i32 %422, i32 %148)
  %424 = tail call i32 @llvm.smax.i32(i32 %423, i32 0)
  %425 = add nuw i32 %421, 1
  %426 = tail call i32 @llvm.smin.i32(i32 %425, i32 %152)
  %427 = tail call i32 @llvm.smax.i32(i32 %426, i32 0)
  %428 = uitofp nneg i32 %417 to float
  %429 = fsub reassoc ninf nsz float %373, %428
  %430 = uitofp nneg i32 %421 to float
  %431 = fsub reassoc ninf nsz float %374, %430
  %432 = mul i32 %421, %243
  %433 = add i32 %417, %432
  %434 = sext i32 %433 to i64
  %435 = getelementptr float, ptr %242, i64 %434
  %436 = load float, ptr %435, align 4
  %437 = add i32 %424, %432
  %438 = sext i32 %437 to i64
  %439 = getelementptr float, ptr %242, i64 %438
  %440 = load float, ptr %439, align 4
  %441 = mul i32 %427, %243
  %442 = add i32 %441, %417
  %443 = sext i32 %442 to i64
  %444 = getelementptr float, ptr %242, i64 %443
  %445 = load float, ptr %444, align 4
  %446 = add i32 %424, %441
  %447 = sext i32 %446 to i64
  %448 = getelementptr float, ptr %242, i64 %447
  %449 = load float, ptr %448, align 4
  %450 = fsub reassoc ninf nsz float 1.000000e+00, %429
  %451 = fmul reassoc ninf nsz float %450, %436
  %452 = fmul reassoc ninf nsz float %429, %440
  %453 = fadd reassoc ninf nsz float %451, %452
  %454 = fmul reassoc ninf nsz float %450, %445
  %455 = fmul reassoc ninf nsz float %429, %449
  %456 = fadd reassoc ninf nsz float %454, %455
  %457 = fsub reassoc ninf nsz float %456, %453
  %458 = fmul reassoc ninf nsz float %457, %431
  %459 = add i32 %398, %383
  %460 = sext i32 %459 to i64
  %461 = getelementptr float, ptr %240, i64 %460
  %462 = load float, ptr %461, align 4
  %463 = fsub reassoc ninf nsz float %453, %462
  %464 = fadd reassoc ninf nsz float %463, %458
  %465 = fmul reassoc ninf nsz float %393, %393
  %466 = fadd reassoc ninf nsz float %465, %.05080
  %467 = fmul reassoc ninf nsz float %413, %393
  %468 = fadd reassoc ninf nsz float %467, %.04981
  %469 = fmul reassoc ninf nsz float %413, %413
  %470 = fadd reassoc ninf nsz float %469, %.04882
  %471 = fmul reassoc ninf nsz float %464, %393
  %472 = fadd reassoc ninf nsz float %471, %.04783
  %473 = fmul reassoc ninf nsz float %464, %413
  %474 = fadd reassoc ninf nsz float %473, %.04684
  %475 = tail call noundef float @llvm.fabs.f32(float %464)
  %476 = fadd reassoc ninf nsz float %475, %.04585
  %477 = add nuw nsw i32 %.04486, 1
  %exitcond.not = icmp eq i32 %42, %477
  br i1 %exitcond.not, label %after_for13.loopexit, label %for_loop_body11, !llvm.loop !13

after_for13.loopexit:                             ; preds = %for_loop_body11
  br label %after_for13

after_for13:                                      ; preds = %after_for13.loopexit, %middle.block, %true_block8
  %.050.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %358, %middle.block ], [ %466, %after_for13.loopexit ]
  %.049.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %357, %middle.block ], [ %468, %after_for13.loopexit ]
  %.048.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %356, %middle.block ], [ %470, %after_for13.loopexit ]
  %.047.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %355, %middle.block ], [ %472, %after_for13.loopexit ]
  %.046.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %354, %middle.block ], [ %474, %after_for13.loopexit ]
  %.045.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %353, %middle.block ], [ %476, %after_for13.loopexit ]
  %478 = fmul reassoc ninf nsz float %.048.lcssa, %.050.lcssa
  %479 = fmul reassoc ninf nsz float %.049.lcssa, %.049.lcssa
  %480 = fsub reassoc ninf nsz float %478, %479
  %481 = tail call noundef float @llvm.fabs.f32(float %480)
  %482 = fdiv reassoc ninf nsz float %.045.lcssa, %47
  %483 = fcmp reassoc ninf nsz olt float %481, 0x3F1A36E2E0000000
  br i1 %483, label %after_if10.thread, label %false_block16

false_block16:                                    ; preds = %after_for13
  %484 = fdiv reassoc ninf nsz float 1.000000e+00, %480
  %485 = fmul reassoc ninf nsz float %.046.lcssa, %.049.lcssa
  %486 = fmul reassoc ninf nsz float %.047.lcssa, %.048.lcssa
  %487 = fsub reassoc ninf nsz float %485, %486
  %488 = fmul reassoc ninf nsz float %487, %484
  %489 = fmul reassoc ninf nsz float %.047.lcssa, %.049.lcssa
  %490 = fmul reassoc ninf nsz float %.046.lcssa, %.050.lcssa
  %491 = fsub reassoc ninf nsz float %489, %490
  %492 = fmul reassoc ninf nsz float %491, %484
  %493 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %29, float %488)
  %494 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg19, float %493)
  %495 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %29, float %492)
  %496 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg19, float %495)
  %497 = fadd reassoc ninf nsz float %494, %.06292
  %498 = fadd reassoc ninf nsz float %496, %.06093
  %499 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %30, float %497)
  %500 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg20, float %499)
  %501 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %30, float %498)
  %502 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg20, float %501)
  %503 = fmul reassoc ninf nsz float %494, %494
  %504 = fmul reassoc ninf nsz float %496, %496
  %505 = fadd reassoc ninf nsz float %503, %504
  %506 = load float, ptr %237, align 4
  %507 = fmul reassoc ninf nsz float %506, %506
  %508 = fcmp reassoc ninf nsz olt float %505, %507
  br i1 %508, label %true_block21, label %after_if10

true_block21:                                     ; preds = %false_block16
  br label %after_if10

true_block24:                                     ; preds = %after_for6, %true_block1
  %.052.lcssa121 = phi float [ %.153, %after_for6 ], [ 0.000000e+00, %true_block1 ]
  %.054.lcssa119 = phi float [ %.155, %after_for6 ], [ 0.000000e+00, %true_block1 ]
  %.060.lcssa118 = phi float [ %.161, %after_for6 ], [ %229, %true_block1 ]
  %.062.lcssa117 = phi float [ %.163, %after_for6 ], [ %204, %true_block1 ]
  store float %.062.lcssa117, ptr %80, align 4
  store float %.060.lcssa118, ptr %89, align 4
  store float 1.000000e+00, ptr %98, align 4
  %509 = fmul reassoc ninf nsz float %.062.lcssa117, %.062.lcssa117
  %510 = fmul reassoc ninf nsz float %.060.lcssa118, %.060.lcssa118
  %511 = fadd reassoc ninf nsz float %510, %509
  %512 = fcmp reassoc ninf nsz ogt float %511, %50
  br i1 %512, label %after_if35.thread, label %after_if35

after_if35:                                       ; preds = %true_block24
  %513 = fcmp reassoc ninf nsz ogt float %511, %51
  %514 = fcmp reassoc ninf nsz ogt float %.054.lcssa119, 1.000000e+01
  %.042 = select i1 %513, i1 true, i1 %514
  %.043 = select i1 %.042, float 1.000000e+00, float 0.000000e+00
  %515 = fcmp reassoc ninf nsz ogt float %.054.lcssa119, 2.200000e+01
  %516 = fcmp reassoc ninf nsz olt float %.052.lcssa121, 0x3F50624DE0000000
  %.0 = select i1 %515, i1 true, i1 %516
  %cond.fr = freeze i1 %.0
  br i1 %cond.fr, label %after_if35.thread, label %517

after_if35.thread:                                ; preds = %after_if35, %true_block24
  br label %517

517:                                              ; preds = %after_if35.thread, %after_if35
  %518 = phi float [ 2.000000e+00, %after_if35.thread ], [ %.043, %after_if35 ]
  store float %.054.lcssa119, ptr %106, align 4
  store float %.052.lcssa121, ptr %115, align 4
  store float %518, ptr %124, align 4
  store float %511, ptr %133, align 4
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !14

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !16

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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.floor.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }
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
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.isvectorized", i32 1}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !12, !11}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
