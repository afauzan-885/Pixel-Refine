# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "{page_name} 菜单正在开发中"
LOADING_THUMBNAIL = "正在加载...."
NOT_IMAGE_PREVIEW = "无可用图像"
MODULE_NOT_IMPLEMENT = "模块尚未实现。"

# Buttons
ADD_IMAGE_BUTTON = "添加"
PREVIEW_IMAGE_BUTTON = "预览"
DELETE_IMAGE_BUTTON = "删除"
CLOSE_BUTTON = "关闭"
APPLY_PARAMETER_BUTTON_TEXT = "应用设置"
APPY_PARAMETER = "应用"
CANCEL_PARAMETER = "取消"

# Labels
PREVIEW_PANEL_LABEL = "预览面板"

# Window Messages
WINDOW_START_PROCESSING = "开始处理..."
WINDOW_PROCESSING_COMPLETE = "处理完成！"

# Application Control
RESTART_APPLICATION_REQUIRED = "需要重启"
RESTART_APPLICATION_DESCRIPTION = "重启以应用更改"
ACCEPT_RESTART_APPLICATION = "立即重启"
REJECT_APPLICATION_DESCRIPTION = "稍后"
COMMAND_APPLICATION_DESCRIPTION = "正在重新加载应用程序..."
TRY_RESTART_APPLICATION = "正在尝试重新加载应用程序"
COMMAND_FAILED_IN_RESTART_APPLICATION = "系统重启失败。"
RESTART_FAILED = "重启失败"
COMMAND_TO_RESTART_MANUALLY = "无法自动重启应用程序。请手动重启。"

# ==============================================================================
# Sidebar UI
# ==============================================================================

SETTINGS_SIDEBAR_LABEL = "设置"
PANORAMA_SIDEBAR_LABEL = "全景图"

# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "导入图像"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "删除图像"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "导入图像"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "删除批处理"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "处理批处理"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "保存至"

# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "没有已保存的批处理。"
UI_NO_CHANGE = "未更改"
UI_ALGORITHM_EDIT_HEADER = "批量编辑算法"
UI_BATCH_HEADER = "批处理"
UI_ALGORIHM_EDIT = "编辑算法"
UI_ALGORITHM_NOT_SET = "尚未选择算法。"
UI_FOLDER_PATH_NOT_SET = "尚未设置目标文件夹。"
UI_BATCH_NOT_CONFIGURE = "批处理尚未配置。"
UI_LABEL_BATCH_NO_PROCESS = "没有正在处理的批处理！"
UI_LABEL_BATCH_SUCCES = "所有批处理已完成！"
UI_LABEL_BATCH_PROCESS = "正在处理 {} 个批次..."
UI_LABEL_BATCH_PROGRESS = "已处理 {}/{} 个批次..."
UI_LABEL_MOVING_FILES = "正在移动 {} 个文件到文件夹 '{}'。请稍候..."
PROCESSING_BATCH = "--- 正在处理批次 {}/{} (已完成: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "待处理的批次数量：{}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "批处理时必须提供 batch_id"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "跳过批次 {}，因为没有图像被加载。"
BATCH_LABEL_FORMAT = "批次 {}   -   ({} 张图像)"
BATCH_CANCELED_BY_USER = "用户已取消批处理。"
BATCH_CANCELED_HEADER = "批处理已取消"
BATCH_CANCELED_INFO = "已取消"
BATCH_CANCELED_PROCESS = "取消处理"
BATCH_CANCELED_CONFIRMATION = "您确定要取消所有正在进行的处理吗？"
BATCH_QUEUE = "等待中"
BATCH_SUCCESS = "批处理完成。"
BATCH_SUCCESS_HEADER = "完成"

# --- Dialogue Title ---
SELECT_OUTPUT_FOLDER_TITLE = "选择用于保存批处理的输出文件夹"
OUTPUT_FOLDER_SELECTION_CANCELLED = "文件夹选择已取消。处理已停止。"
ALGORITHM_SUCCESS_UPDATE = "批次 {} 到 {} 的算法设置已成功更新。"

# --- General Error Messages & Dialogs ---
BATCH_PROCESSING_ERROR_TITLE = "批处理错误"
BATCH_PROCESSING_ERROR_MESSAGE = "处理批次 {} (ID: {}) 失败:\n{}"
BATCH_SAVE_ERROR_TITLE = "保存失败"
TARGET_FOLDER_NOT_ACCESSIBLE = "目标文件夹无法访问:\n{}"
MOVE_FILE_ERROR_TITLE = "移动文件失败"
COULD_NOT_SAVE_FILE_FOR_BATCH = "无法为批次保存文件 '{}':\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "移动失败：源文件 '{}' 不存在。"
TARGET_FOLDER_INVALID = "移动失败：目标文件夹 '{}' 无效。"
BATCH_CONFIGURATION_INFO = "批处理尚未配置"

BATCH_PROCESSING_ERROR_REPORT_TITLE = "批处理错误报告"
BATCH_PROCESSING_ERROR_REPORT_INTRO = "处理完成，总共 {num_total} 个批次中有 {num_failed} 个处理失败。详情如下："
BATCH_PROCESSING_ERROR_REPORT_ITEM = "• 批次 #{seq} (ID: {id})\n  原因: {error}"

# --- Log Message
LOG_BATCH_PROCESSING_START = "开始处理 {} 个批次..."
LOG_PROCESSING_BATCH_DETAIL = "正在处理第 {} 个批次 (ID: {}), 顺序 ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "警告：批次 {} 发现超过1个新文件。移动第一个文件：{}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "批次 {} 处理完成，新输出：{}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "批次 {} 处理完成，但在文件夹 '{}' 中未找到新的输出文件。"
LOG_ERROR_PROCESSING_BATCH = "处理批次 {} 时出错: {}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "所有批处理尝试均已完成。"

LOG_MOVE_SUCCESS = "成功将 '{}' 移动到 '{}'。"
LOG_MOVE_FAILED = "将 '{}' 移动到 '{}' 失败: {}"
LOG_SOURCE_FILE_NOT_FOUND = "源文件未找到: {}"
LOG_TARGET_FOLDER_NOT_FOUND = "目标文件夹无效: {}"

# Toast message for process_all_batches
UI_LABEL_BATCH_NO_PROCESS = "没有选择要处理的批次。"
UI_LABEL_BATCH_PROCESS_START = "开始处理 {} 个批次..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "批次 {} 完成并已保存 ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "批次 {} 完成，但保存失败 ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "批次 {} 完成，但无输出 ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "批次 {} 出错 ({}/{})."

# Final Finished Toast Message
UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "所有 {} 个批次已成功处理并保存到 {}。"
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} 个批次中的 {} 个已保存到 {}。部分批次存在问题。"
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "处理完成。没有批处理结果保存到 {}。"
UI_LABEL_BATCH_NONE_PROCESSED = "没有处理任何批次。"

# Batch Deletion
BATCH_DELETE_LABEL = "确认删除批处理", "您确定要删除批次 {} 吗？"
TITLE_BATCH_ALL_DELETE_BUTTON = "删除所有批处理"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "您确定要删除 {} 个批次吗？"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "没有已保存的批处理数据。"

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "裁剪边缘"
PARAMETER_BATCH_KEEP_EDGE = "保留边缘"
PARAMETER_BATCH_DENOISING = "降噪"
PARAMETER_BATCH_SUPER_RESOLUTION = "超分辨率"
PARAMETER_BATCH_ALIGNMENT = "对齐图像"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "将对齐结果保存到文件夹"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "将对齐结果用于后续处理"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "保存图像失败: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "图像保存成功: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "没有可保存的图像"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "系统文件夹 (database/stack) 不存在"
UI_NO_BATCH_PROCESS = "没有可用的批处理"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "从 HDF5 文件中检索键 {} 时发生错误: {}"

# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "图像文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """将图像拖放到此处<br>
或<br>
使用“导入图像”按钮"""
SUPPORTED_IMAGE_EXTENSION = "支持的图像格式"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "选择图像"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "重复的图像"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "数据库中已存在 {count} 张图像，将被跳过。"
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "已选格式"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "将导入 {count} 张 '{format}' 格式的图像。"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "失败", "没有可导入的有效图像。" # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "导入完成"
ON_IMPORT_COMPLETE_MESSAGES = "已成功导入 {} 张图像。"

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "失败", "没有选择任何图像。" # Tuple for Title, Message
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
OVERALL_PROGRESS = "总体进度:"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "开始处理"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "另存为"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "未选择用于处理的算法"
PROCESS_TERMINATED_BY_USER = "处理被用户终止"
LOADING_IMAGE_PATH = "正在加载 {} 个图像路径..."
LOAD_IMAGE_FROM_HDF5 = "正在从 HDF5 加载 {} 张图像..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "没有要处理的图像路径。"
PROCESSING_IMAGE_FROM_HDF5 = "正在处理来自 HDF5 的图像: {}"
OUTPUT_SAVE_WEIGHT_MAP = "权重图将保存至: {}"
OUTPUT_IMAGE_TO_BE_SAVED = "输出图像将保存至: {}"
NO_IMAGES_PROCESSED = "没有可处理的图像"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "待处理的图像数量: {}"
RETURNING_IMAGE_RESULTS = "正在返回结果 ({}/{} 张图像)。"
FINISHING_ANALYSIS = "正在完成分析"
IMAGE_PROCESS_FINISHED = "图像叠加完成。"
IMAGE_PROCESS_IN_PROGRESS = "正在处理第 {} 张图像，共 {} 张"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "正在叠加批次 {current}，共 {total} 个"

# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "已选择处理 {}，算法: {}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "正在保存已对齐的图像"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "第 {index} 张图像已保存。"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "所有图像已成功保存。"
NO_HDF5_FILE_PROCESSING_FROM_PATH = "未找到 HDF5 文件。从图像路径处理..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "正在保存参考图像。"
RUN_IMAGE_PROCESSING = "正在处理第 {} 张图像，共 {} 张..."
RUN_IMAGE_PROCESSING_SAVING = "第 {i} 张图像已保存。"
RUN_IMAGE_PROCESSING_FINISHED = "处理完成。"
RUN_IMAGE_PROCESS_STARTED = "开始处理..."
RUN_PROCESS_TRANSFORMATION = "[1/2] 计算变换 {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] 保存结果 {}/{}"

# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS = "正在对齐和裁剪图像 {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION = "正在保存图像 {}/{}"
COMPENSATE_MOTION_STATUS = "正在对图像 {image_id} 进行运动补偿..."
COMPENSATE_MOTION_FINISHED = "图像 {image_id} 的运动补偿已完成。"

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "正在处理图像 {current}/{total}..."
ENHANCEMENT = "增强: {}"
STARTING_ENHANCEMENT = "开始增强"
START_IMAGE_ENHANCEMENT = "--- 开始对 {} 张图像进行增强 ---"
ANALYZING_IMAGE = "正在分析图像 {}/{}..."
SAVING_WEIGHT_MAP = "权重图已保存"

# Analysis Steps (e.g., Similarity)
ANALYSIS_STEP_ONE = "第 1/2 步: 创建场景数据..."
ANALYSIS_STEP_ONE_PROGRESS = "第 1/2 步: 分析帧 {}/{}"
ANALYSIS_STEP_TWO = "{} 正在合并数据..."
ANALYSIS_STEP_TWO_PROGRESS = "{} 正在合并图像 {}/{}"
ANALYZING_COMPLETE = "分析完成"

# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "发生错误: {error}"
RUN_ERROR_MESSAGE = "发生错误: {error}"
FAILED_TO_SAVE_IMAGE = "保存最终图像失败。"
FAILED_TO_CREATE_PROCESS_WINDOW = "创建处理窗口失败: {}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "加载图像失败"
RUN_IMAGE_NOT_FOUND = "在数据库中未找到图像。"
RUN_REFERENCE_IMAGE_NOT_FOUND = "无法从 {image_paths[0]} 加载参考图像。"
RUN_IMAGE_PROCESSING_FAILED = "加载第 {i} 张图像失败，路径: {image_paths[i]}。"
FAILED_WHILE_PREPARING_IMAGE = "准备图像时失败: {}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "准备参考图像失败: {}"
IMAGE_LOAD_FAILED = "没有加载任何图像。"
FIRST_IMAGE_CANNOT_BE_OBTAINED = "无法获取第一张图像: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "数据库中未找到图像。"

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "读取 HDF5 文件时出错: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "未找到第 {} 张图像的变换矩阵文件"
LIBRARY_FILE_NOT_FOUND = "库文件未找到: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "累积图像为 None 或总权重无效。"
RUN_STACK_PROCESSING_FAILED = "执行图像叠加失败"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "无法为第 {} 张图像计算运动"
FAIL_COMPENSATE_MOTION_PROCESS = "在第 {} 张图像上估计失败"
UNRECOGNIZED_TRANSFORMATION = "无法识别的变换类型。"
FAILED_TO_COMPUTE_TRANSFORMATION = "无法计算变换。"
FAILED_TO_COMPUTE_CROP = "无法计算有效的裁剪区域。处理已取消。"
FAIL_CROPPING_PROCESS = "裁剪无效。重叠区域不足"
ERROR_IN_FLOW_FIELD = "图像 {} 出错：输入的光流场为 None。无法进行运动补偿。"
ERROR_IN_BASE_IMAGE = "图像 {} 出错：输入的基础图像为 None。无法进行运动补偿。"
STACK_IMAGES_FAILED = "没有要处理的图像。"
DATA_FAILED_COMPLETION_CREATED = "增强数据生成失败。无法执行增强。"
FAILED_IMAGE_ENHANCEMENT = "图像增强处理失败。"
ANALYSIS_FAILURE = "分析失败：没有图像被处理"
ERROR_AT_END_OF_CONVERSION = "转换结束时出错: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "内部错误：意外的缓冲区通道数。"
UNABLE_TO_SAVE_WEIGHT_MAP = "无法保存权重图: {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "保存权重图到 {} 失败"
NORMALIZATION_FAILED = "归一化失败: {}"
FATAL_ERROR_DURING_NORMALIZATION = "归一化期间发生严重错误: {}"
FAILED_TO_ACCUMULATE_IMAGE = "第 {} 张图像累积失败"
COLOR_CHANNEL_DOES_NOT_MATCH = "颜色通道不匹配。"
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "不支持的图像通道: {}."
DATA_TYPE_NOT_SUPPORTED = "不支持的数据类型: {}."
IMAGE_BIT_REQUIRED = "图像必须为 8 位或 16 位。"

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "加载/配置库 {} 失败: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "C++ 库未加载。跳过归一化。"
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "C++ 库未加载。跳过累积。"

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "意外的 GPU 错误: {}。转为使用 CPU 处理。"

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
WINDOW_TITLE_FARNEBACK = "Farneback 光流对齐"
WINDOW_TITLE_AKAZE = "AKAZE 对齐"
WINDOW_TITLE_ORB = "ORB 对齐"
WINDOW_TITLE_LIGHT_GLUE = "LightGlue 对齐"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "平均值叠加"
WINDOW_TITLE_MEDIAN = "中值叠加"
WINDOW_TITLE_SIMILARITY = "相似度叠加"
WINDOW_TITLE_SIMILARITY_V2 = "相似度叠加 V2"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "插值超分辨率"

# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """选择一个算法以查看其参数。"""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "ORB 参数"
ORB_NFEATURES_LABEL = "特征点数量"
ORB_NFEATURES_DESCRIPTION = """特征点的数量决定了在一张图像中能够识别出多少精细的细节。

- 较高的特征点数量可以让算法找到更多细节，从而实现更精确的图像对齐，但这会增加计算时间。

- 通常，500 到 1500 之间的值对于大多数场景已经足够。
  对于精度要求非常高的需求，选择 2500 到 5000 之间的值可以提高精度。"""
ORB_SCALEFACTOR_LABEL = "比例因子"
ORB_SCALEFACTOR_DESCRIPTION = """比例因子决定了在处理过程中图像被逐步缩小的比率。

- 接近 1.0 的值意味着图像会以更多步骤缓慢缩小。
  这有助于检测更精细的细节，但耗时更长。

- 较大的值会更快地缩小图像，使处理速度加快，
  但可能会错过一些微小的细节。

通常，比例因子的值在 1.2 到 1.5 之间。"""
ORB_NLEVELS_LABEL = "金字塔层数"
ORB_NLEVELS_DESCRIPTION = """金字塔层数指用于检测特征的图像金字塔中的层级数量。

- 更多的层级能让算法在不同尺度上捕捉到更多细节，
  这在图像尺寸多变时非常有用。

- 然而，层级数越多，处理时间也越长。

对于大多数场景，2 到 4 层是理想的选择。"""
ORB_TRANSFORMATION_LABEL = "变换类型"
ORB_TRANSFORMATION_DESCRIPTION = """根据您的需求选择图像对齐的方法：

可选的类型包括：
- 单应性变换 (HOMOGRAPHY): 适用于视角差异极大的照片（例如：从顶部和侧面拍摄的桌子）。
  可以校正“透视”效果。

- 仿射变换 (Affine): 可以旋转、缩放（可以非均匀）和移动图像。
  例如：修正一张倾斜且需要局部放大的照片。

- 相似性变换 (Similarity): 只允许旋转、均匀缩放和移动。
  图像的宽高比会保持不变。

- 欧几里得变换 (Euclidean): 最简单的变换：只旋转和移动图像，不改变大小。
  适用于修正轻微倾斜的照片。

选择建议：
- 对于大多数情况（尤其是视角差异较大的照片），选择单应性变换。
- 如果图像只需要简单的位置/旋转调整，欧几里得或相似性变换更合适。
- 仅在需要灵活的形状调整且无透视效果时使用仿射变换。"""
ORB_RANSAC_LABEL = "RANSAC 阈值"
ORB_RANSAC_DESCRIPTION = """RANSAC 阈值决定了算法在对齐图像时过滤异常值
（即偏离正常范围的数据点）的严格程度。

- 较低的值（例如 1-2）意味着过滤更严格，可能会忽略一些重要的特征点。

- 较高的值（例如 4-5）对异常值更宽容，允许使用更多的特征点，
  但这可能会降低对齐的精度。

通常，根据数据中的噪声水平，1 到 3 之间的值已经足够。"""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback 参数"
FARNEBACK_PYRAMID_SCALE_LABEL = "金字塔比例"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """金字塔比例是决定图像金字塔中每一层图像
被缩小程度的因子。

- 这个值决定了从一层到下一层的图像缩小（降采样）比例。
  例如，值为 0.5 意味着每一层的尺寸都是上一层的一半。

- 较小的值（约 0.10 到 0.5）会导致层与层之间的尺寸差异更大。
  这可以加快计算速度，但可能会降低捕捉精细运动的精度。

- 接近 1.00 的值会使层间尺寸变化更小，
  从而实现更精确的运动检测，但计算时间更长。

请根据您的需求调整此值，以在处理速度和运动检测精度之间找到平衡。
推荐值：0.5
"""
FARNEBACK_LEVELS_LABEL = "金字塔层数"
FARNEBACK_LEVELS_DESCRIPTION = """在 Farneback 算法中，层数参数指的是用于计算光流的图像金字塔中的层级数量。

- 更多的层级：算法可以检测到不同尺寸和速度的物体运动，
  包括复杂或大范围的运动。但这需要更长的计算时间。

- 然而，使用的层级越多，所需的计算时间也越长。

您可以根据应用需求在 1 到 10 之间调整。
通常，值 3 被认为是标准值。
"""
FARNEBACK_WIN_SIZE_LABEL = "窗口大小"
FARNEBACK_WIN_SIZE_DESCRIPTION = """窗口大小决定了在光流计算中使用的像素区域（窗口）的大小。

- 较大的窗口尺寸：会产生更稳定和平滑的运动估计，
  因为信息是从更广的区域计算得出的。然而，微小的运动细节可能会被忽略。

- 较小的窗口尺寸：对微小运动更敏感，
  但噪声可能会被误判为运动，导致结果不够稳定。

您可以选择一个能在微小运动细节的敏感度与结果的稳定性之间取得平衡的值。
推荐值：15。
"""
FARNEBACK_ITERATIONS_LABEL = "迭代次数"
FARNEBACK_ITERATIONS_DESCRIPTION = """迭代次数决定了在每个金字塔层级上对光流计算进行优化的次数。

- 迭代次数越多，获得的光流结果就越精确。
- 然而，增加迭代次数也会减慢计算时间。

选择一个既能提高精度又不会过度拖慢处理速度的值。
推荐值：3。
"""
FARNEBACK_POLY_N_LABEL = "多项式展开邻域"
FARNEBACK_POLY_N_DESCRIPTION = """多项式展开邻域 (poly_n) 决定了用于通过多项式展开法
来近似运动的像素邻域大小。

- 这个值决定了计算中使用了多少周围的像素数据。

- 较大的值会产生更平滑的运动估计，
  但可能会降低对微小运动的敏感度。

通常，根据所需的细节和稳定性水平，使用 5 或 7。
"""
FARNEBACK_POLY_SIGMA_LABEL = "多项式 Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """多项式 Sigma 控制在进行多项式展开之前
所应用平滑的程度。

- 这个值是高斯滤波器的标准差，用于减少像素数据中的噪声。
- 较高的 Sigma 值有助于抑制噪声，

  但如果值过高，可能会消除重要的运动细节。

请仔细调整，以在减少噪声的同时不丢失重要的运动细节。
推荐值：1.2。
"""
FARNEBACK_FLAGS_LABEL = "标志位"
FARNEBACK_FLAGS_DESCRIPTION = """标志位 (Flag) 是一个可选参数，允许在 Farneback 算法中
启用特定的选项。

- 标志位常用于应用高斯滤波进行平滑处理，
  这有助于产生更平滑的光流结果。

- 如果不确定，请将此参数保留为默认值 (0)。

如果您希望在处理速度和结果质量之间取得平衡，请选择合适的标志位。
推荐值：0。
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE 参数"
AKAZE_THRESHOLD_LABEL = "阈值"
AKAZE_THRESHOLD_DESCRIPTION = """阈值参数决定了检测器在寻找关键点时的敏感度。

- 较低的值会增加检测到的关键点数量，
  这包括在特征较少或噪声较多的图像中。

- 较高的值会将检测限制在最强的特征点上。

推荐值：0.0010。
"""
AKAZE_OCTAVE_LABEL = "尺度空间倍频程数"
AKAZE_OCTAVE_DESCRIPTION = """这个参数控制在图像中寻找重要特征时将分析多少个尺度级别。
想象一下以不同的缩放级别查看图像；每个缩放级别被称为一个“倍频程 (octave)”。

- 每个倍频程：代表一个不同的缩放级别，允许算法检测不同大小的特征。
  例如，小特征在放大时可见，而大特征在缩小时可以被识别。

- 更多的倍频程：提供了在更多尺度或尺寸上检测特征的能力。
  但这需要更多的计算量，处理时间也更长。

推荐值：4。
"""
AKAZE_LAYER_LABEL = "每倍频程的层数"
AKAZE_LAYER_DESCRIPTION = """每倍频程的层数决定了每个倍频程内的子级别数量。

- 更多的层数可以提供更精细的尺度空间分辨率，
  从而可以提高在不同尺度下检测特征的准确性。

- 然而，增加层数也会增加计算负担。

推荐值：4。
"""
AKAZE_RATIO_LABEL = "比率阈值"
AKAZE_RATIO_DESCRIPTION = """比率阈值是在两张图像之间匹配关键点时使用的一个值。
其目的是确保找到的匹配是真正准确的，而不仅仅是巧合。

- 较低的比率（接近 0.50）：只接受那些非常清晰、明确无疑的匹配。
  换句话说，它在选择匹配时更具选择性，从而减少了错误匹配（假阳性）的可能性。

- 较高的比率（接近 1.00）：意味着我们对接受匹配更加宽容，
  因此会接受更多的匹配。但这同时也增加了错误匹配的可能性。

推荐值：0.80。
"""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "重叠率 %"
OVERLAP_DESCRIPTION = """用于减少图块伪影（在运动区域产生方块效应）。

增加重叠率可以减少这种效应，但会增加计算时间。"""

TILE_SIZE_LABEL = "图块大小"
TILE_SIZE_DESCRIPTION = """图块尺寸越小，检测差异的细节就越丰富。

但这也会增加计算时间，并增加差异检测中出错的可能性。"""

MOTION_SENSIVITY_LABEL = "运动灵敏度"
MOTION_SENSIVITY_DESCRIPTION = """运动灵敏度控制算法在检测图块内差异时的激进程度。

值越低，检测差异时就越激进或敏感，
但这可能导致噪声也被视为差异。"""

NOISE_OFFSET_LABEL = "噪声偏移量"
NOISE_OFFSET_DESCRIPTION = """用于忽略图像中噪声水平的阈值，从而使较高的噪声不被视为运动。

值越高，对于有极端噪声的图像，叠加结果可能更干净，但这也会降低对图像运动的检测能力。"""

# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = "保留边缘"
IGNORE_EDGE_LABEL = "忽略边缘"
KEEP_EDGES_DESCRIPTION = """“保留边缘”功能允许算法在对齐过程中
保持图像边缘的完整性。"""

ENABLE_CROP_LABEL = "启用\n裁剪"
DISABLE_CROP_LABEL = "禁用\n裁剪"
CROP_DESCRIPTION = """启用裁剪以移除图像中未使用的
黑色边框。

注意：偶尔会发生裁剪错误（非常罕见），
例如导致图像变得非常小，或裁剪计算出错。"""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "保存到文件夹"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "不保存到\n文件夹"
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "浏览..."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "默认文件夹"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "选择文件夹"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """将对齐后的图像保存到文件夹。
默认文件夹是您电脑上的“文档”文件夹。"""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = "保存用于\n后续处理"
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = "不保存用于\n后续处理"
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """保存图像用于后续的
降噪或超分辨率处理。"""

# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "对齐算法"
NONE_ALIGNMENT_DESCRIPTION = "不应用任何对齐。"
FARNEBACK_DESCRIPTION = """该算法适用于需要像素级精度和准确性的高级别对齐。
但是，它对显著的旋转和视角差异处理能力很弱。"""
AKAZE_DESCRIPTION = """该算法对于旋转、视角和尺度的巨大差异具有相当的鲁棒性。

性能不错，但在像素级别上不如 Farneback 精确。"""
ORB_DESCRIPTION = """一种速度快但对于显著差异精度较低的算法。

适用于差异最小的图像，并且在具有随机纹理的图像上表现准确。"""

LIGHT_GLUE_DESCRIPTION = """一种用于匹配图像间局部特征的神经网络（深度学习）模型。

LightGlue 比 AKAZE 等算法更强大，能够处理具有显著视角差异和挑战性图像条件的情况。
警告：此过程仅支持功能强大的 NVIDIA GPU (CUDA)，也可以在 CPU 上运行，但处理时间会慢得多。"""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "超分辨率算法"
NONE_SUPER_RESOLUTION_DESCRIPTION = "不应用任何超分辨率处理。"
INTERPOLATION_DESCRIPTION = """一种通过插值方法提高分辨率的简单算法，
能增加少量细节。"""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "降噪算法"
NONE_DENOISING_DESCRIPTION = "不应用任何降噪处理。"
WEIGHTED_AVERAGE_DESCRIPTION = """相似度叠加方法的简化版。
它能很好地处理微小运动，但对于较大运动会产生图像伪影。"""
AVERAGE_DESCRIPTION = """对于静态物体和场景，这是一种非常快速且有效的叠加方法。
不适用于运动场景或区域，但可以与 Farneback 对齐结合使用，
以消除轻微的物体运动。"""
MEDIAN_DESCRIPTION = """一种快速有效的叠加方法，对运动物体的处理效果尚可。
在消除小物体的微小运动方面非常有效，但对于较大运动会产生伪影。"""
SIMILARITY_DESCRIPTION = """一种先进的叠加算法，在消除物体运动方面非常强大
（运动区域的鬼影极少），产生的伪影极少，成功率高达 85%。

灵感来源：
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""

SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 是 Similarity v1 算法的演进版本，
带来了多项显著改进。该算法能够从含有严重噪声的输入中生成更清晰的图像，这得益于它能
智能地区分噪声、纹理和细微运动。它在低光照条件下更可靠，但处理速度比 v1 版本慢。"""

# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "通用"
LANGUAGE_LABEL = "语言"
LANGUAGE_TYPE = "英语", "印尼语", "繁體中文", "马来语"
GPU_ACCELERATION_LABEL = "GPU 加速"
MULTI_CORE_CPU = "多核 CPU 加速"
SETTINGS_SAVED = "设置已成功保存。"

CANT_READ_FILE_SETTINGS = "警告：无法读取设置文件 '{GENERAL_SETTINGS_FILE}'。将使用默认值。"
MULTI_CORE_CPU_DESCRIPTION = """启用此选项将提高图像处理的计算速度，但会略微增加内存使用量。

如果您的计算机内存非常有限，建议不勾选此项。"""

GPU_ACCELERATION_DESCRIPTION = """启用此选项将通过使用 GPU 进行处理来显著提高计算速度。

注意：GPU 当前的加速仅限于 Farneback 和 Lightglue 算法，其他算法的实现将陆续推出。"""

THUMBNAIL_LABEL = "缩略图"
THUMBNAIL_DESCRIPTION = """用于批处理的图像预览，仍处于实验阶段。
添加新批次时，有时可能会导致闪烁或延迟。"""

NOISE_MAD_OFFSET_LABEL = "MAD 噪声因子"
NOISE_MAD_OFFSET_DESCRIPTION = """MAD 检测在处理高噪声图像时的敏感度。

较高的值意味着对噪声的容忍度更高（在高噪声区域不那么敏感），
但如果发生运动，会在这些区域导致鬼影。"""

MAD_SENSITIVITY_LABEL = "MAD 灵敏度"
MAD_SENSITIVITY_DESCRIPTION = """MAD 在处理图像差异时的敏感度。

较高的值对细微差异会更敏感，但如果输入图像噪声很高，
会增加检测错误的可能性。"""

CONF_SKIP_DFT_LABEL = "跳过 DFT 的\n置信度"
CONF_SKIP_DFT_DESCRIPTION = """如果 MBM（基于块的运动）处理效果良好，则用于跳过 DFT（离散傅里叶变换）的阈值。

值越高，就会有越多的处理由 MAD 完成。但 MAD 是一种粗略检测，
它对噪声和低对比度区域很敏感，不过更多地使用 MAD 的好处是计算量更轻。"""

WIENER_C_FACTOR_LABEL = "维纳 C 因子"
WIENER_C_FACTOR_DESCRIPTION = """DCT 维纳滤波计算在检测图像差异时的敏感度。

值越低，对检测细微运动就越敏感，但这会导致噪声增加，
因为噪声本身会引起虚假运动。维纳 C 因子与 MAD 灵敏度协同工作。"""

COARSE_MARGIN_LABEL = "粗对齐边距"
COARSE_MARGIN_DESCRIPTION = """用于图块级别对齐的边距窗口。

这能将对齐精度提高到图块级别，从而提升叠加的准确性。
如果搜索区域过大，会对性能产生较大影响。"""