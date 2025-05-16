from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ai_openai import OpenAIImage2Description, OpenAIDescription2Image
import base64
import traceback
import logging

app = FastAPI(title="MDAnalysisClothing 智能服装分析平台")

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger("mdanalysis")

# 请求体模型
# 增加Field说明，方便API文档展示
class DescriptionRequest(BaseModel):
    description: str | dict = Field(
        ..., 
        title="服装描述",
        description="可以是自然语言（如'红色连衣裙'），也可以是结构化JSON（如{'color': '红色', 'style': '连衣裙'}）"
    )

# AI适配器实例
img2desc = OpenAIImage2Description()
desc2img = OpenAIDescription2Image()

@app.post(
    "/analyze",
    summary="图片转服装描述（上传图片，返回结构化服装特征）",
    description="""
    ## 接口说明：
    上传一张服装图片，AI自动分析并返回结构化服装特征描述。

    ### 参数：
    - file: 服装图片（jpg/png，表单上传，参数名必须为file）

    ### 示例：
    - curl命令：
      ```bash
      curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@tests/test.jpg"
      ```
    - API文档界面直接上传图片

    ### 返回：
    - JSON格式，包含color（颜色）、style（款式）、material（材质）、details（细节）等字段
    - 示例：
      ```json
      {
        "color": "红色",
        "style": "连衣裙",
        "material": "棉",
        "details": "无袖，A字裙摆"
      }
      ```
    """
)
def analyze(file: UploadFile = File(..., description="服装图片文件（jpg/png）")):
    try:
        logger.info(f"收到/analyze请求: 文件名={file.filename}")
        image_bytes = file.file.read()
        result = img2desc.analyze(image_bytes)
        logger.info(f"分析结果: {result}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post(
    "/generate",
    summary="描述转服装图片（输入描述，生成服装图片）",
    description="""
    ## 接口说明：
    输入服装特征描述，AI自动生成符合描述的服装图片。

    ### 参数：
    - description: 服装描述（可以是自然语言字符串，也可以是结构化JSON）
      - 示例1：{"description": "红色连衣裙"}
      - 示例2：{"description": {"color": "红色", "style": "连衣裙"}}

    ### 返回：
    - image_base64: 生成的服装图片，base64字符串
    - 示例：
      ```json
      {
        "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
      }
      ```
    - 可用在线工具将base64转为图片查看
    """
)
def generate(req: DescriptionRequest):
    try:
        logger.info(f"收到/generate请求: 描述={req.description}")
        desc = req.description
        if isinstance(desc, dict):
            desc = ", ".join([f"{k}:{v}" for k,v in desc.items()])
        img_bytes = desc2img.generate(desc)
        logger.info(f"图片生成成功，字节数={len(img_bytes)}")
        img_b64 = base64.b64encode(img_bytes).decode()
        return {"image_base64": img_b64}
    except Exception as e:
        logger.error(f"生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@app.post(
    "/generate_from_analysis",
    summary="结构化描述转服装图片（输入analyze结构化结果，生成服装图片）",
    description="""
    ## 接口说明：
    输入 analyze 返回的结构化 JSON，AI自动生成符合描述的服装图片。

    ### 参数：
    - analysis: analyze接口返回的完整结构化JSON

    ### 返回：
    - image_base64: 生成的服装图片，base64字符串
    """
)
def generate_from_analysis(analysis: dict = Body(...)):
    try:
        logger.info(f"收到/generate_from_analysis请求: {analysis}")
        img_bytes = desc2img.generate_from_analysis(analysis)
        logger.info(f"图片生成成功，字节数={len(img_bytes)}")
        img_b64 = base64.b64encode(img_bytes).decode()
        return {"image_base64": img_b64}
    except Exception as e:
        logger.error(f"生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}") 