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
# Application exit and backend-change prompts
EXIT_APPLICATION_TITLE = "退出应用程序"
EXIT_APPLICATION_MESSAGE = "确定要退出应用程序吗？"
EXIT_APPLICATION_YES = "是"
EXIT_APPLICATION_NO = "否"
PROJECT_SAVE_CHANGES_TITLE = "保存项目"
PROJECT_SAVE_CHANGES_MESSAGE = "此项目有未保存的更改。退出前要保存吗？"
PROJECT_SAVE_CHANGES_SAVE = "保存"
PROJECT_SAVE_CHANGES_DISCARD = "不保存"
PROJECT_SAVE_CHANGES_CANCEL = "取消"
EXIT_APPLICATION_APPLY_BACKEND_TITLE = "后端更改"
MSG_BACKEND_EXIT_REQUIRED = "退出应用程序，然后再次打开以应用新的后端选择？"

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
ORB_NFEATURES_DESCRIPTION = """圖像中識別的特徵點數量。
- 較高：對齊更精確，但會增加處理時間。
- 推薦：普通圖像 500 至 1500；高精度需求 2500 至 5000。"""
ORB_SCALEFACTOR_LABEL = "比例因子"
ORB_SCALEFACTOR_DESCRIPTION = """處理過程中圖像尺寸縮小的速度。
- 接近 1.0：縮小慢，保留更多細節，但耗時更長。
- 較高值：處理較快，但可能會遺漏微小細節。
- 推薦：1.2 至 1.5。"""
ORB_NLEVELS_LABEL = "金字塔层数"
ORB_NLEVELS_DESCRIPTION = """用於檢測特徵的圖像金字塔層數。
- 較高：更好適應不同大小的圖像，但會減慢處理速度。
- 推薦：2 至 4。"""
ORB_TRANSFORMATION_LABEL = "变换类型"
ORB_TRANSFORMATION_DESCRIPTION = """根據需求選擇圖像對齊方法：
- HOMOGRAPHY: 最適合透視變化（如傾斜角度、俯視或側視）。
- AFFINE: 校正圖像的旋轉、縮放和傾斜。
- SIMILARITY: 僅允許旋轉、平移和等比例縮放（保持寬高比）。
- EUCLIDEAN: 僅旋轉和平移，不改變圖像大小。"""
ORB_RANSAC_LABEL = "RANSAC 阈值"
ORB_RANSAC_DESCRIPTION = """過濾未對齊噪點的嚴格程度。
- 較低 (1-2)：過濾極嚴格，精度高，但特徵少時易失敗。
- 較高 (4-5)：容忍度高，成功率高，但精度可能略微下降。
- 推薦：1 至 3。"""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback 参数"
FARNEBACK_PYRAMID_SCALE_LABEL = "金字塔比例"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """金字塔每層圖像縮小的比例。
- 接近 1.0：尺寸變化微小，運動檢測極精確，但速度慢。
- 0.5：每層尺寸減半，速度與精度的最佳平衡。
- 推薦：0.5。"""
FARNEBACK_LEVELS_LABEL = "金字塔层数"
FARNEBACK_LEVELS_DESCRIPTION = """用於計算運動的金字塔層數。
- 層數越多：越能捕捉大範圍或複雜的運動，但增加計算量。
- 推薦：3。"""
FARNEBACK_WIN_SIZE_LABEL = "窗口大小"
FARNEBACK_WIN_SIZE_DESCRIPTION = """計算光流的像素窗口大小。
- 較大：運動估計更平滑穩定，但會遺漏微小運動。
- 較小：對微小運動敏感，但易將噪點誤判為運動。
- 推薦：15。"""
FARNEBACK_ITERATIONS_LABEL = "迭代次数"
FARNEBACK_ITERATIONS_DESCRIPTION = """金字塔每層運動估計的優化次數。
- 較高：運動估計更精確，但速度較慢。
- 推薦：3。"""
FARNEBACK_POLY_N_LABEL = "多项式展开邻域"
FARNEBACK_POLY_N_DESCRIPTION = """用於多項式展開的鄰域大小。
- 較大：運動估計更平滑，但對極微小運動的敏感度降低。
- 推薦：5 或 7。"""
FARNEBACK_POLY_SIGMA_LABEL = "多项式 Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """用於平滑圖像細節的高斯標準差。
- 較高：能更好抑制噪點，但可能模糊關鍵的運動細節。
- 推薦：1.2。"""
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
AKAZE_THRESHOLD_DESCRIPTION = """檢測特徵點的靈敏度閾值。
- 較低：檢測更多細節（適用於低對比度或高噪點場景）。
- 較高：僅限檢測最顯著的特徵。
- 推薦：0.001。"""
AKAZE_OCTAVE_LABEL = "尺度空间倍频程数"
AKAZE_OCTAVE_DESCRIPTION = """分析的縮放層次（八度）數量。
- 較高：可在更大尺寸差異下檢測特徵，但增加處理時間。
- 推薦：4。"""
AKAZE_LAYER_LABEL = "每倍频程的层数"
AKAZE_LAYER_DESCRIPTION = """每個縮放層次內的子層數。
- 較高：尺度檢測更細緻，但增加計算量。
- 推薦：4。"""
AKAZE_RATIO_LABEL = "比率阈值"
AKAZE_RATIO_DESCRIPTION = """特徵點匹配的嚴格程度。
- 較低 (0.5 - 0.7)：匹配嚴格，減少錯誤連接。
- 較高 (0.8 - 0.9)：容忍度高，匹配較多但錯誤連接機率增加。
- 推薦：0.8。"""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "重叠率 %"
OVERLAP_DESCRIPTION = """分塊處理（Tile）之間的重疊區域比例。
- 較高：減少運動區域的分塊邊界痕跡，但會增加處理時間。"""

TILE_SIZE_LABEL = "图块大小"
TILE_SIZE_DESCRIPTION = """圖像分塊處理的大小。
- 較小：捕捉更細微的細節和差異，但處理速度慢。
- 較大：處理速度快，但可能會遺漏微小的運動細節。"""

MOTION_SENSIVITY_LABEL = "运动灵敏度"
MOTION_SENSIVITY_DESCRIPTION = """系統檢測運動差異的靈敏度。
- 較低值：極靈敏（噪點也可能被誤判為運動）。
- 較高值：敏感度低（忽略微小運動）。"""

NOISE_OFFSET_LABEL = "噪声偏移量"
NOISE_OFFSET_DESCRIPTION = """忽略圖像噪點的閾值。
- 較高：極高噪點下圖像疊加更乾淨，但會降低運動檢測能力。"""

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
SETTING_PERFORMANCE_LABEL = "性能"
PROJECT_MENU_LABEL = "项目"
PROJECT_SAVE = "保存项目"
PROJECT_SAVE_AS = "项目另存为..."
PROJECT_OPEN = "打开项目..."
PROJECT_RECENT = "最近项目"
PROJECT_ABOUT = "关于 Pixel Refine"
LANGUAGE_LABEL = "语言"
LANGUAGE_TYPE = "英语", "印尼语", "繁體中文", "马来语"
GPU_ACCELERATION_LABEL = "GPU 加速"
MULTI_CORE_CPU = "多核 CPU 加速"
SETTINGS_SAVED = "设置已成功保存。"

CANT_READ_FILE_SETTINGS = "警告：无法读取设置文件 '{GENERAL_SETTINGS_FILE}'。将使用默认值。"
MULTI_CORE_CPU_DESCRIPTION = """啟用多線程並行處理。
- 開啟：大幅提升速度，但增加內存使用。內存受限時建議關閉。"""

GPU_ACCELERATION_DESCRIPTION = """使用顯卡 (GPU) 加速計算。
- 注意：目前僅支持 Farneback 和 LightGlue 對齊算法。"""

THUMBNAIL_LABEL = "缩略图"
THUMBNAIL_DESCRIPTION = """在批處理過程中顯示圖像預覽（實驗性）。
- 注意：添加新批處理時可能會引起輕微卡頓。"""

NOISE_MAD_OFFSET_LABEL = "MAD 噪声因子"
NOISE_MAD_OFFSET_DESCRIPTION = """MAD 對高噪點圖像的容忍度。
- 較高：噪點容忍度高，但運動區域產生重影的風險增加。"""

MAD_SENSITIVITY_LABEL = "MAD 灵敏度"
MAD_SENSITIVITY_DESCRIPTION = """MAD 對圖像差異的靈敏度。
- 較高：對微小變化更敏感，但高噪點下誤檢率會上升。"""

CONF_SKIP_DFT_LABEL = "跳过 DFT 的\n置信度"
CONF_SKIP_DFT_DESCRIPTION = """當 MBM 足夠好時跳過 DFT 的閾值。
- 較高：更多任務由 MAD 處理（計算輕量但結果較粗糙）。"""

WIENER_C_FACTOR_LABEL = "维纳 C 因子"
WIENER_C_FACTOR_DESCRIPTION = """維納濾波器對運動的靈敏度。
- 較低：對微小運動敏感，但易受噪點影響。"""

COARSE_MARGIN_LABEL = "粗对齐边距"
COARSE_MARGIN_DESCRIPTION = """分塊級別的對齊搜索邊距。
- 較高：疊加更精確，但會顯著減慢處理速度。"""

# --- Missing UI Keys ---
LBL_BATCH_MODE = "Mode Batch"
LBL_BULK_MODE = "Mode Bulk"
LBL_PARAMETER_ALIGNMENT = "圖像对齐设置"
LBL_ALIGNMENT_PLACEHOLDER = "圖像对齐设置将显示在此处"
LBL_PARAMETER_ALGORITHM = "处理方法设置"
LBL_ALGORITHM_PLACEHOLDER = "详细设置将在您选择上述处理方法后显示"
BTN_START = "开始处理"
BTN_NEW_BATCH = "创建新批次"
BTN_DELETE_BATCH = "删除批次"
LBL_ALGORITHM_SETTINGS = "叠加与对齐方法设置"
BTN_PROCESS_ALL_BATCH = "处理所有批次"
LBL_FROM_PROJECT = "从项目编号:"
LBL_TO_PROJECT = "至项目编号:"
MSG_INVALID_RANGE = "起始项目编号不能大于结束项目编号。"
BTN_CLOSE = "关闭"
LBL_STATUS_PROCESSING = "处理中"
BTN_BACK_TO_GRID = "返回网格"
BTN_IMPORT_IMAGES = "导入图像"
MSG_SUCCESS_SAVE_TO = "图像成功保存至:"
LBL_DRAG_DROP_HERE = "拖放图像至此处以添加"
BTN_YES_DELETE = "是，删除"
BTN_NO_CANCEL = "不，取消"
LBL_SELECTED_BATCHES_TITLE = "已选批次完整列表"
LBL_CREATE_NEW_BATCH_TITLE = "创建新批次"
LBL_BATCH_NAME = "批次名称"
BTN_CREATE = "创建"
MSG_CONFIRM_DELETE_BATCH_COUNT = "您确定要删除这 {} 个批次吗？"
MSG_NO_BATCHES_AVAILABLE = "没有可处理的批次列表。"
MSG_RENAME_FAILED = "无法重命名批次。名称可能无效或已被使用。"
TIP_CPU_CORES = "用于并行处理的 CPU 核心数。强烈推荐选择“自动”。"
LBL_SMART_NOISE_ALPHA = "智能噪声 Alpha (AI):"
TIP_SMART_NOISE_ALPHA = "控制人工智能 (AI) 对噪点的容忍度。\n较低值 = 对运动更敏感 (减少鬼影)。\n较高值 = 噪点清除更彻底 (有鬼影风险)。"
LBL_SMART_NOISE_AWARE = "智能感知噪声 (AI):"
TIP_SMART_NOISE_AWARE = "启用或禁用 AI 对图像噪点的自动分析。"
LBL_NOISE_CONTRIB = "噪声清除强度 (%):"
TIP_NOISE_CONTRIB = "调整 AI 过滤噪点的强度 (0% = 禁用，100% = 完全清除)。"
LBL_LIGHT_GLUE_TITLE = "LightGlue 方法设置"
LBL_SELECT_REFERENCE_IMAGE = "选择参考图像"
LBL_DELETE_IMAGES = "删除图像"
MSG_CONFIRM_DELETE_IMAGE = "您确定要从此批次中删除所选图像吗？"
TIP_RIGHT_CLICK_COPY = "右键单击以复制文本"
MSG_UNSUPPORTED_FORMAT_IGNORED = "文件格式不支持或扩展名无效。"
MSG_NO_VALID_IMAGES_GROUP = "没有可导入的有效图像。"
LBL_LOGGING_LEVEL = "日志级别:"
BTN_RESET_TO_DEFAULT = "重置为默认值"
BTN_CLEAR_CACHE = "清除缓存"
LBL_STATUS_READY = "就绪"
LBL_ITEMS_REMAINING = "个进程剩余"
LBL_SPLASH_LOADING = "正 在 加 载 . . ."
MSG_EXIFTOOL_NOT_FOUND = "未找到 Exiftool。请确保它已安装并已添加到系统的 PATH 中。"
MSG_NO_BATCHES_YET = "尚无批次"
MSG_NO_BATCHES_YET_DESC = "创建一个新批次或导入图像以开始。"
MSG_NO_BATCH_SELECTED = "没有选择批次"
LBL_BATCH_IMAGE_COUNT_FORMAT = "批次 {}   -   ({} 张图像)"
DESC_SUPER_RESOLUTION_CARD = "增强细节并缩放图像分辨率。"
DESC_DENOISING_CARD = "减少图像噪点并对齐像素层。"




# --- New UI & Bulk Core Keys ---
BULK_FROM = "从编号:"
BULK_TO = "至编号:"
BULK_MSG_RANGE_ERROR = "起始编号必须 <= 结束编号。"
BULK_ERR_RETRIEVE = "加载项目图像失败。"
BULK_WARN_UNSUPPORTED = "不支持的格式将被忽略。"
CORE_SELECT_REF_IMAGE = "设为基准"
CORE_DELETE_IMAGES = "删除所选"
CORE_MSG_CONFIRM_DELETE = "确认删除所选图像吗？"
CORE_TOOLTIP_COPY = "右键复制"

# 对齐参数提示
PARAMETER_DIRECT_EDIT_TOOLTIP = "可以直接输入数值，然后按 Enter 或移开焦点以应用。"
AKAZE_THRESHOLD_TOOLTIP = "AKAZE 特征灵敏度。较低值会检测更多关键点，适合暗图或低纹理图像，但可能增加噪声匹配；较高值更严格且更快。"
AKAZE_OCTAVES_TOOLTIP = "AKAZE 分析的尺度层级数量。更多 octave 有助于处理帧间较大的缩放变化，但会增加处理时间。"
AKAZE_OCTAVE_LAYERS_TOOLTIP = "每个 octave 内的子层数。较高值可更细致地检测尺度，但特征提取会更慢。"
FEATURE_RATIO_THRESHOLD_TOOLTIP = "特征匹配的 Lowe ratio test 阈值。较低值只保留高置信匹配；较高值保留更多匹配，但可能包含错误匹配。"
FEATURE_MIN_MATCHES_TOOLTIP = "估计图像运动前所需的最少有效匹配数。提高可让对齐更安全；仅在图像特征很少时降低。"
FEATURE_MAX_KEYPOINTS_TOOLTIP = "用于运动估计的最大关键点数量。较高值可能改善困难对齐，但会增加 CPU 时间。"
FEATURE_RANSAC_THRESHOLD_TOOLTIP = "RANSAC 允许的重投影误差。较低值更严格并排除更多离群点；较高值更容忍噪声/运动，但可能接受错误匹配。"
FEATURE_TRANSFORMATION_TOOLTIP = "匹配后的运动模型。Homography 适合透视变化；Affine 更简单，对小幅相机位移更稳定。"
FEATURE_KEEP_EDGES_TOOLTIP = "变形后保留边缘像素。若希望移除不稳定边缘区域，请关闭。"
FEATURE_ENABLE_CROPPING_TOOLTIP = "对齐后裁剪不稳定边缘，使最终堆栈只使用共同可靠的图像区域。"
PARAMETER_USE_MULTI_CORE_TOOLTIP = "可用时使用多个 CPU 核心。通常更快，但 CPU 占用会增加。"
ORB_NFEATURES_TOOLTIP = "ORB 检测的最大特征数量。较高值为困难图像提供更多匹配候选，但处理更重。"
ORB_SCALE_FACTOR_TOOLTIP = "ORB 金字塔层级之间的缩放步长。较小值更细致但更慢；较大值更快但精度较低。"
ORB_LEVELS_TOOLTIP = "ORB 使用的金字塔层数。更多层有助于处理尺度变化，但会增加运行时间。"
FARNEBACK_PYR_SCALE_TOOLTIP = "金字塔层级之间的图像缩放比例。较低值对大运动使用更强下采样；0.5 是常用值。"
FARNEBACK_LEVELS_TOOLTIP = "光流计算的金字塔层数。更多层有助于跟踪大运动，但会增加内存和时间。"
FARNEBACK_WINSIZE_TOOLTIP = "用于估计运动的像素窗口大小。大窗口更平滑且抗噪；小窗口保留更多局部细节。"
FARNEBACK_ITERATIONS_TOOLTIP = "每个金字塔层的细化次数。更多迭代可提高光流精度，但会变慢。"
FARNEBACK_POLY_N_TOOLTIP = "多项式展开的邻域大小。5 更锐利；7 更平滑且更抗噪。"
FARNEBACK_POLY_SIGMA_TOOLTIP = "多项式展开的高斯平滑强度。较高值可抑制噪声，但可能弱化细小运动。"
FARNEBACK_FLAGS_TOOLTIP = "Farneback 可选标志。0 为标准；256 启用 Gaussian window，在部分场景可获得更平滑光流。"
OPTICAL_FLOW_TILE_COLS_TOOLTIP = "块级光流处理的水平 tile 数。更多 tile 可降低单块内存，但会增加拼接开销。"
OPTICAL_FLOW_TILE_ROWS_TOOLTIP = "块级光流处理的垂直 tile 数。更多 tile 可降低单块内存，但会增加拼接开销。"
OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP = "tile 之间的重叠比例。更大重叠可减少 tile 接缝，但会增加重复计算。"
LIGHT_GLUE_MATCH_CONFIDENCE_TOOLTIP = "Light Glue 匹配置信度阈值。数值越高只保留更可靠的特征对；数值越低会得到更多匹配，但可能包含更多噪声。"
LIGHT_GLUE_USE_GPU_TOOLTIP = "当后端可用时使用 GPU 运行 Light Glue 推理。适合神经网络模型，但会占用额外 VRAM。"
LUCAS_KANADE_GRID_STEP_TOOLTIP = "Lucas-Kanade 网格点之间的距离。数值越小光流越密集但更慢；数值越大速度更快。"
LUCAS_KANADE_BORDER_MARGIN_TOOLTIP = "生成网格点前与 tile 边缘保留的安全距离。边缘留白可减少不稳定边界区域的跟踪。"
LUCAS_KANADE_POINT_WORKERS_TOOLTIP = "用于拆分每个 tile 内网格点跟踪的 worker 数量。多核心 CPU 可提高；如果 CPU 过满或出现波动则降低。"
LUCAS_KANADE_WIN_SIZE_TOOLTIP = "Lucas-Kanade 搜索窗口大小。较大的窗口有助于较大运动；较小窗口更保留局部细节。"
LUCAS_KANADE_MAX_LEVEL_TOOLTIP = "光流金字塔层数。层数越多越适合较大运动，但处理时间会增加。"
LUCAS_KANADE_ITERATIONS_TOOLTIP = "每个跟踪点的搜索迭代次数。更多迭代可能提高精度，但处理更慢。"
LUCAS_KANADE_EPSILON_TOOLTIP = "Lucas-Kanade 收敛阈值。数值越小越精细，但可能需要更多迭代。"
UI_STATUS_READY = "就绪"
UI_ITEMS_REMAINING = "剩余"
UI_SPLASH_LOADING = "正在加载..."

PROGRESS_ALIGN = "对齐: {}/{}"
PROGRESS_MERGING = "合并: {}/{}"

# Missing Keys
MSG_DATABASE_ERROR = "数据库错误"
MSG_DB_RETRIEVE_FAILED = "从数据库检索数据失败。"
MSG_FOLDER_ERROR = "文件夹错误"
MSG_CREATE_FOLDER_TIFF_FAILED = "无法创建用于保存 TIFF 文件的文件夹。"
MSG_TIFF_PROCESSING_ISSUES = "TIFF 处理问题"
MSG_TIFF_PROCESS_FAILED_SOME = "部分 TIFF 文件处理失败。"
MSG_IMPORT_FAILED = "导入失败"
MSG_NO_VALID_FILES_IMPORT = "未找到可导入的有效文件。"
MSG_ERROR_TITLE = "错误"
MSG_IMPORT_ERROR_OCCURRED = "导入过程中发生错误。"
MSG_CAUTION_TITLE = "警告"
MSG_CONFIRM_TITLE = "确认"
MSG_WARNING_TITLE = "警告"
MSG_ALIGN_ALGO_NOT_RECOGNIZED = "无法识别对齐算法。"
MSG_NO_PROCESSED_IMAGES_SAVE = "没有可保存的已处理图像。"
MSG_INVALID_FORMAT = "格式无效"
MSG_UNSUPPORTED_FORMAT_EXTENSION = "不支持的文件格式或扩展名。"
MSG_COULD_NOT_READ_SOURCE = "无法读取源文件。"
MSG_CLEANUP_ERROR = "清理错误"
MSG_REMOVE_TEMP_FAILED = "删除临时文件失败。"
MSG_SUCCESS_TITLE = "成功"
MSG_SUCCESS_SAVE = "图像保存成功。"
MSG_FAILED_SAVE_IMAGE = "保存图像失败。"
BTN_CANCEL = "取消"
SIMILARITY_V2_GROUP_TITLE = "Similarity V2 参数"
RESET_TO_DEFAULTS_BUTTON_TEXT = "重置为默认值"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TITLE = "无有效图像"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TEXT = "未选择可导入的有效图像。"
DEVICE_ACCELERATION_LABEL = "GPU 加速"
BTN_TEST_BACKEND_HARDWARE = "测试硬件加速"
MSG_IMPORT_ERROR = "导入错误"
LBL_ANALYSIS_MODE = "分析模式"
LBL_FAST = "快速"
LBL_DEEP = "深度"
MSG_HARDWARE_TEST_DEPTH = "选择硬件加速测试深度："
MSG_HARDWARE_TEST_FAST = "快速检查后端兼容性。"
MSG_HARDWARE_TEST_DEEP = "对每个后端进行全面验证。"
MSG_BACKEND_RESTART_REQUIRED = "需要重启以应用新的后端选择。"
BTN_YES = "是"
BTN_NO = "否"
BTN_OK = "确定"
LBL_ETA = "预计 {0}"
LBL_TESTING = "测试中"
LBL_HARDWARE_PREPARING = "正在准备硬件后端..."
LBL_HARDWARE_BACKEND_ANALYSIS = "硬件后端分析"
MSG_BACKEND_TEST_CANCELLED = "后端测试已取消。"
LBL_INITIALIZATION_FAILED = "初始化失败"
LBL_RENDERER_UNAVAILABLE = "渲染器不可用"
LBL_UNKNOWN = "未知"
LBL_NO_BACKEND_RESULTS = "没有可用的后端结果。"
LBL_BACKEND_COMPATIBILITY_RESULTS = "后端兼容性结果"
LBL_DIAGNOSTIC_LOGS = "诊断日志"
MSG_BACKEND_TEST_FINISHED = "后端测试完成。"
LBL_AUTO_FALLBACK = "自动回退"
LBL_AUTO_FALLBACK_TIP = "启用后，如果所选后端不可用，将自动依次回退到 CUDA、Vulkan、OpenGL，然后是 CPU。"
AUTO_SHUTDOWN_LABEL = "启用自动关闭"
AUTO_SHUTDOWN_DESCRIPTION = "在设定时间内没有用户操作后关闭应用程序。"
AUTO_SHUTDOWN_TIMEOUT_LABEL = "闲置时间（分钟）"
