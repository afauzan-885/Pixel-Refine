; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.38 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @remap_accumulate_cfa_weighted_plane_kernel_c772_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 108
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
  %11 = getelementptr i8, ptr %10, i64 100
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
  %25 = getelementptr i8, ptr %24, i64 104
  %26 = load i32, ptr %25, align 4
  %27 = add i32 %26, -1
  %28 = load ptr, ptr %4, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 28
  store i32 %27, ptr %31, align 4
  %32 = sitofp i32 %27 to float
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 96
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
  %48 = getelementptr i8, ptr %47, i64 116
  %49 = load i32, ptr %48, align 4
  %50 = load ptr, ptr %4, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 48
  store i32 %49, ptr %53, align 4
  %54 = sitofp i32 %49 to float
  %55 = sitofp i32 %12 to float
  %56 = fdiv reassoc ninf nsz float %54, %55
  %57 = load ptr, ptr %4, align 8
  %58 = getelementptr inbounds nuw i8, ptr %57, i64 32872
  %59 = load ptr, ptr %58, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 40
  store float %56, ptr %60, align 4
  %61 = load ptr, ptr %context, align 8
  %62 = getelementptr i8, ptr %61, i64 112
  %63 = load i32, ptr %62, align 4
  %64 = load ptr, ptr %4, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 32872
  %66 = load ptr, ptr %65, align 8
  %67 = getelementptr inbounds nuw i8, ptr %66, i64 52
  store i32 %63, ptr %67, align 4
  %68 = sitofp i32 %63 to float
  %69 = sitofp i32 %35 to float
  %70 = fdiv reassoc ninf nsz float %68, %69
  %71 = load ptr, ptr %4, align 8
  %72 = getelementptr inbounds nuw i8, ptr %71, i64 32872
  %73 = load ptr, ptr %72, align 8
  %74 = getelementptr inbounds nuw i8, ptr %73, i64 44
  store float %70, ptr %74, align 4
  %75 = load ptr, ptr %context, align 8
  %76 = getelementptr i8, ptr %75, i64 120
  %77 = load i32, ptr %76, align 4
  %78 = load ptr, ptr %4, align 8
  %79 = getelementptr inbounds nuw i8, ptr %78, i64 32872
  %80 = load ptr, ptr %79, align 8
  %81 = getelementptr inbounds nuw i8, ptr %80, i64 36
  store i32 %77, ptr %81, align 4
  %82 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %83 = load ptr, ptr %context, align 8
  %84 = getelementptr i8, ptr %83, i64 124
  %85 = load i32, ptr %84, align 4
  %86 = load ptr, ptr %4, align 8
  %87 = getelementptr inbounds nuw i8, ptr %86, i64 32872
  %88 = load ptr, ptr %87, align 8
  %89 = getelementptr inbounds nuw i8, ptr %88, i64 32
  store i32 %85, ptr %89, align 4
  %90 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %91 = load ptr, ptr %4, align 8
  %92 = getelementptr inbounds nuw i8, ptr %91, i64 32872
  %93 = load ptr, ptr %92, align 8
  %94 = getelementptr inbounds nuw i8, ptr %93, i64 4
  store i32 %90, ptr %94, align 4
  %95 = mul i32 %90, %82
  %96 = load ptr, ptr %4, align 8
  %97 = getelementptr inbounds nuw i8, ptr %96, i64 32872
  %98 = load ptr, ptr %97, align 8
  store i32 %95, ptr %98, align 4
  ret void
}

define void @remap_accumulate_cfa_weighted_plane_kernel_c772_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 128
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 132
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %25 = shl i32 %16, 1
  %26 = add i32 %23, %25
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %lsr.iv = phi i32 [ %26, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if3 ]
  %.01024 = phi i32 [ %181, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.01024, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.01024
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.01024, %33
  %37 = and i1 %35, %36
  %.neg16 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg16
  %39 = mul i32 %31, -1
  %40 = mul i32 %39, %38
  %41 = add i32 %.01024, %40
  %42 = shl i32 %38, 1
  %43 = add i32 %42, %21
  %44 = mul i32 %31, -2
  %45 = mul i32 %44, %38
  %46 = add i32 %lsr.iv, %45
  %47 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %48 = load i32, ptr %47, align 4
  %49 = icmp slt i32 %43, %48
  br i1 %49, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %50 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %51 = load i32, ptr %50, align 4
  %52 = icmp slt i32 %46, %51
  br i1 %52, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %53 = sitofp i32 %46 to float
  %54 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = sitofp i32 %43 to float
  %58 = getelementptr inbounds nuw i8, ptr %29, i64 20
  %59 = load float, ptr %58, align 4
  %60 = fmul reassoc ninf nsz float %59, %57
  %61 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %62 = fptosi float %61 to i32
  %63 = tail call reassoc ninf nsz float @llvm.floor.f32(float %60)
  %64 = fptosi float %63 to i32
  %65 = sitofp i32 %62 to float
  %66 = fsub reassoc ninf nsz float %56, %65
  %67 = sitofp i32 %64 to float
  %68 = fsub reassoc ninf nsz float %60, %67
  %69 = tail call i32 @llvm.abs.i32(i32 %62, i1 true)
  %70 = getelementptr inbounds nuw i8, ptr %29, i64 24
  %71 = load i32, ptr %70, align 4
  %72 = sub i32 %69, %71
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = shl nuw i32 %73, 1
  %75 = sub i32 %69, %74
  %76 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %77 = tail call i32 @llvm.smin.i32(i32 %71, i32 %76)
  %78 = tail call i32 @llvm.abs.i32(i32 %64, i1 true)
  %79 = getelementptr inbounds nuw i8, ptr %29, i64 28
  %80 = load i32, ptr %79, align 4
  %81 = sub i32 %78, %80
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = shl nuw i32 %82, 1
  %84 = sub i32 %78, %83
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %80, i32 %85)
  %87 = add i32 %62, 1
  %88 = tail call i32 @llvm.abs.i32(i32 %87, i1 true)
  %89 = sub i32 %88, %71
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = shl nuw i32 %90, 1
  %92 = sub i32 %88, %91
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %71, i32 %93)
  %95 = add i32 %64, 1
  %96 = tail call i32 @llvm.abs.i32(i32 %95, i1 true)
  %97 = sub i32 %96, %80
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = shl nuw i32 %98, 1
  %100 = sub i32 %96, %99
  %101 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %102 = tail call i32 @llvm.smin.i32(i32 %80, i32 %101)
  %103 = load ptr, ptr %0, align 8
  %104 = getelementptr i8, ptr %103, i64 32
  %105 = load ptr, ptr %104, align 8
  %106 = getelementptr i8, ptr %103, i64 20
  %107 = load i32, ptr %106, align 4
  %108 = getelementptr i8, ptr %103, i64 24
  %109 = load i32, ptr %108, align 4
  %110 = mul i32 %86, %107
  %111 = add i32 %110, %77
  %112 = mul i32 %111, %109
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %105, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = add i32 %110, %94
  %117 = mul i32 %116, %109
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, ptr %105, i64 %118
  %120 = load float, ptr %119, align 4
  %121 = mul i32 %102, %107
  %122 = add i32 %121, %77
  %123 = mul i32 %122, %109
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %105, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %121, %94
  %128 = mul i32 %127, %109
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %105, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = fsub reassoc ninf nsz float 1.000000e+00, %66
  %133 = fmul reassoc ninf nsz float %115, %132
  %134 = fmul reassoc ninf nsz float %120, %66
  %135 = fadd reassoc ninf nsz float %134, %133
  %136 = fmul reassoc ninf nsz float %126, %132
  %137 = fmul reassoc ninf nsz float %131, %66
  %138 = fadd reassoc ninf nsz float %137, %136
  %139 = fsub reassoc ninf nsz float 1.000000e+00, %68
  %140 = fmul reassoc ninf nsz float %135, %139
  %141 = fmul reassoc ninf nsz float %138, %68
  %142 = fadd reassoc ninf nsz float %141, %140
  %143 = add i32 %112, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %105, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %117, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %105, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %123, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %105, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %128, 1
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %105, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %146, %132
  %160 = fmul reassoc ninf nsz float %150, %66
  %161 = fadd reassoc ninf nsz float %160, %159
  %162 = fmul reassoc ninf nsz float %154, %132
  %163 = fmul reassoc ninf nsz float %158, %66
  %164 = fadd reassoc ninf nsz float %163, %162
  %165 = fmul reassoc ninf nsz float %161, %139
  %166 = fmul reassoc ninf nsz float %164, %68
  %167 = fadd reassoc ninf nsz float %166, %165
  %168 = sitofp i32 %41 to float
  %169 = getelementptr i8, ptr %103, i64 140
  %170 = load float, ptr %169, align 4
  %171 = fmul reassoc ninf nsz float %142, 5.000000e-01
  %172 = fmul reassoc ninf nsz float %171, %170
  %173 = fadd reassoc ninf nsz float %172, %168
  %174 = sitofp i32 %38 to float
  %175 = getelementptr i8, ptr %103, i64 144
  %176 = load float, ptr %175, align 4
  %177 = fmul reassoc ninf nsz float %176, 5.000000e-01
  %178 = fmul reassoc ninf nsz float %177, %167
  %179 = fadd reassoc ninf nsz float %178, %174
  %180 = fcmp reassoc ninf nsz ult float %173, 0.000000e+00
  br i1 %180, label %after_if3, label %true_block4

after_if3:                                        ; preds = %true_block13, %true_block10, %true_block4, %true_block1, %true_block, %for_loop_body
  %181 = add nsw i32 %.01024, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %181
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %182 = getelementptr inbounds nuw i8, ptr %29, i64 32
  %183 = load i32, ptr %182, align 4
  %184 = add i32 %183, -1
  %185 = sitofp i32 %184 to float
  %186 = fcmp reassoc ninf nsz ugt float %173, %185
  %187 = fcmp reassoc ninf nsz ult float %179, 0.000000e+00
  %or.cond = select i1 %186, i1 true, i1 %187
  br i1 %or.cond, label %after_if3, label %true_block10

true_block10:                                     ; preds = %true_block4
  %188 = getelementptr inbounds nuw i8, ptr %29, i64 36
  %189 = load i32, ptr %188, align 4
  %190 = add i32 %189, -1
  %191 = sitofp i32 %190 to float
  %192 = fcmp reassoc ninf nsz ugt float %179, %191
  br i1 %192, label %after_if3, label %true_block13

true_block13:                                     ; preds = %true_block10
  %193 = tail call reassoc ninf nsz float @llvm.floor.f32(float %173)
  %194 = fptosi float %193 to i32
  %195 = tail call reassoc ninf nsz float @llvm.floor.f32(float %179)
  %196 = fptosi float %195 to i32
  %197 = add i32 %194, 1
  %198 = tail call i32 @llvm.smin.i32(i32 %197, i32 %184)
  %199 = add i32 %196, 1
  %200 = tail call i32 @llvm.smin.i32(i32 %199, i32 %190)
  %201 = sitofp i32 %194 to float
  %202 = fsub reassoc ninf nsz float %173, %201
  %203 = sitofp i32 %196 to float
  %204 = fsub reassoc ninf nsz float %179, %203
  %205 = fsub reassoc ninf nsz float 1.000000e+00, %202
  %206 = getelementptr i8, ptr %103, i64 8
  %207 = load ptr, ptr %206, align 8
  %208 = getelementptr i8, ptr %103, i64 4
  %209 = load i32, ptr %208, align 4
  %210 = mul i32 %209, %196
  %211 = add i32 %210, %194
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %207, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = fmul reassoc ninf nsz float %214, %205
  %216 = add i32 %210, %198
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %207, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %219, %202
  %221 = mul i32 %209, %200
  %222 = add i32 %221, %194
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %207, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = fmul reassoc ninf nsz float %225, %205
  %227 = add i32 %221, %198
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, ptr %207, i64 %228
  %230 = load float, ptr %229, align 4
  %231 = fmul reassoc ninf nsz float %230, %202
  %reass.add = fadd reassoc ninf nsz float %231, %226
  %reass.add18 = fadd reassoc ninf nsz float %220, %215
  %232 = fsub reassoc ninf nsz float %reass.add, %reass.add18
  %233 = fmul reassoc ninf nsz float %204, %232
  %234 = fadd reassoc ninf nsz float %reass.add18, %233
  %235 = getelementptr inbounds nuw i8, ptr %29, i64 40
  %236 = load float, ptr %235, align 4
  %237 = fmul reassoc ninf nsz float %236, %53
  %238 = getelementptr inbounds nuw i8, ptr %29, i64 44
  %239 = load float, ptr %238, align 4
  %240 = fmul reassoc ninf nsz float %239, %57
  %241 = tail call reassoc ninf nsz float @llvm.floor.f32(float %237)
  %242 = fptosi float %241 to i32
  %243 = tail call i32 @llvm.smax.i32(i32 %242, i32 0)
  %244 = tail call reassoc ninf nsz float @llvm.floor.f32(float %240)
  %245 = fptosi float %244 to i32
  %246 = tail call i32 @llvm.smax.i32(i32 %245, i32 0)
  %247 = add nuw i32 %243, 1
  %248 = getelementptr inbounds nuw i8, ptr %29, i64 48
  %249 = load i32, ptr %248, align 4
  %250 = add i32 %249, -1
  %251 = tail call i32 @llvm.smin.i32(i32 %247, i32 %250)
  %252 = add nuw i32 %246, 1
  %253 = getelementptr inbounds nuw i8, ptr %29, i64 52
  %254 = load i32, ptr %253, align 4
  %255 = add i32 %254, -1
  %256 = tail call i32 @llvm.smin.i32(i32 %252, i32 %255)
  %257 = uitofp nneg i32 %243 to float
  %258 = fsub reassoc ninf nsz float %237, %257
  %259 = uitofp nneg i32 %246 to float
  %260 = fsub reassoc ninf nsz float %240, %259
  %261 = fsub reassoc ninf nsz float 1.000000e+00, %258
  %262 = getelementptr i8, ptr %103, i64 136
  %263 = load i32, ptr %262, align 4
  %264 = getelementptr i8, ptr %103, i64 56
  %265 = load ptr, ptr %264, align 8
  %266 = getelementptr i8, ptr %103, i64 44
  %267 = load i32, ptr %266, align 4
  %268 = getelementptr i8, ptr %103, i64 48
  %269 = load i32, ptr %268, align 4
  %270 = mul i32 %267, %246
  %271 = add i32 %270, %243
  %272 = mul i32 %271, %269
  %273 = add i32 %272, %263
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, ptr %265, i64 %274
  %276 = load float, ptr %275, align 4
  %277 = fmul reassoc ninf nsz float %276, %261
  %278 = add i32 %270, %251
  %279 = mul i32 %278, %269
  %280 = add i32 %279, %263
  %281 = sext i32 %280 to i64
  %282 = getelementptr float, ptr %265, i64 %281
  %283 = load float, ptr %282, align 4
  %284 = fmul reassoc ninf nsz float %283, %258
  %285 = mul i32 %256, %267
  %286 = add i32 %285, %243
  %287 = mul i32 %286, %269
  %288 = add i32 %287, %263
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %265, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = fmul reassoc ninf nsz float %291, %261
  %293 = add i32 %285, %251
  %294 = mul i32 %293, %269
  %295 = add i32 %294, %263
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, ptr %265, i64 %296
  %298 = load float, ptr %297, align 4
  %299 = fmul reassoc ninf nsz float %298, %258
  %reass.add20 = fadd reassoc ninf nsz float %299, %292
  %reass.add22 = fadd reassoc ninf nsz float %277, %284
  %300 = fsub reassoc ninf nsz float %reass.add20, %reass.add22
  %301 = fmul reassoc ninf nsz float %260, %300
  %302 = fadd reassoc ninf nsz float %reass.add22, %301
  %303 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %302, float 1.000000e+00)
  %304 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %303, float 0.000000e+00)
  %305 = fmul reassoc ninf nsz float %304, %234
  %306 = getelementptr i8, ptr %103, i64 72
  %307 = load ptr, ptr %306, align 8
  %308 = getelementptr i8, ptr %103, i64 68
  %309 = load i32, ptr %308, align 4
  %310 = mul i32 %309, %43
  %311 = shl i32 %31, 1
  %312 = mul i32 %311, %38
  %313 = sub i32 %310, %312
  %314 = add i32 %lsr.iv, %313
  %315 = sext i32 %314 to i64
  %316 = getelementptr float, ptr %307, i64 %315
  %317 = atomicrmw fadd ptr %316, float %305 seq_cst, align 4
  %318 = load ptr, ptr %0, align 8
  %319 = getelementptr i8, ptr %318, i64 88
  %320 = load ptr, ptr %319, align 8
  %321 = getelementptr i8, ptr %318, i64 84
  %322 = load i32, ptr %321, align 4
  %323 = mul i32 %322, %43
  %324 = sub i32 %323, %312
  %325 = add i32 %lsr.iv, %324
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, ptr %320, i64 %326
  %328 = atomicrmw fadd ptr %327, float %304 seq_cst, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.38, align 8
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
