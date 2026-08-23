; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @robust_splat_kernel_c1330_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 76
  %4 = load i32, ptr %3, align 4
  %5 = getelementptr i8, ptr %0, i64 80
  %6 = load i32, ptr %5, align 4
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 20
  store i32 %6, ptr %11, align 4
  %12 = load ptr, ptr %context, align 8
  %13 = getelementptr i8, ptr %12, i64 4
  %14 = load i32, ptr %13, align 4
  %15 = load ptr, ptr %7, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 32872
  %17 = load ptr, ptr %16, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 8
  store i32 %14, ptr %18, align 4
  %19 = load ptr, ptr %context, align 8
  %20 = getelementptr i8, ptr %19, i64 8
  %21 = load i32, ptr %20, align 4
  %22 = load ptr, ptr %7, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 12
  store i32 %21, ptr %25, align 4
  %26 = load ptr, ptr %context, align 8
  %27 = getelementptr i8, ptr %26, i64 120
  %28 = load float, ptr %27, align 4
  %29 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %28, float 0x3F1A36E2E0000000)
  %30 = fmul reassoc ninf nsz float %29, %29
  %31 = fdiv reassoc ninf nsz float 5.000000e-01, %30
  %32 = load ptr, ptr %7, align 8
  %33 = getelementptr inbounds nuw i8, ptr %32, i64 32872
  %34 = load ptr, ptr %33, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 16
  store float %31, ptr %35, align 4
  %36 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %37 = tail call i32 @llvm.smax.i32(i32 %4, i32 0)
  %38 = load ptr, ptr %7, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 4
  store i32 %37, ptr %41, align 4
  %42 = mul i32 %37, %36
  %43 = load ptr, ptr %7, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  store i32 %42, ptr %45, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @robust_splat_kernel_c1330_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
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
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = sitofp i32 %21 to float
  %24 = getelementptr i8, ptr %19, i64 88
  %25 = getelementptr i8, ptr %19, i64 76
  %26 = getelementptr i8, ptr %19, i64 80
  %27 = getelementptr i8, ptr %19, i64 104
  %28 = getelementptr i8, ptr %19, i64 100
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for23, %for_loop_body.lr.ph
  %.02442 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %367, %after_for23 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.02442, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.02442
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %35, %.02442
  %39 = and i1 %37, %38
  %.neg30 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg30
  %41 = mul i32 %40, %33
  %42 = sub i32 %.02442, %41
  %43 = load ptr, ptr %0, align 8
  %44 = load i32, ptr %43, align 4
  %45 = tail call i32 @llvm.smax.i32(i32 %44, i32 0)
  %46 = mul i32 %45, 49
  %47 = icmp sgt i32 %46, 0
  br i1 %47, label %for_loop_body1.lr.ph, label %for_loop_body.after_for3_crit_edge

for_loop_body.after_for3_crit_edge:               ; preds = %for_loop_body
  %.pre = sext i32 %40 to i64
  %.pre57 = sext i32 %42 to i64
  br label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %48 = sdiv i32 %42, %21
  %49 = mul i32 %48, %21
  %50 = icmp ne i32 %49, %42
  %51 = icmp ne i32 %.02442, %41
  %52 = xor i32 %42, %21
  %53 = icmp slt i32 %52, 0
  %54 = and i1 %51, %53
  %55 = and i1 %50, %54
  %.neg32 = sext i1 %55 to i32
  %56 = sdiv i32 %40, %21
  %57 = mul i32 %56, %21
  %58 = icmp ne i32 %57, %40
  %59 = xor i32 %40, %21
  %60 = icmp slt i32 %59, 0
  %61 = and i1 %58, %60
  %.neg31 = sext i1 %61 to i32
  %62 = add i32 %56, -3
  %63 = add i32 %62, %.neg31
  %64 = add i32 %48, -3
  %65 = add i32 %64, %.neg32
  %66 = sitofp i32 %42 to float
  %67 = sitofp i32 %40 to float
  %68 = sext i32 %40 to i64
  %69 = sext i32 %42 to i64
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for23
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if13, %for_loop_body1.lr.ph
  %lsr.iv72 = phi i64 [ 0, %for_loop_body1.lr.ph ], [ %lsr.iv.next73, %after_if13 ]
  %lsr.iv = phi i32 [ %65, %for_loop_body1.lr.ph ], [ %lsr.iv.next, %after_if13 ]
  %.02339 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %220, %after_if13 ]
  %lsr83 = trunc i64 %lsr.iv72 to i32
  %70 = udiv i32 %lsr83, 49
  %71 = mul nuw nsw i32 %70, 49
  %72 = udiv i64 %lsr.iv72, 49
  %.neg34 = mul i32 %70, -49
  %73 = add i32 %.neg34, %lsr83
  %74 = sdiv i32 %73, 7
  %75 = icmp slt i32 %73, 0
  %76 = mul nsw i32 %74, 7
  %77 = icmp ne i32 %76, %73
  %78 = and i1 %75, %77
  %.neg35 = sext i1 %78 to i32
  %79 = add nsw i32 %74, %.neg35
  %.neg36 = mul i32 %79, -7
  %80 = add i32 %63, %79
  %81 = add i32 %65, %73
  %82 = add i32 %81, %.neg36
  %83 = icmp sgt i32 %80, -1
  br i1 %83, label %true_block, label %after_if13

after_for3.loopexit:                              ; preds = %after_if13
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body.after_for3_crit_edge
  %.pre-phi58 = phi i64 [ %.pre57, %for_loop_body.after_for3_crit_edge ], [ %69, %after_for3.loopexit ]
  %.pre-phi = phi i64 [ %.pre, %for_loop_body.after_for3_crit_edge ], [ %68, %after_for3.loopexit ]
  %.023.lcssa = phi float [ 0.000000e+00, %for_loop_body.after_for3_crit_edge ], [ %220, %after_for3.loopexit ]
  %84 = load ptr, ptr %27, align 8
  %85 = load i32, ptr %28, align 4
  %86 = sext i32 %85 to i64
  %87 = mul nsw i64 %.pre-phi, %86
  %88 = getelementptr float, ptr %84, i64 %87
  %89 = getelementptr float, ptr %88, i64 %.pre-phi58
  store float %.023.lcssa, ptr %89, align 4
  %90 = load ptr, ptr %3, align 8
  %91 = getelementptr inbounds nuw i8, ptr %90, i64 32872
  %92 = load ptr, ptr %91, align 8
  %93 = getelementptr inbounds nuw i8, ptr %92, i64 20
  %94 = load i32, ptr %93, align 4
  %95 = icmp sgt i32 %94, 0
  br i1 %95, label %for_loop_body21.lr.ph, label %after_for23

for_loop_body21.lr.ph:                            ; preds = %after_for3
  %96 = fcmp reassoc nsz ogt float %.023.lcssa, 0x3E45798EE0000000
  %wide.trip.count54 = zext nneg i32 %94 to i64
  br i1 %96, label %for_loop_body21.us.preheader, label %for_loop_body21.preheader

for_loop_body21.preheader:                        ; preds = %for_loop_body21.lr.ph
  %xtraiter62 = and i64 %wide.trip.count54, 3
  %97 = icmp ult i32 %94, 4
  br i1 %97, label %after_for23.loopexit61.unr-lcssa, label %for_loop_body21.preheader.new

for_loop_body21.preheader.new:                    ; preds = %for_loop_body21.preheader
  %unroll_iter64 = and i64 %wide.trip.count54, 2147483644
  br label %for_loop_body21

for_loop_body21.us.preheader:                     ; preds = %for_loop_body21.lr.ph
  %xtraiter66 = and i64 %wide.trip.count54, 3
  %98 = icmp ult i32 %94, 4
  br i1 %98, label %after_for23.loopexit.unr-lcssa, label %for_loop_body21.us.preheader.new

for_loop_body21.us.preheader.new:                 ; preds = %for_loop_body21.us.preheader
  %unroll_iter69 = and i64 %wide.trip.count54, 2147483644
  br label %for_loop_body21.us

for_loop_body21.us:                               ; preds = %for_loop_body21.us, %for_loop_body21.us.preheader.new
  %indvars.iv51 = phi i64 [ 0, %for_loop_body21.us.preheader.new ], [ %indvars.iv.next52.3, %for_loop_body21.us ]
  %99 = load ptr, ptr %24, align 8
  %100 = load i32, ptr %25, align 4
  %101 = sext i32 %100 to i64
  %102 = load i32, ptr %26, align 4
  %103 = sext i32 %102 to i64
  %104 = mul nsw i64 %.pre-phi, %101
  %105 = add nsw i64 %104, %.pre-phi58
  %106 = mul i64 %105, %103
  %107 = getelementptr float, ptr %99, i64 %106
  %108 = shl nuw nsw i64 %indvars.iv51, 2
  %scevgep100 = getelementptr i8, ptr %107, i64 %108
  %109 = load float, ptr %scevgep100, align 4
  %110 = fdiv reassoc ninf nsz float %109, %.023.lcssa
  store float %110, ptr %scevgep100, align 4
  %111 = load ptr, ptr %24, align 8
  %112 = load i32, ptr %25, align 4
  %113 = sext i32 %112 to i64
  %114 = load i32, ptr %26, align 4
  %115 = sext i32 %114 to i64
  %116 = mul nsw i64 %.pre-phi, %113
  %117 = add nsw i64 %116, %.pre-phi58
  %118 = mul i64 %117, %115
  %119 = getelementptr float, ptr %111, i64 %118
  %scevgep98 = getelementptr i8, ptr %119, i64 %108
  %scevgep99 = getelementptr i8, ptr %scevgep98, i64 4
  %120 = load float, ptr %scevgep99, align 4
  %121 = fdiv reassoc ninf nsz float %120, %.023.lcssa
  store float %121, ptr %scevgep99, align 4
  %122 = load ptr, ptr %24, align 8
  %123 = load i32, ptr %25, align 4
  %124 = sext i32 %123 to i64
  %125 = load i32, ptr %26, align 4
  %126 = sext i32 %125 to i64
  %127 = mul nsw i64 %.pre-phi, %124
  %128 = add nsw i64 %127, %.pre-phi58
  %129 = mul i64 %128, %126
  %130 = getelementptr float, ptr %122, i64 %129
  %scevgep96 = getelementptr i8, ptr %130, i64 %108
  %scevgep97 = getelementptr i8, ptr %scevgep96, i64 8
  %131 = load float, ptr %scevgep97, align 4
  %132 = fdiv reassoc ninf nsz float %131, %.023.lcssa
  store float %132, ptr %scevgep97, align 4
  %133 = load ptr, ptr %24, align 8
  %134 = load i32, ptr %25, align 4
  %135 = sext i32 %134 to i64
  %136 = load i32, ptr %26, align 4
  %137 = sext i32 %136 to i64
  %138 = mul nsw i64 %.pre-phi, %135
  %139 = add nsw i64 %138, %.pre-phi58
  %140 = mul i64 %139, %137
  %141 = getelementptr float, ptr %133, i64 %140
  %scevgep94 = getelementptr i8, ptr %141, i64 %108
  %scevgep95 = getelementptr i8, ptr %scevgep94, i64 12
  %142 = load float, ptr %scevgep95, align 4
  %143 = fdiv reassoc ninf nsz float %142, %.023.lcssa
  store float %143, ptr %scevgep95, align 4
  %indvars.iv.next52.3 = add nuw nsw i64 %indvars.iv51, 4
  %niter70.ncmp.3 = icmp eq i64 %unroll_iter69, %indvars.iv.next52.3
  br i1 %niter70.ncmp.3, label %after_for23.loopexit.unr-lcssa.loopexit, label %for_loop_body21.us

true_block:                                       ; preds = %for_loop_body1
  %144 = load ptr, ptr %3, align 8
  %145 = getelementptr inbounds nuw i8, ptr %144, i64 32872
  %146 = load ptr, ptr %145, align 8
  %147 = getelementptr inbounds nuw i8, ptr %146, i64 8
  %148 = load i32, ptr %147, align 4
  %149 = icmp slt i32 %80, %148
  %150 = icmp sgt i32 %82, -1
  %or.cond = select i1 %149, i1 %150, i1 false
  br i1 %or.cond, label %true_block8, label %after_if13

true_block8:                                      ; preds = %true_block
  %151 = getelementptr inbounds nuw i8, ptr %146, i64 12
  %152 = load i32, ptr %151, align 4
  %153 = icmp slt i32 %82, %152
  br i1 %153, label %true_block11, label %after_if13

true_block11:                                     ; preds = %true_block8
  %154 = uitofp nneg i32 %82 to float
  %155 = load ptr, ptr %0, align 8
  %156 = getelementptr i8, ptr %155, i64 64
  %157 = load ptr, ptr %156, align 8
  %158 = getelementptr i8, ptr %155, i64 52
  %159 = load i32, ptr %158, align 4
  %160 = sext i32 %159 to i64
  %161 = getelementptr i8, ptr %155, i64 56
  %162 = load i32, ptr %161, align 4
  %163 = sext i32 %162 to i64
  %164 = getelementptr i8, ptr %155, i64 60
  %165 = load i32, ptr %164, align 4
  %166 = sext i32 %165 to i64
  %167 = zext nneg i32 %70 to i64
  %168 = mul nsw i64 %160, %167
  %169 = zext nneg i32 %80 to i64
  %170 = add nsw i64 %168, %169
  %171 = mul i64 %170, %163
  %172 = zext nneg i32 %82 to i64
  %173 = add i64 %171, %172
  %174 = mul i64 %173, %166
  %175 = getelementptr float, ptr %157, i64 %174
  %176 = load float, ptr %175, align 4
  %177 = fadd reassoc ninf nsz float %176, %154
  %178 = fmul reassoc ninf nsz float %177, %23
  %179 = uitofp nneg i32 %80 to float
  %180 = getelementptr i8, ptr %175, i64 4
  %181 = load float, ptr %180, align 4
  %182 = fadd reassoc ninf nsz float %181, %179
  %183 = fmul reassoc ninf nsz float %182, %23
  %184 = fsub reassoc ninf nsz float %66, %178
  %185 = fsub reassoc ninf nsz float %67, %183
  %186 = fmul reassoc ninf nsz float %184, %184
  %187 = fmul reassoc ninf nsz float %185, %185
  %188 = fadd reassoc ninf nsz float %187, %186
  %189 = getelementptr i8, ptr %155, i64 116
  %190 = load float, ptr %189, align 4
  %191 = fmul reassoc ninf nsz float %190, %190
  %192 = fcmp reassoc ninf nsz ugt float %188, %191
  br i1 %192, label %after_if13, label %true_block14

after_if13.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body17
  br label %after_if13.loopexit.unr-lcssa

after_if13.loopexit.unr-lcssa:                    ; preds = %for_loop_body17.lr.ph, %after_if13.loopexit.unr-lcssa.loopexit
  %indvars.iv.unr = phi i64 [ 0, %for_loop_body17.lr.ph ], [ %indvars.iv.next.1, %after_if13.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_if13, label %for_loop_body17.epil

for_loop_body17.epil:                             ; preds = %after_if13.loopexit.unr-lcssa
  %193 = load ptr, ptr %248, align 8
  %194 = load i32, ptr %249, align 4
  %195 = sext i32 %194 to i64
  %196 = load i32, ptr %250, align 4
  %197 = sext i32 %196 to i64
  %198 = load i32, ptr %251, align 4
  %199 = sext i32 %198 to i64
  %200 = mul nsw i64 %195, %167
  %201 = add nsw i64 %200, %169
  %202 = mul i64 %201, %197
  %203 = add i64 %202, %172
  %204 = mul i64 %203, %199
  %205 = getelementptr float, ptr %193, i64 %204
  %206 = getelementptr float, ptr %205, i64 %indvars.iv.unr
  %207 = load float, ptr %206, align 4
  %208 = fmul reassoc ninf nsz float %207, %239
  %209 = load ptr, ptr %24, align 8
  %210 = load i32, ptr %25, align 4
  %211 = sext i32 %210 to i64
  %212 = load i32, ptr %26, align 4
  %213 = sext i32 %212 to i64
  %214 = mul nsw i64 %211, %68
  %215 = add nsw i64 %214, %69
  %216 = mul i64 %215, %213
  %217 = getelementptr float, ptr %209, i64 %216
  %218 = getelementptr float, ptr %217, i64 %indvars.iv.unr
  %219 = atomicrmw fadd ptr %218, float %208 seq_cst, align 4
  br label %after_if13

after_if13:                                       ; preds = %true_block14, %for_loop_body17.epil, %after_if13.loopexit.unr-lcssa, %true_block11, %true_block8, %true_block, %for_loop_body1
  %.1 = phi float [ %.02339, %true_block11 ], [ %.02339, %true_block8 ], [ %.02339, %for_loop_body1 ], [ %.02339, %true_block ], [ %240, %true_block14 ], [ %240, %after_if13.loopexit.unr-lcssa ], [ %240, %for_loop_body17.epil ]
  %220 = freeze float %.1
  %lsr.iv.next73 = add nuw nsw i64 %lsr.iv72, 1
  %lsr = trunc i64 %lsr.iv.next73 to i32
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond45.not = icmp eq i32 %lsr, %46
  br i1 %exitcond45.not, label %after_for3.loopexit, label %for_loop_body1

true_block14:                                     ; preds = %true_block11
  %221 = getelementptr i8, ptr %155, i64 40
  %222 = load ptr, ptr %221, align 8
  %223 = getelementptr i8, ptr %155, i64 28
  %224 = load i32, ptr %223, align 4
  %225 = sext i32 %224 to i64
  %226 = getelementptr i8, ptr %155, i64 32
  %227 = load i32, ptr %226, align 4
  %228 = sext i32 %227 to i64
  %229 = mul nsw i64 %225, %167
  %230 = add nsw i64 %229, %169
  %231 = mul i64 %230, %228
  %232 = getelementptr float, ptr %222, i64 %231
  %233 = getelementptr float, ptr %232, i64 %172
  %234 = load float, ptr %233, align 4
  %neg = fneg reassoc ninf nsz float %188
  %235 = getelementptr inbounds nuw i8, ptr %146, i64 16
  %236 = load float, ptr %235, align 4
  %237 = fmul reassoc ninf nsz float %236, %neg
  %238 = tail call noundef float @expf(float noundef %237) #8
  %239 = fmul reassoc ninf nsz float %238, %234
  %240 = fadd reassoc ninf nsz float %239, %.02339
  %241 = load ptr, ptr %3, align 8
  %242 = getelementptr inbounds nuw i8, ptr %241, i64 32872
  %243 = load ptr, ptr %242, align 8
  %244 = getelementptr inbounds nuw i8, ptr %243, i64 20
  %245 = load i32, ptr %244, align 4
  %246 = icmp sgt i32 %245, 0
  br i1 %246, label %for_loop_body17.lr.ph, label %after_if13

for_loop_body17.lr.ph:                            ; preds = %true_block14
  %247 = load ptr, ptr %0, align 8
  %248 = getelementptr i8, ptr %247, i64 16
  %249 = getelementptr i8, ptr %247, i64 4
  %250 = getelementptr i8, ptr %247, i64 8
  %251 = getelementptr i8, ptr %247, i64 12
  %wide.trip.count = zext nneg i32 %245 to i64
  %xtraiter = and i64 %wide.trip.count, 1
  %252 = icmp eq i32 %245, 1
  br i1 %252, label %after_if13.loopexit.unr-lcssa, label %for_loop_body17.lr.ph.new

for_loop_body17.lr.ph.new:                        ; preds = %for_loop_body17.lr.ph
  %unroll_iter = and i64 %wide.trip.count, 2147483646
  %253 = mul i32 %79, 7
  %254 = sub i32 %lsr.iv, %253
  %255 = sub i32 %254, %71
  %256 = zext i32 %255 to i64
  br label %for_loop_body17

for_loop_body17:                                  ; preds = %for_loop_body17, %for_loop_body17.lr.ph.new
  %indvars.iv = phi i64 [ 0, %for_loop_body17.lr.ph.new ], [ %indvars.iv.next.1, %for_loop_body17 ]
  %257 = load ptr, ptr %248, align 8
  %258 = load i32, ptr %249, align 4
  %259 = sext i32 %258 to i64
  %260 = load i32, ptr %250, align 4
  %261 = sext i32 %260 to i64
  %262 = load i32, ptr %251, align 4
  %263 = sext i32 %262 to i64
  %264 = mul nsw i64 %72, %259
  %265 = add nsw i64 %169, %264
  %266 = mul i64 %265, %261
  %267 = add i64 %256, %266
  %268 = shl i64 %267, 2
  %269 = mul i64 %268, %263
  %scevgep81 = getelementptr i8, ptr %257, i64 %269
  %270 = shl i64 %indvars.iv, 2
  %scevgep82 = getelementptr i8, ptr %scevgep81, i64 %270
  %271 = load float, ptr %scevgep82, align 4
  %272 = fmul reassoc ninf nsz float %271, %239
  %273 = load ptr, ptr %24, align 8
  %274 = load i32, ptr %25, align 4
  %275 = sext i32 %274 to i64
  %276 = load i32, ptr %26, align 4
  %277 = sext i32 %276 to i64
  %278 = mul nsw i64 %275, %68
  %279 = add nsw i64 %69, %278
  %280 = shl i64 %279, 2
  %281 = mul i64 %280, %277
  %scevgep79 = getelementptr i8, ptr %273, i64 %281
  %scevgep80 = getelementptr i8, ptr %scevgep79, i64 %270
  %282 = atomicrmw fadd ptr %scevgep80, float %272 seq_cst, align 4
  %283 = load ptr, ptr %248, align 8
  %284 = load i32, ptr %249, align 4
  %285 = sext i32 %284 to i64
  %286 = load i32, ptr %250, align 4
  %287 = sext i32 %286 to i64
  %288 = load i32, ptr %251, align 4
  %289 = sext i32 %288 to i64
  %290 = mul nsw i64 %72, %285
  %291 = add nsw i64 %169, %290
  %292 = mul i64 %291, %287
  %293 = add i64 %256, %292
  %294 = shl i64 %293, 2
  %295 = mul i64 %294, %289
  %scevgep = getelementptr i8, ptr %283, i64 %295
  %scevgep74 = getelementptr i8, ptr %scevgep, i64 %270
  %scevgep75 = getelementptr i8, ptr %scevgep74, i64 4
  %296 = load float, ptr %scevgep75, align 4
  %297 = fmul reassoc ninf nsz float %296, %239
  %298 = load ptr, ptr %24, align 8
  %299 = load i32, ptr %25, align 4
  %300 = sext i32 %299 to i64
  %301 = load i32, ptr %26, align 4
  %302 = sext i32 %301 to i64
  %303 = mul nsw i64 %300, %68
  %304 = add nsw i64 %69, %303
  %305 = shl i64 %304, 2
  %306 = mul i64 %305, %302
  %scevgep76 = getelementptr i8, ptr %298, i64 %306
  %scevgep77 = getelementptr i8, ptr %scevgep76, i64 %270
  %scevgep78 = getelementptr i8, ptr %scevgep77, i64 4
  %307 = atomicrmw fadd ptr %scevgep78, float %297 seq_cst, align 4
  %indvars.iv.next.1 = add nuw i64 %indvars.iv, 2
  %niter.ncmp.1 = icmp eq i64 %unroll_iter, %indvars.iv.next.1
  br i1 %niter.ncmp.1, label %after_if13.loopexit.unr-lcssa.loopexit, label %for_loop_body17

for_loop_body21:                                  ; preds = %for_loop_body21, %for_loop_body21.preheader.new
  %indvars.iv46 = phi i64 [ 0, %for_loop_body21.preheader.new ], [ %indvars.iv.next47.3, %for_loop_body21 ]
  %308 = load ptr, ptr %24, align 8
  %309 = load i32, ptr %25, align 4
  %310 = sext i32 %309 to i64
  %311 = load i32, ptr %26, align 4
  %312 = sext i32 %311 to i64
  %313 = mul nsw i64 %.pre-phi, %310
  %314 = add nsw i64 %313, %.pre-phi58
  %315 = mul i64 %314, %312
  %316 = getelementptr float, ptr %308, i64 %315
  %317 = shl nuw nsw i64 %indvars.iv46, 2
  %scevgep90 = getelementptr i8, ptr %316, i64 %317
  store float 0.000000e+00, ptr %scevgep90, align 4
  %318 = load ptr, ptr %24, align 8
  %319 = load i32, ptr %25, align 4
  %320 = sext i32 %319 to i64
  %321 = load i32, ptr %26, align 4
  %322 = sext i32 %321 to i64
  %323 = mul nsw i64 %.pre-phi, %320
  %324 = add nsw i64 %323, %.pre-phi58
  %325 = mul i64 %324, %322
  %326 = getelementptr float, ptr %318, i64 %325
  %scevgep88 = getelementptr i8, ptr %326, i64 %317
  %scevgep89 = getelementptr i8, ptr %scevgep88, i64 4
  store float 0.000000e+00, ptr %scevgep89, align 4
  %327 = load ptr, ptr %24, align 8
  %328 = load i32, ptr %25, align 4
  %329 = sext i32 %328 to i64
  %330 = load i32, ptr %26, align 4
  %331 = sext i32 %330 to i64
  %332 = mul nsw i64 %.pre-phi, %329
  %333 = add nsw i64 %332, %.pre-phi58
  %334 = mul i64 %333, %331
  %335 = getelementptr float, ptr %327, i64 %334
  %scevgep86 = getelementptr i8, ptr %335, i64 %317
  %scevgep87 = getelementptr i8, ptr %scevgep86, i64 8
  store float 0.000000e+00, ptr %scevgep87, align 4
  %336 = load ptr, ptr %24, align 8
  %337 = load i32, ptr %25, align 4
  %338 = sext i32 %337 to i64
  %339 = load i32, ptr %26, align 4
  %340 = sext i32 %339 to i64
  %341 = mul nsw i64 %.pre-phi, %338
  %342 = add nsw i64 %341, %.pre-phi58
  %343 = mul i64 %342, %340
  %344 = getelementptr float, ptr %336, i64 %343
  %scevgep84 = getelementptr i8, ptr %344, i64 %317
  %scevgep85 = getelementptr i8, ptr %scevgep84, i64 12
  store float 0.000000e+00, ptr %scevgep85, align 4
  %indvars.iv.next47.3 = add nuw nsw i64 %indvars.iv46, 4
  %niter65.ncmp.3 = icmp eq i64 %unroll_iter64, %indvars.iv.next47.3
  br i1 %niter65.ncmp.3, label %after_for23.loopexit61.unr-lcssa.loopexit, label %for_loop_body21

after_for23.loopexit.unr-lcssa.loopexit:          ; preds = %for_loop_body21.us
  br label %after_for23.loopexit.unr-lcssa

after_for23.loopexit.unr-lcssa:                   ; preds = %after_for23.loopexit.unr-lcssa.loopexit, %for_loop_body21.us.preheader
  %indvars.iv51.unr = phi i64 [ 0, %for_loop_body21.us.preheader ], [ %indvars.iv.next52.3, %after_for23.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod68.not = icmp eq i64 %xtraiter66, 0
  br i1 %lcmp.mod68.not, label %after_for23, label %for_loop_body21.us.epil.preheader

for_loop_body21.us.epil.preheader:                ; preds = %after_for23.loopexit.unr-lcssa
  br label %for_loop_body21.us.epil

for_loop_body21.us.epil:                          ; preds = %for_loop_body21.us.epil, %for_loop_body21.us.epil.preheader
  %lsr.iv102 = phi i64 [ %xtraiter66, %for_loop_body21.us.epil.preheader ], [ %lsr.iv.next103, %for_loop_body21.us.epil ]
  %indvars.iv51.epil = phi i64 [ %indvars.iv.next52.epil, %for_loop_body21.us.epil ], [ %indvars.iv51.unr, %for_loop_body21.us.epil.preheader ]
  %345 = load ptr, ptr %24, align 8
  %346 = load i32, ptr %25, align 4
  %347 = sext i32 %346 to i64
  %348 = load i32, ptr %26, align 4
  %349 = sext i32 %348 to i64
  %350 = mul nsw i64 %.pre-phi, %347
  %351 = add nsw i64 %350, %.pre-phi58
  %352 = mul i64 %351, %349
  %353 = getelementptr float, ptr %345, i64 %352
  %354 = shl nuw nsw i64 %indvars.iv51.epil, 2
  %scevgep101 = getelementptr i8, ptr %353, i64 %354
  %355 = load float, ptr %scevgep101, align 4
  %356 = fdiv reassoc ninf nsz float %355, %.023.lcssa
  store float %356, ptr %scevgep101, align 4
  %indvars.iv.next52.epil = add nuw nsw i64 %indvars.iv51.epil, 1
  %lsr.iv.next103 = add nsw i64 %lsr.iv102, -1
  %epil.iter67.cmp.not = icmp eq i64 %lsr.iv.next103, 0
  br i1 %epil.iter67.cmp.not, label %after_for23.loopexit, label %for_loop_body21.us.epil, !llvm.loop !11

after_for23.loopexit61.unr-lcssa.loopexit:        ; preds = %for_loop_body21
  br label %after_for23.loopexit61.unr-lcssa

after_for23.loopexit61.unr-lcssa:                 ; preds = %after_for23.loopexit61.unr-lcssa.loopexit, %for_loop_body21.preheader
  %indvars.iv46.unr = phi i64 [ 0, %for_loop_body21.preheader ], [ %indvars.iv.next47.3, %after_for23.loopexit61.unr-lcssa.loopexit ]
  %lcmp.mod63.not = icmp eq i64 %xtraiter62, 0
  br i1 %lcmp.mod63.not, label %after_for23, label %for_loop_body21.epil.preheader

for_loop_body21.epil.preheader:                   ; preds = %after_for23.loopexit61.unr-lcssa
  br label %for_loop_body21.epil

for_loop_body21.epil:                             ; preds = %for_loop_body21.epil, %for_loop_body21.epil.preheader
  %lsr.iv92 = phi i64 [ %xtraiter62, %for_loop_body21.epil.preheader ], [ %lsr.iv.next93, %for_loop_body21.epil ]
  %indvars.iv46.epil = phi i64 [ %indvars.iv.next47.epil, %for_loop_body21.epil ], [ %indvars.iv46.unr, %for_loop_body21.epil.preheader ]
  %357 = load ptr, ptr %24, align 8
  %358 = load i32, ptr %25, align 4
  %359 = sext i32 %358 to i64
  %360 = load i32, ptr %26, align 4
  %361 = sext i32 %360 to i64
  %362 = mul nsw i64 %.pre-phi, %359
  %363 = add nsw i64 %362, %.pre-phi58
  %364 = mul i64 %363, %361
  %365 = getelementptr float, ptr %357, i64 %364
  %366 = shl nuw nsw i64 %indvars.iv46.epil, 2
  %scevgep91 = getelementptr i8, ptr %365, i64 %366
  store float 0.000000e+00, ptr %scevgep91, align 4
  %indvars.iv.next47.epil = add nuw nsw i64 %indvars.iv46.epil, 1
  %lsr.iv.next93 = add nsw i64 %lsr.iv92, -1
  %epil.iter.cmp.not = icmp eq i64 %lsr.iv.next93, 0
  br i1 %epil.iter.cmp.not, label %after_for23.loopexit71, label %for_loop_body21.epil, !llvm.loop !13

after_for23.loopexit:                             ; preds = %for_loop_body21.us.epil
  br label %after_for23

after_for23.loopexit71:                           ; preds = %for_loop_body21.epil
  br label %after_for23

after_for23:                                      ; preds = %after_for23.loopexit71, %after_for23.loopexit, %after_for23.loopexit61.unr-lcssa, %after_for23.loopexit.unr-lcssa, %after_for3
  %367 = add nsw i32 %.02442, 1
  %exitcond56.not = icmp eq i32 %367, %18
  br i1 %exitcond56.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext, align 8
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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
!12 = !{!"llvm.loop.unroll.disable"}
!13 = distinct !{!13, !12}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
