; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { ptr, ptr, i64 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_admm_step1_kernel_c90_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %1, i64 0, i32 5
  %3 = load i32, ptr %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, ptr %context, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %5, i64 0, i32 14
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds i8, ptr %7, i64 8
  %9 = bitcast ptr %8 to ptr
  store i32 %3, ptr %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load ptr, ptr %0, align 8
  %12 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %11, i64 0, i32 6
  %13 = load i32, ptr %12, align 4
  %14 = load ptr, ptr %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %14, i64 0, i32 14
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds i8, ptr %16, i64 12
  %18 = bitcast ptr %17 to ptr
  store i32 %13, ptr %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load ptr, ptr %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %20, i64 0, i32 14
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds i8, ptr %22, i64 4
  %24 = bitcast ptr %23 to ptr
  store i32 %19, ptr %24, align 4
  %25 = mul i32 %19, %10
  %26 = load ptr, ptr %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %26, i64 0, i32 14
  %28 = bitcast ptr %27 to ptr
  %29 = load ptr, ptr %28, align 8
  store i32 %25, ptr %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_admm_step1_kernel_c90_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %0, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %0, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %0, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %0, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.36, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %4, i64 0, i32 14
  %6 = bitcast ptr %5 to ptr
  %7 = load ptr, ptr %6, align 8
  %8 = load i32, ptr %7, align 4
  %9 = add i32 %8, 7
  %10 = sdiv i32 %9, 8
  %11 = icmp slt i32 %9, 0
  %12 = shl nsw i32 %10, 3
  %13 = icmp ne i32 %12, %9
  %14 = and i1 %11, %13
  %.neg = sext i1 %14 to i32
  %15 = add nsw i32 %10, %.neg
  %16 = tail call i32 @llvm.smax.i32(i32 %15, i32 512)
  %17 = mul i32 %16, %2
  %18 = add i32 %17, %16
  %19 = tail call i32 @llvm.smin.i32(i32 %8, i32 %18)
  %20 = bitcast ptr %0 to ptr
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load ptr, ptr %20, align 8
  %23 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 3, i32 1
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 3, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 4, i32 1
  %28 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %22, i64 0, i32 4, i32 0, i32 1
  %29 = sub i32 0, %19
  %30 = add i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if105, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %30, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if105 ]
  %.0102213 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %463, %after_if105 ]
  %31 = add nsw i32 %lsr.iv, -1
  %32 = load ptr, ptr %3, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %32, i64 0, i32 14
  %34 = load ptr, ptr %33, align 8
  %35 = getelementptr inbounds i8, ptr %34, i64 4
  %36 = bitcast ptr %35 to ptr
  %37 = load i32, ptr %36, align 4
  %38 = sdiv i32 %31, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %31
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %lsr.iv, 1
  %43 = icmp ne i32 %31, %39
  %44 = and i1 %42, %41
  %45 = and i1 %44, %43
  %.neg139 = sext i1 %45 to i32
  %46 = add i32 %38, %.neg139
  %47 = mul i32 %46, %37
  %48 = sub i32 %.0102213, %47
  %49 = mul i32 %37, -1
  %50 = mul i32 %49, %46
  %51 = add i32 %lsr.iv, %50
  %52 = add i32 %51, -1
  %53 = add i32 %46, -1
  %54 = add i32 %51, -2
  %55 = icmp sgt i32 %53, -1
  br i1 %55, label %true_block, label %after_if21

after_for.loopexit:                               ; preds = %after_if105
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %56 = getelementptr inbounds i8, ptr %34, i64 8
  %57 = bitcast ptr %56 to ptr
  %58 = load i32, ptr %57, align 4
  %59 = icmp slt i32 %53, %58
  %60 = icmp sgt i32 %54, -1
  %or.cond = select i1 %59, i1 %60, i1 false
  br i1 %or.cond, label %true_block4, label %true_block10

true_block4:                                      ; preds = %true_block
  %61 = getelementptr inbounds i8, ptr %34, i64 12
  %62 = bitcast ptr %61 to ptr
  %63 = load i32, ptr %62, align 4
  %64 = icmp slt i32 %54, %63
  br i1 %64, label %true_block7, label %true_block10

true_block7:                                      ; preds = %true_block4
  %65 = load ptr, ptr %20, align 8
  %66 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %65, i64 0, i32 1, i32 1
  %67 = load ptr, ptr %66, align 8
  %68 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %65, i64 0, i32 1, i32 0, i32 1
  %69 = load i32, ptr %68, align 4
  %70 = mul i32 %69, %53
  %71 = sub i32 %70, %47
  %72 = add i32 %lsr.iv, %71
  %73 = add i32 %72, -2
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %67, i64 %74
  %76 = load float, ptr %75, align 4
  %77 = load ptr, ptr %23, align 8
  %78 = load i32, ptr %24, align 4
  %79 = mul i32 %78, %53
  %80 = sub i32 %79, %47
  %81 = add i32 %lsr.iv, %80
  %82 = add i32 %81, -2
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %77, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fsub reassoc ninf nsz float %76, %85
  %87 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %65, i64 0, i32 2, i32 1
  %88 = load ptr, ptr %87, align 8
  %89 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %65, i64 0, i32 2, i32 0, i32 1
  %90 = load i32, ptr %89, align 4
  %91 = mul i32 %90, %53
  %92 = sub i32 %91, %47
  %93 = add i32 %lsr.iv, %92
  %94 = add i32 %93, -2
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %88, i64 %95
  %97 = load float, ptr %96, align 4
  %98 = fsub reassoc ninf nsz float %97, %85
  br label %true_block10

true_block10:                                     ; preds = %true_block7, %true_block4, %true_block
  %.093.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ %86, %true_block7 ]
  %.084.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ %98, %true_block7 ]
  %.083.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ 1.000000e+00, %true_block7 ]
  %99 = icmp sgt i32 %52, -1
  %or.cond149 = select i1 %59, i1 %99, i1 false
  br i1 %or.cond149, label %true_block16, label %true_block22

true_block16:                                     ; preds = %true_block10
  %100 = getelementptr inbounds i8, ptr %34, i64 12
  %101 = bitcast ptr %100 to ptr
  %102 = load i32, ptr %101, align 4
  %103 = icmp slt i32 %52, %102
  br i1 %103, label %true_block19, label %true_block22

true_block19:                                     ; preds = %true_block16
  %104 = load ptr, ptr %20, align 8
  %105 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %104, i64 0, i32 1, i32 1
  %106 = load ptr, ptr %105, align 8
  %107 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %104, i64 0, i32 1, i32 0, i32 1
  %108 = load i32, ptr %107, align 4
  %109 = mul i32 %108, %53
  %110 = sub i32 %109, %47
  %111 = add i32 %lsr.iv, %110
  %112 = add i32 %111, -1
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %106, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = load ptr, ptr %23, align 8
  %117 = load i32, ptr %24, align 4
  %118 = mul i32 %117, %53
  %119 = sub i32 %118, %47
  %120 = add i32 %lsr.iv, %119
  %121 = add i32 %120, -1
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %116, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fadd reassoc ninf nsz float %115, %.093.ph
  %126 = fsub reassoc ninf nsz float %125, %124
  %127 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %104, i64 0, i32 2, i32 1
  %128 = load ptr, ptr %127, align 8
  %129 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %104, i64 0, i32 2, i32 0, i32 1
  %130 = load i32, ptr %129, align 4
  %131 = mul i32 %130, %53
  %132 = sub i32 %131, %47
  %133 = add i32 %lsr.iv, %132
  %134 = add i32 %133, -1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %128, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = fsub reassoc ninf nsz float %.084.ph, %124
  %139 = fadd reassoc ninf nsz float %138, %137
  %140 = fadd reassoc ninf nsz float %.083.ph, 1.000000e+00
  br label %true_block22

after_if21:                                       ; preds = %for_loop_body
  %141 = add i32 %48, 1
  br label %after_if33

true_block22:                                     ; preds = %true_block19, %true_block16, %true_block10
  %.194.ph = phi float [ %.093.ph, %true_block10 ], [ %.093.ph, %true_block16 ], [ %126, %true_block19 ]
  %.185.ph = phi float [ %.084.ph, %true_block10 ], [ %.084.ph, %true_block16 ], [ %139, %true_block19 ]
  %.1.ph = phi float [ %.083.ph, %true_block10 ], [ %.083.ph, %true_block16 ], [ %140, %true_block19 ]
  %142 = icmp sgt i32 %51, -1
  %or.cond150 = select i1 %59, i1 %142, i1 false
  br i1 %or.cond150, label %true_block28, label %true_block22.after_if33_crit_edge

true_block22.after_if33_crit_edge:                ; preds = %true_block22
  br label %after_if33

true_block28:                                     ; preds = %true_block22
  %143 = getelementptr inbounds i8, ptr %34, i64 12
  %144 = bitcast ptr %143 to ptr
  %145 = load i32, ptr %144, align 4
  %146 = icmp slt i32 %51, %145
  br i1 %146, label %true_block31, label %true_block28.true_block34_crit_edge

true_block28.true_block34_crit_edge:              ; preds = %true_block28
  br label %true_block34

true_block31:                                     ; preds = %true_block28
  %147 = load ptr, ptr %20, align 8
  %148 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %147, i64 0, i32 1, i32 1
  %149 = load ptr, ptr %148, align 8
  %150 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %147, i64 0, i32 1, i32 0, i32 1
  %151 = load i32, ptr %150, align 4
  %152 = mul i32 %151, %53
  %153 = sub i32 %152, %47
  %154 = add i32 %lsr.iv, %153
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %149, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = load ptr, ptr %23, align 8
  %159 = load i32, ptr %24, align 4
  %160 = mul i32 %159, %53
  %161 = sub i32 %160, %47
  %162 = add i32 %lsr.iv, %161
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %158, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = fadd reassoc ninf nsz float %157, %.194.ph
  %167 = fsub reassoc ninf nsz float %166, %165
  %168 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %147, i64 0, i32 2, i32 1
  %169 = load ptr, ptr %168, align 8
  %170 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %147, i64 0, i32 2, i32 0, i32 1
  %171 = load i32, ptr %170, align 4
  %172 = mul i32 %171, %53
  %173 = sub i32 %172, %47
  %174 = add i32 %lsr.iv, %173
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %169, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = fsub reassoc ninf nsz float %.185.ph, %165
  %179 = fadd reassoc ninf nsz float %178, %177
  %180 = fadd reassoc ninf nsz float %.1.ph, 1.000000e+00
  br label %true_block34

after_if33:                                       ; preds = %true_block22.after_if33_crit_edge, %after_if21
  %181 = phi i32 [ %141, %after_if21 ], [ %51, %true_block22.after_if33_crit_edge ]
  %.295 = phi float [ 0.000000e+00, %after_if21 ], [ %.194.ph, %true_block22.after_if33_crit_edge ]
  %.286 = phi float [ 0.000000e+00, %after_if21 ], [ %.185.ph, %true_block22.after_if33_crit_edge ]
  %.2 = phi float [ 0.000000e+00, %after_if21 ], [ %.1.ph, %true_block22.after_if33_crit_edge ]
  %182 = icmp sgt i32 %46, -1
  br i1 %182, label %after_if33.true_block34_crit_edge, label %after_if69

after_if33.true_block34_crit_edge:                ; preds = %after_if33
  %.phi.trans.insert = getelementptr inbounds i8, ptr %34, i64 8
  %.phi.trans.insert214 = bitcast ptr %.phi.trans.insert to ptr
  %.pre = load i32, ptr %.phi.trans.insert214, align 4
  br label %true_block34

true_block34:                                     ; preds = %after_if33.true_block34_crit_edge, %true_block31, %true_block28.true_block34_crit_edge
  %183 = phi i32 [ %.pre, %after_if33.true_block34_crit_edge ], [ %58, %true_block28.true_block34_crit_edge ], [ %58, %true_block31 ]
  %.2174 = phi float [ %.2, %after_if33.true_block34_crit_edge ], [ %.1.ph, %true_block28.true_block34_crit_edge ], [ %180, %true_block31 ]
  %.286173 = phi float [ %.286, %after_if33.true_block34_crit_edge ], [ %.185.ph, %true_block28.true_block34_crit_edge ], [ %179, %true_block31 ]
  %.295172 = phi float [ %.295, %after_if33.true_block34_crit_edge ], [ %.194.ph, %true_block28.true_block34_crit_edge ], [ %167, %true_block31 ]
  %184 = phi i32 [ %181, %after_if33.true_block34_crit_edge ], [ %51, %true_block28.true_block34_crit_edge ], [ %51, %true_block31 ]
  %185 = icmp slt i32 %46, %183
  %186 = icmp sgt i32 %54, -1
  %or.cond151 = select i1 %185, i1 %186, i1 false
  br i1 %or.cond151, label %true_block40, label %true_block46

true_block40:                                     ; preds = %true_block34
  %187 = getelementptr inbounds i8, ptr %34, i64 12
  %188 = bitcast ptr %187 to ptr
  %189 = load i32, ptr %188, align 4
  %190 = icmp slt i32 %54, %189
  br i1 %190, label %true_block43, label %true_block46

true_block43:                                     ; preds = %true_block40
  %191 = load ptr, ptr %20, align 8
  %192 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %191, i64 0, i32 1, i32 1
  %193 = load ptr, ptr %192, align 8
  %194 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %191, i64 0, i32 1, i32 0, i32 1
  %195 = load i32, ptr %194, align 4
  %196 = sub i32 %195, %37
  %197 = mul i32 %196, %46
  %198 = add i32 %lsr.iv, %197
  %199 = add i32 %198, -2
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, ptr %193, i64 %200
  %202 = load float, ptr %201, align 4
  %203 = load ptr, ptr %23, align 8
  %204 = load i32, ptr %24, align 4
  %205 = sub i32 %204, %37
  %206 = mul i32 %205, %46
  %207 = add i32 %lsr.iv, %206
  %208 = add i32 %207, -2
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, ptr %203, i64 %209
  %211 = load float, ptr %210, align 4
  %212 = fadd reassoc ninf nsz float %202, %.295172
  %213 = fsub reassoc ninf nsz float %212, %211
  %214 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %191, i64 0, i32 2, i32 1
  %215 = load ptr, ptr %214, align 8
  %216 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %191, i64 0, i32 2, i32 0, i32 1
  %217 = load i32, ptr %216, align 4
  %218 = sub i32 %217, %37
  %219 = mul i32 %218, %46
  %220 = add i32 %lsr.iv, %219
  %221 = add i32 %220, -2
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %215, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = fsub reassoc ninf nsz float %.286173, %211
  %226 = fadd reassoc ninf nsz float %225, %224
  %227 = fadd reassoc ninf nsz float %.2174, 1.000000e+00
  br label %true_block46

true_block46:                                     ; preds = %true_block43, %true_block40, %true_block34
  %.3180 = phi float [ %227, %true_block43 ], [ %.2174, %true_block34 ], [ %.2174, %true_block40 ]
  %.387179 = phi float [ %226, %true_block43 ], [ %.286173, %true_block34 ], [ %.286173, %true_block40 ]
  %.396178 = phi float [ %213, %true_block43 ], [ %.295172, %true_block34 ], [ %.295172, %true_block40 ]
  %228 = icmp sgt i32 %52, -1
  %or.cond152 = select i1 %185, i1 %228, i1 false
  br i1 %or.cond152, label %true_block52, label %true_block58

true_block52:                                     ; preds = %true_block46
  %229 = getelementptr inbounds i8, ptr %34, i64 12
  %230 = bitcast ptr %229 to ptr
  %231 = load i32, ptr %230, align 4
  %232 = icmp slt i32 %52, %231
  br i1 %232, label %true_block55, label %true_block58

true_block55:                                     ; preds = %true_block52
  %233 = load ptr, ptr %20, align 8
  %234 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %233, i64 0, i32 1, i32 1
  %235 = load ptr, ptr %234, align 8
  %236 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %233, i64 0, i32 1, i32 0, i32 1
  %237 = load i32, ptr %236, align 4
  %238 = sub i32 %237, %37
  %239 = mul i32 %238, %46
  %240 = add i32 %lsr.iv, %239
  %241 = add i32 %240, -1
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %235, i64 %242
  %244 = load float, ptr %243, align 4
  %245 = load ptr, ptr %23, align 8
  %246 = load i32, ptr %24, align 4
  %247 = sub i32 %246, %37
  %248 = mul i32 %247, %46
  %249 = add i32 %lsr.iv, %248
  %250 = add i32 %249, -1
  %251 = sext i32 %250 to i64
  %252 = getelementptr float, ptr %245, i64 %251
  %253 = load float, ptr %252, align 4
  %254 = fadd reassoc ninf nsz float %244, %.396178
  %255 = fsub reassoc ninf nsz float %254, %253
  %256 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %233, i64 0, i32 2, i32 1
  %257 = load ptr, ptr %256, align 8
  %258 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %233, i64 0, i32 2, i32 0, i32 1
  %259 = load i32, ptr %258, align 4
  %260 = sub i32 %259, %37
  %261 = mul i32 %260, %46
  %262 = add i32 %lsr.iv, %261
  %263 = add i32 %262, -1
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %257, i64 %264
  %266 = load float, ptr %265, align 4
  %267 = fsub reassoc ninf nsz float %.387179, %253
  %268 = fadd reassoc ninf nsz float %267, %266
  %269 = fadd reassoc ninf nsz float %.3180, 1.000000e+00
  br label %true_block58

true_block58:                                     ; preds = %true_block55, %true_block52, %true_block46
  %.497.ph = phi float [ %.396178, %true_block46 ], [ %.396178, %true_block52 ], [ %255, %true_block55 ]
  %.488.ph = phi float [ %.387179, %true_block46 ], [ %.387179, %true_block52 ], [ %268, %true_block55 ]
  %.4.ph = phi float [ %.3180, %true_block46 ], [ %.3180, %true_block52 ], [ %269, %true_block55 ]
  %270 = icmp sgt i32 %184, -1
  %or.cond153 = select i1 %185, i1 %270, i1 false
  br i1 %or.cond153, label %true_block64, label %after_if69

true_block64:                                     ; preds = %true_block58
  %271 = getelementptr inbounds i8, ptr %34, i64 12
  %272 = bitcast ptr %271 to ptr
  %273 = load i32, ptr %272, align 4
  %274 = icmp slt i32 %184, %273
  br i1 %274, label %true_block67, label %after_if69.thread

true_block67:                                     ; preds = %true_block64
  %275 = load ptr, ptr %20, align 8
  %276 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %275, i64 0, i32 1, i32 1
  %277 = load ptr, ptr %276, align 8
  %278 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %275, i64 0, i32 1, i32 0, i32 1
  %279 = load i32, ptr %278, align 4
  %280 = mul i32 %279, %46
  %281 = add i32 %280, %184
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, ptr %277, i64 %282
  %284 = load float, ptr %283, align 4
  %285 = load ptr, ptr %23, align 8
  %286 = load i32, ptr %24, align 4
  %287 = mul i32 %286, %46
  %288 = add i32 %287, %184
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %285, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = fadd reassoc ninf nsz float %284, %.497.ph
  %293 = fsub reassoc ninf nsz float %292, %291
  %294 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %275, i64 0, i32 2, i32 1
  %295 = load ptr, ptr %294, align 8
  %296 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %275, i64 0, i32 2, i32 0, i32 1
  %297 = load i32, ptr %296, align 4
  %298 = mul i32 %297, %46
  %299 = add i32 %298, %184
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %295, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = fsub reassoc ninf nsz float %.488.ph, %291
  %304 = fadd reassoc ninf nsz float %303, %302
  %305 = fadd reassoc ninf nsz float %.4.ph, 1.000000e+00
  br label %after_if69.thread

after_if69.thread:                                ; preds = %true_block67, %true_block64
  %.598.ph = phi float [ %.497.ph, %true_block64 ], [ %293, %true_block67 ]
  %.589.ph = phi float [ %.488.ph, %true_block64 ], [ %304, %true_block67 ]
  %.5.ph = phi float [ %.4.ph, %true_block64 ], [ %305, %true_block67 ]
  %306 = add nuw nsw i32 %46, 1
  br label %true_block70

after_if69:                                       ; preds = %true_block58, %after_if33
  %307 = phi i32 [ %184, %true_block58 ], [ %181, %after_if33 ]
  %.598 = phi float [ %.497.ph, %true_block58 ], [ %.295, %after_if33 ]
  %.589 = phi float [ %.488.ph, %true_block58 ], [ %.286, %after_if33 ]
  %.5 = phi float [ %.4.ph, %true_block58 ], [ %.2, %after_if33 ]
  %308 = add i32 %46, 1
  %309 = icmp sgt i32 %308, -1
  br i1 %309, label %after_if69.true_block70_crit_edge, label %after_if105

after_if69.true_block70_crit_edge:                ; preds = %after_if69
  %.phi.trans.insert215 = getelementptr inbounds i8, ptr %34, i64 8
  %.phi.trans.insert216 = bitcast ptr %.phi.trans.insert215 to ptr
  %.pre217 = load i32, ptr %.phi.trans.insert216, align 4
  br label %true_block70

true_block70:                                     ; preds = %after_if69.true_block70_crit_edge, %after_if69.thread
  %310 = phi i32 [ %183, %after_if69.thread ], [ %.pre217, %after_if69.true_block70_crit_edge ]
  %311 = phi i32 [ %306, %after_if69.thread ], [ %308, %after_if69.true_block70_crit_edge ]
  %.5192 = phi float [ %.5.ph, %after_if69.thread ], [ %.5, %after_if69.true_block70_crit_edge ]
  %.589191 = phi float [ %.589.ph, %after_if69.thread ], [ %.589, %after_if69.true_block70_crit_edge ]
  %.598190 = phi float [ %.598.ph, %after_if69.thread ], [ %.598, %after_if69.true_block70_crit_edge ]
  %312 = phi i32 [ %184, %after_if69.thread ], [ %307, %after_if69.true_block70_crit_edge ]
  %313 = icmp slt i32 %311, %310
  %314 = icmp sgt i32 %54, -1
  %or.cond154 = select i1 %313, i1 %314, i1 false
  br i1 %or.cond154, label %true_block76, label %true_block82

true_block76:                                     ; preds = %true_block70
  %315 = getelementptr inbounds i8, ptr %34, i64 12
  %316 = bitcast ptr %315 to ptr
  %317 = load i32, ptr %316, align 4
  %318 = icmp slt i32 %54, %317
  br i1 %318, label %true_block79, label %true_block82

true_block79:                                     ; preds = %true_block76
  %319 = load ptr, ptr %20, align 8
  %320 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %319, i64 0, i32 1, i32 1
  %321 = load ptr, ptr %320, align 8
  %322 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %319, i64 0, i32 1, i32 0, i32 1
  %323 = load i32, ptr %322, align 4
  %324 = mul i32 %323, %311
  %325 = sub i32 %324, %47
  %326 = add i32 %lsr.iv, %325
  %327 = add i32 %326, -2
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %321, i64 %328
  %330 = load float, ptr %329, align 4
  %331 = load ptr, ptr %23, align 8
  %332 = load i32, ptr %24, align 4
  %333 = mul i32 %332, %311
  %334 = sub i32 %333, %47
  %335 = add i32 %lsr.iv, %334
  %336 = add i32 %335, -2
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, ptr %331, i64 %337
  %339 = load float, ptr %338, align 4
  %340 = fadd reassoc ninf nsz float %330, %.598190
  %341 = fsub reassoc ninf nsz float %340, %339
  %342 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %319, i64 0, i32 2, i32 1
  %343 = load ptr, ptr %342, align 8
  %344 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %319, i64 0, i32 2, i32 0, i32 1
  %345 = load i32, ptr %344, align 4
  %346 = mul i32 %345, %311
  %347 = sub i32 %346, %47
  %348 = add i32 %lsr.iv, %347
  %349 = add i32 %348, -2
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, ptr %343, i64 %350
  %352 = load float, ptr %351, align 4
  %353 = fsub reassoc ninf nsz float %.589191, %339
  %354 = fadd reassoc ninf nsz float %353, %352
  %355 = fadd reassoc ninf nsz float %.5192, 1.000000e+00
  br label %true_block82

true_block82:                                     ; preds = %true_block79, %true_block76, %true_block70
  %.6198 = phi float [ %355, %true_block79 ], [ %.5192, %true_block70 ], [ %.5192, %true_block76 ]
  %.690197 = phi float [ %354, %true_block79 ], [ %.589191, %true_block70 ], [ %.589191, %true_block76 ]
  %.699196 = phi float [ %341, %true_block79 ], [ %.598190, %true_block70 ], [ %.598190, %true_block76 ]
  %356 = icmp sgt i32 %52, -1
  %or.cond155 = select i1 %313, i1 %356, i1 false
  br i1 %or.cond155, label %true_block88, label %true_block94

true_block88:                                     ; preds = %true_block82
  %357 = getelementptr inbounds i8, ptr %34, i64 12
  %358 = bitcast ptr %357 to ptr
  %359 = load i32, ptr %358, align 4
  %360 = icmp slt i32 %52, %359
  br i1 %360, label %true_block91, label %true_block94

true_block91:                                     ; preds = %true_block88
  %361 = load ptr, ptr %20, align 8
  %362 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %361, i64 0, i32 1, i32 1
  %363 = load ptr, ptr %362, align 8
  %364 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %361, i64 0, i32 1, i32 0, i32 1
  %365 = load i32, ptr %364, align 4
  %366 = mul i32 %365, %311
  %367 = sub i32 %366, %47
  %368 = add i32 %lsr.iv, %367
  %369 = add i32 %368, -1
  %370 = sext i32 %369 to i64
  %371 = getelementptr float, ptr %363, i64 %370
  %372 = load float, ptr %371, align 4
  %373 = load ptr, ptr %23, align 8
  %374 = load i32, ptr %24, align 4
  %375 = mul i32 %374, %311
  %376 = sub i32 %375, %47
  %377 = add i32 %lsr.iv, %376
  %378 = add i32 %377, -1
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, ptr %373, i64 %379
  %381 = load float, ptr %380, align 4
  %382 = fadd reassoc ninf nsz float %372, %.699196
  %383 = fsub reassoc ninf nsz float %382, %381
  %384 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %361, i64 0, i32 2, i32 1
  %385 = load ptr, ptr %384, align 8
  %386 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %361, i64 0, i32 2, i32 0, i32 1
  %387 = load i32, ptr %386, align 4
  %388 = mul i32 %387, %311
  %389 = sub i32 %388, %47
  %390 = add i32 %lsr.iv, %389
  %391 = add i32 %390, -1
  %392 = sext i32 %391 to i64
  %393 = getelementptr float, ptr %385, i64 %392
  %394 = load float, ptr %393, align 4
  %395 = fsub reassoc ninf nsz float %.690197, %381
  %396 = fadd reassoc ninf nsz float %395, %394
  %397 = fadd reassoc ninf nsz float %.6198, 1.000000e+00
  br label %true_block94

true_block94:                                     ; preds = %true_block91, %true_block88, %true_block82
  %.7100.ph = phi float [ %.699196, %true_block82 ], [ %.699196, %true_block88 ], [ %383, %true_block91 ]
  %.791.ph = phi float [ %.690197, %true_block82 ], [ %.690197, %true_block88 ], [ %396, %true_block91 ]
  %.7.ph = phi float [ %.6198, %true_block82 ], [ %.6198, %true_block88 ], [ %397, %true_block91 ]
  %398 = icmp sgt i32 %312, -1
  %or.cond156 = select i1 %313, i1 %398, i1 false
  br i1 %or.cond156, label %true_block100, label %after_if105

true_block100:                                    ; preds = %true_block94
  %399 = getelementptr inbounds i8, ptr %34, i64 12
  %400 = bitcast ptr %399 to ptr
  %401 = load i32, ptr %400, align 4
  %402 = icmp slt i32 %312, %401
  br i1 %402, label %true_block103, label %after_if105

true_block103:                                    ; preds = %true_block100
  %403 = load ptr, ptr %20, align 8
  %404 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %403, i64 0, i32 1, i32 1
  %405 = load ptr, ptr %404, align 8
  %406 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %403, i64 0, i32 1, i32 0, i32 1
  %407 = load i32, ptr %406, align 4
  %408 = mul i32 %407, %311
  %409 = add i32 %408, %312
  %410 = sext i32 %409 to i64
  %411 = getelementptr float, ptr %405, i64 %410
  %412 = load float, ptr %411, align 4
  %413 = load ptr, ptr %23, align 8
  %414 = load i32, ptr %24, align 4
  %415 = mul i32 %414, %311
  %416 = add i32 %415, %312
  %417 = sext i32 %416 to i64
  %418 = getelementptr float, ptr %413, i64 %417
  %419 = load float, ptr %418, align 4
  %420 = fadd reassoc ninf nsz float %412, %.7100.ph
  %421 = fsub reassoc ninf nsz float %420, %419
  %422 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %403, i64 0, i32 2, i32 1
  %423 = load ptr, ptr %422, align 8
  %424 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32 }, ptr %403, i64 0, i32 2, i32 0, i32 1
  %425 = load i32, ptr %424, align 4
  %426 = mul i32 %425, %311
  %427 = add i32 %426, %312
  %428 = sext i32 %427 to i64
  %429 = getelementptr float, ptr %423, i64 %428
  %430 = load float, ptr %429, align 4
  %431 = fsub reassoc ninf nsz float %.791.ph, %419
  %432 = fadd reassoc ninf nsz float %431, %430
  %433 = fadd reassoc ninf nsz float %.7.ph, 1.000000e+00
  br label %after_if105

after_if105:                                      ; preds = %true_block103, %true_block100, %true_block94, %after_if69
  %.8101 = phi float [ %421, %true_block103 ], [ %.7100.ph, %true_block100 ], [ %.7100.ph, %true_block94 ], [ %.598, %after_if69 ]
  %.892 = phi float [ %432, %true_block103 ], [ %.791.ph, %true_block100 ], [ %.791.ph, %true_block94 ], [ %.589, %after_if69 ]
  %.8 = phi float [ %433, %true_block103 ], [ %.7.ph, %true_block100 ], [ %.7.ph, %true_block94 ], [ %.5, %after_if69 ]
  %434 = load ptr, ptr %23, align 8
  %435 = load i32, ptr %24, align 4
  %436 = sub i32 %435, %37
  %437 = mul i32 %436, %46
  %438 = add i32 %lsr.iv, %437
  %439 = add i32 %438, -1
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, ptr %434, i64 %440
  %442 = load float, ptr %441, align 4
  %443 = fdiv reassoc ninf nsz float %.8101, %.8
  %444 = fadd reassoc ninf nsz float %442, %443
  %445 = load ptr, ptr %25, align 8
  %446 = load i32, ptr %26, align 4
  %447 = sub i32 %446, %37
  %448 = mul i32 %447, %46
  %449 = add i32 %lsr.iv, %448
  %450 = add i32 %449, -1
  %451 = sext i32 %450 to i64
  %452 = getelementptr float, ptr %445, i64 %451
  store float %444, ptr %452, align 4
  %453 = fdiv reassoc ninf nsz float %.892, %.8
  %454 = fadd reassoc ninf nsz float %442, %453
  %455 = load ptr, ptr %27, align 8
  %456 = load i32, ptr %28, align 4
  %457 = sub i32 %456, %37
  %458 = mul i32 %457, %46
  %459 = add i32 %lsr.iv, %458
  %460 = add i32 %459, -1
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %455, i64 %461
  store float %454, ptr %462, align 4
  %463 = add nsw i32 %.0102213, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %464 = add i32 %29, %lsr.iv.next
  %exitcond.not = icmp eq i32 %464, 1
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.36, align 8
  %.sroa.0.0..sroa_cast = bitcast ptr %0 to ptr
  %.sroa.0.0.copyload = load ptr, ptr %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast ptr %.sroa.4.0..sroa_idx to ptr
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast ptr %.sroa.5.0..sroa_idx to ptr
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast ptr %.sroa.7.0..sroa_idx to ptr
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast ptr %.sroa.8.0..sroa_idx to ptr
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast ptr %.sroa.9.0..sroa_idx to ptr
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast ptr %.sroa.12.0..sroa_idx to ptr
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast ptr %.sroa.15.0..sroa_idx to ptr
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast ptr %.sroa.17.0..sroa_idx to ptr
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast ptr %.sroa.0.0.copyload to ptr
  %9 = bitcast ptr %4 to ptr
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %9, ptr noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.36, ptr %4, i64 0, i32 2
  store i32 %1, ptr %10, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %11
    i32 -1, label %19
  ]

11:                                               ; preds = %7
  %12 = mul nsw i32 %.sroa.15.0.copyload, %2
  %13 = add nsw i32 %12, %.sroa.9.0.copyload
  %14 = add nsw i32 %13, %.sroa.15.0.copyload
  %15 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %14)
  %16 = icmp slt i32 %13, %15
  br i1 %16, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %11
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.02038 = phi i32 [ %17, %.lr.ph ], [ %13, %.lr.ph.preheader ]
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !9

19:                                               ; preds = %7
  %20 = mul nsw i32 %.sroa.15.0.copyload, %2
  %21 = sub nsw i32 %.sroa.12.0.copyload, %20
  %22 = mul nsw i32 %21, %.sroa.15.0.copyload
  %23 = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %22)
  %.not25.not39 = icmp sgt i32 %21, %23
  br i1 %.not25.not39, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %19
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.0.in40 = phi i32 [ %.0, %.lr.ph41 ], [ %21, %.lr.ph41.preheader ]
  %.0 = add nsw i32 %.0.in40, -1
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }

!llvm.linker.options = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}
!llvm.module.flags = !{!6, !7, !8}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"clang version 14.0.6"}
!6 = !{i32 1, !"wchar_size", i32 2}
!7 = !{i32 8, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
