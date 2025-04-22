  # Main Content
UNDER_DEVELOPMENT = "功能頁面「{page_name}」開發中，敬請期待"

# Sidebar
SETTINGS_SIDEBAR_LABEL= "設定"
HDR_SIDEBAR_LABEL= "HDR 重建"

TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "导入图片"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "删除图片"
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "创建批次"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "批量删除"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "批量处理"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "保存到"

NO_DATA_BATCH = "没有批次数据"

BATCH_DELETE_LABEL = "确认批量删除", "您确定要删除批次{}吗？"
LOADING_THUMBNAIL = "正在加载...."
ADD_IMAGE_BUTTON = "添加"
PREVIEW_IMAGE_BUTTON = "预览"
DELETE_IMAGE_BUTTON = "删除"

PARAMETER_BATCH_CROP_EDGE = "裁剪边缘"
PARAMETER_BATCH_KEEP_EDGE = "保留边缘"
PARAMETER_BATCH_DENOISING = "去噪"
PARAMETER_BATCH_SUPER_RESOLUTION = "超级分辨率"
PARAMETER_BATCH_ALIGNMENT = "对齐图像"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "将对齐结果保存至文件夹"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "保存对齐结果以供下一步处理"

TITLE_BATCH_ALL_DELETE_BUTTON = "删除所有批次"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "您确定要删除所有批次数据吗？"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "未存储批次数据。"

UI_LABEL_BATCH_NO_PROCESS = "没有可处理的批次！"
UI_LABEL_BATCH_SUCCES = "所有批次均已处理完毕！"
UI_LABEL_BATCH_PROCESS = "正在处理 {} 批次..."
UI_LABEL_BATCH_PROGRESS = "{}/{} 批次已处理..."
UI_FAILED_TO_SAVE_IMAGE_BATCH = "无法保存图像：{}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "图像保存成功：{}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "无图像"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "系统文件夹（数据库/堆栈）不存在"

CONSOL_LOG_RUNNING_ALGORITHM = "选择了进程 {}，算法：{}"

# Main Content
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "匯入圖片"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "刪除圖片"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "開始處理"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "另存新檔"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "圖片格式 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "選擇圖片"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "重複圖片"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "已跳過 {count} 張重複圖片"
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "已選格式"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "即將匯入 {count} 張「{format}」格式圖片"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "錯誤", "未選擇有效圖片"

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "錯誤", "未選擇圖片"
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "確認刪除選取的 {count} 張圖片？"

PREVIEW_PANEL_LABEL = "預覽面板"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "圖片處理中，請稍候..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "未選取圖片"

UPDATE_PROGRESS_BAR_STATUS = "已完成 {value}%（剩餘 {images_left} 項）"

ON_IMPORT_COMPLETE_STATUS = "匯入完成"
ON_IMPORT_COMPLETE_MESSAGES = "成功匯入 {successful_images} 張圖片"

PROCESS_ALGORITHM_PROCESS_SKIPPED = "未選擇處理演算法"

# PARAMETER STACKING 
NOT_IMAGE_PREVIEW = "無預覽圖片"
MODULE_NOT_IMPLEMENT = "功能模組未實裝"
NO_ALIGNMENT_PROCESS = "確定不進行影像預對齊處理？"

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "圖片載入失敗"

SAVE_TO_HDF5_ALIGNED_SAVING = "儲存已對齊圖片"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "第 {index} 張圖片已儲存"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "所有圖片儲存完成"

RUN_IMAGE_NOT_FOUND = "資料庫中找不到圖片"
RUN_REFERENCE_IMAGE_NOT_FOUND = "無法從 {image_paths[0]} 載入參考圖"
RUN_SAVING_REFERENCE_IMAGE = "參考圖儲存中"
RUN_IMAGE_PROCESSING = "正在處理第 {i} 張（共 {total_images} 張）..."
RUN_IMAGE_PROCESSING_FAILED = "無法載入第 {i} 張圖片：{image_paths[i]}"
RUN_IMAGE_PROCESSING_SAVING = "第 {i} 張圖片已儲存"
RUN_IMAGE_PROCESSING_FINISHED = "處理完成"

ERROR_ACCUMULATE_IMAGE = "累积图像为无或总重量无效。"
RUN_STACK_PROCESSING_FAILED = "无法堆叠图像"

FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "第 {} 張圖片全域運動計算失敗"
FAIL_COMPENSATE_MOTION_PROCESS = "第 {} 張圖片運動補償失敗"

UNRECOGNIZED_TRANSFORMATION = "无法识别的转换类型。"
FAILED_TO_COMPUTE_TRANSFORMATION ="无法计算转换。"
FAILED_TO_COMPUTE_CROP = "无法计算有效裁剪。进程中止。"

FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "第 {} 張圖片轉換矩陣檔案遺失"
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="影像對齊與裁切中（{}/{}）"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="儲存影像中（{}/{}）"

FAIL_CROPPING_PROCESS ="裁切失敗：重疊區域不足"

CANCEL_PROCESSING = "確定要中止處理程序？"

RUN_ERROR_STATUS = "錯誤發生：{error}"
RUN_ERROR_MESSAGE = "錯誤訊息：{error}"

WINDOW_START_PROCESSING = "開始處理..."
WINDOW_PROCESSING_COMPLETE = "處理完成！"

# Farneback Optical Flow
WINDOW_TITLE_FARNEBACK = "Farneback 光流對齊演算法"

COMPENSATE_MOTION_STATUS = "正在補償第 {image_id} 張圖片運動..."
COMPENSATE_MOTION_FINISHED = "第 {image_id} 張圖片運動補償完成"

# AKAZE, ORB
WINDOW_TITLE_AKAZE = "AKAZE 特徵對齊"
WINDOW_TITLE_ORB = "ORB 特徵對齊"

# Algorithm Denoising
STACK_IMAGES_FAILED = "無可用處理圖片"
STACK_IMAGES_PROCESS = "處理進度（{current}/{total}）..."

RUN_IMAGE_PROCESS_STARTED = "程序啟動中..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "資料庫中找不到圖片"
RUN_IMAGE_PROCESS_STACK_SUCCESS = "影像堆疊完成！結果已儲存至：{output_path}"

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "平均值堆疊"
WINDOW_TITLE_MEDIAN = "中位數堆疊"
WINDOW_TITLE_WEIGHTED_AVERAGE = "加權平均堆疊"

WINDOW_TITLE_SIMILARITY = "相似度堆疊"
SIMILARITY_MNFR_LOAD_FAILED = "未提供輸入圖片"
SIMILARITY_MNFR_BIT_REQUIRED = "圖片需為 8bit 或 16bit 格式"
SIMILARITY_MNFR_PROCESS_FINISHED = "堆疊處理完成"
SIMILARITY_MNFR_PROCESS = "堆疊處理中{}/{}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "批次堆疊進度（{current}/{total}）"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "插值超解析度"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = """請選擇演算法以檢視參數"""

# ORB Parameters
ORB_PARAMETER_SETTING_LABEL = "ORB 參數設定"
ORB_NFEATURES_LABEL = "特徵點數量"
ORB_NFEATURES_DESCRIPTION = """控制演算法可偵測的影像細節特徵數量

- 數值越高：可識別更多細微特徵，提升對齊精度，但增加運算時間
- 建議範圍：一般場景 500-1500，高精度需求 2500-5000"""

ORB_SCALEFACTOR_LABEL = "縮放係數"
ORB_SCALEFACTOR_DESCRIPTION = """控制影像金字塔的縮放比例層級

- 接近 1.0：多層次細微縮放，精度高但速度慢
- 較大數值：快速縮放層級，運算快但可能遺失細節
- 建議範圍：1.2-1.5"""

ORB_NLEVELS_LABEL = "金字塔層級數"
ORB_NLEVELS_DESCRIPTION = """設定影像金字塔的層級數量

- 層級越多：可捕捉多尺度特徵，適合尺寸多變的影像
- 層級越少：運算速度越快
- 建議值：2-4 層"""

ORB_TRANSFORMATION_LABEL = "變換類型"
ORB_TRANSFORMATION_DESCRIPTION = """選擇最適合您需求的影像對齊方式：

可用選項：
- 【單應變換】HOMOGRAPHI
  適用拍攝角度差異較大的情況（例如：從上方和側面拍攝的桌子照片）
  可調整透視效果模擬3D立體感

- 【仿射變換】AFFINE
  支援旋轉、非等比縮放和平移操作
  範例：修正傾斜照片並局部放大特定區域

- 【相似變換】SIMILARITY
  僅允許旋轉、等比例縮放和平移
  保持原始比例不變形（如商標圖案保真）

- 【歐式變換】EUCLIDEAN
  最基礎調整：僅旋轉與平移，不改變尺寸
  適合微調輕微偏移的照片

選用建議：
✓ 多數情況推薦單應變換（特別是多角度拍攝素材）
✓ 簡單的位置/角度修正優先選歐式或相似變換
✓ 仿射變換僅在需要彈性形變調整時使用"""

ORB_RANSAC_LABEL = "RANSAC 閾值"
ORB_RANSAC_DESCRIPTION = """控制特徵匹配的容錯閾值

- 較低值 (1-3)：嚴格過濾異常值，精度高但可能遺失有效特徵
- 較高值 (4-5)：寬鬆匹配，特徵點多但可能包含誤匹配
- 建議範圍：1-3（依影像雜訊程度調整）"""

# Farneback Optical Flow
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback 參數設定"

FARNEBACK_PYRAMID_SCALE_LABEL = "金字塔縮放率"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """控制影像金字塔各層級的縮放比例

- 較小值 (0.1-0.5)：大幅縮減影像尺寸，運算快但精度低
- 接近 1.0：輕微縮放，精度高但速度慢
- 建議值：0.5"""

FARNEBACK_LEVELS_LABEL = "金字塔層數"
FARNEBACK_LEVELS_DESCRIPTION = """設定影像金字塔的總層級數

- 層數越多：可檢測多尺度運動，適用複雜大範圍位移
- 層數越少：運算速度越快
- 建議範圍：1-10（預設值 3）"""

FARNEBACK_WIN_SIZE_LABEL = "運算視窗尺寸"
FARNEBACK_WIN_SIZE_DESCRIPTION = """控制光流計算的局部區域大小

- 較大視窗：運動估算穩定，適合全域運動
- 較小視窗：敏感於局部運動，但易受雜訊影響
- 建議值：15"""

FARNEBACK_ITERATIONS_LABEL = "迭代次數"
FARNEBACK_ITERATIONS_DESCRIPTION = """設定每層金字塔的光流計算迭代次數

- 次數越多：結果越精確，耗時增加
- 建議值：3"""

FARNEBACK_POLY_N_LABEL = "多項式展開階數"
FARNEBACK_POLY_N_DESCRIPTION = """控制像素鄰域的多項式擬合複雜度

- 數值越大：運動場估算更平滑，細節敏感度降低
- 常用值：5 或 7"""

FARNEBACK_POLY_SIGMA_LABEL = "高斯平滑係數"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """控制前置高斯濾波的強度

- 較高值：有效抑制雜訊，但可能模糊運動細節
- 建議值：1.2"""

FARNEBACK_FLAGS_LABEL = "運算模式標誌"
FARNEBACK_FLAGS_DESCRIPTION = """特殊計算模式旗標

- 通常保持預設值 0 即可
- 進階使用者可依需求調整"""

# AKAZE Parameters
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE 參數設定"

AKAZE_THRESHOLD_LABEL = "特徵閾值"
AKAZE_THRESHOLD_DESCRIPTION = """控制特徵點檢測靈敏度

- 較低值：檢測更多特徵點（含雜訊）
- 較高值：僅保留顯著特徵
- 建議值：0.0010"""

AKAZE_OCTAVE_LABEL = "尺度空間層級"
AKAZE_OCTAVE_DESCRIPTION = """設定影像尺度空間的分析層級

- 層級越多：多尺度特徵檢測能力越強
- 建議值：4"""

AKAZE_LAYER_LABEL = "每層子級數"
AKAZE_LAYER_DESCRIPTION = """控制每層尺度空間的子層數量

- 子層越多：尺度解析度越高
- 建議值：4"""

AKAZE_RATIO_LABEL = "匹配閾值比率"
AKAZE_RATIO_DESCRIPTION = """控制特徵匹配的嚴格程度

- 較低值 (0.5)：嚴格匹配，錯誤率低
- 較高值 (0.8)：寬鬆匹配，特徵對應多
- 建議值：0.8"""

KEEP_EDGES_LABEL = """保留
边缘"""
IGNORE_EDGE_LABEL= """忽略边缘"""

KEEP_EDGES_DESCRIPTION = """保留边缘功能允许算法在对齐过程
中保持图像边缘完整。"""

ENABLE_CROP_LABEL = """启用 裁剪"""
DISABLE_CROP_LABEL = """禁用 裁剪"""
CROP_DESCRIPTION = """启用裁剪以移除
未使用的图像边框

注意：有时会发生截断错误（非常罕见）
例如非常小的图像，或者裁剪图像时出现错误。"""


ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "保存到文件夹"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = """不保存到
文件夹"""

SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "搜索.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "默认文件夹"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "选择文件夹"

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """保存用于
后续处理"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """不保存用于
后续处理"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """保存图像以用于去噪或超分辨率处理"""

SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """将对齐后的图像保存到文件夹中
默认文件夹为PC中的文档文件夹"""

APPLY_PARAMETER_BUTTON_TEXT = "套用設定"

RESTART_APPLICATION_REQUIRED = "需要重新启动"
RESTART_APPLICATION_DESCRIPTION = "重新启动以查看更改"
ACCEPT_RESTART_APPLICATION = "重启"
REJECT_APPLICATION_DESCRIPTION = "稍后"
COMMAND_APPLICATION_DESCRIPTION = "重新加载应用程序..."


# ------------ Parameter Setting Algorithm --------------------- #


# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "影像對齊演算法"
NONE_ALIGNMENT_DESCRIPTION = "不進行影像對齊處理"
FARNEBACK_DESCRIPTION = """像素級高精度對齊演算法
優勢：適用精細位移
限制：對旋轉/透視變形敏感"""

AKAZE_DESCRIPTION = """強健特徵對齊演算法
優勢：耐受旋轉/透視/尺度變化
限制：精度略低於 Farneback"""
ORB_DESCRIPTION = """快速特徵對齊演算法
優勢：運算速度快
限制：適用輕微位移場景"""

SUPER_RESOLUTION_NAME = "超解析度演算法"
NONE_SUPER_RESOLUTION_DESCRIPTION = "不進行解析度提升"
INTERPOLATION_DESCRIPTION = """基礎插值演算法
優勢：運算快速
限制：細節增強有限"""

DENOISING_NAME = "降噪演算法"
NONE_DENOISING_DESCRIPTION = "不進行降噪處理"
WEIGHTED_AVERAGE_DESCRIPTION = """動態加權平均法
優勢：處理輕微位移
限制：大幅移動會產生殘影"""
                        
AVERAGE_DESCRIPTION = """快速平均堆疊法
優勢：靜態場景最佳化
限制：需配合位移補償使用"""

MEDIAN_DESCRIPTION = """中位數濾波法
優勢：有效消除輕微雜訊
限制：大幅移動會產生瑕疵"""

SIMILARITY_DESCRIPTION = """先進相似度堆疊法
優勢：85% 無殘影，運動補償優異
技術來源：
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021).
HDR+ 降噪方法實作與分析
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""

SIMILARITY_MOTION_V2_DESCRIPTION_ZH = """Similarity V2是基于similarity v1算法开发的，并在此基础上实现了多项显著改进。
该算法能够生成更干净的图像，即便输入图像噪声严重，也能凭借其智能区分噪声、纹理和细微运动的能力达到这一效果。在低照明环境下表现更为出色，但其处理速度较v1版本较慢。"""

# ------------------ General Settings ------------------ #
SETTING_GENERAL_LABEL = "通用設定"
LANGUAGE_LABEL = "介面語言"
LANGUAGE_TYPE = "英语", "印尼语", "繁体中文", "马来语"