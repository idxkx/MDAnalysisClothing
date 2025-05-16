from abc import ABC, abstractmethod
from typing import Dict, Any

class Image2Description(ABC):
    """
    图片转结构化服装特征描述的AI能力接口。
    所有图片识别模型（如OpenAI、CLIP、BLIP2等）都应实现本接口。
    """
    @abstractmethod
    def analyze(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        输入：图片二进制数据
        输出：结构化服装特征描述（如颜色、款式、材质等，字典格式）
        """
        pass

class Description2Image(ABC):
    """
    服装特征描述转图片的AI能力接口。
    所有图片生成模型（如OpenAI、Stable Diffusion、DALL·E等）都应实现本接口。
    """
    @abstractmethod
    def generate(self, description: str) -> bytes:
        """
        输入：服装特征描述（字符串）
        输出：生成的图片（二进制数据，jpg/png格式）
        """
        pass 