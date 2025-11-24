# back/models.py
import httpx
from config import settings


class AIModels:
    """
    封装调用多模态 + 文生图模型的逻辑：
    - img2text: 用 Qwen3-VL-8B-Instruct 读取图片并生成英文提示词
    - pearlGen: 用 Stability SD3.5 生成 1:1 珍珠图片
    """

    @staticmethod
    async def img2text(username: str, imgurl: str):
        """
        调用 SiliconFlow 的 Qwen3-VL，读取图片中文字并生成珍珠设计描述（英文 prompt）
        :param username: 用户名（目前未使用，预留）
        :param imgurl:  后端可访问的图片 URL
        :return:        SiliconFlow 原始 JSON 响应
        """
        api_key = settings.SILICONFLOW_API_KEY
        url = settings.IMAGE2TEXT_API_URL

        payload = {
            "model": settings.IMG2TEXT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "detail": "auto",
                                "url": imgurl,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "读取图片中的文字，如果文段不完整，请根据大意补全。"
                                "理解文字中蕴含的情绪，用英文生成能够展现这一情绪的珍珠的"
                                "设计描述性文字，细节详细。"
                            ),
                        },
                    ],
                }
            ],
            "stream": False,
            "max_tokens": 4096,
            "enable_thinking": False,
            "thinking_budget": 4096,
            "min_p": 0.05,
            "stop": [],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    async def pearlGen(prompt: str) -> bytes:
        """
        调用 Stability SD3.5 文生图接口，生成 1:1 珍珠图片
        :param prompt:  英文设计描述，用于驱动模型
        :return:        图片二进制内容（JPEG）
        """
        api_key = settings.STABILITY_API_KEY
        url = settings.STABILITY_API_URL

        headers = {
            "Accept": "image/*",
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "seed": 0,
            "output_format": "jpeg",
            "model": settings.STABILITY_MODEL,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                url,
                headers=headers,
                files={"none": ""},  # 按官方要求带一个空 multipart 字段
                data=data,
            )
            resp.raise_for_status()
            return resp.content
