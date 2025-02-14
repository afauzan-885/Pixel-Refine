# Main Content
UNDER_DEVELOPMENT = "{page_name} 菜单正在开发中"

# Enhance Stack Page
TOPBAR_IMPORT_BUTTON_TEXT = "导入图像"
TOPBAR_DELETE_BUTTON_TEXT = "删除图像"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "开始处理"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "另存为"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "图像文件 (*.jpg; *.jpeg; *.png; *.bmp; *.tif; *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "选择图像"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "重复文件"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} 个文件已存在于数据库中，将被跳过。"
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "已选格式"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} 个格式为 '{format}' 的文件将被导入。"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "错误", "没有有效的文件可导入。"

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "错误", "未选择任何图像。"
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "确定要删除 {count} 个已选图像吗？"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "正在处理图像，请稍候..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "未选择任何图像。"

UPDATE_PROGRESS_BAR_STATUS = "{value}% （剩余 {images_left} 个处理）"

ON_IMPORT_COMPLETE_STATUS = "导入完成"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} 个图像已成功导入。"

PROCESS_ALGORITHM_PROCESS_SKIPPED = "未选择任何处理算法"

# PARAMETER STACKING 
RUN_PROCESS_STOPPED = "处理已停止"
NOT_IMAGE_PREVIEW = "没有可用的图像"
MODULE_NOT_IMPLEMENT = "模块尚未实现。"
NO_ALIGNMENT_PROCESS = "确定不先进行图像对齐吗？"

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "加载图像失败"

SAVE_TO_HDF5_ALIGNED_SAVING = "正在将对齐的图像保存到 HDF5"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "第 {index} 张图像已存储到 HDF5。"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "所有图像已成功保存到 HDF5。"
RESIZING_IMAGES_PROCESS = "调整图像大小"

RUN_IMAGE_NOT_FOUND = "数据库中未找到图像。"
RUN_REFERENCE_IMAGE_NOT_FOUND = "无法从 {image_paths[0]} 加载参考图像。"
RUN_SAVING_REFERENCE_IMAGE = "正在将参考图像保存到 HDF5。"
RUN_IMAGE_PROCESSING = "正在处理第 {i} 张图像，共 {total_images} 张..."
RUN_IMAGE_PROCESSING_FAILED = "无法从 {image_paths[i]} 加载第 {i} 张图像。"
RUN_IMAGE_PROCESSING_SAVING = "第 {i} 张图像已保存到 HDF5。"
RUN_IMAGE_PROCESSING_FINISHED = "处理完成。"

CANCEL_PROCESSING = "确定要取消处理吗？"

RUN_ERROR_STATUS = "发生错误：{error}"
RUN_ERROR_MESSAGE = "发生错误：{error}"

DELETE_DEBUG_IMAGES_STATUS = "正在删除调试图像..."
DELETE_DEBUG_IMAGES_ONE_BY_ONE = "正在删除调试图像 {image_id}..."
DELETE_DEBUG_IMAGES_FINISHED = "调试图像已成功删除。"

WINDOW_INITIATION = "开始..."
WINDOW_START_PROCESSING = "开始处理..."
WINDOW_PROCESSING_COMPLETE = "完成！"


# Farneback Optical Flow
WINDOW_TITLE_FARNEBACK = "Farneback 光流对齐"

CALCULATE_OPTICAL_FLOW_STATUS = "正在使用 {device} 计算光流..."
CALCULATE_OPTICAL_FLOW_FINISHED = "光流计算完成。"

COMPENSATE_MOTION_STATUS = "正在对图像 {image_id} 进行运动补偿..."
COMPENSATE_MOTION_FINISHED = "图像 {image_id} 的运动补偿已完成。"


# AKAZE, ORB
WINDOW_TITLE_AKAZE = "AKAZE 对齐"
ALIGN_IMAGES_STATUS_AKAZE = "正在使用 AKAZE 对图像 {image_id} 进行对齐..."

WINDOW_TITLE_ORB = "ORB 对齐"
ALIGN_IMAGES_STATUS_ORB = "正在使用 ORB 对图像 {image_id} 进行对齐..."

WINDOW_TITLE_EEC = "EEC 对齐"
WINDOW_TITLE_STATUS_EEC = "使用 EEC 对齐图像 {image_id}..."

ALIGN_IMAGES_CALCULATE_FAILED = "在图像 {image_id} 中未检测到任何特征。返回原始图像。"
ALIGN_IMAGES_CALCULATE_FINISHED = "图像 {image_id} 对齐完成。"
ALIGN_IMAGES_COMPENSATE_FAILED = "无法为图像 {image_id} 计算单应性矩阵。返回原始图像。"
ALIGN_IMAGES_MATCHING_FAILED = "图像 {image_id} 的匹配数量不足。返回原始图像。"


# Algorithm Denoising
STACK_IMAGES_FAILED = "没有可处理的图像。"
STACK_AVERAGE_IMAGES_PROCESS = "正在处理图像 {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "开始处理..."
RUN_IMAGE_PROCESS_LOAD_HDF5 = "正在从 HDF5 加载图像..."
RUN_IMAGE_PROCESS_LOAD_PROGRESS = "正在加载图像 {current}/{total}..."

RUN_IMAGE_PROCESS_LOAD_PATH = "正在从数据库获取图像列表..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "数据库中未找到图像。"
RUN_IMAGE_PROCESS_STACK_SUCCESS = "图像堆叠完成！结果已保存至：{output_path}"

WINDOW_PROCESS_SUCCESS = "处理已完成。"

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "平均堆叠"
WINDOW_TITLE_MEDIAN = "中值堆叠"
WINDOW_TITLE_WEIGHTED_AVERAGE = "加权平均堆叠"

WINDOW_TITLE_SIMILARITY = "相似性堆叠"
SIMILARITY_MNFR_LOAD_FAILED = "未提供图像。"
SIMILARITY_MNFR_BIT_REQUIRED = "图像必须为 8 位或 16 位。"
SIMILARITY_MNFR_TILE_SLICE = "图像尺寸：{height}x{width}，图块大小：{tile_size}"
SIMILARITY_MNFR_SIZE_FAILED = "图像 {i} 的尺寸与参考图像不匹配。"
SIMILARITY_MNFR_PROCESS_SUCCESS = "图像 {i}/{count} 处理成功。"
SIMILARITY_MNFR_PROCESS_FINISHED = "堆叠完成。"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "批处理堆叠：{current} / {total}"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "插值超分辨率"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = "选择一个算法以查看参数设置。"

# ORB Parameters
ORB_PARAMETER_SETTING_LABEL = "ORB 参数"
ORB_NFEATURES_LABEL = "特征数量"
ORB_NFEATURES_DESCRIPTION = """特征数量表示图像中可识别的细节数量。

更多的特征使算法能够识别更多细节，从而实现更精确的图像对齐。
然而，检测更多特征会增加计算时间。

对于大多数应用，通常 500 到 1500 之间的值就足够了。
对于要求非常高的精度，可以选择 2500 到 5000 之间的值以提高精度。"""

ORB_SCALEFACTOR_LABEL = "缩放因子"
ORB_SCALEFACTOR_DESCRIPTION = """缩放因子决定了图像在处理过程中逐步下采样的速度。

- 接近 1.0 的值意味着图像会被逐步缩小（步骤更多），从而能够检测到更精细的细节，但需要更长时间。
- 较高的值则会更快速地下采样图像，处理速度更快，但可能会遗漏一些细微的细节。

常用值范围为 1.2 至 1.5。"""

ORB_NLEVELS_LABEL = "层数"
ORB_NLEVELS_DESCRIPTION = """层数表示用于特征检测的图像金字塔中的层数。

更多的层数使算法能够捕捉到不同尺度下的细节，这对于尺寸各异的图像很有帮助，
但层数增加也意味着处理时间延长。

对于大多数应用，2 到 4 之间的值是理想的。"""

ORB_TRANSFORMATION_LABEL = "变换类型"
ORB_TRANSFORMATION_DESCRIPTION = """变换类型决定了用于图像对齐的方法。

可选项包括：
- 单应性（Homography）：允许透视变换，适用于从不同角度拍摄的图像。
- 仿射（Affine）：允许旋转、缩放和平移（位移）。
- 相似（Similarity）：只允许旋转、均匀缩放和平移，保持图像的宽高比。
- 欧式（Euclidean）：只允许旋转和平移，不进行缩放，提供最简单的选项。

选择哪种变换取决于待对齐图像之间的差异。
对于大多数应用，通常选择单应性，因为它在处理透视差异方面具有灵活性。"""

ORB_RANSAC_LABEL = "RANSAC 阈值"
ORB_RANSAC_DESCRIPTION = """RANSAC 阈值决定了算法在图像对齐过程中筛选离群值的严格程度。

- 较低的值（例如 1-2）会实施更严格的筛选，可能会丢弃一些关键特征。
- 较高的值（例如 4-5）则对离群值更宽容，允许使用更多特征，但可能会降低对齐精度。

通常，1 到 3 之间的值就足够了，这取决于数据中的噪声水平。"""

# Farneback Optical Flow
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback 参数"

FARNEBACK_PYRAMID_SCALE_LABEL = "金字塔比例"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """金字塔比例是指在金字塔的每一层中图像被缩小的比例因子。

- 该值决定了图像从一层到下一层缩小的幅度。
  例如，如果该值为 0.5，则每一层的大小将是上一层的一半。

- 较小的值（例如介于 0.10 和 0.5 之间）会导致各层之间的尺寸差异更大，
  这可以加快计算速度，但可能降低捕捉细微运动细节的准确性。

- 接近 1.00 的值会使各层之间的尺寸变化最小，从而更精确地捕捉运动细节，
  但需要更长的计算时间。

根据您的需求调整此值，以在处理速度和运动检测准确性之间取得平衡。
推荐值：0.5。"""

FARNEBACK_LEVELS_LABEL = "层数"
FARNEBACK_LEVELS_DESCRIPTION = """层数决定了用于光流计算的图像金字塔中的层数。

- 更多层数可以使算法在不同尺度下检测运动，这在图像运动复杂或覆盖范围较大时非常有利。
- 但是，增加层数也会增加计算时间。

通常使用 3 作为基准值，但您可以根据应用需求将其设置为 1 到 10 之间的任意值。
推荐值：3。"""

FARNEBACK_WIN_SIZE_LABEL = "窗口大小"
FARNEBACK_WIN_SIZE_DESCRIPTION = """窗口大小是用于计算光流的像素区域（窗口）的尺寸。

- 较大的窗口通过在更宽的区域内平均信息，能产生更稳定、平滑的结果。
- 然而，如果窗口太大，可能会掩盖细小的运动细节。

选择一个在平滑性和对细节敏感度之间取得平衡的值。
推荐值：15。"""

FARNEBACK_ITERATIONS_LABEL = "迭代次数"
FARNEBACK_ITERATIONS_DESCRIPTION = """迭代次数指定了在每个金字塔层上光流计算被细化的次数。

- 更多的迭代会产生更准确的光流结果。
- 然而，增加迭代次数也会增加计算时间。

选择一个在提高准确性的同时不会显著降低处理速度的值。
推荐值：3。"""

FARNEBACK_POLY_N_LABEL = "多项式展开"
FARNEBACK_POLY_N_DESCRIPTION = """多项式展开（poly_n）定义了用于通过多项式展开估计运动的像素邻域的大小。

- 此值决定了计算中使用多少周围的像素数据。
- 较大的值会产生更平滑的估计，但可能降低对细小运动的敏感度。

常用的值通常为 5 或 7，具体取决于所需的细节和稳定性水平。
推荐值：5 或 7。"""

FARNEBACK_POLY_SIGMA_LABEL = "多项式 Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """多项式 Sigma 控制在执行多项式展开之前所应用的平滑程度。

- 它代表了用于减少像素数据噪声的高斯滤波器的标准差。
- 较高的 sigma 值可以帮助降低噪声，但如果设置过高，可能会丢失重要的运动细节。

调整此值以在降低噪声的同时不牺牲重要的运动细节。
推荐值：1.2。"""

FARNEBACK_FLAGS_LABEL = "标志"
FARNEBACK_FLAGS_DESCRIPTION = """标志是可选参数，用于启用 Farneback 算法中的特定选项。

- 例如，一个常用的标志是使用高斯滤波器进行平滑，这可以产生更平滑的光流。
- 如果不确定，该参数通常保持默认值（0）。

如果您希望在处理速度和结果质量之间取得平衡，请选择适当的标志。
推荐值：0。"""

FARNEBACK_INTERPOLATION_LABEL = "插值"
FARNEBACK_INTERPOLATION_DESCRIPTION = """插值设置了用于估计像素间光流值的方法。

- 高质量的插值方法（例如线性或三次插值）可以产生更平滑的运动过渡。
- 然而，更复杂的方法也可能增加计算时间。

选择一种在平滑性和处理效率之间取得平衡的插值方法。
推荐：三次插值。"""


#------------------ EEC ------------------#
EEC_PARAMETER_SETTING_LABEL = "EEC 参数"

EEC_ITERATIONS_LABEL = "迭代次数"
EEC_ITERATIONS_DESCRIPTION = """迭代次数决定了EEC算法在图像配准过程中执行细化调整的步数。

- 更多的迭代能实现更精确的对齐，但需要更多的计算资源。
- 较少的迭代可以加快处理速度，但可能会降低配准质量。

推荐：5000次迭代，在精度与性能之间达到平衡。
"""

EEC_EPS_LABEL = "终止阈值"
EEC_EPS_DESCRIPTION = """终止阈值设定了各迭代间最小允许改进的幅度，以确保算法能持续优化变换。

- 较小的阈值允许更精细的调整，从而实现更准确的对齐。
- 然而，过小的阈值会显著增加处理时间。
- 较大的阈值虽然能加快收敛速度，但可能会降低精度。

推荐：1e-6，以在精度与计算效率之间达到最佳平衡。
"""

EEC_MOTION_LABEL = "运动类型"
EEC_MOTION_DESCRIPTION = """运动类型决定了在图像配准过程中使用的变换模型。

- “Affine”（仿射变换）支持旋转、缩放和平移。
- “Homography”（单应性变换）能够处理透视失真。
- “Translasi”（平移变换）仅适用于简单的线性位移，不包括旋转和缩放。

推荐：对于大多数任务，选择‘Affine’变换模型。
"""



AKAZE_PARAMETER_SETTING_LABEL = "AKAZE 参数"

AKAZE_THRESHOLD_LABEL = "阈值"
AKAZE_THRESHOLD_DESCRIPTION = """阈值参数设定了接受一个关键点所需的最小检测响应。

较低的值允许检测到更多关键点（包括较弱或噪声较大的），
而较高的值则限制检测仅针对最强的特征。

推荐值：大约 30。"""

AKAZE_OCTAVE_LABEL = "八度数"
AKAZE_OCTAVE_DESCRIPTION = """该参数指定了尺度空间中的八度数。

每个八度代表原始图像分辨率的一半，使检测器能够捕捉到多尺度的特征。更多的八度数提高了尺度不变性，但也增加了计算时间。

推荐值：4。"""

AKAZE_LAYER_LABEL = "每个八度的层数"
AKAZE_LAYER_DESCRIPTION = """每个八度的层数定义了每个八度内的子层数量。

更多的层数提供了更细致的尺度空间分辨率，可以改善跨尺度的特征检测，但也会增加计算量。

推荐值：4。"""

AKAZE_RATIO_LABEL = "比率阈值"
AKAZE_RATIO_DESCRIPTION = """比率阈值在匹配过程中用于比较关键点描述符中最佳匹配与次佳匹配之间的距离。

较低的比率（接近 0.50）意味着只接受非常独特、明确的匹配，而较高的比率（接近 1.00）则允许更多匹配，但可能包含误匹配。

推荐值：0.80。"""

APPLY_PARAMETER_BUTTON_TEXT = "应用设置"

# ------------ Parameter Setting Algorithm --------------------- #




# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "对齐算法"
NONE_ALIGNMENT_DESCRIPTION = "不进行任何对齐。"
FARNEBACK_DESCRIPTION = """该算法适用于需要达到像素级精度和准确度的高级对齐。

但对于显著的旋转和透视差异，其效果较弱。"""

EEC_DESCRIPTION = """该算法旨在高精度地对齐图像。
该算法采用先进的相关技术来更好地估计转换参数。

可以抵抗光强度的变化和相当高的偏移，但是该算法需要计算时间。
这可能比光流法更准确，但可能不如光流法准确"""

AKAZE_DESCRIPTION = """该算法对旋转、透视和缩放的较大差异具有较强的鲁棒性。

效果足够好，但在像素级对齐上不如 Farneback。"""
ORB_DESCRIPTION = """算法速度快，但对于显著差异的情况准确性较低。

适用于差异较小的图像。"""

# Deskripsi untuk Super Resolution
SUPER_RESOLUTION_NAME = "超分辨率算法"
NONE_SUPER_RESOLUTION_DESCRIPTION = "不进行超分辨率处理。"
INTERPOLATION_DESCRIPTION = """一种通过插值提高分辨率的简单算法，能够增加少量细节。"""

# Deskripsi untuk Denoising
DENOISING_NAME = "去噪算法"
NONE_DENOISING_DESCRIPTION = "不进行降噪处理。"
WEIGHTED_AVERAGE_DESCRIPTION = """简化的相似性堆叠方法在处理小幅运动时效果相当不错。

对于小幅运动效果良好，但在较大运动下会产生图像伪影。"""

AVERAGE_DESCRIPTION = """一种非常快速且有效的静态对象和场景堆叠方法。

不适用于运动场景，但可与 Farneback 对齐结合以消除轻微的物体运动。"""

MEDIAN_DESCRIPTION = """堆叠方法快速且有效，对于移动物体也相当不错。

在移除物体运动（最多达 12 帧）方面非常有效，但在此之后运动物体上会出现伪影。"""

SIMILARITY_DESCRIPTION = """一种先进的堆叠算法，在去除物体运动方面非常强大（运动区域无鬼影现象），
且在高达 90% 的情况下产生极少的伪影。

灵感来源：
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336
"""

# ------------------ General Settings ------------------ #

SETTING_GENERAL_LABEL = "通用"
LANGUAGE_LABEL = "语言"
