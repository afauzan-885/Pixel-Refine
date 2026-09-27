; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.38 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @remap_accumulate_spatial_vec3_tile_kernel_c778_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 140
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
  %11 = getelementptr i8, ptr %10, i64 132
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
  %25 = getelementptr i8, ptr %24, i64 136
  %26 = load i32, ptr %25, align 4
  %27 = add i32 %26, -1
  %28 = load ptr, ptr %4, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 28
  store i32 %27, ptr %31, align 4
  %32 = sitofp i32 %27 to float
  %33 = load ptr, ptr %context, align 8
  %34 = getelementptr i8, ptr %33, i64 128
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
  %48 = getelementptr i8, ptr %47, i64 148
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
  %62 = getelementptr i8, ptr %61, i64 144
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
  %76 = getelementptr i8, ptr %75, i64 160
  %77 = load i32, ptr %76, align 4
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = getelementptr i8, ptr %75, i64 164
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

define void @remap_accumulate_spatial_vec3_tile_kernel_c778_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 168
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 172
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.047 = phi i32 [ %544, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  %29 = load i32, ptr %28, align 4
  %30 = sdiv i32 %.047, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.047
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.047, %31
  %35 = and i1 %33, %34
  %.neg6 = sext i1 %35 to i32
  %36 = add i32 %30, %.neg6
  %37 = mul i32 %36, %29
  %38 = add i32 %36, %21
  %39 = mul i32 %29, -1
  %40 = mul i32 %39, %36
  %41 = add i32 %23, %.047
  %42 = add i32 %41, %40
  %43 = getelementptr inbounds nuw i8, ptr %27, i64 8
  %44 = load i32, ptr %43, align 4
  %45 = icmp slt i32 %38, %44
  br i1 %45, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = getelementptr inbounds nuw i8, ptr %27, i64 12
  %47 = load i32, ptr %46, align 4
  %48 = icmp slt i32 %42, %47
  br i1 %48, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %49 = sitofp i32 %42 to float
  %50 = getelementptr inbounds nuw i8, ptr %27, i64 16
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sitofp i32 %38 to float
  %54 = getelementptr inbounds nuw i8, ptr %27, i64 20
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %58 = fptosi float %57 to i32
  %59 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %60 = fptosi float %59 to i32
  %61 = sitofp i32 %58 to float
  %62 = fsub reassoc ninf nsz float %52, %61
  %63 = sitofp i32 %60 to float
  %64 = fsub reassoc ninf nsz float %56, %63
  %65 = tail call i32 @llvm.abs.i32(i32 %58, i1 true)
  %66 = getelementptr inbounds nuw i8, ptr %27, i64 24
  %67 = load i32, ptr %66, align 4
  %68 = sub i32 %65, %67
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = shl nuw i32 %69, 1
  %71 = sub i32 %65, %70
  %72 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %73 = tail call i32 @llvm.smin.i32(i32 %67, i32 %72)
  %74 = tail call i32 @llvm.abs.i32(i32 %60, i1 true)
  %75 = getelementptr inbounds nuw i8, ptr %27, i64 28
  %76 = load i32, ptr %75, align 4
  %77 = sub i32 %74, %76
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = shl nuw i32 %78, 1
  %80 = sub i32 %74, %79
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = tail call i32 @llvm.smin.i32(i32 %76, i32 %81)
  %83 = add i32 %58, 1
  %84 = tail call i32 @llvm.abs.i32(i32 %83, i1 true)
  %85 = sub i32 %84, %67
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = shl nuw i32 %86, 1
  %88 = sub i32 %84, %87
  %89 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %67, i32 %89)
  %91 = add i32 %60, 1
  %92 = tail call i32 @llvm.abs.i32(i32 %91, i1 true)
  %93 = sub i32 %92, %76
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = shl nuw i32 %94, 1
  %96 = sub i32 %92, %95
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = tail call i32 @llvm.smin.i32(i32 %76, i32 %97)
  %99 = load ptr, ptr %0, align 8
  %100 = getelementptr i8, ptr %99, i64 40
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr i8, ptr %99, i64 28
  %103 = load i32, ptr %102, align 4
  %104 = getelementptr i8, ptr %99, i64 32
  %105 = load i32, ptr %104, align 4
  %106 = mul i32 %82, %103
  %107 = add i32 %106, %73
  %108 = mul i32 %107, %105
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %101, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = add i32 %106, %90
  %113 = mul i32 %112, %105
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %101, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = mul i32 %98, %103
  %118 = add i32 %117, %73
  %119 = mul i32 %118, %105
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %101, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %117, %90
  %124 = mul i32 %123, %105
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %101, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = fsub reassoc ninf nsz float 1.000000e+00, %62
  %129 = fmul reassoc ninf nsz float %111, %128
  %130 = fmul reassoc ninf nsz float %116, %62
  %131 = fadd reassoc ninf nsz float %130, %129
  %132 = fmul reassoc ninf nsz float %122, %128
  %133 = fmul reassoc ninf nsz float %127, %62
  %134 = fadd reassoc ninf nsz float %133, %132
  %135 = fsub reassoc ninf nsz float 1.000000e+00, %64
  %136 = fmul reassoc ninf nsz float %131, %135
  %137 = fmul reassoc ninf nsz float %134, %64
  %138 = fadd reassoc ninf nsz float %137, %136
  %139 = add i32 %108, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %101, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %113, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %101, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %119, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %101, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %124, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %101, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %142, %128
  %156 = fmul reassoc ninf nsz float %146, %62
  %157 = fadd reassoc ninf nsz float %156, %155
  %158 = fmul reassoc ninf nsz float %150, %128
  %159 = fmul reassoc ninf nsz float %154, %62
  %160 = fadd reassoc ninf nsz float %159, %158
  %161 = fmul reassoc ninf nsz float %157, %135
  %162 = fmul reassoc ninf nsz float %160, %64
  %163 = fadd reassoc ninf nsz float %162, %161
  %164 = getelementptr i8, ptr %99, i64 152
  %165 = load float, ptr %164, align 4
  %166 = fmul reassoc ninf nsz float %165, %138
  %167 = fadd reassoc ninf nsz float %166, %49
  %168 = getelementptr i8, ptr %99, i64 156
  %169 = load float, ptr %168, align 4
  %170 = fmul reassoc ninf nsz float %163, %169
  %171 = fadd reassoc ninf nsz float %170, %53
  %172 = getelementptr inbounds nuw i8, ptr %27, i64 32
  %173 = load float, ptr %172, align 4
  %174 = fmul reassoc ninf nsz float %173, %49
  %175 = getelementptr inbounds nuw i8, ptr %27, i64 36
  %176 = load float, ptr %175, align 4
  %177 = fmul reassoc ninf nsz float %176, %53
  %178 = tail call reassoc ninf nsz float @llvm.floor.f32(float %174)
  %179 = fptosi float %178 to i32
  %180 = tail call reassoc ninf nsz float @llvm.floor.f32(float %177)
  %181 = fptosi float %180 to i32
  %182 = add i32 %179, 1
  %183 = getelementptr inbounds nuw i8, ptr %27, i64 40
  %184 = load i32, ptr %183, align 4
  %185 = add i32 %184, -1
  %186 = tail call i32 @llvm.smin.i32(i32 %182, i32 %185)
  %187 = add i32 %181, 1
  %188 = getelementptr inbounds nuw i8, ptr %27, i64 44
  %189 = load i32, ptr %188, align 4
  %190 = add i32 %189, -1
  %191 = tail call i32 @llvm.smin.i32(i32 %187, i32 %190)
  %192 = tail call i32 @llvm.smax.i32(i32 %179, i32 0)
  %193 = tail call i32 @llvm.smax.i32(i32 %181, i32 0)
  %194 = uitofp nneg i32 %192 to float
  %195 = fsub reassoc ninf nsz float %174, %194
  %196 = uitofp nneg i32 %193 to float
  %197 = fsub reassoc ninf nsz float %177, %196
  %198 = fsub reassoc ninf nsz float 1.000000e+00, %197
  %199 = fsub reassoc ninf nsz float 1.000000e+00, %195
  %200 = fmul reassoc ninf nsz float %198, %199
  %201 = getelementptr i8, ptr %99, i64 64
  %202 = load ptr, ptr %201, align 8
  %203 = getelementptr i8, ptr %99, i64 52
  %204 = load i32, ptr %203, align 4
  %205 = getelementptr i8, ptr %99, i64 56
  %206 = load i32, ptr %205, align 4
  %207 = mul i32 %193, %204
  %208 = add i32 %207, %192
  %209 = mul i32 %208, %206
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, ptr %202, i64 %210
  %212 = load float, ptr %211, align 4
  %213 = fmul reassoc ninf nsz float %200, %212
  %214 = fmul reassoc ninf nsz float %198, %195
  %215 = add i32 %207, %186
  %216 = mul i32 %215, %206
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %202, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %214, %219
  %221 = fadd reassoc ninf nsz float %213, %220
  %222 = fmul reassoc ninf nsz float %197, %199
  %223 = mul i32 %191, %204
  %224 = add i32 %223, %192
  %225 = mul i32 %224, %206
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %202, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = fmul reassoc ninf nsz float %228, %222
  %230 = fadd reassoc ninf nsz float %221, %229
  %231 = fmul reassoc ninf nsz float %197, %195
  %232 = add i32 %223, %186
  %233 = mul i32 %232, %206
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, ptr %202, i64 %234
  %236 = load float, ptr %235, align 4
  %237 = fmul reassoc ninf nsz float %236, %231
  %238 = fadd reassoc ninf nsz float %230, %237
  %239 = getelementptr i8, ptr %99, i64 120
  %240 = load i32, ptr %239, align 4
  %241 = getelementptr i8, ptr %99, i64 124
  %242 = load i32, ptr %241, align 4
  %243 = tail call reassoc ninf nsz float @llvm.floor.f32(float %167)
  %244 = fptosi float %243 to i32
  %245 = tail call reassoc ninf nsz float @llvm.floor.f32(float %171)
  %246 = fptosi float %245 to i32
  %247 = sitofp i32 %244 to float
  %248 = fsub reassoc ninf nsz float %167, %247
  %249 = sitofp i32 %246 to float
  %250 = fsub reassoc ninf nsz float %171, %249
  %251 = tail call i32 @llvm.abs.i32(i32 %244, i1 true)
  %252 = add i32 %242, -1
  %253 = sub i32 %251, %252
  %254 = tail call i32 @llvm.smax.i32(i32 %253, i32 0)
  %255 = shl nuw i32 %254, 1
  %256 = sub i32 %251, %255
  %257 = tail call i32 @llvm.smax.i32(i32 %256, i32 0)
  %258 = tail call i32 @llvm.smin.i32(i32 %252, i32 %257)
  %259 = tail call i32 @llvm.abs.i32(i32 %246, i1 true)
  %260 = add i32 %240, -1
  %261 = sub i32 %259, %260
  %262 = tail call i32 @llvm.smax.i32(i32 %261, i32 0)
  %263 = shl nuw i32 %262, 1
  %264 = sub i32 %259, %263
  %265 = tail call i32 @llvm.smax.i32(i32 %264, i32 0)
  %266 = tail call i32 @llvm.smin.i32(i32 %260, i32 %265)
  %267 = add i32 %244, 1
  %268 = tail call i32 @llvm.abs.i32(i32 %267, i1 true)
  %269 = sub i32 %268, %252
  %270 = tail call i32 @llvm.smax.i32(i32 %269, i32 0)
  %271 = shl nuw i32 %270, 1
  %272 = sub i32 %268, %271
  %273 = tail call i32 @llvm.smax.i32(i32 %272, i32 0)
  %274 = tail call i32 @llvm.smin.i32(i32 %252, i32 %273)
  %275 = add i32 %246, 1
  %276 = tail call i32 @llvm.abs.i32(i32 %275, i1 true)
  %277 = sub i32 %276, %260
  %278 = tail call i32 @llvm.smax.i32(i32 %277, i32 0)
  %279 = shl nuw i32 %278, 1
  %280 = sub i32 %276, %279
  %281 = tail call i32 @llvm.smax.i32(i32 %280, i32 0)
  %282 = tail call i32 @llvm.smin.i32(i32 %260, i32 %281)
  %283 = getelementptr i8, ptr %99, i64 16
  %284 = load ptr, ptr %283, align 8
  %285 = getelementptr i8, ptr %99, i64 4
  %286 = load i32, ptr %285, align 4
  %287 = getelementptr i8, ptr %99, i64 8
  %288 = load i32, ptr %287, align 4
  %289 = mul i32 %266, %286
  %290 = add i32 %289, %258
  %291 = mul i32 %290, %288
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, ptr %284, i64 %292
  %294 = load float, ptr %293, align 4
  %295 = add i32 %289, %274
  %296 = mul i32 %295, %288
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %284, i64 %297
  %299 = load float, ptr %298, align 4
  %300 = mul i32 %282, %286
  %301 = add i32 %300, %258
  %302 = mul i32 %301, %288
  %303 = sext i32 %302 to i64
  %304 = getelementptr float, ptr %284, i64 %303
  %305 = load float, ptr %304, align 4
  %306 = add i32 %300, %274
  %307 = mul i32 %306, %288
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %284, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = fsub reassoc ninf nsz float 1.000000e+00, %248
  %312 = fmul reassoc ninf nsz float %294, %311
  %313 = fmul reassoc ninf nsz float %299, %248
  %314 = fadd reassoc ninf nsz float %313, %312
  %315 = fmul reassoc ninf nsz float %305, %311
  %316 = fmul reassoc ninf nsz float %310, %248
  %317 = fadd reassoc ninf nsz float %316, %315
  %318 = fsub reassoc ninf nsz float 1.000000e+00, %250
  %319 = fmul reassoc ninf nsz float %314, %318
  %320 = fmul reassoc ninf nsz float %317, %250
  %321 = fadd reassoc ninf nsz float %320, %319
  %322 = fmul reassoc ninf nsz float %321, %238
  %323 = getelementptr i8, ptr %99, i64 88
  %324 = load ptr, ptr %323, align 8
  %325 = getelementptr i8, ptr %99, i64 76
  %326 = load i32, ptr %325, align 4
  %327 = getelementptr i8, ptr %99, i64 80
  %328 = load i32, ptr %327, align 4
  %329 = mul i32 %326, %38
  %330 = sub i32 %329, %37
  %331 = add i32 %41, %330
  %332 = mul i32 %331, %328
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, ptr %324, i64 %333
  %335 = atomicrmw fadd ptr %334, float %322 seq_cst, align 4
  %336 = load ptr, ptr %0, align 8
  %337 = getelementptr i8, ptr %336, i64 112
  %338 = load ptr, ptr %337, align 8
  %339 = getelementptr i8, ptr %336, i64 100
  %340 = load i32, ptr %339, align 4
  %341 = getelementptr i8, ptr %336, i64 104
  %342 = load i32, ptr %341, align 4
  %343 = mul i32 %340, %38
  %344 = sub i32 %343, %37
  %345 = add i32 %41, %344
  %346 = mul i32 %345, %342
  %347 = sext i32 %346 to i64
  %348 = getelementptr float, ptr %338, i64 %347
  %349 = atomicrmw fadd ptr %348, float %238 seq_cst, align 4
  %350 = load ptr, ptr %201, align 8
  %351 = load i32, ptr %203, align 4
  %352 = load i32, ptr %205, align 4
  %353 = mul i32 %351, %193
  %354 = add i32 %353, %192
  %355 = mul i32 %354, %352
  %356 = add i32 %355, 1
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, ptr %350, i64 %357
  %359 = load float, ptr %358, align 4
  %360 = fmul reassoc ninf nsz float %359, %200
  %361 = add i32 %353, %186
  %362 = mul i32 %361, %352
  %363 = add i32 %362, 1
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %350, i64 %364
  %366 = load float, ptr %365, align 4
  %367 = fmul reassoc ninf nsz float %366, %214
  %368 = fadd reassoc ninf nsz float %367, %360
  %369 = mul i32 %351, %191
  %370 = add i32 %369, %192
  %371 = mul i32 %370, %352
  %372 = add i32 %371, 1
  %373 = sext i32 %372 to i64
  %374 = getelementptr float, ptr %350, i64 %373
  %375 = load float, ptr %374, align 4
  %376 = fmul reassoc ninf nsz float %375, %222
  %377 = fadd reassoc ninf nsz float %368, %376
  %378 = add i32 %369, %186
  %379 = mul i32 %378, %352
  %380 = add i32 %379, 1
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, ptr %350, i64 %381
  %383 = load float, ptr %382, align 4
  %384 = fmul reassoc ninf nsz float %383, %231
  %385 = fadd reassoc ninf nsz float %377, %384
  %386 = load ptr, ptr %283, align 8
  %387 = load i32, ptr %285, align 4
  %388 = load i32, ptr %287, align 4
  %389 = mul i32 %387, %266
  %390 = add i32 %389, %258
  %391 = mul i32 %390, %388
  %392 = add i32 %391, 1
  %393 = sext i32 %392 to i64
  %394 = getelementptr float, ptr %386, i64 %393
  %395 = load float, ptr %394, align 4
  %396 = add i32 %389, %274
  %397 = mul i32 %396, %388
  %398 = add i32 %397, 1
  %399 = sext i32 %398 to i64
  %400 = getelementptr float, ptr %386, i64 %399
  %401 = load float, ptr %400, align 4
  %402 = mul i32 %387, %282
  %403 = add i32 %402, %258
  %404 = mul i32 %403, %388
  %405 = add i32 %404, 1
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %386, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = add i32 %402, %274
  %410 = mul i32 %409, %388
  %411 = add i32 %410, 1
  %412 = sext i32 %411 to i64
  %413 = getelementptr float, ptr %386, i64 %412
  %414 = load float, ptr %413, align 4
  %415 = fmul reassoc ninf nsz float %395, %311
  %416 = fmul reassoc ninf nsz float %401, %248
  %417 = fadd reassoc ninf nsz float %416, %415
  %418 = fmul reassoc ninf nsz float %408, %311
  %419 = fmul reassoc ninf nsz float %414, %248
  %420 = fadd reassoc ninf nsz float %419, %418
  %421 = fmul reassoc ninf nsz float %417, %318
  %422 = fmul reassoc ninf nsz float %420, %250
  %423 = fadd reassoc ninf nsz float %422, %421
  %424 = fmul reassoc ninf nsz float %423, %385
  %425 = load ptr, ptr %323, align 8
  %426 = load i32, ptr %325, align 4
  %427 = load i32, ptr %327, align 4
  %428 = mul i32 %426, %38
  %429 = sub i32 %428, %37
  %430 = add i32 %41, %429
  %431 = mul i32 %430, %427
  %432 = add i32 %431, 1
  %433 = sext i32 %432 to i64
  %434 = getelementptr float, ptr %425, i64 %433
  %435 = atomicrmw fadd ptr %434, float %424 seq_cst, align 4
  %436 = load ptr, ptr %337, align 8
  %437 = load i32, ptr %339, align 4
  %438 = load i32, ptr %341, align 4
  %439 = mul i32 %437, %38
  %440 = sub i32 %439, %37
  %441 = add i32 %41, %440
  %442 = mul i32 %441, %438
  %443 = add i32 %442, 1
  %444 = sext i32 %443 to i64
  %445 = getelementptr float, ptr %436, i64 %444
  %446 = atomicrmw fadd ptr %445, float %385 seq_cst, align 4
  %447 = load ptr, ptr %201, align 8
  %448 = load i32, ptr %203, align 4
  %449 = load i32, ptr %205, align 4
  %450 = mul i32 %448, %193
  %451 = add i32 %450, %192
  %452 = mul i32 %451, %449
  %453 = add i32 %452, 2
  %454 = sext i32 %453 to i64
  %455 = getelementptr float, ptr %447, i64 %454
  %456 = load float, ptr %455, align 4
  %457 = fmul reassoc ninf nsz float %456, %200
  %458 = add i32 %450, %186
  %459 = mul i32 %458, %449
  %460 = add i32 %459, 2
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %447, i64 %461
  %463 = load float, ptr %462, align 4
  %464 = fmul reassoc ninf nsz float %463, %214
  %465 = fadd reassoc ninf nsz float %464, %457
  %466 = mul i32 %448, %191
  %467 = add i32 %466, %192
  %468 = mul i32 %467, %449
  %469 = add i32 %468, 2
  %470 = sext i32 %469 to i64
  %471 = getelementptr float, ptr %447, i64 %470
  %472 = load float, ptr %471, align 4
  %473 = fmul reassoc ninf nsz float %472, %222
  %474 = fadd reassoc ninf nsz float %465, %473
  %475 = add i32 %466, %186
  %476 = mul i32 %475, %449
  %477 = add i32 %476, 2
  %478 = sext i32 %477 to i64
  %479 = getelementptr float, ptr %447, i64 %478
  %480 = load float, ptr %479, align 4
  %481 = fmul reassoc ninf nsz float %480, %231
  %482 = fadd reassoc ninf nsz float %474, %481
  %483 = load ptr, ptr %283, align 8
  %484 = load i32, ptr %285, align 4
  %485 = load i32, ptr %287, align 4
  %486 = mul i32 %484, %266
  %487 = add i32 %486, %258
  %488 = mul i32 %487, %485
  %489 = add i32 %488, 2
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, ptr %483, i64 %490
  %492 = load float, ptr %491, align 4
  %493 = add i32 %486, %274
  %494 = mul i32 %493, %485
  %495 = add i32 %494, 2
  %496 = sext i32 %495 to i64
  %497 = getelementptr float, ptr %483, i64 %496
  %498 = load float, ptr %497, align 4
  %499 = mul i32 %484, %282
  %500 = add i32 %499, %258
  %501 = mul i32 %500, %485
  %502 = add i32 %501, 2
  %503 = sext i32 %502 to i64
  %504 = getelementptr float, ptr %483, i64 %503
  %505 = load float, ptr %504, align 4
  %506 = add i32 %499, %274
  %507 = mul i32 %506, %485
  %508 = add i32 %507, 2
  %509 = sext i32 %508 to i64
  %510 = getelementptr float, ptr %483, i64 %509
  %511 = load float, ptr %510, align 4
  %512 = fmul reassoc ninf nsz float %492, %311
  %513 = fmul reassoc ninf nsz float %498, %248
  %514 = fadd reassoc ninf nsz float %513, %512
  %515 = fmul reassoc ninf nsz float %505, %311
  %516 = fmul reassoc ninf nsz float %511, %248
  %517 = fadd reassoc ninf nsz float %516, %515
  %518 = fmul reassoc ninf nsz float %514, %318
  %519 = fmul reassoc ninf nsz float %517, %250
  %520 = fadd reassoc ninf nsz float %519, %518
  %521 = fmul reassoc ninf nsz float %520, %482
  %522 = load ptr, ptr %323, align 8
  %523 = load i32, ptr %325, align 4
  %524 = load i32, ptr %327, align 4
  %525 = mul i32 %523, %38
  %526 = sub i32 %525, %37
  %527 = add i32 %41, %526
  %528 = mul i32 %527, %524
  %529 = add i32 %528, 2
  %530 = sext i32 %529 to i64
  %531 = getelementptr float, ptr %522, i64 %530
  %532 = atomicrmw fadd ptr %531, float %521 seq_cst, align 4
  %533 = load ptr, ptr %337, align 8
  %534 = load i32, ptr %339, align 4
  %535 = load i32, ptr %341, align 4
  %536 = mul i32 %534, %38
  %537 = sub i32 %536, %37
  %538 = add i32 %41, %537
  %539 = mul i32 %538, %535
  %540 = add i32 %539, 2
  %541 = sext i32 %540 to i64
  %542 = getelementptr float, ptr %533, i64 %541
  %543 = atomicrmw fadd ptr %542, float %482 seq_cst, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %true_block, %for_loop_body
  %544 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %18, %544
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

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
