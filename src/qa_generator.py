import os
import json
import base64
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class QAGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not api_key or api_key == "sk-your-api-key-here":
            raise ValueError("请在 .env 文件中设置 API Key")
        
        import openai
        openai.api_key = api_key
        openai.api_base = base_url
        self.client = openai
        
        # 检测是哪家API
        if "zhipu" in base_url or "bigmodel" in base_url:
            self.api_type = "zhipu"
            print("使用智谱 GLM-4V 视觉模型")
        elif "deepseek" in base_url:
            self.api_type = "deepseek"
            print("使用 DeepSeek（文本模式，不支持视觉）")
        else:
            self.api_type = "openai"
            print(f"使用 OpenAI 兼容 API: {base_url}")
    
    def analyze_image(self, image_path: str, timestamp: str, laser_duration: float) -> Dict:
        """
        调用视觉模型分析图片
        """
        # 读取图片转base64
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = f"""这是一张学习/工作场景的截图，用户用激光笔做了标记。

标记信息：
- 时间：{timestamp}
- 标记时长：{laser_duration:.1f}秒（时间越长越重要）

请详细描述：
1. 画面内容：看到了什么？（文字、图表、代码、界面等，尽可能详细转录文字）
2. 激光标记位置：标记了哪个区域？什么内容？
3. 推测：用户为什么可能标记这里？

用中文详细描述，让用户一看就能回忆起来当时的情境。"""

        try:
            if self.api_type == "zhipu":
                # 智谱 GLM-4V 格式
                response = self.client.ChatCompletion.create(
                    model="glm-4v",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1024
                )
            elif self.api_type == "openai":
                # OpenAI GPT-4V 格式
                response = self.client.ChatCompletion.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1024
                )
            else:
                # DeepSeek 或其他不支持视觉的，返回提示
                raise Exception("该API不支持视觉模型")
            
            description = response.choices[0].message.content
            
            return {
                "ai_description": description,
                "question": f"【{timestamp}】看到上面的描述，你想起来当时为什么标记这里了吗？",
                "ai_answer": "【待你回答】",
                "confidence": "待确认",
                "tags": ["待分类"],
                "key_point": "【待你总结】"
            }
            
        except Exception as e:
            print(f"视觉API调用失败: {e}")
            # 备用：返回基础信息，让用户手动查看
            return {
                "ai_description": f"""【API不支持视觉或调用失败】
时间：{timestamp}
标记时长：{laser_duration:.1f}秒
截图已保存：{image_path}

请手动查看上方截图，然后告诉我：
1. 你看到了什么内容？
2. 激光标记了哪个位置？""",
                "question": f"【{timestamp}】看到截图后，你想起来当时为什么标记这里了吗？",
                "ai_answer": "【待你回答】",
                "confidence": "低",
                "tags": ["API失败"],
                "key_point": "【待补充】"
            }
    
    def reset_memory(self):
        pass