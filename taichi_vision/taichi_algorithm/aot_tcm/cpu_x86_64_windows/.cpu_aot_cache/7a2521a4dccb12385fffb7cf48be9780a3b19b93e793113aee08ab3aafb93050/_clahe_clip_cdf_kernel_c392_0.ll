; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_clahe_clip_cdf_kernel_c392_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_clahe_clip_cdf_kernel_c392_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 36
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 40
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 44
  %25 = load i32, ptr %24, align 4
  %26 = add i32 %21, -1
  %27 = sitofp i32 %25 to float
  %28 = sitofp i32 %26 to float
  %29 = icmp slt i32 %21, 0
  %30 = icmp slt i32 %16, %18
  br i1 %30, label %for_loop_test4.preheader.lr.ph, label %after_for

for_loop_test4.preheader.lr.ph:                   ; preds = %allocs
  %31 = icmp sgt i32 %21, 0
  %32 = getelementptr i8, ptr %19, i64 8
  %33 = getelementptr i8, ptr %19, i64 4
  %34 = getelementptr i8, ptr %19, i64 24
  %35 = getelementptr i8, ptr %19, i64 20
  %xtraiter = and i32 %21, 1
  %36 = icmp eq i32 %26, 0
  %unroll_iter = and i32 %21, 2147483646
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  %xtraiter49 = and i32 %21, 3
  %37 = icmp ult i32 %21, 4
  %unroll_iter51 = and i32 %21, 2147483644
  %lcmp.mod50.not = icmp eq i32 %xtraiter49, 0
  br label %for_loop_test4.preheader

after_for.loopexit:                               ; preds = %after_for20
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_test4.preheader:                         ; preds = %after_for20, %for_loop_test4.preheader.lr.ph
  %.02743 = phi i32 [ %16, %for_loop_test4.preheader.lr.ph ], [ %200, %after_for20 ]
  br i1 %31, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_test4.preheader
  br i1 %36, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader63

for_loop_body1.preheader63:                       ; preds = %for_loop_body1.preheader
  br label %for_loop_body1

for_loop_body1:                                   ; preds = %after_if.1, %for_loop_body1.preheader63
  %.02537 = phi i32 [ %78, %after_if.1 ], [ 0, %for_loop_body1.preheader63 ]
  %.02636 = phi i32 [ %.1.1, %after_if.1 ], [ 0, %for_loop_body1.preheader63 ]
  %38 = load ptr, ptr %32, align 8
  %39 = load i32, ptr %33, align 4
  %40 = mul i32 %.02743, %39
  %41 = add i32 %.02537, %40
  %42 = sext i32 %41 to i64
  %43 = getelementptr i32, ptr %38, i64 %42
  %44 = load i32, ptr %43, align 4
  %45 = icmp sgt i32 %44, %23
  br i1 %45, label %true_block, label %after_if

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %after_if.1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %.1.lcssa.ph = phi i32 [ poison, %for_loop_body1.preheader ], [ %.1.1, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.02537.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %78, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.02636.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %.1.1, %after_for3.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %after_for3.loopexit.unr-lcssa
  %46 = load ptr, ptr %32, align 8
  %47 = load i32, ptr %33, align 4
  %48 = mul i32 %47, %.02743
  %49 = add i32 %48, %.02537.unr
  %50 = sext i32 %49 to i64
  %51 = getelementptr i32, ptr %46, i64 %50
  %52 = load i32, ptr %51, align 4
  %53 = icmp sgt i32 %52, %23
  br i1 %53, label %true_block.epil, label %after_for3

true_block.epil:                                  ; preds = %for_loop_body1.epil
  %54 = sub i32 %.02636.unr, %23
  %55 = add i32 %54, %52
  store i32 %23, ptr %51, align 4
  br label %after_for3

after_for3:                                       ; preds = %true_block.epil, %for_loop_body1.epil, %after_for3.loopexit.unr-lcssa, %for_loop_test4.preheader
  %.026.lcssa = phi i32 [ 0, %for_loop_test4.preheader ], [ %.1.lcssa.ph, %after_for3.loopexit.unr-lcssa ], [ %55, %true_block.epil ], [ %.02636.unr, %for_loop_body1.epil ]
  %56 = sdiv i32 %.026.lcssa, %21
  %57 = mul i32 %56, %21
  %58 = xor i32 %.026.lcssa, %21
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %57, %.026.lcssa
  %61 = and i1 %59, %60
  %.neg33 = sext i1 %61 to i32
  %62 = add i32 %56, %.neg33
  %63 = mul i32 %62, %21
  %64 = sub i32 %.026.lcssa, %63
  br i1 %31, label %for_loop_body5.preheader, label %after_for7

for_loop_body5.preheader:                         ; preds = %after_for3
  br i1 %37, label %after_for7.loopexit.unr-lcssa, label %for_loop_body5.preheader62

for_loop_body5.preheader62:                       ; preds = %for_loop_body5.preheader
  br label %for_loop_body5

true_block:                                       ; preds = %for_loop_body1
  %65 = sub i32 %.02636, %23
  %66 = add i32 %65, %44
  store i32 %23, ptr %43, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body1
  %.1 = phi i32 [ %66, %true_block ], [ %.02636, %for_loop_body1 ]
  %67 = load ptr, ptr %32, align 8
  %68 = load i32, ptr %33, align 4
  %69 = mul i32 %.02743, %68
  %70 = add i32 %.02537, %69
  %71 = add i32 %70, 1
  %72 = sext i32 %71 to i64
  %73 = getelementptr i32, ptr %67, i64 %72
  %74 = load i32, ptr %73, align 4
  %75 = icmp sgt i32 %74, %23
  br i1 %75, label %true_block.1, label %after_if.1

true_block.1:                                     ; preds = %after_if
  %76 = sub i32 %.1, %23
  %77 = add i32 %76, %74
  store i32 %23, ptr %73, align 4
  br label %after_if.1

after_if.1:                                       ; preds = %true_block.1, %after_if
  %.1.1 = phi i32 [ %77, %true_block.1 ], [ %.1, %after_if ]
  %78 = add nuw i32 %.02537, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %78
  br i1 %niter.ncmp.1, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

for_loop_body5:                                   ; preds = %for_loop_body5, %for_loop_body5.preheader62
  %.02438 = phi i32 [ %114, %for_loop_body5 ], [ 0, %for_loop_body5.preheader62 ]
  %79 = load ptr, ptr %32, align 8
  %80 = load i32, ptr %33, align 4
  %81 = mul i32 %.02743, %80
  %82 = add i32 %.02438, %81
  %83 = sext i32 %82 to i64
  %84 = getelementptr i32, ptr %79, i64 %83
  %85 = load i32, ptr %84, align 4
  %86 = add i32 %85, %62
  store i32 %86, ptr %84, align 4
  %87 = load ptr, ptr %32, align 8
  %88 = load i32, ptr %33, align 4
  %89 = mul i32 %.02743, %88
  %90 = add i32 %.02438, %89
  %91 = add i32 %90, 1
  %92 = sext i32 %91 to i64
  %93 = getelementptr i32, ptr %87, i64 %92
  %94 = load i32, ptr %93, align 4
  %95 = add i32 %94, %62
  store i32 %95, ptr %93, align 4
  %96 = load ptr, ptr %32, align 8
  %97 = load i32, ptr %33, align 4
  %98 = mul i32 %.02743, %97
  %99 = add i32 %.02438, %98
  %100 = add i32 %99, 2
  %101 = sext i32 %100 to i64
  %102 = getelementptr i32, ptr %96, i64 %101
  %103 = load i32, ptr %102, align 4
  %104 = add i32 %103, %62
  store i32 %104, ptr %102, align 4
  %105 = load ptr, ptr %32, align 8
  %106 = load i32, ptr %33, align 4
  %107 = mul i32 %.02743, %106
  %108 = add i32 %.02438, %107
  %109 = add i32 %108, 3
  %110 = sext i32 %109 to i64
  %111 = getelementptr i32, ptr %105, i64 %110
  %112 = load i32, ptr %111, align 4
  %113 = add i32 %112, %62
  store i32 %113, ptr %111, align 4
  %114 = add nuw nsw i32 %.02438, 4
  %niter52.ncmp.3 = icmp eq i32 %unroll_iter51, %114
  br i1 %niter52.ncmp.3, label %after_for7.loopexit.unr-lcssa.loopexit, label %for_loop_body5

after_for7.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body5
  br label %after_for7.loopexit.unr-lcssa

after_for7.loopexit.unr-lcssa:                    ; preds = %after_for7.loopexit.unr-lcssa.loopexit, %for_loop_body5.preheader
  %.02438.unr = phi i32 [ 0, %for_loop_body5.preheader ], [ %114, %after_for7.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod50.not, label %after_for7, label %for_loop_body5.epil.preheader

for_loop_body5.epil.preheader:                    ; preds = %after_for7.loopexit.unr-lcssa
  br label %for_loop_body5.epil

for_loop_body5.epil:                              ; preds = %for_loop_body5.epil, %for_loop_body5.epil.preheader
  %lsr.iv = phi i32 [ %xtraiter49, %for_loop_body5.epil.preheader ], [ %lsr.iv.next, %for_loop_body5.epil ]
  %.02438.epil = phi i32 [ %123, %for_loop_body5.epil ], [ %.02438.unr, %for_loop_body5.epil.preheader ]
  %115 = load ptr, ptr %32, align 8
  %116 = load i32, ptr %33, align 4
  %117 = mul i32 %.02743, %116
  %118 = add i32 %.02438.epil, %117
  %119 = sext i32 %118 to i64
  %120 = getelementptr i32, ptr %115, i64 %119
  %121 = load i32, ptr %120, align 4
  %122 = add i32 %121, %62
  store i32 %122, ptr %120, align 4
  %123 = add nuw nsw i32 %.02438.epil, 1
  %lsr.iv.next = add nsw i32 %lsr.iv, -1
  %epil.iter.cmp.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %epil.iter.cmp.not, label %after_for7.loopexit, label %for_loop_body5.epil, !llvm.loop !10

after_for7.loopexit:                              ; preds = %for_loop_body5.epil
  br label %after_for7

after_for7:                                       ; preds = %after_for7.loopexit, %after_for7.loopexit.unr-lcssa, %after_for3
  %124 = icmp sgt i32 %64, 0
  br i1 %124, label %true_block9, label %after_if11

true_block9:                                      ; preds = %after_for7
  %125 = sdiv i32 %21, %64
  %126 = mul i32 %125, %64
  %127 = icmp ne i32 %126, %21
  %128 = and i1 %29, %127
  %.neg34 = sext i1 %128 to i32
  %129 = add i32 %125, %.neg34
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 1)
  br i1 %31, label %after_if17.preheader, label %after_for20

after_if17.preheader:                             ; preds = %true_block9
  br label %after_if17

after_if11.loopexit:                              ; preds = %after_if17
  br label %after_if11

after_if11:                                       ; preds = %after_if11.loopexit, %after_for7
  br i1 %31, label %for_loop_body18.preheader, label %after_for20

for_loop_body18.preheader:                        ; preds = %after_if11
  br i1 %36, label %after_for20.loopexit.unr-lcssa, label %for_loop_body18.preheader61

for_loop_body18.preheader61:                      ; preds = %for_loop_body18.preheader
  br label %for_loop_body18

after_if17:                                       ; preds = %after_if17, %after_if17.preheader
  %.02240 = phi i32 [ %139, %after_if17 ], [ %64, %after_if17.preheader ]
  %.02339 = phi i32 [ %140, %after_if17 ], [ 0, %after_if17.preheader ]
  %131 = load ptr, ptr %32, align 8
  %132 = load i32, ptr %33, align 4
  %133 = mul i32 %.02743, %132
  %134 = add i32 %.02339, %133
  %135 = sext i32 %134 to i64
  %136 = getelementptr i32, ptr %131, i64 %135
  %137 = load i32, ptr %136, align 4
  %138 = add i32 %137, 1
  store i32 %138, ptr %136, align 4
  %139 = add nsw i32 %.02240, -1
  %140 = add i32 %.02339, %130
  %141 = icmp samesign ugt i32 %.02240, 1
  %142 = icmp slt i32 %140, %21
  %spec.select = select i1 %141, i1 %142, i1 false
  br i1 %spec.select, label %after_if17, label %after_if11.loopexit

for_loop_body18:                                  ; preds = %for_loop_body18, %for_loop_body18.preheader61
  %.042 = phi i32 [ %181, %for_loop_body18 ], [ 0, %for_loop_body18.preheader61 ]
  %.02041 = phi i32 [ %169, %for_loop_body18 ], [ 0, %for_loop_body18.preheader61 ]
  %143 = load ptr, ptr %32, align 8
  %144 = load i32, ptr %33, align 4
  %145 = mul i32 %.02743, %144
  %146 = add i32 %.042, %145
  %147 = sext i32 %146 to i64
  %148 = getelementptr i32, ptr %143, i64 %147
  %149 = load i32, ptr %148, align 4
  %150 = add i32 %149, %.02041
  %151 = sitofp i32 %150 to float
  %152 = fmul reassoc ninf nsz float %151, %28
  %153 = fdiv reassoc ninf nsz float %152, %27
  %154 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %153, float %28)
  %155 = load ptr, ptr %34, align 8
  %156 = load i32, ptr %35, align 4
  %157 = mul i32 %.02743, %156
  %158 = add i32 %.042, %157
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %155, i64 %159
  store float %154, ptr %160, align 4
  %161 = load ptr, ptr %32, align 8
  %162 = load i32, ptr %33, align 4
  %163 = mul i32 %.02743, %162
  %164 = add i32 %.042, %163
  %165 = add i32 %164, 1
  %166 = sext i32 %165 to i64
  %167 = getelementptr i32, ptr %161, i64 %166
  %168 = load i32, ptr %167, align 4
  %169 = add i32 %168, %150
  %170 = sitofp i32 %169 to float
  %171 = fmul reassoc ninf nsz float %170, %28
  %172 = fdiv reassoc ninf nsz float %171, %27
  %173 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %172, float %28)
  %174 = load ptr, ptr %34, align 8
  %175 = load i32, ptr %35, align 4
  %176 = mul i32 %.02743, %175
  %177 = add i32 %.042, %176
  %178 = add i32 %177, 1
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, ptr %174, i64 %179
  store float %173, ptr %180, align 4
  %181 = add nuw i32 %.042, 2
  %niter57.ncmp.1 = icmp eq i32 %unroll_iter, %181
  br i1 %niter57.ncmp.1, label %after_for20.loopexit.unr-lcssa.loopexit, label %for_loop_body18

after_for20.loopexit.unr-lcssa.loopexit:          ; preds = %for_loop_body18
  br label %after_for20.loopexit.unr-lcssa

after_for20.loopexit.unr-lcssa:                   ; preds = %after_for20.loopexit.unr-lcssa.loopexit, %for_loop_body18.preheader
  %.042.unr = phi i32 [ 0, %for_loop_body18.preheader ], [ %181, %after_for20.loopexit.unr-lcssa.loopexit ]
  %.02041.unr = phi i32 [ 0, %for_loop_body18.preheader ], [ %169, %after_for20.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for20, label %for_loop_body18.epil

for_loop_body18.epil:                             ; preds = %after_for20.loopexit.unr-lcssa
  %182 = load ptr, ptr %32, align 8
  %183 = load i32, ptr %33, align 4
  %184 = mul i32 %183, %.02743
  %185 = add i32 %184, %.042.unr
  %186 = sext i32 %185 to i64
  %187 = getelementptr i32, ptr %182, i64 %186
  %188 = load i32, ptr %187, align 4
  %189 = add i32 %188, %.02041.unr
  %190 = sitofp i32 %189 to float
  %191 = fmul reassoc ninf nsz float %190, %28
  %192 = fdiv reassoc ninf nsz float %191, %27
  %193 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %192, float %28)
  %194 = load ptr, ptr %34, align 8
  %195 = load i32, ptr %35, align 4
  %196 = mul i32 %195, %.02743
  %197 = add i32 %196, %.042.unr
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %194, i64 %198
  store float %193, ptr %199, align 4
  br label %after_for20

after_for20:                                      ; preds = %for_loop_body18.epil, %after_for20.loopexit.unr-lcssa, %after_if11, %true_block9
  %200 = add nsw i32 %.02743, 1
  %exitcond47.not = icmp eq i32 %200, %18
  br i1 %exitcond47.not, label %after_for.loopexit, label %for_loop_test4.preheader
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !12

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !14

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
!11 = !{!"llvm.loop.unroll.disable"}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
