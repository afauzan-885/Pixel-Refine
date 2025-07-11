# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "菜单 {page_name} 正在开发中"
LOADING_THUMBNAIL = "加载中...."
NOT_IMAGE_PREVIEW = "无可用图像"
MODULE_NOT_IMPLEMENT = "模块尚未实现。"

# Buttons
ADD_IMAGE_BUTTON = "添加"
PREVIEW_IMAGE_BUTTON = "预览"
DELETE_IMAGE_BUTTON = "删除"
APPLY_PARAMETER_BUTTON_TEXT = "应用设置"

# Labels
PREVIEW_PANEL_LABEL = "预览面板"

# Window Messages
WINDOW_START_PROCESSING = "开始处理..."
WINDOW_PROCESSING_COMPLETE = "完成！"

# Application Control
RESTART_APPLICATION_REQUIRED = "需要重启"
RESTART_APPLICATION_DESCRIPTION = "重启以查看更改"
ACCEPT_RESTART_APPLICATION = "立即重启"
REJECT_APPLICATION_DESCRIPTION = "稍后"
COMMAND_APPLICATION_DESCRIPTION = "重新加载应用程序..."
TRY_RESTART_APPLICATION = "尝试重新加载应用程序"
COMMAND_FAILED_IN_RESTART_APPLICATION = "系统未能重新启动。"
RESTART_FAILED = "重启失败"
COMMAND_TO_RESTART_MANUALLY = "无法自动重启应用程序。请手动重启。"


# ==============================================================================
# Sidebar UI
# ==============================================================================
SETTINGS_SIDEBAR_LABEL= "设置"
PANORAMA_SIDEBAR_LABEL= "全景"


# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "导入图像"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "删除图像"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "导入图像"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "删除 Batch"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "处理 Batch"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "保存到"


# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "没有已保存的 Batch。"
UI_LABEL_BATCH_NO_PROCESS = "没有 Batch 被处理！"
UI_LABEL_BATCH_SUCCES = "所有 Batch 已处理完毕！"
UI_LABEL_BATCH_PROCESS = "正在处理 {} 个 Batch..."
UI_LABEL_MOVING_FILES = "正在将 {} 个文件移动到文件夹“{}”。请稍候..."
UI_LABEL_BATCH_PROGRESS = "已处理 {}/{} 个 Batch..."
PROCESSING_BATCH = "--- 正在处理 Batch {}/{} (已处理: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "待处理的 Batch 数量：{}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "Batch 处理必须提供 batch_id"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "跳过 Batch {} 因为没有加载图像。"
BATCH_LABEL_FORMAT = "批次 {}   -   ({} 张图像)"


SELECT_OUTPUT_FOLDER_TITLE = "选择输出文件夹以保存批处理"
OUTPUT_FOLDER_SELECTION_CANCELLED = "文件夹选择已取消。处理已停止。"

BATCH_PROCESSING_ERROR_TITLE = "批处理错误"
BATCH_PROCESSING_ERROR_MESSAGE = "处理批次失败 {} (ID: {}):\n{}"
BATCH_SAVE_ERROR_TITLE = "保存失败"
TARGET_FOLDER_NOT_ACCESSIBLE = "目标文件夹无法访问：\n{}"
MOVE_FILE_ERROR_TITLE = "文件移动失败"
COULD_NOT_SAVE_FILE_FOR_BATCH = "无法保存文件 '{}' 到批次：\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "移动失败：源文件 '{}' 未找到。"
TARGET_FOLDER_INVALID = "移动失败：目标文件夹 '{}' 无效。"
BATCH_PROCESSING_ERROR_REPORT_TITLE = "批处理错误报告"
BATCH_PROCESSING_ERROR_REPORT_INTRO = "处理完成，但有 {num_failed} 个批次失败（共 {num_total} 个批次）。详情如下："
BATCH_PROCESSING_ERROR_REPORT_ITEM = "• 批次 #{seq} (ID: {id}) \n  原因：{error}"

LOG_BATCH_PROCESSING_START = "开始处理 {} 个批次..."
LOG_PROCESSING_BATCH_DETAIL = "正在处理第 {} 批 (ID: {}), 进度 ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "警告：批次 {} 有多个新文件。已移动第一个：{}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "批次 {} 完成，输出文件：{}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "批次 {} 完成，但文件夹 '{}' 中无新输出。"
LOG_ERROR_PROCESSING_BATCH = "处理批次 {} 出错：{}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "所有批次处理已完成。"

LOG_MOVE_SUCCESS = "成功将 '{}' 移动到 '{}'"
LOG_MOVE_FAILED = "无法将 '{}' 移动到 '{}': {}"
LOG_SOURCE_FILE_NOT_FOUND = "源文件未找到：{}"
LOG_TARGET_FOLDER_NOT_FOUND = "目标文件夹无效：{}"

UI_LABEL_BATCH_NO_PROCESS = "未选择要处理的批次。"
UI_LABEL_BATCH_PROCESS_START = "开始处理 {} 个批次..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "批次 {} 完成并已保存 ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "批次 {} 完成但保存失败 ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "批次 {} 完成，无输出 ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "批次 {} 错误 ({}/{})."

UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "所有 {} 批次处理并保存到 {}。"
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} / {} 批次已保存到 {}。部分失败。"
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "处理完成。没有批次结果保存到 {}。"
UI_LABEL_BATCH_NONE_PROCESSED = "没有批次被处理。"



# Batch Deletion
BATCH_DELETE_LABEL = "确认删除 Batch", "您确定要删除 Batch {} 吗？" # Tuple for Title, Message
TITLE_BATCH_ALL_DELETE_BUTTON = "删除所有 Batch"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "您确定要删除 {} 个 Batch 吗？"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "没有已保存的 Batch 数据。"

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "裁剪边缘"
PARAMETER_BATCH_KEEP_EDGE = "保留边缘"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolution"
PARAMETER_BATCH_ALIGNMENT = "对齐图像"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "将对齐结果保存到文件夹"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "保存对齐结果用于后续处理"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "保存图像失败：{}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "图像保存成功：{}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "无图像"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "系统文件夹 (database/stack) 不存在"
UI_NO_BATCH_PROCESS = "没有 Batch 处理"


# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "从 HDF5 检索键 {} 时出错：{}"


# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "图像文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """将图片拖放到此处<br>
或<br>
使用“导入图片”按钮"""
SUPPORTED_IMAGE_EXTENSION = "支持的图片格式"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "选择图像"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "重复图像"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "数据库中已存在 {count} 张图像，将跳过。"
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "选定格式"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "将导入 {count} 张格式为 '{format}' 的图像。"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "失败", "没有有效的图像可导入。" # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "导入完成"
ON_IMPORT_COMPLETE_MESSAGES = "已成功导入 {} 张图像。"

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "失败", "未选择图像。" # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "您确定要删除所选的 {} 张图像吗？"


# ==============================================================================
# Preview Panel UI & Messages
# ==============================================================================
UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "正在处理图像，请稍候..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "未选择图像。"


# ==============================================================================
# Progress & Status Messages (General)
# ==============================================================================
# Progress Bar
UPDATE_PROGRESS_BAR_STATUS = "{}% (剩余 {} 个进程)"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "开始处理"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "另存为"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "未选择用于处理的算法"
PROCESS_TERMINATED_BY_USER = "用户终止了进程"
LOADING_IMAGE_PATH = "正在加载 {num_in_this_batch} 个图像路径..."
LOAD_IMAGE_FROM_HDF5 = "正在从 HDF5 加载 {} 张图像..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "没有要处理的图像路径。"
PROCESSING_IMAGE_FROM_HDF5 = "正在处理来自 HDF5 的图像：{}"
OUTPUT_SAVE_WEIGHT_MAP = "权重图 (Weight Map) 将保存到：{}"
OUTPUT_IMAGE_TO_BE_SAVED = "输出图像将保存到：{}"
NO_IMAGES_PROCESSED = "没有可处理的图像"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "待处理的图像数量：{}"
RETURNING_IMAGE_RESULTS = "正在返回结果 ({}/{} 张图像)。"
FINISHING_ANALYSIS = "完成分析"
IMAGE_PROCESS_FINISHED = "堆叠完成。"
IMAGE_PROCESS_IN_PROGRESS = "正在处理图像 {}/{}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "正在堆叠 Batch {current}/{total}"


# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "选择了进程 {}，算法：{}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "正在保存对齐的图像"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "图像 {index} 已保存。"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "所有图像已成功保存。"
NO_HDF5_FILE_PROCESSING_FROM_PATH = "未找到 HDF5 文件。正在从图像路径处理..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "正在保存参考图像。"
RUN_IMAGE_PROCESSING = "正在处理图像 {i}/{total_images}..."
RUN_IMAGE_PROCESSING_SAVING = "图像 {i} 已保存。"
RUN_IMAGE_PROCESSING_FINISHED = "处理完成。"
RUN_IMAGE_PROCESS_STARTED = "开始处理..."
RUN_PROCESS_TRANSFORMATION = "[1/2] 计算转换 {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] 保存结果 {}/{}"

# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="正在对齐和裁剪图像 {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="正在保存图像 {}/{}"
COMPENSATE_MOTION_STATUS = "正在对图像 {image_id} 进行运动补偿..."
COMPENSATE_MOTION_FINISHED = "图像 {image_id} 的运动补偿完成。"

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "正在处理图像 {current}/{total}..."
ENHANCEMENT = "增强中：{}"
STARTING_ENHANCEMENT = "开始增强"
START_IMAGE_ENHANCEMENT = "--- 开始对 {} 张图像进行增强 ---"
ANALYZING_IMAGE = "正在分析图像 {}/{}..."
SAVING_WEIGHT_MAP = "权重图 (Weight Map) 已保存"

# Analysis Steps (e.g., Similarity)
ANALYZING_COMPLETE = "分析完成"


# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "发生错误：{error}"
RUN_ERROR_MESSAGE = "发生错误：{error}"
FAILED_TO_SAVE_IMAGE = "保存最终图像失败。"
FAILED_TO_CREATE_PROCESS_WINDOW = "创建处理窗口失败：{}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "加载图像失败"
RUN_IMAGE_NOT_FOUND = "在数据库中找不到图像。"
RUN_REFERENCE_IMAGE_NOT_FOUND = "无法从 {image_paths[0]} 加载参考图像。"
RUN_IMAGE_PROCESSING_FAILED = "加载图像 {i} (来自 {image_paths[i]}) 失败。"
FAILED_WHILE_PREPARING_IMAGE = "准备图像失败：{}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "准备参考图像失败：{}"
IMAGE_LOAD_FAILED = "未加载图像。"
FIRST_IMAGE_CANNOT_BE_OBTAINED = "无法获取第一张图像：{}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "数据库中未找到图像。"

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "读取 HDF5 出错：{}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "找不到图像 {} 的 transformation matrix 文件"
LIBRARY_FILE_NOT_FOUND = "未找到库文件：{}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "累积图像 (Accumulated image) 为 None 或总权重 (total weights) 无效。"
RUN_STACK_PROCESSING_FAILED = "堆叠图像失败"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "无法计算图像 {} 的运动"
FAIL_COMPENSATE_MOTION_PROCESS = "图像 {} 的估计失败"
UNRECOGNIZED_TRANSFORMATION = "无法识别的变换类型。"
FAILED_TO_COMPUTE_TRANSFORMATION ="无法计算变换。"
FAILED_TO_COMPUTE_CROP = "无法计算有效的裁剪。进程已取消。"
FAIL_CROPPING_PROCESS = "裁剪无效。重叠不足。"
ERROR_IN_FLOW_FIELD = "图像 {} 出错：光流场 (Flow field) 输入为 None。无法进行运动补偿。"
ERROR_IN_BASE_IMAGE = "图像 {} 出错：基准图像 (Base image) 输入为 None。无法进行运动补偿。"
STACK_IMAGES_FAILED = "没有要处理的图像。"
DATA_FAILED_COMPLETION_CREATED = "细化数据生成失败。无法执行细化。"
FAILED_IMAGE_ENHANCEMENT = "增强处理失败。"
ANALYSIS_FAILURE = "分析失败：未处理任何图像"
ERROR_AT_END_OF_CONVERSION = "转换结束时出错：{}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "内部错误：意外的缓冲区通道数。"
UNABLE_TO_SAVE_WEIGHT_MAP = "无法保存权重图 (Weight Map)：{}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "保存权重图 (weight map) 到 {} 失败"
NORMALIZATION_FAILED = "归一化失败：{}"
FATAL_ERROR_DURING_NORMALIZATION = "归一化期间发生致命错误：{}"
FAILED_TO_ACCUMULATE_IMAGE= "图像 {} 累积失败"
COLOR_CHANNEL_DOES_NOT_MATCH = "颜色通道不匹配。"
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "不支持的图像通道：{}。"
DATA_TYPE_NOT_SUPPORTED = "不支持的数据类型：{}。"
IMAGE_BIT_REQUIRED = "图像必须是 8 Bit 或 16 Bit。"

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "加载/配置库 {} 失败：{}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "C++ 库未加载。跳过归一化。"
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "C++ 库未加载。跳过累积。"

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "意外的 GPU 错误：{}。回退到 CPU 处理。"

# Validation Errors
IMAGE_DATA_MUST_BE_VALID = "'images' 列表中的项目必须是有效的图像数据 (NumPy 数组)。"

# ==============================================================================
# Confirmation Dialogs / Warnings
# ==============================================================================
NO_ALIGNMENT_PROCESS = "您确定不想先对齐图像吗？"
CANCEL_PROCESSING = "您确定要取消处理吗？"
# Note: Batch deletion confirmations are kept within the Batch section for context


# ==============================================================================
# Algorithm Specific Window Titles
# ==============================================================================
# Alignment
WINDOW_TITLE_FARNEBACK = "Farneback Optical Flow 对齐"
WINDOW_TITLE_AKAZE = "AKAZE 对齐"
WINDOW_TITLE_ORB = "ORB 对齐"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "Average 堆叠"
WINDOW_TITLE_MEDIAN = "Median 堆叠"
WINDOW_TITLE_SIMILARITY = "Similarity 堆叠"
WINDOW_TITLE_SIMILARITY_V2 = "Similarity V2 堆叠"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Interpolation Super Resolution"


# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """选择一个算法以查看其参数。"""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "ORB 参数"
ORB_NFEATURES_LABEL = "特征点数量"
ORB_NFEATURES_DESCRIPTION = """特征点数量决定了图像中可以识别多少精细细节。

- 较高的特征点数量允许算法查找更多细节，
  从而实现更精确的图像对齐。但这会增加计算时间。

- 通常，对于大多数图像场景，500 到 1500 之间的值就足够了。
  对于非常高的精度需求，选择 2500 到 5000 之间的值可以提高精度。"""
ORB_SCALEFACTOR_LABEL = "Scale Factor (比例因子)"
ORB_SCALEFACTOR_DESCRIPTION = """Scale Factor 决定了处理过程中图像比例逐步缩小的速率。

- 如果该值接近 1.0，则图像会以更多步骤缓慢缩小。
  这允许检测更精细的细节，但需要更长时间。

- 如果该值较大，则图像缩小得更快，处理时间更短，
  但可能会丢失一些小细节。

通常，Scale Factor 的值在 1.2 到 1.5 之间。"""
ORB_NLEVELS_LABEL = "Level 数量 (金字塔层数)"
ORB_NLEVELS_DESCRIPTION = """Level 数量表示用于检测特征的图像金字塔中的层数。

- 更多的 Level 允许算法捕捉不同尺度的细节，
  这在图像尺寸变化时很有用。

- 然而，Level 数量越高，处理时间越长。

对于大多数场景，2 到 4 之间的值是理想的。"""
ORB_TRANSFORMATION_LABEL = "变换类型"
ORB_TRANSFORMATION_DESCRIPTION = """根据您的需求选择对齐图像的方法：

可用选项包括：
- HOMOGRAPHY (单应性)：适用于视角差异较大的照片（例如：从上方与侧面拍摄的桌子图像）。
  可以调整“透视”效果。

- AFFINE (仿射)：可以旋转、调整大小（可以是非均匀的）和平移图像。
  示例：校正需要部分放大的倾斜照片。

- SIMILARITY (相似性)：只允许均匀的旋转、缩放和平移。
  保持长宽比。

- EUCLIDEAN (欧几里得)：最简单的：只旋转和平移图像而不改变大小。
  适用于校正轻微倾斜的照片。

选择建议：
- 对于大多数情况（特别是视角差异较大的照片），选择 Homography。
- 如果图像只需要简单的位置/旋转调整，Euclidean 或 Similarity 更合适。
- 仅在需要灵活的形状调整而不需要透视效果时使用 Affine。"""
ORB_RANSAC_LABEL = "RANSAC Threshold (阈值)"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold 决定了算法在对齐图像时过滤异常值 (outliers)
（显著偏离的数据点）的严格程度。

- 较低的值（例如 1-2）意味着更严格的过滤，可能会忽略一些重要特征。

- 较高的值（例如 4-5）对异常值更宽容，允许使用更多特征，
  但可能会降低对齐精度。

通常，根据数据中的噪声水平，1 到 3 之间的值就足够了。"""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback 参数"
FARNEBACK_PYRAMID_SCALE_LABEL = "Piramid Scale (金字塔比例)"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Piramid Scale 是决定在每个金字塔 Level 上图像缩小多少的因子。

- 此值决定了从一个 Level 到下一个 Level 图像尺寸减小的程度 (downscale)。
  例如，如果值为 0.5，则每个 Level 的尺寸将是前一个 Level 的一半。

- 较小的值（约 0.10 到 0.5）会导致 Level 之间的尺寸差异更大。
  这可以加快计算速度，但可能会降低捕捉精细运动的准确性。

- 接近 1.00 的值会导致 Level 之间的尺寸变化更小，
  允许更准确的运动检测，但计算时间更长。

根据您的需求调整此值，以在处理速度和运动检测精度之间找到平衡。
推荐值：0.5
"""
FARNEBACK_LEVELS_LABEL = "Level (层数)"
FARNEBACK_LEVELS_DESCRIPTION = """Farneback 算法中的 Levels 参数指的是用于计算 optical flow 的图像金字塔中的层数。

- 更多 Level：算法可以检测不同尺寸和速度的物体运动，
  包括复杂运动或覆盖大面积的运动。然而，这需要
  更长的计算时间。

- 然而，使用的 Level 越多，所需的计算时间就越长。

您可以根据应用程序的需求在 1 到 10 之间进行调整。
通常，值 3 被认为是标准值。
"""
FARNEBACK_WIN_SIZE_LABEL = "Window Size (窗口大小)"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Window Size 决定了在 optical flow 计算中使用了多大的像素区域（窗口）。

- 更大的 Window Size：产生更稳定、更平滑的运动估计，因为
  信息是从更宽的区域计算的。然而，可能会丢失小的运动细节。

- 更小的 Window Size：对小运动更敏感，
  但噪声可能被误认为是运动，且稳定性较差。

您可以在对小运动细节的敏感度
和稳定结果之间选择一个值。
推荐值：15。
"""
FARNEBACK_ITERATIONS_LABEL = "Iterations (迭代次数)"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterations 决定了在每个金字塔 Level 上 optical flow 计算被优化的次数。

- 更多 Iterations 会得到更准确的 optical flow 结果。
- 然而，增加 Iterations 次数也会减慢计算时间。

选择一个能在不过分减慢处理速度的情况下提高精度的值。
推荐值：3。
"""
FARNEBACK_POLY_N_LABEL = "Polynomial Expansion (多项式展开邻域)"
FARNEBACK_POLY_N_DESCRIPTION = """Polynomial Expansion (poly_n) 决定了使用多项式展开方法估计运动时所使用的像素邻域的大小。

- 此值决定了计算中使用了多少周围像素数据。

- 较大的值将产生更平滑的运动估计，
  但可能会降低对小运动的敏感度。

通常，根据所需的细节和稳定性水平，使用值 5 或 7。
"""
FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma (多项式 Sigma)"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polynomial Sigma 控制在执行多项式展开之前应用的平滑量。

- 此值是用于减少像素数据中噪声的 Gaussian 滤波器的标准差。
- 较高的 Sigma 有助于抑制噪声，

  但如果过高，可能会消除重要的运动细节。

请仔细调整以减少噪声，同时不丢失重要的运动细节。
推荐值：1.2。
"""
FARNEBACK_FLAGS_LABEL = "Flag (标志)"
FARNEBACK_FLAGS_DESCRIPTION = """Flags 是一个可选参数，允许在 Farneback 算法中激活特定选项。

- Flags 通常用于应用 Gaussian 滤波器进行平滑处理，
  这用于产生更平滑的 optical flow。

- 如果不确定，请将此参数保留为默认值 (0)。

如果您想平衡处理速度和结果质量，请选择适当的 flag。
推荐值：0。
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE 参数"
AKAZE_THRESHOLD_LABEL = "Threshold (阈值)"
AKAZE_THRESHOLD_DESCRIPTION = """Threshold 参数决定了检测器在搜索关键点 (keypoint) 时的敏感度。

- 较低的值会增加检测到的关键点数量，
  包括在特征较少和噪声较多的图像中。

- 较高的值仅将检测限制在最强的特征上。

推荐值：0.0010。
"""
AKAZE_OCTAVE_LABEL = "Octave 数量 (倍频程数)"
AKAZE_OCTAVE_DESCRIPTION = """ 该参数控制在搜索图像中重要特征时将分析多少个尺度级别。想象一下以不同的缩放级别查看图像；
每个缩放级别称为一个“Octave”。

- 每个 Octave：代表不同的缩放级别，允许算法检测不同尺寸的特征。
  例如，放大时可以看到小特征，而在较远的缩放级别可以识别大特征。

- 更多 Octave：提供检测更多尺度或尺寸特征的能力。
  然而，计算机需要进行更多工作，处理时间也会变长。

推荐值：4。
"""
AKAZE_LAYER_LABEL = "每 Octave 层数"
AKAZE_LAYER_DESCRIPTION = """每 Octave 层数决定了每个 Octave 内的子级别数量。

- 更多层提供更精细的尺度空间分辨率，
  可以改善跨各种尺度的特征检测。

- 然而，增加层数也会增加计算负载。

推荐值：4。
"""
AKAZE_RATIO_LABEL = "Ratio Threshold (比率阈值)"
AKAZE_RATIO_DESCRIPTION = """Ratio Threshold 是在匹配两个图像之间的重要特征（关键点 keypoint）时使用的值。目标是确保找到的匹配确实准确，而不是巧合。

- 较低的比率（接近 0.50）：只接受非常清晰、毋庸置疑的匹配。
  换句话说，它在选择匹配时更具选择性，从而降低了错误匹配
  虚假关键点的可能性。

- 较高的比率（接近 1.00）：意味着我们在接受匹配时更宽容，
  因此接受了更多匹配。然而，这也增加了错误匹配
  关键点的可能性。

推荐值：0.80。
"""


# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "重叠百分比"
OVERLAP_DESCRIPTION = """用于减少瓦片伪影（在运动区域产生块状效果的问题）。

增加重叠率可以减少这种伪影，但也会增加计算时间。"""

TILE_SIZE_LABEL = "瓦片大小"
TILE_SIZE_DESCRIPTION = """瓦片越小，差异检测越精细。

但这也会增加计算时间，并提高检测错误的可能性。"""

MOTION_SENSIVITY_LABEL = "运动灵敏度"
MOTION_SENSIVITY_DESCRIPTION = """运动灵敏度控制算法在一个瓦片中检测差异的激进程度。

值越低，检测越敏感或激进，但也可能将噪声误判为真实差异。"""

NOISE_OFFSET_LABEL = "噪声偏移"
NOISE_OFFSET_DESCRIPTION = """用于忽略图像中某一水平的噪声的阈值，这样较高的噪声就不会被误认为是运动。

值越高，对于噪声极高的图像可以获得更干净的堆叠效果，但可能降低运动检测的准确性。"""


# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = """保留边缘"""
IGNORE_EDGE_LABEL= """忽略边缘"""
KEEP_EDGES_DESCRIPTION = """“保留边缘”功能允许算法在对齐过程中保持图像边缘完整。"""

ENABLE_CROP_LABEL = """启用
裁剪"""
DISABLE_CROP_LABEL = """禁用
裁剪"""
CROP_DESCRIPTION = """启用裁剪以移除
未使用的图像边界。

注意：有时会出现裁剪错误（非常罕见）。
例如图像非常小，或裁剪图像时出错。"""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "保存到文件夹"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = """不保存
到文件夹"""
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "浏览.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "默认文件夹"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "选择文件夹"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """将对齐后的图像保存到文件夹。
默认文件夹是您 PC 上的“文档”文件夹。"""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """保存以用于
后续处理"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """不保存以用于
后续处理"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """保存图像用于
Denoising 或 Super Resolution 处理"""


# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "对齐算法"
NONE_ALIGNMENT_DESCRIPTION = "将不应用任何对齐。"
FARNEBACK_DESCRIPTION = """该算法适用于需要像素级精度和准确性的高级别对齐。
然而，它对于显著的旋转和视角差异非常敏感。"""
AKAZE_DESCRIPTION = """该算法对于旋转、视角和尺度的巨大差异具有相当的鲁棒性。

效果不错，但在像素级别不如 Farneback。"""
ORB_DESCRIPTION = """算法速度快，但对于显著差异不够准确。

适用于差异最小的图像，并且在具有随机纹理的图像上准确。"""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Super Resolution 算法"
NONE_SUPER_RESOLUTION_DESCRIPTION = "将不应用任何 Super Resolution。"
INTERPOLATION_DESCRIPTION = """使用插值方法提高分辨率的简单算法，
增加少量细节。"""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "降噪 (Denoising) 算法"
NONE_DENOISING_DESCRIPTION = "将不应用任何降噪 (Denoising)。"
WEIGHTED_AVERAGE_DESCRIPTION = """简化 Similarity 堆叠方法的结果。
在处理小幅运动方面效果不错，但在较大幅度运动时会产生图像伪影 (artifacts)。"""
AVERAGE_DESCRIPTION = """对于静态物体和场景，这是一种非常快速有效的堆叠方法。
不适用于移动场景或区域，但可以与 Farneback 对齐结合使用
以消除轻微的物体运动。"""
MEDIAN_DESCRIPTION = """堆叠速度快且有效，对移动物体效果不错。
在消除小物体的运动方面非常有效，但在较大幅度运动时会出现伪影 (artifacts)。"""
SIMILARITY_DESCRIPTION = """先进的堆叠算法，在消除物体运动方面非常强大
（移动区域的鬼影 ghosting 极少），并且产生的伪影 (artifacts) 非常少（高达 85%）。

灵感来源：
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""
SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 是 Similarity v1 算法经过多项重大改进后的开发成果。
该算法能够智能地区分噪声、纹理和细微运动，即使输入包含严重噪声，也能产生更清晰的图像。
在低光照条件下更可靠，但处理过程比 v1 版本慢。"""


# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "常规"
LANGUAGE_LABEL = "语言"
LANGUAGE_TYPE = "英语", "印尼语", "繁体中文", "马来语"
GPU_ACCELERATION_LABEL = "GPU 加速"
MULTI_CORE_CPU = "多核 CPU"
SETTINGS_SAVED = "设置已保存"

CANT_READ_FILE_SETTINGS = "警告：无法读取设置文件 '{GENERAL_SETTINGS_FILE}'。使用默认值。"

MULTI_CORE_CPU_DESCRIPTION = """启用此功能将提高图像处理时的计算速度，但会略微增加 RAM 使用量。

如果计算机的 RAM 非常有限，建议不要启用。"""
GPU_ACCELERATION_DESCRIPTION = """启用此功能将大幅提升计算速度，因为它在处理过程中使用了 GPU。

注意：GPU 的使用目前仅限于 Farneback 过程，其他算法的实现将随后跟进。"""

THUMBNAIL_LABEL = "缩略图"
THUMBNAIL_DESCRIPTION = """批量处理的图像预览，仍处于实验阶段
添加新批次时有时会导致闪烁或延迟"""

NOISE_MAD_OFFSET_LABEL = "MAD 噪声因子"
NOISE_MAD_OFFSET_DESCRIPTION = """MAD检测在处理高噪声图像时的敏感程度。

较高的数值可以容忍更多的噪声（即在高噪声区域不那么敏感），
但在发生运动时可能会在该区域产生重影现象。
"""

MAD_SENSITIVITY_LABEL = "MAD 灵敏度"
MAD_SENSITIVITY_DESCRIPTION = """衡量MAD在检测图像差异时的敏感度。

较高的数值会使其对细微差别更为敏感，但如果输入图像噪声较高，则可能增加误检的风险。
"""

CONF_SKIP_DFT_LABEL = "跳过 DFT 过程的置信度"
CONF_SKIP_DFT_DESCRIPTION = """用于在MBM过程已妥善处理时跳过DFT过程的阈值。

数值越高，MAD承担的处理工作越多。但需要注意的是，MAD作为一种粗略的检测方法，
对噪声和低对比度区域较为敏感，其优势在于计算量较低。
"""

WIENER_C_FACTOR_LABEL = "Wiener C 因子"
WIENER_C_FACTOR_DESCRIPTION = """衡量DCT Wiener计算在检测图像差异时的敏感度。

数值越低，对细微运动的检测就越敏感，但这也可能引起更多噪声，
因为噪声本身可能产生伪运动。Wiener C因子与MAD灵敏度协同工作。
"""

COARSE_MARGIN_LABEL = "粗略对齐边界"
COARSE_MARGIN_DESCRIPTION = """用于在tile级别对齐时设置的边界窗口。

该参数可以提高至tile级别的对齐精度，从而提升堆叠的准确性。
如果搜索区域过大，则可能对性能造成显著影响。
"""

