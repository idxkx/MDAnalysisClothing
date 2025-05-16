# MDAnalysisClothing

## 项目简介
MDAnalysisClothing 是一个基于 FastAPI 的智能服装分析与生成平台，支持：
1. 上传服装图片，自动识别并输出结构化服装特征描述。
2. 输入服装特征描述，自动生成符合描述的新服装图片。

本项目默认使用 OpenAI API 实现 AI 能力，但支持后续扩展为本地或其他云端模型（如 CLIP、BLIP2、Stable Diffusion 等）。

---

## 主要功能

### 1. 图片反推服装特征描述
- **输入**：服装图片（jpg/png 格式）
- **输出**：结构化服装特征描述（JSON，包含颜色、款式、材质、细节等字段）

### 2. 描述生成服装图片
- **输入**：服装特征描述（自然语言或结构化 JSON）
- **输出**：生成的服装图片（base64 字符串或图片 URL）

---

## 技术架构与扩展性

### AI 能力适配层设计
本项目采用"接口实现分离"架构，所有 AI 能力都通过统一接口调用，便于未来切换或扩展不同模型。

- `Image2Description`：图片转结构化描述的接口
- `Description2Image`：描述转图片的接口

每种 AI 实现（如 OpenAI、CLIP、Stable Diffusion）都需实现上述接口，主业务逻辑无需关心底层细节。

#### 扩展方式
1. 新增模型时，实现对应接口类（如 `CLIPImage2Description`）。
2. 在配置文件或环境变量中切换使用的模型。
3. 主接口自动适配，无需修改主业务代码。

---

## 安装与运行

### 方式一：推荐（pip，适合所有用户）

```bash
pip install -r requirements.txt
```

### 方式二：进阶（conda虚拟环境，适合有经验用户）

```bash
conda create -n md_analysis python=3.10
conda activate md_analysis
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --reload
```

### 访问API文档

浏览器访问：http://127.0.0.1:8000/docs

---

## API 接口说明

### 1. 图片反推服装特征描述
- **接口地址**：`/analyze`
- **请求方式**：POST
- **参数**：
  - `file`：服装图片（form-data 上传）
- **返回**：
  - JSON 格式的服装特征描述

#### 示例
```bash
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@test.jpg"
```

### 2. 描述生成服装图片
- **接口地址**：`/generate`
- **请求方式**：POST
- **参数**：
  - `description`：服装特征描述（字符串或 JSON）
- **返回**：
  - 生成的服装图片（base64 字符串）

#### 示例
```bash
curl -X POST "http://127.0.0.1:8000/generate" -H "Content-Type: application/json" -d '{"description": {"color": "红色", "style": "连衣裙"}}'
```

---

## 日志与错误监控

本项目已内置详细日志与错误监控，便于开发和生产环境排查问题。

### 日志功能
- 记录每次API请求、AI适配器调用、异常信息。
- 日志分级：INFO（正常流程）、ERROR（异常）。
- 默认输出到控制台。

### 如何查看日志
- 启动服务后，所有日志会实时输出在终端。
- 典型日志示例：
  ```
  2024-05-01 12:00:00 INFO mdanalysis 收到/analyze请求: 文件名=test.jpg
  2024-05-01 12:00:00 INFO mdanalysis.ai 调用OpenAI图片转描述，输入字节数=12345
  2024-05-01 12:00:00 ERROR mdanalysis 分析失败: ...
  ```

### 自定义日志输出
- 如需写入日志文件，可在`main.py`中调整`logging.basicConfig`配置。
- 支持按需调整日志级别、格式、输出位置。

---

## 测试方法

### 1. 运行全部测试

```bash
pytest
```

### 2. 测试覆盖内容
- /analyze 接口返回结构化描述
- /generate 接口返回base64图片

---

## 目录结构规划

```
MDAnalysisClothing/
├── main.py                # FastAPI 主入口
├── ai_interfaces.py       # AI 能力接口定义
├── ai_openai.py           # OpenAI 实现的适配器
├── ai_clip.py             # CLIP 实现的适配器（可选）
├── ai_sd.py               # Stable Diffusion 实现的适配器（可选）
├── requirements.txt       # 依赖包列表
├── README.md              # 项目说明文档
├── tests/                 # 测试用例
└── ...
```

---

## 未来规划
- 支持更多服装细节字段
- 增加用户管理与历史记录
- 支持多语言描述与生成
- 集成更多 AI 模型

---

## 开发 TODO 清单

- [x] 设计并实现 AI 能力接口（`ai_interfaces.py`）
    - [x] `Image2Description` 抽象类
    - [x] `Description2Image` 抽象类
- [x] 实现 OpenAI 适配器（`ai_openai.py`）
    - [x] 图片转描述的 OpenAI 实现
    - [x] 描述转图片的 OpenAI 实现
- [x] 设计 FastAPI 主接口（`main.py`）
    - [x] `/analyze` 图片反推描述接口
    - [x] `/generate` 描述生成图片接口
    - [x] 接口参数校验与异常处理
- [x] 编写 requirements.txt 依赖文件
- [x] 实现基础的测试用例（tests/）
    - [x] 图片转描述接口测试
    - [x] 描述转图片接口测试
- [ ] 预留/实现其他模型适配器（如 CLIP、Stable Diffusion）
- [ ] 完善日志与错误监控
- [x] 优化接口文档与交互体验
- [x] 持续完善 README 文档 
- [x] 持续完善 README 文档 

---

## 单元测试

本项目已实现完善的单元测试，覆盖AI适配器和API接口。

### 测试范围
- AI能力适配器（ai_openai.py）
  - 图片转描述
  - 描述转图片
- FastAPI接口（main.py）
  - /analyze
  - /generate
  - 参数异常、边界情况

### 如何运行

```bash
pytest
```

### 期望输出
- 所有测试用例通过，终端显示绿色"passed"。
- 如有失败，终端会显示详细错误信息，便于定位问题。

--- 