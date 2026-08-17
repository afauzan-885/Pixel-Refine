; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_ha_rgb_half_res_fused_kernel_c716_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 8
  store float %4, ptr %9, align 4
  %10 = fsub reassoc ninf nsz float %2, %4
  %11 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %10, float 1.000000e+00)
  %12 = fdiv reassoc ninf nsz float 1.000000e+00, %11
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 12
  store float %12, ptr %16, align 4
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 80
  %19 = load i32, ptr %18, align 4
  %20 = sdiv i32 %19, 2
  %21 = icmp slt i32 %19, 0
  %22 = shl nsw i32 %20, 1
  %23 = icmp ne i32 %22, %19
  %24 = and i1 %21, %23
  %.neg = sext i1 %24 to i32
  %25 = add nsw i32 %20, %.neg
  %26 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %25, i32 range(i32 -1073741825, 1073741824) 0)
  %27 = getelementptr i8, ptr %17, i64 84
  %28 = load i32, ptr %27, align 4
  %29 = sdiv i32 %28, 2
  %30 = icmp slt i32 %28, 0
  %31 = shl nsw i32 %29, 1
  %32 = icmp ne i32 %31, %28
  %33 = and i1 %30, %32
  %.neg1 = sext i1 %33 to i32
  %34 = add nsw i32 %29, %.neg1
  %35 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %34, i32 range(i32 -1073741825, 1073741824) 0)
  %36 = load ptr, ptr %5, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 4
  store i32 %35, ptr %39, align 4
  %40 = mul i32 %35, %26
  %41 = load ptr, ptr %5, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  store i32 %40, ptr %43, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_ha_rgb_half_res_fused_kernel_c716_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %14 = add i32 %9, %.neg
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
  %28 = getelementptr i8, ptr %19, i64 56
  %29 = load float, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 60
  %31 = load float, ptr %30, align 4
  %32 = getelementptr i8, ptr %19, i64 68
  %33 = load float, ptr %32, align 4
  %34 = getelementptr i8, ptr %19, i64 64
  %35 = load float, ptr %34, align 4
  %36 = getelementptr i8, ptr %19, i64 24
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr i8, ptr %19, i64 20
  %39 = load i32, ptr %38, align 4
  %40 = getelementptr i8, ptr %37, i64 4
  %41 = getelementptr i8, ptr %37, i64 8
  %42 = sext i32 %39 to i64
  %43 = getelementptr float, ptr %37, i64 %42
  %44 = add i32 %39, 1
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, ptr %37, i64 %45
  %47 = add i32 %39, 2
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, ptr %37, i64 %48
  %50 = shl i32 %39, 1
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, ptr %37, i64 %51
  %53 = getelementptr i8, ptr %52, i64 4
  %54 = add i32 %50, 2
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, ptr %37, i64 %55
  %factor.op.fmul = fmul reassoc ninf nsz float %31, 5.000000e-01
  %factor.op.fmul30 = fmul reassoc ninf nsz float %33, 5.000000e-01
  %57 = icmp slt i32 %16, %18
  br i1 %57, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %58 = getelementptr i8, ptr %19, i64 8
  %59 = getelementptr i8, ptr %19, i64 4
  %60 = getelementptr i8, ptr %19, i64 48
  %61 = getelementptr i8, ptr %19, i64 36
  %62 = getelementptr i8, ptr %19, i64 40
  %63 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if27, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %63, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if27 ]
  %.01932 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %217, %after_if27 ]
  %64 = load ptr, ptr %3, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 32872
  %66 = load ptr, ptr %65, align 8
  %67 = getelementptr inbounds nuw i8, ptr %66, i64 4
  %68 = load i32, ptr %67, align 4
  %69 = sdiv i32 %.01932, %68
  %70 = mul i32 %69, %68
  %71 = xor i32 %68, %.01932
  %72 = icmp slt i32 %71, 0
  %73 = icmp ne i32 %.01932, %70
  %74 = and i1 %72, %73
  %.neg24 = sext i1 %74 to i32
  %75 = add i32 %69, %.neg24
  %76 = shl i32 %75, 1
  %77 = load ptr, ptr %58, align 8
  %78 = load i32, ptr %59, align 4
  %79 = shl i32 %78, 1
  %80 = shl i32 %68, 1
  %81 = sub i32 %79, %80
  %82 = mul i32 %81, %75
  %83 = add i32 %lsr.iv, %82
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, ptr %77, i64 %84
  %86 = load float, ptr %85, align 4
  %87 = getelementptr inbounds nuw i8, ptr %66, i64 8
  %88 = load float, ptr %87, align 4
  %89 = fsub reassoc ninf nsz float %86, %88
  %90 = getelementptr inbounds nuw i8, ptr %66, i64 12
  %91 = load float, ptr %90, align 4
  %92 = fmul reassoc ninf nsz float %89, %91
  %93 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %92, float 0.000000e+00)
  %94 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %93, float 1.000000e+00)
  %95 = add i32 %83, 1
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %77, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = fsub reassoc ninf nsz float %98, %88
  %100 = fmul reassoc ninf nsz float %99, %91
  %101 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %100, float 0.000000e+00)
  %102 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %101, float 1.000000e+00)
  %103 = or disjoint i32 %76, 1
  %104 = mul i32 %103, %78
  %105 = mul i32 %80, %75
  %106 = sub i32 %104, %105
  %107 = add i32 %lsr.iv, %106
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %77, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = fsub reassoc ninf nsz float %110, %88
  %112 = fmul reassoc ninf nsz float %111, %91
  %113 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %112, float 0.000000e+00)
  %114 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %113, float 1.000000e+00)
  %115 = add i32 %107, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %77, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = fsub reassoc ninf nsz float %118, %88
  %120 = fmul reassoc ninf nsz float %119, %91
  %121 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %120, float 0.000000e+00)
  %122 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %121, float 1.000000e+00)
  switch i32 %21, label %false_block5 [
    i32 0, label %after_if
    i32 1, label %true_block1
    i32 2, label %true_block4
  ]

after_for.loopexit:                               ; preds = %after_if27
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %false_block5, %true_block4, %true_block1, %for_loop_body
  %.015 = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ %94, %for_loop_body ]
  %.011 = phi float [ %94, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  %.07 = phi float [ 0.000000e+00, %true_block1 ], [ %94, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  %.0 = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ %94, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  switch i32 %23, label %false_block14 [
    i32 0, label %after_if9
    i32 1, label %true_block10
    i32 2, label %true_block13
  ]

true_block1:                                      ; preds = %for_loop_body
  br label %after_if

true_block4:                                      ; preds = %for_loop_body
  br label %after_if

false_block5:                                     ; preds = %for_loop_body
  br label %after_if

after_if9:                                        ; preds = %false_block14, %true_block13, %true_block10, %after_if
  %.116 = phi float [ %.015, %true_block10 ], [ %.015, %true_block13 ], [ %.015, %false_block14 ], [ %102, %after_if ]
  %.112 = phi float [ %102, %true_block10 ], [ %.011, %true_block13 ], [ %.011, %false_block14 ], [ %.011, %after_if ]
  %.18 = phi float [ %.07, %true_block10 ], [ %102, %true_block13 ], [ %.07, %false_block14 ], [ %.07, %after_if ]
  %.1 = phi float [ %.0, %true_block10 ], [ %.0, %true_block13 ], [ %102, %false_block14 ], [ %.0, %after_if ]
  switch i32 %25, label %false_block23 [
    i32 0, label %after_if18
    i32 1, label %true_block19
    i32 2, label %true_block22
  ]

true_block10:                                     ; preds = %after_if
  br label %after_if9

true_block13:                                     ; preds = %after_if
  br label %after_if9

false_block14:                                    ; preds = %after_if
  br label %after_if9

after_if18:                                       ; preds = %false_block23, %true_block22, %true_block19, %after_if9
  %.217 = phi float [ %.116, %true_block19 ], [ %.116, %true_block22 ], [ %.116, %false_block23 ], [ %114, %after_if9 ]
  %.213 = phi float [ %114, %true_block19 ], [ %.112, %true_block22 ], [ %.112, %false_block23 ], [ %.112, %after_if9 ]
  %.29 = phi float [ %.18, %true_block19 ], [ %114, %true_block22 ], [ %.18, %false_block23 ], [ %.18, %after_if9 ]
  %.2 = phi float [ %.1, %true_block19 ], [ %.1, %true_block22 ], [ %114, %false_block23 ], [ %.1, %after_if9 ]
  switch i32 %27, label %false_block32 [
    i32 0, label %after_if27
    i32 1, label %true_block28
    i32 2, label %true_block31
  ]

true_block19:                                     ; preds = %after_if9
  br label %after_if18

true_block22:                                     ; preds = %after_if9
  br label %after_if18

false_block23:                                    ; preds = %after_if9
  br label %after_if18

after_if27:                                       ; preds = %false_block32, %true_block31, %true_block28, %after_if18
  %.318 = phi float [ %.217, %true_block28 ], [ %.217, %true_block31 ], [ %.217, %false_block32 ], [ %122, %after_if18 ]
  %.314 = phi float [ %122, %true_block28 ], [ %.213, %true_block31 ], [ %.213, %false_block32 ], [ %.213, %after_if18 ]
  %.310 = phi float [ %.29, %true_block28 ], [ %122, %true_block31 ], [ %.29, %false_block32 ], [ %.29, %after_if18 ]
  %.3 = phi float [ %.2, %true_block28 ], [ %.2, %true_block31 ], [ %122, %false_block32 ], [ %.2, %after_if18 ]
  %123 = fadd reassoc ninf nsz float %.3, %.314
  %124 = fmul reassoc ninf nsz float %123, 5.000000e-01
  %125 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float %.310)
  %126 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %.318, float %125)
  %127 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %124, float %.310)
  %128 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.318, float %127)
  %129 = fmul reassoc ninf nsz float %128, 0x40029ACA60000000
  %130 = fadd reassoc ninf nsz float %129, 0xBFF47711E0000000
  %131 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %130, float 0.000000e+00)
  %132 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %132, -2.000000e+00
  %133 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %134 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %128, float 0x3EE4F8B580000000)
  %135 = fmul reassoc ninf nsz float %126, 0x4001C71C80000000
  %136 = fdiv reassoc ninf nsz float %135, %134
  %137 = fadd reassoc ninf nsz float %136, 0xBFEC71C740000000
  %138 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %137, float 0.000000e+00)
  %139 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %138, float 1.000000e+00)
  %factor29 = fmul reassoc ninf nsz float %139, -2.000000e+00
  %140 = fadd reassoc ninf nsz float %factor29, 3.000000e+00
  %141 = fmul reassoc ninf nsz float %139, %132
  %142 = fmul reassoc ninf nsz float %141, %141
  %143 = fmul reassoc ninf nsz float %142, %133
  %144 = fmul reassoc ninf nsz float %143, %140
  %145 = fmul reassoc ninf nsz float %.318, %29
  %.reass = fmul reassoc ninf nsz float %.314, %factor.op.fmul
  %.reass31 = fmul reassoc ninf nsz float %.3, %factor.op.fmul30
  %146 = fadd reassoc ninf nsz float %.reass31, %.reass
  %147 = fmul reassoc ninf nsz float %.310, %35
  %148 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %146, float %147)
  %149 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %145, float %148)
  %150 = fsub reassoc ninf nsz float 1.000000e+00, %144
  %151 = fmul reassoc ninf nsz float %150, %145
  %152 = fmul reassoc ninf nsz float %144, %149
  %153 = fadd reassoc ninf nsz float %151, %152
  %154 = fmul reassoc ninf nsz float %150, %146
  %155 = fadd reassoc ninf nsz float %154, %152
  %156 = fmul reassoc ninf nsz float %150, %147
  %157 = fadd reassoc ninf nsz float %156, %152
  %158 = load float, ptr %37, align 4
  %159 = fmul reassoc ninf nsz float %153, %158
  %160 = load float, ptr %40, align 4
  %161 = fmul reassoc ninf nsz float %155, %160
  %162 = fadd reassoc ninf nsz float %159, %161
  %163 = load float, ptr %41, align 4
  %164 = fmul reassoc ninf nsz float %157, %163
  %165 = fadd reassoc ninf nsz float %162, %164
  %166 = load float, ptr %43, align 4
  %167 = fmul reassoc ninf nsz float %153, %166
  %168 = load float, ptr %46, align 4
  %169 = fmul reassoc ninf nsz float %155, %168
  %170 = fadd reassoc ninf nsz float %167, %169
  %171 = load float, ptr %49, align 4
  %172 = fmul reassoc ninf nsz float %157, %171
  %173 = fadd reassoc ninf nsz float %170, %172
  %174 = load float, ptr %52, align 4
  %175 = fmul reassoc ninf nsz float %153, %174
  %176 = load float, ptr %53, align 4
  %177 = fmul reassoc ninf nsz float %155, %176
  %178 = fadd reassoc ninf nsz float %175, %177
  %179 = load float, ptr %56, align 4
  %180 = fmul reassoc ninf nsz float %157, %179
  %181 = fadd reassoc ninf nsz float %178, %180
  %182 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %165, float 0.000000e+00)
  %183 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %182, float 1.000000e+00)
  %184 = load ptr, ptr %60, align 8
  %185 = load i32, ptr %61, align 4
  %186 = load i32, ptr %62, align 4
  %187 = sub i32 %185, %68
  %188 = mul i32 %187, %75
  %189 = add i32 %.01932, %188
  %190 = mul i32 %189, %186
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %184, i64 %191
  store float %183, ptr %192, align 4
  %193 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %173, float 0.000000e+00)
  %194 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %193, float 1.000000e+00)
  %195 = load ptr, ptr %60, align 8
  %196 = load i32, ptr %61, align 4
  %197 = load i32, ptr %62, align 4
  %198 = sub i32 %196, %68
  %199 = mul i32 %198, %75
  %200 = add i32 %.01932, %199
  %201 = mul i32 %200, %197
  %202 = add i32 %201, 1
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %195, i64 %203
  store float %194, ptr %204, align 4
  %205 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %181, float 0.000000e+00)
  %206 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %205, float 1.000000e+00)
  %207 = load ptr, ptr %60, align 8
  %208 = load i32, ptr %61, align 4
  %209 = load i32, ptr %62, align 4
  %210 = sub i32 %208, %68
  %211 = mul i32 %210, %75
  %212 = add i32 %.01932, %211
  %213 = mul i32 %212, %209
  %214 = add i32 %213, 2
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, ptr %207, i64 %215
  store float %206, ptr %216, align 4
  %217 = add nsw i32 %.01932, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %217
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block28:                                     ; preds = %after_if18
  br label %after_if27

true_block31:                                     ; preds = %after_if18
  br label %after_if27

false_block32:                                    ; preds = %after_if18
  br label %after_if27
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.9, align 8
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
