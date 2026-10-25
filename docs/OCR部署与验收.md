# OCR 部署与验收

## 1. 安装 CPU 引擎

后端基础依赖不包含 OCR 模型运行时。在项目虚拟环境中先安装基础依赖，再安装可选 OCR 依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
# PaddleX 使用 contrib 版本；同一环境不要同时保留多个 cv2 发行包。
.\.venv\Scripts\python.exe -m pip uninstall -y opencv-python-headless opencv-python opencv-contrib-python
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-ocr.txt
```

本轮实际测试环境为 Windows、Python 3.13、PaddlePaddle 3.3.1、PaddleOCR 3.3.2、PaddleX 3.3.13，使用 CPU 和 PP-OCRv5 mobile 检测/识别模型。版本文件将 OpenCV contrib 随 PaddleX 安装；重新安装基础 requirements 后需重新检查 OpenCV 发行包是否冲突。该环境没有验证 GPU 部署或打包后的桌面 EXE。

## 2. 模型加载和首次识别

在 `backend/.env` 设置 `OCR_MODEL_CACHE_DIR=C:/PartyReviewModels` 等英文目录。首次运行会从模型官方发布源下载权重，后续使用缓存。Windows 下模型目录含中文会导致 Paddle 原生加载错误，本轮已重现；缓存目录和显式模型目录都应使用英文路径。

```powershell
.\.venv\Scripts\python.exe backend/ocr_check.py
```

命令会真正识别本地生成的 `OCR 12345` 测试图片，只有识别正确才返回 `ok: true` 和退出码 0；“安装了 paddleocr 包”不再等同于“模型可用”。系统设置中的“测试 OCR”执行同一检查，并展示等待、成功或失败及识别文字。首次下载较慢时可预先运行命令行自检。

离线部署可预先下载官方 `PP-OCRv5_mobile_det` 和 `PP-OCRv5_mobile_rec` 目录，分别设置 `OCR_DET_MODEL_DIR`、`OCR_REC_MODEL_DIR`，并设置 `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True` 跳过联网探测。目录须包含完整的模型文件和配置；不要只复制权重文件。权重下载不包含材料上传，材料识别在本地 CPU 子进程内进行。

依赖和模型参数参考：[官方安装说明](https://www.paddleocr.ai/v3.3.0/en/version3.x/installation.html)、[官方模型发布](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_rec)。

## 3. 上传、解析和定位

PNG、JPEG 和没有可选文本的 PDF 页面进入 OCR，普通有文本 PDF 保留原来的文本抽取。纯扫描 PDF 标记为 `OCR`，混合文档标记为 `MIXED`。OCR 图像像素框转换为 PDF 页坐标后保存，避免前端按页面尺寸定位时产生偏移。

后台保存文本、页码、识别框、置信度、引擎、预览和警告；材料详情的解析面板展示这些数据。OCR 引擎故障会将版本标记为 `FAILED`，保留已获得的部分结果和警告，不再把空识别当作解析成功。

## 4. 超时与重试

默认单次识别等待上限为 `OCR_TIMEOUT_S=180` 秒。原生引擎只运行在单独的子进程中，超时或崩溃后终止该子进程，后续请求重新启动；并发请求按序执行，等待队列也有超时。服务仍可处理其他 API 请求。

解析任务沿用后台的有限自动重试。重试耗尽后，草稿/退回状态下有上传权限的用户可在材料详情点击“重试解析”；只允许当前未冻结版本，重复请求复用已有排队/运行任务，不会创建重复解析记录。审核中的材料、其他人的档案、历史或冻结版本不可通过此入口重试。管理员仍可在任务页面处理失败任务。

## 5. 验收边界

2026-10-25 已在隔离 PostgreSQL 16 实例和真实 CPU 模型上验证：中文 PNG/JPEG/扫描 PDF 上传、后台任务处理、文本与框坐标保存、解析 API 返回、故障状态与重试恢复。测试材料由代码生成，仅含虚构内容；并未使用真实学生材料。前端采用 DOM 交互测试验证自检状态、中文文本展示及重试触发。

手写正文、手写签名、印章文字和真实拍摄材料的准确率 **待验收**：当前没有带正确文字标注的代表性样本，不能由清晰印刷体样例推断准确率。现有红色印章/签名区域启发式也不等同于印章真实性或手写内容识别。用户已确认将这两类保留为待验收。

可复现测试（使用专用测试数据库，创建随机 schema 后清理）：

```powershell
$env:TEST_DATABASE_URL='postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/ocr_test'
$env:RUN_OCR_INTEGRATION='1'
$env:OCR_MODEL_CACHE_DIR='C:/PartyReviewModels'
.\.venv\Scripts\python.exe -m pytest backend/tests/test_ocr_runtime.py backend/tests/test_ocr_integration.py -q
cd frontend
npm run test:ui
npm run build
```

普通 CI 默认只运行无需权重下载的 OCR 回归。设置 `RUN_OCR_INTEGRATION=1` 后真实模型失败会使验收失败，不会降级为模拟识别通过。
