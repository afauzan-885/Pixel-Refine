; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_sample_kernel_vec3_c160_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_bicubic_sample_kernel_vec3_c160_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 52
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 56
  %23 = load i32, ptr %22, align 4
  %24 = add i32 %21, -1
  %25 = add i32 %23, -1
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr i8, ptr %19, i64 24
  %28 = getelementptr i8, ptr %19, i64 20
  %29 = getelementptr i8, ptr %19, i64 8
  %30 = getelementptr i8, ptr %19, i64 4
  %31 = getelementptr i8, ptr %19, i64 40
  %32 = sext i32 %16 to i64
  %wide.trip.count = sext i32 %18 to i64
  %broadcast.splatinsert77 = insertelement <4 x i32> poison, i32 %24, i64 0
  %broadcast.splat78 = shufflevector <4 x i32> %broadcast.splatinsert77, <4 x i32> poison, <4 x i32> zeroinitializer
  %33 = mul i32 %16, 3
  %34 = sub i64 %32, %wide.trip.count
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv106 = phi i64 [ %34, %for_loop_body.lr.ph ], [ %lsr.iv.next107, %for_loop_body ]
  %lsr.iv104 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %lsr.iv.next105, %for_loop_body ]
  %lsr.iv = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %35 = load ptr, ptr %27, align 8
  %36 = load i32, ptr %28, align 4
  %37 = mul i32 %36, %lsr.iv104
  %38 = sext i32 %37 to i64
  %39 = getelementptr float, ptr %35, i64 %38
  %40 = load float, ptr %39, align 4
  %41 = add i32 %37, 1
  %42 = sext i32 %41 to i64
  %43 = getelementptr float, ptr %35, i64 %42
  %44 = load float, ptr %43, align 4
  %45 = tail call reassoc ninf nsz float @llvm.floor.f32(float %44)
  %46 = fptosi float %45 to i32
  %47 = sitofp i32 %46 to float
  %48 = load ptr, ptr %29, align 8
  %49 = tail call reassoc ninf nsz float @llvm.floor.f32(float %40)
  %50 = fptosi float %49 to i32
  %51 = add i32 %50, 2
  %52 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %53 = tail call i32 @llvm.smin.i32(i32 %25, i32 %52)
  %54 = add i32 %50, 1
  %55 = tail call i32 @llvm.smax.i32(i32 %54, i32 0)
  %56 = tail call i32 @llvm.smin.i32(i32 %25, i32 %55)
  %57 = tail call i32 @llvm.smax.i32(i32 %50, i32 0)
  %58 = tail call i32 @llvm.smin.i32(i32 %25, i32 %57)
  %59 = add i32 %50, -1
  %60 = tail call i32 @llvm.smax.i32(i32 %59, i32 0)
  %61 = tail call i32 @llvm.smin.i32(i32 %25, i32 %60)
  %62 = sitofp i32 %50 to float
  %63 = fsub reassoc ninf nsz float %40, %62
  %64 = fmul reassoc ninf nsz float %63, %63
  %65 = load i32, ptr %30, align 4
  %66 = add i32 %46, -1
  %broadcast.splatinsert = insertelement <4 x i32> poison, i32 %66, i64 0
  %broadcast.splat = shufflevector <4 x i32> %broadcast.splatinsert, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert79 = insertelement <4 x i32> poison, i32 %65, i64 0
  %broadcast.splat80 = shufflevector <4 x i32> %broadcast.splatinsert79, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert81 = insertelement <4 x i32> poison, i32 %61, i64 0
  %broadcast.splat82 = shufflevector <4 x i32> %broadcast.splatinsert81, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert85 = insertelement <4 x i32> poison, i32 %58, i64 0
  %broadcast.splat86 = shufflevector <4 x i32> %broadcast.splatinsert85, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert90 = insertelement <4 x i32> poison, i32 %56, i64 0
  %broadcast.splat91 = shufflevector <4 x i32> %broadcast.splatinsert90, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert95 = insertelement <4 x i32> poison, i32 %53, i64 0
  %broadcast.splat96 = shufflevector <4 x i32> %broadcast.splatinsert95, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert100 = insertelement <4 x float> poison, float %63, i64 0
  %broadcast.splat101 = shufflevector <4 x float> %broadcast.splatinsert100, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert102 = insertelement <4 x float> poison, float %64, i64 0
  %broadcast.splat103 = shufflevector <4 x float> %broadcast.splatinsert102, <4 x float> poison, <4 x i32> zeroinitializer
  %67 = add <4 x i32> %broadcast.splat, <i32 0, i32 1, i32 2, i32 3>
  %68 = tail call <4 x i32> @llvm.smax.v4i32(<4 x i32> %67, <4 x i32> zeroinitializer)
  %69 = tail call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat78, <4 x i32> %68)
  %70 = mul <4 x i32> %broadcast.splat80, %69
  %71 = add <4 x i32> %70, %broadcast.splat82
  %72 = mul <4 x i32> %71, splat (i32 3)
  %73 = sext <4 x i32> %72 to <4 x i64>
  %74 = getelementptr float, ptr %48, <4 x i64> %73
  %wide.masked.gather = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %74, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %75 = add <4 x i32> %72, splat (i32 1)
  %76 = sext <4 x i32> %75 to <4 x i64>
  %77 = getelementptr float, ptr %48, <4 x i64> %76
  %wide.masked.gather83 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %77, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %78 = add <4 x i32> %72, splat (i32 2)
  %79 = sext <4 x i32> %78 to <4 x i64>
  %80 = getelementptr float, ptr %48, <4 x i64> %79
  %wide.masked.gather84 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %80, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %81 = add <4 x i32> %70, %broadcast.splat86
  %82 = mul <4 x i32> %81, splat (i32 3)
  %83 = sext <4 x i32> %82 to <4 x i64>
  %84 = getelementptr float, ptr %48, <4 x i64> %83
  %wide.masked.gather87 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %84, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %85 = add <4 x i32> %82, splat (i32 1)
  %86 = sext <4 x i32> %85 to <4 x i64>
  %87 = getelementptr float, ptr %48, <4 x i64> %86
  %wide.masked.gather88 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %87, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %88 = add <4 x i32> %82, splat (i32 2)
  %89 = sext <4 x i32> %88 to <4 x i64>
  %90 = getelementptr float, ptr %48, <4 x i64> %89
  %wide.masked.gather89 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %90, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %91 = add <4 x i32> %70, %broadcast.splat91
  %92 = mul <4 x i32> %91, splat (i32 3)
  %93 = sext <4 x i32> %92 to <4 x i64>
  %94 = getelementptr float, ptr %48, <4 x i64> %93
  %wide.masked.gather92 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %94, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %95 = add <4 x i32> %92, splat (i32 1)
  %96 = sext <4 x i32> %95 to <4 x i64>
  %97 = getelementptr float, ptr %48, <4 x i64> %96
  %wide.masked.gather93 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %97, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %98 = add <4 x i32> %92, splat (i32 2)
  %99 = sext <4 x i32> %98 to <4 x i64>
  %100 = getelementptr float, ptr %48, <4 x i64> %99
  %wide.masked.gather94 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %100, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %101 = add <4 x i32> %70, %broadcast.splat96
  %102 = mul <4 x i32> %101, splat (i32 3)
  %103 = sext <4 x i32> %102 to <4 x i64>
  %104 = getelementptr float, ptr %48, <4 x i64> %103
  %wide.masked.gather97 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %104, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %105 = add <4 x i32> %102, splat (i32 1)
  %106 = sext <4 x i32> %105 to <4 x i64>
  %107 = getelementptr float, ptr %48, <4 x i64> %106
  %wide.masked.gather98 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %107, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %108 = add <4 x i32> %102, splat (i32 2)
  %109 = sext <4 x i32> %108 to <4 x i64>
  %110 = getelementptr float, ptr %48, <4 x i64> %109
  %wide.masked.gather99 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %110, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %111 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather, splat (float -5.000000e-01)
  %112 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather83, splat (float -5.000000e-01)
  %113 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather84, splat (float -5.000000e-01)
  %114 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather97, splat (float 5.000000e-01)
  %115 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather98, splat (float 5.000000e-01)
  %116 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather99, splat (float 5.000000e-01)
  %117 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather87, %wide.masked.gather92
  %118 = fmul reassoc ninf nsz <4 x float> %117, splat (float 1.500000e+00)
  %119 = fadd reassoc ninf nsz <4 x float> %118, %111
  %120 = fadd reassoc ninf nsz <4 x float> %119, %114
  %121 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather88, %wide.masked.gather93
  %122 = fmul reassoc ninf nsz <4 x float> %121, splat (float 1.500000e+00)
  %123 = fadd reassoc ninf nsz <4 x float> %122, %112
  %124 = fadd reassoc ninf nsz <4 x float> %123, %115
  %125 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather89, %wide.masked.gather94
  %126 = fmul reassoc ninf nsz <4 x float> %125, splat (float 1.500000e+00)
  %127 = fadd reassoc ninf nsz <4 x float> %126, %113
  %128 = fadd reassoc ninf nsz <4 x float> %127, %116
  %129 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather87, splat (float -2.500000e+00)
  %130 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather92, splat (float 2.000000e+00)
  %131 = fadd reassoc ninf nsz <4 x float> %129, %wide.masked.gather
  %132 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather88, splat (float -2.500000e+00)
  %133 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather93, splat (float 2.000000e+00)
  %134 = fadd reassoc ninf nsz <4 x float> %132, %wide.masked.gather83
  %135 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather89, splat (float -2.500000e+00)
  %136 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather94, splat (float 2.000000e+00)
  %137 = fadd reassoc ninf nsz <4 x float> %135, %wide.masked.gather84
  %138 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather92, splat (float 5.000000e-01)
  %139 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather93, splat (float 5.000000e-01)
  %140 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather94, splat (float 5.000000e-01)
  %141 = fadd reassoc ninf nsz <4 x float> %138, %111
  %142 = fadd reassoc ninf nsz <4 x float> %139, %112
  %143 = fadd reassoc ninf nsz <4 x float> %140, %113
  %144 = fmul reassoc ninf nsz <4 x float> %120, %broadcast.splat101
  %145 = fmul reassoc ninf nsz <4 x float> %124, %broadcast.splat101
  %146 = fmul reassoc ninf nsz <4 x float> %128, %broadcast.splat101
  %147 = fmul reassoc ninf nsz <4 x float> %141, %broadcast.splat101
  %148 = fmul reassoc ninf nsz <4 x float> %142, %broadcast.splat101
  %149 = fmul reassoc ninf nsz <4 x float> %143, %broadcast.splat101
  %150 = fadd reassoc ninf nsz <4 x float> %131, %130
  %151 = fsub reassoc ninf nsz <4 x float> %150, %114
  %152 = fadd reassoc ninf nsz <4 x float> %151, %144
  %153 = fmul reassoc ninf nsz <4 x float> %152, %broadcast.splat103
  %154 = fadd reassoc ninf nsz <4 x float> %147, %wide.masked.gather87
  %155 = fadd reassoc ninf nsz <4 x float> %154, %153
  %156 = fadd reassoc ninf nsz <4 x float> %134, %133
  %157 = fsub reassoc ninf nsz <4 x float> %156, %115
  %158 = fadd reassoc ninf nsz <4 x float> %157, %145
  %159 = fmul reassoc ninf nsz <4 x float> %158, %broadcast.splat103
  %160 = fadd reassoc ninf nsz <4 x float> %148, %wide.masked.gather88
  %161 = fadd reassoc ninf nsz <4 x float> %160, %159
  %162 = fadd reassoc ninf nsz <4 x float> %137, %136
  %163 = fsub reassoc ninf nsz <4 x float> %162, %116
  %164 = fadd reassoc ninf nsz <4 x float> %163, %146
  %165 = fmul reassoc ninf nsz <4 x float> %164, %broadcast.splat103
  %166 = fadd reassoc ninf nsz <4 x float> %149, %wide.masked.gather89
  %167 = fadd reassoc ninf nsz <4 x float> %166, %165
  %168 = fsub reassoc ninf nsz float %44, %47
  %.sroa.0.0.vec.extract = extractelement <4 x float> %155, i64 0
  %.sroa.0.4.vec.extract = extractelement <4 x float> %161, i64 0
  %.sroa.0.8.vec.extract = extractelement <4 x float> %167, i64 0
  %.sroa.0.12.vec.extract = extractelement <4 x float> %155, i64 1
  %.sroa.0.16.vec.extract = extractelement <4 x float> %161, i64 1
  %.sroa.0.20.vec.extract = extractelement <4 x float> %167, i64 1
  %.sroa.0.24.vec.extract = extractelement <4 x float> %155, i64 2
  %.sroa.0.28.vec.extract = extractelement <4 x float> %161, i64 2
  %.sroa.0.32.vec.extract = extractelement <4 x float> %167, i64 2
  %.sroa.0.36.vec.extract = extractelement <4 x float> %155, i64 3
  %.sroa.0.40.vec.extract = extractelement <4 x float> %161, i64 3
  %.sroa.0.44.vec.extract = extractelement <4 x float> %167, i64 3
  %169 = fmul reassoc ninf nsz float %.sroa.0.0.vec.extract, -5.000000e-01
  %170 = fmul reassoc ninf nsz float %.sroa.0.4.vec.extract, -5.000000e-01
  %171 = fmul reassoc ninf nsz float %.sroa.0.8.vec.extract, -5.000000e-01
  %172 = fmul reassoc ninf nsz float %.sroa.0.36.vec.extract, 5.000000e-01
  %173 = fmul reassoc ninf nsz float %.sroa.0.40.vec.extract, 5.000000e-01
  %174 = fmul reassoc ninf nsz float %.sroa.0.44.vec.extract, 5.000000e-01
  %reass.add30 = fsub reassoc ninf nsz float %.sroa.0.12.vec.extract, %.sroa.0.24.vec.extract
  %reass.mul31 = fmul reassoc ninf nsz float %reass.add30, 1.500000e+00
  %175 = fadd reassoc ninf nsz float %reass.mul31, %169
  %176 = fadd reassoc ninf nsz float %175, %172
  %reass.add33 = fsub reassoc ninf nsz float %.sroa.0.16.vec.extract, %.sroa.0.28.vec.extract
  %reass.mul34 = fmul reassoc ninf nsz float %reass.add33, 1.500000e+00
  %177 = fadd reassoc ninf nsz float %reass.mul34, %170
  %178 = fadd reassoc ninf nsz float %177, %173
  %reass.add36 = fsub reassoc ninf nsz float %.sroa.0.20.vec.extract, %.sroa.0.32.vec.extract
  %reass.mul37 = fmul reassoc ninf nsz float %reass.add36, 1.500000e+00
  %179 = fadd reassoc ninf nsz float %reass.mul37, %171
  %180 = fadd reassoc ninf nsz float %179, %174
  %.neg15 = fmul reassoc ninf nsz float %.sroa.0.12.vec.extract, -2.500000e+00
  %factor = fmul reassoc ninf nsz float %.sroa.0.24.vec.extract, 2.000000e+00
  %181 = fadd reassoc ninf nsz float %.neg15, %.sroa.0.0.vec.extract
  %.neg18 = fmul reassoc ninf nsz float %.sroa.0.16.vec.extract, -2.500000e+00
  %factor21 = fmul reassoc ninf nsz float %.sroa.0.28.vec.extract, 2.000000e+00
  %182 = fadd reassoc ninf nsz float %.neg18, %.sroa.0.4.vec.extract
  %.neg22 = fmul reassoc ninf nsz float %.sroa.0.20.vec.extract, -2.500000e+00
  %factor25 = fmul reassoc ninf nsz float %.sroa.0.32.vec.extract, 2.000000e+00
  %183 = fadd reassoc ninf nsz float %.neg22, %.sroa.0.8.vec.extract
  %184 = fmul reassoc ninf nsz float %.sroa.0.24.vec.extract, 5.000000e-01
  %185 = fmul reassoc ninf nsz float %.sroa.0.28.vec.extract, 5.000000e-01
  %186 = fmul reassoc ninf nsz float %.sroa.0.32.vec.extract, 5.000000e-01
  %187 = fadd reassoc ninf nsz float %184, %169
  %188 = fadd reassoc ninf nsz float %185, %170
  %189 = fadd reassoc ninf nsz float %186, %171
  %190 = fmul reassoc ninf nsz float %168, %168
  %191 = fmul reassoc ninf nsz float %176, %168
  %192 = fmul reassoc ninf nsz float %178, %168
  %193 = fmul reassoc ninf nsz float %180, %168
  %194 = fmul reassoc ninf nsz float %187, %168
  %195 = fmul reassoc ninf nsz float %188, %168
  %196 = fmul reassoc ninf nsz float %189, %168
  %197 = fadd reassoc ninf nsz float %181, %factor
  %198 = fsub reassoc ninf nsz float %197, %172
  %reass.add = fadd reassoc ninf nsz float %198, %191
  %reass.mul = fmul reassoc ninf nsz float %reass.add, %190
  %199 = fadd reassoc ninf nsz float %194, %.sroa.0.12.vec.extract
  %200 = fadd reassoc ninf nsz float %199, %reass.mul
  %201 = fadd reassoc ninf nsz float %182, %factor21
  %202 = fsub reassoc ninf nsz float %201, %173
  %reass.add26 = fadd reassoc ninf nsz float %202, %192
  %reass.mul27 = fmul reassoc ninf nsz float %reass.add26, %190
  %203 = fadd reassoc ninf nsz float %195, %.sroa.0.16.vec.extract
  %204 = fadd reassoc ninf nsz float %203, %reass.mul27
  %205 = fadd reassoc ninf nsz float %183, %factor25
  %206 = fsub reassoc ninf nsz float %205, %174
  %reass.add28 = fadd reassoc ninf nsz float %206, %193
  %reass.mul29 = fmul reassoc ninf nsz float %reass.add28, %190
  %207 = fadd reassoc ninf nsz float %196, %.sroa.0.20.vec.extract
  %208 = fadd reassoc ninf nsz float %207, %reass.mul29
  %209 = load ptr, ptr %31, align 8
  %210 = sext i32 %lsr.iv to i64
  %211 = getelementptr float, ptr %209, i64 %210
  store float %200, ptr %211, align 4
  %212 = load ptr, ptr %31, align 8
  %213 = add i32 %lsr.iv, 1
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %212, i64 %214
  store float %204, ptr %215, align 4
  %216 = load ptr, ptr %31, align 8
  %217 = add i32 %lsr.iv, 2
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %216, i64 %218
  store float %208, ptr %219, align 4
  %lsr.iv.next = add i32 %lsr.iv, 3
  %lsr.iv.next105 = add i32 %lsr.iv104, 1
  %lsr.iv.next107 = add i64 %lsr.iv106, 1
  %exitcond76.not = icmp eq i64 %lsr.iv.next107, 0
  br i1 %exitcond76.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.5, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr>, i32 immarg, <4 x i1>, <4 x float>) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }
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
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
