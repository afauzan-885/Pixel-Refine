; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_ha_red_blue_direct_kernel_c708_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 76
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 72
  %4 = load float, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 16
  store float %4, ptr %9, align 4
  %10 = fsub reassoc ninf nsz float %2, %4
  %11 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %10, float 1.000000e+00)
  %12 = fdiv reassoc ninf nsz float 1.000000e+00, %11
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 20
  store float %12, ptr %16, align 4
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 56
  %19 = load float, ptr %18, align 4
  %20 = load ptr, ptr %5, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 24
  store float %19, ptr %23, align 4
  %24 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %19, float 0x3FB99999A0000000)
  %25 = fdiv reassoc ninf nsz float 1.000000e+00, %24
  %26 = load ptr, ptr %5, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32
  store float %25, ptr %29, align 4
  %30 = load ptr, ptr %context, align 8
  %31 = getelementptr i8, ptr %30, i64 60
  %32 = load float, ptr %31, align 4
  %33 = getelementptr i8, ptr %30, i64 68
  %34 = load float, ptr %33, align 4
  %35 = fadd reassoc ninf nsz float %34, %32
  %36 = fmul reassoc ninf nsz float %35, 5.000000e-01
  %37 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %36, float 0x3FB99999A0000000)
  %38 = fdiv reassoc ninf nsz float 1.000000e+00, %37
  %39 = load ptr, ptr %5, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 36
  store float %38, ptr %42, align 4
  %43 = load ptr, ptr %context, align 8
  %44 = getelementptr i8, ptr %43, i64 64
  %45 = load float, ptr %44, align 4
  %46 = load ptr, ptr %5, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 32872
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 28
  store float %45, ptr %49, align 4
  %50 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %45, float 0x3FB99999A0000000)
  %51 = fdiv reassoc ninf nsz float 1.000000e+00, %50
  %52 = load ptr, ptr %5, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 32872
  %54 = load ptr, ptr %53, align 8
  %55 = getelementptr inbounds nuw i8, ptr %54, i64 40
  store float %51, ptr %55, align 4
  %56 = load ptr, ptr %context, align 8
  %57 = getelementptr i8, ptr %56, i64 80
  %58 = load i32, ptr %57, align 4
  %59 = load ptr, ptr %5, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 32872
  %61 = load ptr, ptr %60, align 8
  %62 = getelementptr inbounds nuw i8, ptr %61, i64 8
  store i32 %58, ptr %62, align 4
  %63 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %64 = load ptr, ptr %context, align 8
  %65 = getelementptr i8, ptr %64, i64 84
  %66 = load i32, ptr %65, align 4
  %67 = load ptr, ptr %5, align 8
  %68 = getelementptr inbounds nuw i8, ptr %67, i64 32872
  %69 = load ptr, ptr %68, align 8
  %70 = getelementptr inbounds nuw i8, ptr %69, i64 12
  store i32 %66, ptr %70, align 4
  %71 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %72 = load ptr, ptr %5, align 8
  %73 = getelementptr inbounds nuw i8, ptr %72, i64 32872
  %74 = load ptr, ptr %73, align 8
  %75 = getelementptr inbounds nuw i8, ptr %74, i64 4
  store i32 %71, ptr %75, align 4
  %76 = mul i32 %71, %63
  %77 = load ptr, ptr %5, align 8
  %78 = getelementptr inbounds nuw i8, ptr %77, i64 32872
  %79 = load ptr, ptr %78, align 8
  store i32 %76, ptr %79, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_ha_red_blue_direct_kernel_c708_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 88
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 96
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 100
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 24
  %30 = getelementptr i8, ptr %19, i64 20
  %31 = getelementptr i8, ptr %19, i64 48
  %32 = getelementptr i8, ptr %19, i64 36
  %33 = getelementptr i8, ptr %19, i64 40
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.03292 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %188, %after_if ]
  %34 = load ptr, ptr %3, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 4
  %38 = load i32, ptr %37, align 4
  %39 = sdiv i32 %.03292, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.03292
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.03292, %40
  %44 = and i1 %42, %43
  %.neg51 = sext i1 %44 to i32
  %45 = add i32 %39, %.neg51
  %46 = mul i32 %45, %38
  %47 = mul i32 %38, -1
  %48 = mul i32 %47, %45
  %49 = add i32 %.03292, %48
  %50 = sdiv i32 %45, 2
  %51 = icmp slt i32 %45, 0
  %52 = shl nsw i32 %50, 1
  %53 = icmp ne i32 %52, %45
  %54 = and i1 %51, %53
  %.neg52 = sext i1 %54 to i32
  %55 = add nsw i32 %50, %.neg52
  %56 = shl i32 %55, 1
  %57 = sdiv i32 %49, 2
  %58 = icmp slt i32 %49, 0
  %59 = shl nsw i32 %57, 1
  %60 = icmp ne i32 %49, %59
  %61 = and i1 %58, %60
  %.neg53 = sext i1 %61 to i32
  %62 = add nsw i32 %57, %.neg53
  %63 = shl i32 %62, 1
  %.not = icmp eq i32 %45, %56
  %.not54 = icmp eq i32 %49, %63
  %64 = select i1 %.not54, i32 %21, i32 %23
  %65 = select i1 %.not54, i32 %25, i32 %27
  %66 = select i1 %.not, i32 %64, i32 %65
  %67 = load ptr, ptr %29, align 8
  %68 = load i32, ptr %30, align 4
  %69 = sub i32 %68, %38
  %70 = mul i32 %69, %45
  %71 = add i32 %.03292, %70
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %67, i64 %72
  %74 = load float, ptr %73, align 4
  switch i32 %66, label %false_block14 [
    i32 0, label %true_block
    i32 2, label %true_block13
  ]

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %75 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %76 = load i32, ptr %75, align 4
  %77 = add i32 %76, -1
  %78 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %79 = tail call i32 @llvm.smin.i32(i32 %77, i32 %78)
  %80 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %81 = load i32, ptr %80, align 4
  %82 = add i32 %81, -1
  %83 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %82, i32 %83)
  %85 = load ptr, ptr %0, align 8
  %86 = getelementptr i8, ptr %85, i64 8
  %87 = load ptr, ptr %86, align 8
  %88 = getelementptr i8, ptr %85, i64 4
  %89 = load i32, ptr %88, align 4
  %90 = mul i32 %89, %79
  %91 = add i32 %90, %84
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %87, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %96 = load float, ptr %95, align 4
  %97 = fsub reassoc ninf nsz float %94, %96
  %98 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %99 = load float, ptr %98, align 4
  %100 = fmul reassoc ninf nsz float %97, %99
  %101 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %100, float 0.000000e+00)
  %102 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %101, float 1.000000e+00)
  %103 = getelementptr inbounds nuw i8, ptr %36, i64 24
  %104 = load float, ptr %103, align 4
  %105 = fmul reassoc ninf nsz float %102, %104
  %106 = icmp sgt i32 %45, 0
  %107 = icmp slt i32 %45, %77
  %or.cond = and i1 %106, %107
  br i1 %or.cond, label %true_block4, label %after_if

after_if:                                         ; preds = %true_block61, %true_block58, %after_if57, %true_block49, %true_block46, %after_if45, %true_block25, %true_block19, %true_block13, %true_block10, %true_block4, %true_block
  %.030 = phi float [ %105, %true_block10 ], [ %402, %true_block25 ], [ %.131, %true_block49 ], [ %.2, %true_block61 ], [ %105, %true_block ], [ %105, %true_block4 ], [ %74, %true_block13 ], [ %74, %true_block19 ], [ %.131, %after_if45 ], [ %.131, %true_block46 ], [ %.2, %after_if57 ], [ %.2, %true_block58 ]
  %.029 = phi float [ %276, %true_block10 ], [ %307, %true_block25 ], [ %520, %true_block49 ], [ %636, %true_block61 ], [ %74, %true_block ], [ %74, %true_block4 ], [ %307, %true_block13 ], [ %307, %true_block19 ], [ %74, %after_if45 ], [ %74, %true_block46 ], [ %74, %after_if57 ], [ %74, %true_block58 ]
  %108 = getelementptr inbounds nuw i8, ptr %36, i64 32
  %109 = load float, ptr %108, align 4
  %110 = fmul reassoc ninf nsz float %109, %.030
  %111 = getelementptr inbounds nuw i8, ptr %36, i64 36
  %112 = load float, ptr %111, align 4
  %113 = fmul reassoc ninf nsz float %112, %74
  %114 = getelementptr inbounds nuw i8, ptr %36, i64 40
  %115 = load float, ptr %114, align 4
  %116 = fmul reassoc ninf nsz float %115, %.029
  %117 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %113, float %116)
  %118 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %110, float %117)
  %119 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %113, float %116)
  %120 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %110, float %119)
  %121 = fmul reassoc ninf nsz float %118, 0x40029ACA60000000
  %122 = fadd reassoc ninf nsz float %121, 0xBFF47711E0000000
  %123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %122, float 0.000000e+00)
  %124 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %123, float 1.000000e+00)
  %factor88 = fmul reassoc ninf nsz float %124, -2.000000e+00
  %125 = fadd reassoc ninf nsz float %factor88, 3.000000e+00
  %126 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0x3EE4F8B580000000)
  %127 = fmul reassoc ninf nsz float %120, 0x4001C71C80000000
  %128 = fdiv reassoc ninf nsz float %127, %126
  %129 = fadd reassoc ninf nsz float %128, 0xBFEC71C740000000
  %130 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %129, float 0.000000e+00)
  %131 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %130, float 1.000000e+00)
  %factor91 = fmul reassoc ninf nsz float %131, -2.000000e+00
  %132 = fadd reassoc ninf nsz float %factor91, 3.000000e+00
  %133 = fmul reassoc ninf nsz float %131, %124
  %134 = fmul reassoc ninf nsz float %133, %133
  %135 = fmul reassoc ninf nsz float %134, %125
  %136 = fmul reassoc ninf nsz float %135, %132
  %137 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %74, float %.029)
  %138 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.030, float %137)
  %139 = fsub reassoc ninf nsz float 1.000000e+00, %136
  %140 = fmul reassoc ninf nsz float %139, %.030
  %141 = fmul reassoc ninf nsz float %136, %138
  %142 = fadd reassoc ninf nsz float %140, %141
  %143 = fmul reassoc ninf nsz float %139, %74
  %144 = fadd reassoc ninf nsz float %143, %141
  %145 = fmul reassoc ninf nsz float %139, %.029
  %146 = fadd reassoc ninf nsz float %145, %141
  %147 = fmul reassoc ninf nsz float %142, %142
  %148 = fadd reassoc ninf nsz float %147, 1.000000e+00
  %149 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %148)
  %150 = fdiv reassoc ninf nsz float %142, %149
  %151 = load ptr, ptr %31, align 8
  %152 = load i32, ptr %32, align 4
  %153 = load i32, ptr %33, align 4
  %154 = sub i32 %152, %38
  %155 = mul i32 %154, %45
  %156 = add i32 %.03292, %155
  %157 = mul i32 %156, %153
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %151, i64 %158
  store float %150, ptr %159, align 4
  %160 = fmul reassoc ninf nsz float %144, %144
  %161 = fadd reassoc ninf nsz float %160, 1.000000e+00
  %162 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %161)
  %163 = fdiv reassoc ninf nsz float %144, %162
  %164 = load ptr, ptr %31, align 8
  %165 = load i32, ptr %32, align 4
  %166 = load i32, ptr %33, align 4
  %167 = sub i32 %165, %38
  %168 = mul i32 %167, %45
  %169 = add i32 %.03292, %168
  %170 = mul i32 %169, %166
  %171 = add i32 %170, 1
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %164, i64 %172
  store float %163, ptr %173, align 4
  %174 = fmul reassoc ninf nsz float %146, %146
  %175 = fadd reassoc ninf nsz float %174, 1.000000e+00
  %176 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %175)
  %177 = fdiv reassoc ninf nsz float %146, %176
  %178 = load ptr, ptr %31, align 8
  %179 = load i32, ptr %32, align 4
  %180 = load i32, ptr %33, align 4
  %181 = sub i32 %179, %38
  %182 = mul i32 %181, %45
  %183 = add i32 %.03292, %182
  %184 = mul i32 %183, %180
  %185 = add i32 %184, 2
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %178, i64 %186
  store float %177, ptr %187, align 4
  %188 = add nsw i32 %.03292, 1
  %exitcond.not = icmp eq i32 %18, %188
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block
  %189 = icmp sgt i32 %49, 0
  %190 = icmp slt i32 %49, %82
  %spec.select = and i1 %189, %190
  br i1 %spec.select, label %true_block10, label %after_if

true_block10:                                     ; preds = %true_block4
  %191 = add nsw i32 %45, -1
  %192 = mul i32 %191, %68
  %193 = sub i32 %192, %46
  %194 = add i32 %.03292, %193
  %195 = add i32 %194, -1
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, ptr %67, i64 %196
  %198 = load float, ptr %197, align 4
  %199 = add nuw nsw i32 %45, 1
  %200 = mul i32 %199, %68
  %201 = sub i32 %200, %46
  %202 = add i32 %.03292, %201
  %203 = add i32 %202, 1
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %67, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = add i32 %194, 1
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %67, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i32 %202, -1
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %67, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = fsub reassoc ninf nsz float %198, %206
  %216 = tail call noundef float @llvm.fabs.f32(float %215)
  %217 = fadd reassoc ninf nsz float %216, 1.000000e+00
  %218 = fdiv reassoc ninf nsz float 1.000000e+00, %217
  %219 = fsub reassoc ninf nsz float %210, %214
  %220 = tail call noundef float @llvm.fabs.f32(float %219)
  %221 = fadd reassoc ninf nsz float %220, 1.000000e+00
  %222 = fdiv reassoc ninf nsz float 1.000000e+00, %221
  %223 = mul i32 %89, %191
  %224 = sub i32 %223, %46
  %225 = add i32 %.03292, %224
  %226 = add i32 %225, -1
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %87, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = fsub reassoc ninf nsz float %229, %96
  %231 = fmul reassoc ninf nsz float %230, %99
  %232 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %231, float 0.000000e+00)
  %233 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %232, float 1.000000e+00)
  %234 = getelementptr inbounds nuw i8, ptr %36, i64 28
  %235 = load float, ptr %234, align 4
  %236 = mul i32 %89, %199
  %237 = sub i32 %236, %46
  %238 = add i32 %.03292, %237
  %239 = add i32 %238, 1
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, ptr %87, i64 %240
  %242 = load float, ptr %241, align 4
  %243 = fsub reassoc ninf nsz float %242, %96
  %244 = fmul reassoc ninf nsz float %243, %99
  %245 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %244, float 0.000000e+00)
  %246 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %245, float 1.000000e+00)
  %247 = add i32 %225, 1
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %87, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = fsub reassoc ninf nsz float %250, %96
  %252 = fmul reassoc ninf nsz float %251, %99
  %253 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %252, float 0.000000e+00)
  %254 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %253, float 1.000000e+00)
  %255 = add i32 %238, -1
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, ptr %87, i64 %256
  %258 = load float, ptr %257, align 4
  %259 = fsub reassoc ninf nsz float %258, %96
  %260 = fmul reassoc ninf nsz float %259, %99
  %261 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %260, float 0.000000e+00)
  %262 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %261, float 1.000000e+00)
  %263 = fadd reassoc ninf nsz float %246, %233
  %264 = fmul reassoc ninf nsz float %263, %235
  %265 = fadd reassoc ninf nsz float %198, %206
  %266 = fsub reassoc ninf nsz float %264, %265
  %267 = fmul reassoc ninf nsz float %266, %218
  %268 = fadd reassoc ninf nsz float %262, %254
  %269 = fmul reassoc ninf nsz float %268, %235
  %270 = fadd reassoc ninf nsz float %210, %214
  %271 = fsub reassoc ninf nsz float %269, %270
  %272 = fmul reassoc ninf nsz float %271, %222
  %273 = fadd reassoc ninf nsz float %272, %267
  %274 = fadd reassoc ninf nsz float %222, %218
  %factor73 = fmul reassoc ninf nsz float %274, 2.000000e+00
  %275 = fdiv reassoc ninf nsz float %273, %factor73
  %276 = fadd reassoc ninf nsz float %275, %74
  br label %after_if

true_block13:                                     ; preds = %for_loop_body
  %277 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %278 = load i32, ptr %277, align 4
  %279 = add i32 %278, -1
  %280 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %281 = tail call i32 @llvm.smin.i32(i32 %279, i32 %280)
  %282 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %283 = load i32, ptr %282, align 4
  %284 = add i32 %283, -1
  %285 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %286 = tail call i32 @llvm.smin.i32(i32 %284, i32 %285)
  %287 = load ptr, ptr %0, align 8
  %288 = getelementptr i8, ptr %287, i64 8
  %289 = load ptr, ptr %288, align 8
  %290 = getelementptr i8, ptr %287, i64 4
  %291 = load i32, ptr %290, align 4
  %292 = mul i32 %291, %281
  %293 = add i32 %292, %286
  %294 = sext i32 %293 to i64
  %295 = getelementptr float, ptr %289, i64 %294
  %296 = load float, ptr %295, align 4
  %297 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %298 = load float, ptr %297, align 4
  %299 = fsub reassoc ninf nsz float %296, %298
  %300 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %301 = load float, ptr %300, align 4
  %302 = fmul reassoc ninf nsz float %299, %301
  %303 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %302, float 0.000000e+00)
  %304 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %303, float 1.000000e+00)
  %305 = getelementptr inbounds nuw i8, ptr %36, i64 28
  %306 = load float, ptr %305, align 4
  %307 = fmul reassoc ninf nsz float %304, %306
  %308 = icmp sgt i32 %45, 0
  %309 = icmp slt i32 %45, %279
  %or.cond60 = and i1 %308, %309
  br i1 %or.cond60, label %true_block19, label %after_if

false_block14:                                    ; preds = %for_loop_body
  %310 = mul i32 %57, -2
  %311 = shl nsw i32 %.neg53, 1
  %312 = sub i32 %310, %311
  %313 = add i32 %49, %312
  %314 = add i32 %313, -1
  %.not55 = icmp eq i32 %314, 0
  %. = select i1 %.not55, i32 %21, i32 %23
  %.59 = select i1 %.not55, i32 %25, i32 %27
  %.022.in = select i1 %.not, i32 %., i32 %.59
  %.022 = icmp eq i32 %.022.in, 0
  br i1 %.022, label %true_block37, label %false_block38

true_block19:                                     ; preds = %true_block13
  %315 = icmp sgt i32 %49, 0
  %316 = icmp slt i32 %49, %284
  %spec.select57 = and i1 %315, %316
  br i1 %spec.select57, label %true_block25, label %after_if

true_block25:                                     ; preds = %true_block19
  %317 = add nsw i32 %45, -1
  %318 = mul i32 %317, %68
  %319 = sub i32 %318, %46
  %320 = add i32 %.03292, %319
  %321 = add i32 %320, -1
  %322 = sext i32 %321 to i64
  %323 = getelementptr float, ptr %67, i64 %322
  %324 = load float, ptr %323, align 4
  %325 = add nuw nsw i32 %45, 1
  %326 = mul i32 %325, %68
  %327 = sub i32 %326, %46
  %328 = add i32 %.03292, %327
  %329 = add i32 %328, 1
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, ptr %67, i64 %330
  %332 = load float, ptr %331, align 4
  %333 = add i32 %320, 1
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, ptr %67, i64 %334
  %336 = load float, ptr %335, align 4
  %337 = add i32 %328, -1
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %67, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = fsub reassoc ninf nsz float %324, %332
  %342 = tail call noundef float @llvm.fabs.f32(float %341)
  %343 = fadd reassoc ninf nsz float %342, 1.000000e+00
  %344 = fdiv reassoc ninf nsz float 1.000000e+00, %343
  %345 = fsub reassoc ninf nsz float %336, %340
  %346 = tail call noundef float @llvm.fabs.f32(float %345)
  %347 = fadd reassoc ninf nsz float %346, 1.000000e+00
  %348 = fdiv reassoc ninf nsz float 1.000000e+00, %347
  %349 = mul i32 %291, %317
  %350 = sub i32 %349, %46
  %351 = add i32 %.03292, %350
  %352 = add i32 %351, -1
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, ptr %289, i64 %353
  %355 = load float, ptr %354, align 4
  %356 = fsub reassoc ninf nsz float %355, %298
  %357 = fmul reassoc ninf nsz float %356, %301
  %358 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %357, float 0.000000e+00)
  %359 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %358, float 1.000000e+00)
  %360 = getelementptr inbounds nuw i8, ptr %36, i64 24
  %361 = load float, ptr %360, align 4
  %362 = mul i32 %291, %325
  %363 = sub i32 %362, %46
  %364 = add i32 %.03292, %363
  %365 = add i32 %364, 1
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, ptr %289, i64 %366
  %368 = load float, ptr %367, align 4
  %369 = fsub reassoc ninf nsz float %368, %298
  %370 = fmul reassoc ninf nsz float %369, %301
  %371 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %370, float 0.000000e+00)
  %372 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %371, float 1.000000e+00)
  %373 = add i32 %351, 1
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %289, i64 %374
  %376 = load float, ptr %375, align 4
  %377 = fsub reassoc ninf nsz float %376, %298
  %378 = fmul reassoc ninf nsz float %377, %301
  %379 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %378, float 0.000000e+00)
  %380 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %379, float 1.000000e+00)
  %381 = add i32 %364, -1
  %382 = sext i32 %381 to i64
  %383 = getelementptr float, ptr %289, i64 %382
  %384 = load float, ptr %383, align 4
  %385 = fsub reassoc ninf nsz float %384, %298
  %386 = fmul reassoc ninf nsz float %385, %301
  %387 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %386, float 0.000000e+00)
  %388 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %387, float 1.000000e+00)
  %389 = fadd reassoc ninf nsz float %372, %359
  %390 = fmul reassoc ninf nsz float %389, %361
  %391 = fadd reassoc ninf nsz float %324, %332
  %392 = fsub reassoc ninf nsz float %390, %391
  %393 = fmul reassoc ninf nsz float %392, %344
  %394 = fadd reassoc ninf nsz float %388, %380
  %395 = fmul reassoc ninf nsz float %394, %361
  %396 = fadd reassoc ninf nsz float %336, %340
  %397 = fsub reassoc ninf nsz float %395, %396
  %398 = fmul reassoc ninf nsz float %397, %348
  %399 = fadd reassoc ninf nsz float %398, %393
  %400 = fadd reassoc ninf nsz float %348, %344
  %factor = fmul reassoc ninf nsz float %400, 2.000000e+00
  %401 = fdiv reassoc ninf nsz float %399, %factor
  %402 = fadd reassoc ninf nsz float %401, %74
  br label %after_if

true_block37:                                     ; preds = %false_block14
  %403 = icmp sgt i32 %49, 0
  br i1 %403, label %true_block40, label %after_if45

false_block38:                                    ; preds = %false_block14
  %404 = icmp sgt i32 %45, 0
  br i1 %404, label %true_block52, label %after_if57

true_block40:                                     ; preds = %true_block37
  %405 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %406 = load i32, ptr %405, align 4
  %407 = add i32 %406, -1
  %408 = icmp slt i32 %49, %407
  br i1 %408, label %true_block43, label %after_if45

true_block43:                                     ; preds = %true_block40
  %409 = add i32 %49, -1
  %410 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %411 = load i32, ptr %410, align 4
  %412 = add i32 %411, -1
  %413 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %414 = tail call i32 @llvm.smin.i32(i32 %412, i32 %413)
  %415 = tail call i32 @llvm.umin.i32(i32 %407, i32 %409)
  %416 = load ptr, ptr %0, align 8
  %417 = getelementptr i8, ptr %416, i64 8
  %418 = load ptr, ptr %417, align 8
  %419 = getelementptr i8, ptr %416, i64 4
  %420 = load i32, ptr %419, align 4
  %421 = mul i32 %420, %414
  %422 = add i32 %421, %415
  %423 = sext i32 %422 to i64
  %424 = getelementptr float, ptr %418, i64 %423
  %425 = load float, ptr %424, align 4
  %426 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %427 = load float, ptr %426, align 4
  %428 = fsub reassoc ninf nsz float %425, %427
  %429 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %430 = load float, ptr %429, align 4
  %431 = fmul reassoc ninf nsz float %428, %430
  %432 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %431, float 0.000000e+00)
  %433 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %432, float 1.000000e+00)
  %434 = getelementptr inbounds nuw i8, ptr %36, i64 24
  %435 = load float, ptr %434, align 4
  %436 = add i32 %49, 1
  %437 = tail call i32 @llvm.umin.i32(i32 %407, i32 %436)
  %438 = add i32 %421, %437
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %418, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = fsub reassoc ninf nsz float %441, %427
  %443 = fmul reassoc ninf nsz float %442, %430
  %444 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %443, float 0.000000e+00)
  %445 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %444, float 1.000000e+00)
  %446 = add i32 %71, -1
  %447 = sext i32 %446 to i64
  %448 = getelementptr float, ptr %67, i64 %447
  %449 = load float, ptr %448, align 4
  %450 = add i32 %71, 1
  %451 = sext i32 %450 to i64
  %452 = getelementptr float, ptr %67, i64 %451
  %453 = load float, ptr %452, align 4
  %454 = fadd reassoc ninf nsz float %445, %433
  %455 = fmul reassoc ninf nsz float %454, %435
  %456 = fadd reassoc ninf nsz float %449, %453
  %457 = fsub reassoc ninf nsz float %455, %456
  %458 = fmul reassoc ninf nsz float %457, 5.000000e-01
  %459 = fadd reassoc ninf nsz float %458, %74
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %true_block40, %true_block37
  %.131 = phi float [ %459, %true_block43 ], [ %74, %true_block37 ], [ %74, %true_block40 ]
  %460 = icmp sgt i32 %45, 0
  br i1 %460, label %true_block46, label %after_if

true_block46:                                     ; preds = %after_if45
  %461 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %462 = load i32, ptr %461, align 4
  %463 = add i32 %462, -1
  %464 = icmp slt i32 %45, %463
  br i1 %464, label %true_block49, label %after_if

true_block49:                                     ; preds = %true_block46
  %465 = add nsw i32 %45, -1
  %466 = tail call i32 @llvm.umin.i32(i32 %463, i32 %465)
  %467 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %468 = load i32, ptr %467, align 4
  %469 = add i32 %468, -1
  %470 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %471 = tail call i32 @llvm.smin.i32(i32 %469, i32 %470)
  %472 = load ptr, ptr %0, align 8
  %473 = getelementptr i8, ptr %472, i64 8
  %474 = load ptr, ptr %473, align 8
  %475 = getelementptr i8, ptr %472, i64 4
  %476 = load i32, ptr %475, align 4
  %477 = mul i32 %476, %466
  %478 = add i32 %477, %471
  %479 = sext i32 %478 to i64
  %480 = getelementptr float, ptr %474, i64 %479
  %481 = load float, ptr %480, align 4
  %482 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %483 = load float, ptr %482, align 4
  %484 = fsub reassoc ninf nsz float %481, %483
  %485 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %486 = load float, ptr %485, align 4
  %487 = fmul reassoc ninf nsz float %484, %486
  %488 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %487, float 0.000000e+00)
  %489 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %488, float 1.000000e+00)
  %490 = getelementptr inbounds nuw i8, ptr %36, i64 28
  %491 = load float, ptr %490, align 4
  %492 = add nuw nsw i32 %45, 1
  %493 = tail call i32 @llvm.umin.i32(i32 %463, i32 %492)
  %494 = mul i32 %476, %493
  %495 = add i32 %494, %471
  %496 = sext i32 %495 to i64
  %497 = getelementptr float, ptr %474, i64 %496
  %498 = load float, ptr %497, align 4
  %499 = fsub reassoc ninf nsz float %498, %483
  %500 = fmul reassoc ninf nsz float %499, %486
  %501 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %500, float 0.000000e+00)
  %502 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %501, float 1.000000e+00)
  %503 = mul i32 %465, %68
  %504 = sub i32 %503, %46
  %505 = add i32 %.03292, %504
  %506 = sext i32 %505 to i64
  %507 = getelementptr float, ptr %67, i64 %506
  %508 = load float, ptr %507, align 4
  %509 = mul i32 %492, %68
  %510 = sub i32 %509, %46
  %511 = add i32 %.03292, %510
  %512 = sext i32 %511 to i64
  %513 = getelementptr float, ptr %67, i64 %512
  %514 = load float, ptr %513, align 4
  %515 = fadd reassoc ninf nsz float %502, %489
  %516 = fmul reassoc ninf nsz float %515, %491
  %517 = fadd reassoc ninf nsz float %508, %514
  %518 = fsub reassoc ninf nsz float %516, %517
  %519 = fmul reassoc ninf nsz float %518, 5.000000e-01
  %520 = fadd reassoc ninf nsz float %519, %74
  br label %after_if

true_block52:                                     ; preds = %false_block38
  %521 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %522 = load i32, ptr %521, align 4
  %523 = add i32 %522, -1
  %524 = icmp slt i32 %45, %523
  br i1 %524, label %true_block55, label %after_if57

true_block55:                                     ; preds = %true_block52
  %525 = add nsw i32 %45, -1
  %526 = tail call i32 @llvm.umin.i32(i32 %523, i32 %525)
  %527 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %528 = load i32, ptr %527, align 4
  %529 = add i32 %528, -1
  %530 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %531 = tail call i32 @llvm.smin.i32(i32 %529, i32 %530)
  %532 = load ptr, ptr %0, align 8
  %533 = getelementptr i8, ptr %532, i64 8
  %534 = load ptr, ptr %533, align 8
  %535 = getelementptr i8, ptr %532, i64 4
  %536 = load i32, ptr %535, align 4
  %537 = mul i32 %536, %526
  %538 = add i32 %537, %531
  %539 = sext i32 %538 to i64
  %540 = getelementptr float, ptr %534, i64 %539
  %541 = load float, ptr %540, align 4
  %542 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %543 = load float, ptr %542, align 4
  %544 = fsub reassoc ninf nsz float %541, %543
  %545 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %546 = load float, ptr %545, align 4
  %547 = fmul reassoc ninf nsz float %544, %546
  %548 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %547, float 0.000000e+00)
  %549 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %548, float 1.000000e+00)
  %550 = getelementptr inbounds nuw i8, ptr %36, i64 24
  %551 = load float, ptr %550, align 4
  %552 = add nuw nsw i32 %45, 1
  %553 = tail call i32 @llvm.umin.i32(i32 %523, i32 %552)
  %554 = mul i32 %536, %553
  %555 = add i32 %554, %531
  %556 = sext i32 %555 to i64
  %557 = getelementptr float, ptr %534, i64 %556
  %558 = load float, ptr %557, align 4
  %559 = fsub reassoc ninf nsz float %558, %543
  %560 = fmul reassoc ninf nsz float %559, %546
  %561 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %560, float 0.000000e+00)
  %562 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %561, float 1.000000e+00)
  %563 = mul i32 %525, %68
  %564 = sub i32 %563, %46
  %565 = add i32 %.03292, %564
  %566 = sext i32 %565 to i64
  %567 = getelementptr float, ptr %67, i64 %566
  %568 = load float, ptr %567, align 4
  %569 = mul i32 %552, %68
  %570 = sub i32 %569, %46
  %571 = add i32 %.03292, %570
  %572 = sext i32 %571 to i64
  %573 = getelementptr float, ptr %67, i64 %572
  %574 = load float, ptr %573, align 4
  %575 = fadd reassoc ninf nsz float %562, %549
  %576 = fmul reassoc ninf nsz float %575, %551
  %577 = fadd reassoc ninf nsz float %568, %574
  %578 = fsub reassoc ninf nsz float %576, %577
  %579 = fmul reassoc ninf nsz float %578, 5.000000e-01
  %580 = fadd reassoc ninf nsz float %579, %74
  br label %after_if57

after_if57:                                       ; preds = %true_block55, %true_block52, %false_block38
  %.2 = phi float [ %580, %true_block55 ], [ %74, %false_block38 ], [ %74, %true_block52 ]
  %581 = icmp sgt i32 %49, 0
  br i1 %581, label %true_block58, label %after_if

true_block58:                                     ; preds = %after_if57
  %582 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %583 = load i32, ptr %582, align 4
  %584 = add i32 %583, -1
  %585 = icmp slt i32 %49, %584
  br i1 %585, label %true_block61, label %after_if

true_block61:                                     ; preds = %true_block58
  %586 = add i32 %49, -1
  %587 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %588 = load i32, ptr %587, align 4
  %589 = add i32 %588, -1
  %590 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %591 = tail call i32 @llvm.smin.i32(i32 %589, i32 %590)
  %592 = tail call i32 @llvm.umin.i32(i32 %584, i32 %586)
  %593 = load ptr, ptr %0, align 8
  %594 = getelementptr i8, ptr %593, i64 8
  %595 = load ptr, ptr %594, align 8
  %596 = getelementptr i8, ptr %593, i64 4
  %597 = load i32, ptr %596, align 4
  %598 = mul i32 %597, %591
  %599 = add i32 %598, %592
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %595, i64 %600
  %602 = load float, ptr %601, align 4
  %603 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %604 = load float, ptr %603, align 4
  %605 = fsub reassoc ninf nsz float %602, %604
  %606 = getelementptr inbounds nuw i8, ptr %36, i64 20
  %607 = load float, ptr %606, align 4
  %608 = fmul reassoc ninf nsz float %605, %607
  %609 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %608, float 0.000000e+00)
  %610 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %609, float 1.000000e+00)
  %611 = getelementptr inbounds nuw i8, ptr %36, i64 28
  %612 = load float, ptr %611, align 4
  %613 = add i32 %49, 1
  %614 = tail call i32 @llvm.umin.i32(i32 %584, i32 %613)
  %615 = add i32 %598, %614
  %616 = sext i32 %615 to i64
  %617 = getelementptr float, ptr %595, i64 %616
  %618 = load float, ptr %617, align 4
  %619 = fsub reassoc ninf nsz float %618, %604
  %620 = fmul reassoc ninf nsz float %619, %607
  %621 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %620, float 0.000000e+00)
  %622 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %621, float 1.000000e+00)
  %623 = add i32 %71, -1
  %624 = sext i32 %623 to i64
  %625 = getelementptr float, ptr %67, i64 %624
  %626 = load float, ptr %625, align 4
  %627 = add i32 %71, 1
  %628 = sext i32 %627 to i64
  %629 = getelementptr float, ptr %67, i64 %628
  %630 = load float, ptr %629, align 4
  %631 = fadd reassoc ninf nsz float %622, %610
  %632 = fmul reassoc ninf nsz float %631, %612
  %633 = fadd reassoc ninf nsz float %626, %630
  %634 = fsub reassoc ninf nsz float %632, %633
  %635 = fmul reassoc ninf nsz float %634, 5.000000e-01
  %636 = fadd reassoc ninf nsz float %635, %74
  br label %after_if
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #1

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
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
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
