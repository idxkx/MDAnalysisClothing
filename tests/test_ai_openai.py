import pytest
from ai_openai import OpenAIImage2Description, OpenAIDescription2Image
import io
from PIL import Image

# 用真实图片文件进行测试
TEST_IMG_PATH = "tests/test.jpg"

def test_image2description():
    ai = OpenAIImage2Description()
    with open(TEST_IMG_PATH, "rb") as f:
        img_bytes = f.read()
    result = ai.analyze(img_bytes)
    assert isinstance(result, dict)
    # 只要包含color和style字段即可
    assert "color" in result and "style" in result
    print("图片转描述AI返回：", result)

def test_description2image():
    ai = OpenAIDescription2Image()
    desc = "红色连衣裙"
    img_bytes = ai.generate(desc)
    assert isinstance(img_bytes, bytes)
    # 检查是否为图片格式
    img = Image.open(io.BytesIO(img_bytes))
    assert img.format in ["PNG", "JPEG"]
    print("描述转图片AI生成图片尺寸：", img.size) 