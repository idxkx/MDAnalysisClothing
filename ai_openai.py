import logging
from ai_interfaces import Image2Description, Description2Image
from typing import Dict, Any, List
import os
import openai
from dotenv import load_dotenv
import requests
import base64
import imghdr
import re
from pydantic import BaseModel
import json
from datetime import datetime

logger = logging.getLogger("mdanalysis.ai")

# 加载.env中的环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("未检测到OPENAI_API_KEY，请在.env文件中配置！")
openai.api_key = OPENAI_API_KEY

class ClothingDesc(BaseModel):
    """
    服装结构化描述Pydantic模型
    """
    category_level1: str
    category_level2: str
    noun_features: List[str]
    adj_features: List[str]
    details: str
    prompt: str

class OpenAIImage2Description(Image2Description):
    """
    OpenAI图片转描述能力的真实实现。
    使用gpt-4o模型，输入图片，输出结构化服装描述。
    """
    @staticmethod
    def parse_ai_response(content: str, as_model: bool = False):
        """
        解析AI返回的内容，优先直接尝试json.loads解析。
        若失败，则去除markdown代码块（```）后重试。
        :param content: AI原始返回内容
        :param as_model: 是否转为ClothingDesc模型对象，默认False返回dict
        """
        try:
            # 先直接尝试解析
            return json.loads(content)
        except Exception:
            # 若失败，去除markdown代码块再试
            content_clean = re.sub(r"^```[a-zA-Z]*\\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
            content_clean = re.sub(r"```", "", content_clean).strip()
            idx = content_clean.find('{')
            if idx != -1:
                content_clean = content_clean[idx:]
            content_clean = content_clean.rstrip('`').strip()
            data = json.loads(content_clean)
            if as_model:
                return ClothingDesc(**data)
            return data

    @staticmethod
    def get_structured_prompt(prompt_json_path: str = 'gpt_prompt.json') -> str:
        """
        从gpt_prompt.json读取并拼接完整prompt（包含description、requirements、example_output）。
        :param prompt_json_path: prompt配置文件路径
        :return: 完整prompt字符串
        """
        with open(prompt_json_path, 'r', encoding='utf-8') as f:
            prompt_json = json.load(f)
        prompt = (
            prompt_json["description"] + "\n" +
            "\n".join([f"{i+1}. {item}" for i, item in enumerate(prompt_json["requirements"])]) +
            "\n\n请严格按照如下JSON结构输出，不要有多余解释：\n" +
            json.dumps(prompt_json["example_output"], ensure_ascii=False, indent=2)
        )
        return prompt

    @staticmethod
    def get_image_data_url(image_bytes: bytes) -> str:
        """
        将图片bytes转为data url字符串，自动识别图片格式。
        :param image_bytes: 图片字节流
        :return: data url字符串
        """
        img_type = imghdr.what(None, h=image_bytes)
        if img_type is None:
            img_type = "jpeg"  # 默认jpg
        img_b64 = base64.b64encode(image_bytes).decode()
        img_data_url = f"data:image/{img_type};base64,{img_b64}"
        return img_data_url

    def analyze(self, image_bytes: bytes) -> Dict[str, Any]:
        logger.info(f"调用OpenAI图片转描述，输入字节数={len(image_bytes)}")
        # 通过静态方法获取prompt
        prompt = self.get_structured_prompt()
        try:
            # 通过静态方法获取图片data url
            img_data_url = self.get_image_data_url(image_bytes)
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一名专业的服装分析师，特别善意描述一件服装的细节，甚至于可以通过你描述的细节通过文生图直接生成一件一模一样的衣服，输出结构化的JSON。"},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_data_url}}
                    ]}
                ],
                max_tokens=1024
            )
            # 解析返回内容
            content = response.choices[0].message.content
            logger.info(f"OpenAI图片转描述原始返回: {content}")
            result = self.parse_ai_response(content)
            logger.info(f"OpenAI图片转描述结构化结果: {result}")
            return result
        except Exception as e:
            logger.error(f"OpenAI图片转描述失败: {e}", exc_info=True)
            raise

class OpenAIDescription2Image(Description2Image):
    """
    OpenAI描述转图片能力的真实实现。
    使用dall-e-3模型，输入描述，输出图片bytes。
    """
    def generate(self, description: str) -> bytes:
        logger.info(f"调用OpenAI描述转图片，描述={description}")
        # 英文扩展提示内容
        # extra_prompt = (
        #     "1. Don't include character models, but you can drape clothes on fully transparent models to maintain their three-dimensional appearance.\n"
        #     "2. Don't include the hanger and the hand.\n"
        #     "3. The background of the clothing can be pure white, and it doesn't need to include any other colors.\n"
        #     "4. Only generate jackets or tops, not including other innerwear and pants.\n"
        #     "5. Don't make it so smooth. It should have some natural wrinkles and shine.\n"
        # )
        extra_prompt = (
            "0.必须使用 GPT-4o 模型来生成图片\n"
            "1.只生成衣服，不包含人物,保持立体效果\n"
            "2.不要包括衣架和手.\n"
            "3.无背景\n"
            "4.干净写实的风格，可以还原出现实环境和现实服装材质\n"
            # "A Ghibli-style countryside scene with a soft, hand-painted look, featuring a small cottage surrounded by lush green fields, "
            # "a warm sunset glow, and a whimsical, magical atmosphere. Soft, painterly textures with vibrant colors and a slightly dreamy feel."
        )
        full_prompt = extra_prompt + description
        logger.info(f"OpenAI用于生图的完整prompt: {full_prompt}")
        try:
            # response = openai.images.generate(
            #     model="dall-e-3",
            #     prompt=full_prompt,
            #     n=1,
            #     size="1024x1024"
            # )
            response = openai.images.generate(
                # model="gpt-image-1",
                # model="gpt-4o",
                model="dall-e-3",
                prompt=full_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            logger.info(f"OpenAI描述转图片生成图片URL: {image_url}")
            img_data = requests.get(image_url).content
            logger.info(f"OpenAI描述转图片生成成功，字节数={len(img_data)}")
            return img_data
        except Exception as e:
            logger.error(f"OpenAI描述转图片失败: {e}", exc_info=True)
            raise

    def generate_from_analysis(self, analysis: dict, output_path: str = "generated_from_analysis.png") -> bytes:
        """
        根据analyze返回的结构化内容，自动将details内的信息拼接为英文描述，调用generate生成图片，并保存到本地。
        :param analysis: analyze返回的结构化字典
        :param output_path: 图片保存路径，默认自动带时间戳
        :return: 图片bytes
        """
        details = analysis.get("details", {})
        # 拼接details内所有英文描述为一段description，格式为 key: value
        description = "\n".join([
            f"{k}: {v}" for k, v in details.items() if isinstance(v, str)
        ])
        img_bytes = self.generate(description)
        # 自动生成带时间戳的文件名（如果未自定义）
        if output_path == "generated_from_analysis.png":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 确保temp目录存在
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            output_path = os.path.join(temp_dir, f"generated_from_analysis_{timestamp}.png")
        # 保存图片到本地
        try:
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            logger.info(f"图片已保存到: {output_path}")
        except Exception as e:
            logger.error(f"图片保存失败: {e}", exc_info=True)
        return img_bytes

if __name__ == "__main__":
    import sys, json
    # 用法: python ai_openai.py analysis.json output.png
    if len(sys.argv) != 3:
        print("用法: python ai_openai.py <analyze结构化json路径> <输出图片路径>")
        sys.exit(1)
    analysis_path = sys.argv[1]
    output_path = sys.argv[2]
    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    generator = OpenAIDescription2Image()
    img_bytes = generator.generate_from_analysis(analysis)
    with open(output_path, 'wb') as f:
        f.write(img_bytes)
    print(f"图片已保存到: {output_path}") 