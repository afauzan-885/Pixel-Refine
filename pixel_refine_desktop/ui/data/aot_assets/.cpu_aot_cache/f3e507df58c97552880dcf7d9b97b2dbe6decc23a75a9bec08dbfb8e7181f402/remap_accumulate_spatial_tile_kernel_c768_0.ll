; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.34 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @remap_accumulate_spatial_tile_kernel_c768_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 124
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
  %11 = getelementptr i8, ptr %10, i64 116
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
  %25 = getelementptr i8, ptr %24, i64 120
  %26 = load i32, ptr %25, align 4
  %27 = add i32 %26, -1
  %28 = load ptr, ptr %4, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 28
  store i32 %27, ptr %31, align 4
  %32 = sitofp i32 %27 to float
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 112
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
  %48 = getelementptr i8, ptr %47, i64 132
  %49 = load i32, ptr %48, align 4
  %50 = load ptr, ptr %4, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 40
  store i32 %49, ptr %53, align 4
  %54 = sitofp i32 %49 to float
  %55 = sitofp i32 %12 to float
  %56 = fdiv reassoc ninf nsz float %54, %55
  %57 = load ptr, ptr %4, align 8
  %58 = getelementptr inbounds nuw i8, ptr %57, i64 32872
  %59 = load ptr, ptr %58, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 32
  store float %56, ptr %60, align 4
  %61 = load ptr, ptr %context, align 8
  %62 = getelementptr i8, ptr %61, i64 128
  %63 = load i32, ptr %62, align 4
  %64 = load ptr, ptr %4, align 8
  %65 = getelementptr inbounds nuw i8, ptr %64, i64 32872
  %66 = load ptr, ptr %65, align 8
  %67 = getelementptr inbounds nuw i8, ptr %66, i64 44
  store i32 %63, ptr %67, align 4
  %68 = sitofp i32 %63 to float
  %69 = sitofp i32 %35 to float
  %70 = fdiv reassoc ninf nsz float %68, %69
  %71 = load ptr, ptr %4, align 8
  %72 = getelementptr inbounds nuw i8, ptr %71, i64 32872
  %73 = load ptr, ptr %72, align 8
  %74 = getelementptr inbounds nuw i8, ptr %73, i64 36
  store float %70, ptr %74, align 4
  %75 = load ptr, ptr %context, align 8
  %76 = getelementptr i8, ptr %75, i64 144
  %77 = load i32, ptr %76, align 4
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = getelementptr i8, ptr %75, i64 148
  %80 = load i32, ptr %79, align 4
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = load ptr, ptr %4, align 8
  %83 = getelementptr inbounds nuw i8, ptr %82, i64 32872
  %84 = load ptr, ptr %83, align 8
  %85 = getelementptr inbounds nuw i8, ptr %84, i64 4
  store i32 %81, ptr %85, align 4
  %86 = mul i32 %81, %78
  %87 = load ptr, ptr %4, align 8
  %88 = getelementptr inbounds nuw i8, ptr %87, i64 32872
  %89 = load ptr, ptr %88, align 8
  store i32 %86, ptr %89, align 4
  ret void
}

define void @remap_accumulate_spatial_tile_kernel_c768_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 152
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 156
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %25 = sub i32 %18, %16
  %26 = add i32 %23, %16
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %lsr.iv10 = phi i32 [ %26, %for_loop_body.preheader ], [ %lsr.iv.next11, %after_if3 ]
  %lsr.iv = phi i32 [ %25, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if3 ]
  %.049 = phi i32 [ %437, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.049, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.049
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.049, %33
  %37 = and i1 %35, %36
  %.neg6 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg6
  %39 = mul i32 %38, %31
  %40 = add i32 %38, %21
  %41 = mul i32 %31, -1
  %42 = mul i32 %41, %38
  %43 = add i32 %lsr.iv10, %42
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
  %165 = getelementptr i8, ptr %100, i64 136
  %166 = load float, ptr %165, align 4
  %167 = fmul reassoc ninf nsz float %166, %139
  %168 = fadd reassoc ninf nsz float %167, %50
  %169 = getelementptr i8, ptr %100, i64 140
  %170 = load float, ptr %169, align 4
  %171 = fmul reassoc ninf nsz float %164, %170
  %172 = fadd reassoc ninf nsz float %171, %54
  %173 = getelementptr inbounds nuw i8, ptr %29, i64 32
  %174 = load float, ptr %173, align 4
  %175 = fmul reassoc ninf nsz float %174, %50
  %176 = getelementptr inbounds nuw i8, ptr %29, i64 36
  %177 = load float, ptr %176, align 4
  %178 = fmul reassoc ninf nsz float %177, %54
  %179 = tail call reassoc ninf nsz float @llvm.floor.f32(float %175)
  %180 = fptosi float %179 to i32
  %181 = tail call reassoc ninf nsz float @llvm.floor.f32(float %178)
  %182 = fptosi float %181 to i32
  %183 = add i32 %180, 1
  %184 = getelementptr inbounds nuw i8, ptr %29, i64 40
  %185 = load i32, ptr %184, align 4
  %186 = add i32 %185, -1
  %187 = tail call i32 @llvm.smin.i32(i32 %183, i32 %186)
  %188 = add i32 %182, 1
  %189 = getelementptr inbounds nuw i8, ptr %29, i64 44
  %190 = load i32, ptr %189, align 4
  %191 = add i32 %190, -1
  %192 = tail call i32 @llvm.smin.i32(i32 %188, i32 %191)
  %193 = tail call i32 @llvm.smax.i32(i32 %180, i32 0)
  %194 = tail call i32 @llvm.smax.i32(i32 %182, i32 0)
  %195 = uitofp nneg i32 %193 to float
  %196 = fsub reassoc ninf nsz float %175, %195
  %197 = uitofp nneg i32 %194 to float
  %198 = fsub reassoc ninf nsz float %178, %197
  %199 = fsub reassoc ninf nsz float 1.000000e+00, %196
  %200 = getelementptr i8, ptr %100, i64 56
  %201 = load ptr, ptr %200, align 8
  %202 = getelementptr i8, ptr %100, i64 52
  %203 = load i32, ptr %202, align 4
  %204 = mul i32 %194, %203
  %205 = add i32 %204, %193
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %201, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = fmul reassoc ninf nsz float %199, %208
  %210 = add i32 %204, %187
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %201, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fmul reassoc ninf nsz float %213, %196
  %215 = mul i32 %192, %203
  %216 = add i32 %215, %193
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %201, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %219, %199
  %221 = add i32 %215, %187
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %201, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = fmul reassoc ninf nsz float %224, %196
  %reass.add = fadd reassoc ninf nsz float %209, %214
  %reass.add7 = fadd reassoc ninf nsz float %225, %220
  %226 = fsub reassoc ninf nsz float %reass.add7, %reass.add
  %227 = fmul reassoc ninf nsz float %198, %226
  %228 = fadd reassoc ninf nsz float %reass.add, %227
  %229 = getelementptr i8, ptr %100, i64 104
  %230 = load i32, ptr %229, align 4
  %231 = getelementptr i8, ptr %100, i64 108
  %232 = load i32, ptr %231, align 4
  %233 = tail call reassoc ninf nsz float @llvm.floor.f32(float %168)
  %234 = fptosi float %233 to i32
  %235 = tail call reassoc ninf nsz float @llvm.floor.f32(float %172)
  %236 = fptosi float %235 to i32
  %237 = sitofp i32 %234 to float
  %238 = fsub reassoc ninf nsz float %168, %237
  %239 = sitofp i32 %236 to float
  %240 = fsub reassoc ninf nsz float %172, %239
  %241 = tail call i32 @llvm.abs.i32(i32 %234, i1 true)
  %242 = add i32 %232, -1
  %243 = sub i32 %241, %242
  %244 = tail call i32 @llvm.smax.i32(i32 %243, i32 0)
  %245 = shl nuw i32 %244, 1
  %246 = sub i32 %241, %245
  %247 = tail call i32 @llvm.smax.i32(i32 %246, i32 0)
  %248 = tail call i32 @llvm.smin.i32(i32 %242, i32 %247)
  %249 = tail call i32 @llvm.abs.i32(i32 %236, i1 true)
  %250 = add i32 %230, -1
  %251 = sub i32 %249, %250
  %252 = tail call i32 @llvm.smax.i32(i32 %251, i32 0)
  %253 = shl nuw i32 %252, 1
  %254 = sub i32 %249, %253
  %255 = tail call i32 @llvm.smax.i32(i32 %254, i32 0)
  %256 = tail call i32 @llvm.smin.i32(i32 %250, i32 %255)
  %257 = add i32 %234, 1
  %258 = tail call i32 @llvm.abs.i32(i32 %257, i1 true)
  %259 = sub i32 %258, %242
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = shl nuw i32 %260, 1
  %262 = sub i32 %258, %261
  %263 = tail call i32 @llvm.smax.i32(i32 %262, i32 0)
  %264 = tail call i32 @llvm.smin.i32(i32 %242, i32 %263)
  %265 = add i32 %236, 1
  %266 = tail call i32 @llvm.abs.i32(i32 %265, i1 true)
  %267 = sub i32 %266, %250
  %268 = tail call i32 @llvm.smax.i32(i32 %267, i32 0)
  %269 = shl nuw i32 %268, 1
  %270 = sub i32 %266, %269
  %271 = tail call i32 @llvm.smax.i32(i32 %270, i32 0)
  %272 = tail call i32 @llvm.smin.i32(i32 %250, i32 %271)
  %273 = getelementptr i8, ptr %100, i64 16
  %274 = load ptr, ptr %273, align 8
  %275 = getelementptr i8, ptr %100, i64 4
  %276 = load i32, ptr %275, align 4
  %277 = getelementptr i8, ptr %100, i64 8
  %278 = load i32, ptr %277, align 4
  %279 = mul i32 %256, %276
  %280 = add i32 %279, %248
  %281 = mul i32 %280, %278
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, ptr %274, i64 %282
  %284 = load float, ptr %283, align 4
  %285 = add i32 %279, %264
  %286 = mul i32 %285, %278
  %287 = sext i32 %286 to i64
  %288 = getelementptr float, ptr %274, i64 %287
  %289 = load float, ptr %288, align 4
  %290 = mul i32 %272, %276
  %291 = add i32 %290, %248
  %292 = mul i32 %291, %278
  %293 = sext i32 %292 to i64
  %294 = getelementptr float, ptr %274, i64 %293
  %295 = load float, ptr %294, align 4
  %296 = add i32 %290, %264
  %297 = mul i32 %296, %278
  %298 = sext i32 %297 to i64
  %299 = getelementptr float, ptr %274, i64 %298
  %300 = load float, ptr %299, align 4
  %301 = fsub reassoc ninf nsz float 1.000000e+00, %238
  %302 = fmul reassoc ninf nsz float %284, %301
  %303 = fmul reassoc ninf nsz float %289, %238
  %304 = fadd reassoc ninf nsz float %303, %302
  %305 = fmul reassoc ninf nsz float %295, %301
  %306 = fmul reassoc ninf nsz float %300, %238
  %307 = fadd reassoc ninf nsz float %306, %305
  %308 = fsub reassoc ninf nsz float 1.000000e+00, %240
  %309 = fmul reassoc ninf nsz float %304, %308
  %310 = fmul reassoc ninf nsz float %307, %240
  %311 = fadd reassoc ninf nsz float %310, %309
  %312 = fmul reassoc ninf nsz float %311, %228
  %313 = getelementptr i8, ptr %100, i64 80
  %314 = load ptr, ptr %313, align 8
  %315 = getelementptr i8, ptr %100, i64 68
  %316 = load i32, ptr %315, align 4
  %317 = getelementptr i8, ptr %100, i64 72
  %318 = load i32, ptr %317, align 4
  %319 = mul i32 %316, %40
  %320 = sub i32 %319, %39
  %321 = add i32 %lsr.iv10, %320
  %322 = mul i32 %321, %318
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, ptr %314, i64 %323
  %325 = atomicrmw fadd ptr %324, float %312 seq_cst, align 4
  %326 = load ptr, ptr %273, align 8
  %327 = load i32, ptr %275, align 4
  %328 = load i32, ptr %277, align 4
  %329 = mul i32 %327, %256
  %330 = add i32 %329, %248
  %331 = mul i32 %330, %328
  %332 = add i32 %331, 1
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, ptr %326, i64 %333
  %335 = load float, ptr %334, align 4
  %336 = add i32 %329, %264
  %337 = mul i32 %336, %328
  %338 = add i32 %337, 1
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, ptr %326, i64 %339
  %341 = load float, ptr %340, align 4
  %342 = mul i32 %327, %272
  %343 = add i32 %342, %248
  %344 = mul i32 %343, %328
  %345 = add i32 %344, 1
  %346 = sext i32 %345 to i64
  %347 = getelementptr float, ptr %326, i64 %346
  %348 = load float, ptr %347, align 4
  %349 = add i32 %342, %264
  %350 = mul i32 %349, %328
  %351 = add i32 %350, 1
  %352 = sext i32 %351 to i64
  %353 = getelementptr float, ptr %326, i64 %352
  %354 = load float, ptr %353, align 4
  %355 = fmul reassoc ninf nsz float %335, %301
  %356 = fmul reassoc ninf nsz float %341, %238
  %357 = fadd reassoc ninf nsz float %356, %355
  %358 = fmul reassoc ninf nsz float %348, %301
  %359 = fmul reassoc ninf nsz float %354, %238
  %360 = fadd reassoc ninf nsz float %359, %358
  %361 = fmul reassoc ninf nsz float %357, %308
  %362 = fmul reassoc ninf nsz float %360, %240
  %363 = fadd reassoc ninf nsz float %362, %361
  %364 = fmul reassoc ninf nsz float %363, %228
  %365 = load ptr, ptr %313, align 8
  %366 = load i32, ptr %315, align 4
  %367 = load i32, ptr %317, align 4
  %368 = mul i32 %366, %40
  %369 = sub i32 %368, %39
  %370 = add i32 %lsr.iv10, %369
  %371 = mul i32 %370, %367
  %372 = add i32 %371, 1
  %373 = sext i32 %372 to i64
  %374 = getelementptr float, ptr %365, i64 %373
  %375 = atomicrmw fadd ptr %374, float %364 seq_cst, align 4
  %376 = load ptr, ptr %273, align 8
  %377 = load i32, ptr %275, align 4
  %378 = load i32, ptr %277, align 4
  %379 = mul i32 %377, %256
  %380 = add i32 %379, %248
  %381 = mul i32 %380, %378
  %382 = add i32 %381, 2
  %383 = sext i32 %382 to i64
  %384 = getelementptr float, ptr %376, i64 %383
  %385 = load float, ptr %384, align 4
  %386 = add i32 %379, %264
  %387 = mul i32 %386, %378
  %388 = add i32 %387, 2
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %376, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = mul i32 %377, %272
  %393 = add i32 %392, %248
  %394 = mul i32 %393, %378
  %395 = add i32 %394, 2
  %396 = sext i32 %395 to i64
  %397 = getelementptr float, ptr %376, i64 %396
  %398 = load float, ptr %397, align 4
  %399 = add i32 %392, %264
  %400 = mul i32 %399, %378
  %401 = add i32 %400, 2
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %376, i64 %402
  %404 = load float, ptr %403, align 4
  %405 = fmul reassoc ninf nsz float %385, %301
  %406 = fmul reassoc ninf nsz float %391, %238
  %407 = fadd reassoc ninf nsz float %406, %405
  %408 = fmul reassoc ninf nsz float %398, %301
  %409 = fmul reassoc ninf nsz float %404, %238
  %410 = fadd reassoc ninf nsz float %409, %408
  %411 = fmul reassoc ninf nsz float %407, %308
  %412 = fmul reassoc ninf nsz float %410, %240
  %413 = fadd reassoc ninf nsz float %412, %411
  %414 = fmul reassoc ninf nsz float %413, %228
  %415 = load ptr, ptr %313, align 8
  %416 = load i32, ptr %315, align 4
  %417 = load i32, ptr %317, align 4
  %418 = mul i32 %416, %40
  %419 = sub i32 %418, %39
  %420 = add i32 %lsr.iv10, %419
  %421 = mul i32 %420, %417
  %422 = add i32 %421, 2
  %423 = sext i32 %422 to i64
  %424 = getelementptr float, ptr %415, i64 %423
  %425 = atomicrmw fadd ptr %424, float %414 seq_cst, align 4
  %426 = load ptr, ptr %0, align 8
  %427 = getelementptr i8, ptr %426, i64 96
  %428 = load ptr, ptr %427, align 8
  %429 = getelementptr i8, ptr %426, i64 92
  %430 = load i32, ptr %429, align 4
  %431 = mul i32 %430, %40
  %432 = sub i32 %431, %39
  %433 = add i32 %lsr.iv10, %432
  %434 = sext i32 %433 to i64
  %435 = getelementptr float, ptr %428, i64 %434
  %436 = atomicrmw fadd ptr %435, float %228 seq_cst, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %true_block, %for_loop_body
  %437 = add nsw i32 %.049, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %lsr.iv.next11 = add i32 %lsr.iv10, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.34, align 8
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
