# api_handler.py
import os
import json
import hashlib
from datetime import datetime, timedelta
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

class APIClient:
    def __init__(self, api_key_file="api_key.json"):
        self.api_key_file = api_key_file
        self.client = None
        self.last_prompt_hash = None
        self.cached_response = None
        self.load_api_key()

    def load_api_key(self):
        try:
            if os.path.exists(self.api_key_file):
                with open(self.api_key_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'api_key' in data:
                        self.client = OpenAI(
                            api_key=data['api_key'],
                            base_url="https://api.deepseek.com/v1"
                        )
                        return data['api_key']
        except Exception as e:
            print(f"加载API密钥失败: {str(e)}")
        return None

    def save_api_key(self, api_key):
        try:
            with open(self.api_key_file, 'w', encoding='utf-8') as f:
                json.dump({'api_key': api_key}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存API密钥失败: {str(e)}")
            return False

    def update_api_key(self, new_key):
        if new_key:
            try:
                self.client = OpenAI(
                    api_key=new_key,
                    base_url="https://api.deepseek.com/v1"
                )
                test_response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": "测试"}],
                    max_tokens=5
                )
                if test_response.choices:
                    self.save_api_key(new_key)
                    return True, "API 密钥更新成功"
                else:
                    return False, "API 密钥无效"
            except Exception as e:
                return False, f"API 密钥验证失败: {str(e)}"
        return False, "API 密钥不能为空"

    def _build_prompt(self, text):
        return f"""请从以下文本中提取所有事件信息，并以严格的JSON格式输出。输出必须是有效的JSON对象，包含一个"events"数组，每个事件必须包含独立的日期、地点、时间和事项字段。

输出JSON示例：
{{
    "events": [
        {{
            "日期": "2023-10-05",
            "地点": "会议室",
            "时间": "14:00",
            "事项": "项目会议"
        }},
        {{
            "日期": "2023-10-05",
            "地点": "咖啡厅",
            "时间": "16:00",
            "事项": "客户见面"
        }}
    ]
}}

处理规则：
1. 多项活动处理：
   - 当文本中出现"然后"、"接着"、"之后"等连接词时，视为多个独立事件
   - 每个事件必须有明确的时间或顺序指示
   - 当文本出现"即日起至n月m日"则视为今天至n月m日每天都有的独立事件
   - 当文本出现"周x至周y"等星期段则视为该星期段的每一天都有的独立事件

2. 模糊时间处理：
   - "今天" = {datetime.now().strftime('%Y-%m-%d')}
   - "明天" = {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}
   - "后天" = {(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}
   - "上午" = "06:00-11:00"
   - "中午" = "11:00-13:00"
   - "下午" = "13:00-17:00"
   - "晚上" = "17:00-24:00"
   - "凌晨" = "24:00-06:00"

3. 地点处理：
   - 没有明确地点时使用"未指定"
   - 模糊地点如"会议室"保持原样

待分析文本：
{text}"""

    def analyze_text_async(self, text, callback):
        if not self.client:
            callback(False, "请先设置有效的API密钥")
            return

        current_prompt = self._build_prompt(text)
        current_hash = hashlib.md5(current_prompt.encode('utf-8')).hexdigest()
        
        if current_hash == self.last_prompt_hash and self.cached_response:
            callback(True, self.cached_response)
            return

        future = executor.submit(self._async_analyze_text, current_prompt, current_hash)
        future.add_done_callback(lambda f: self._on_analysis_complete(f, callback))

    def _async_analyze_text(self, prompt, prompt_hash):
        try:
            response = self._call_api_with_prompt(prompt)
            return (response, prompt_hash)
        except Exception as e:
            return e

    def _call_api_with_prompt(self, prompt):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的日历助手，能精确识别多项活动并以JSON格式输出结果。请确保输出是有效的JSON对象，包含'events'数组。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # 降低温度以获得更稳定的JSON输出
            max_tokens=2000,   # 增加token限制以防JSON被截断
            stream=False,
            response_format={"type": "json_object"},
        )
        try:
            # 验证返回的JSON是否有效
            json.loads(response.choices[0].message.content)
            return response.choices[0].message.content
        except json.JSONDecodeError:
            raise ValueError("API返回了无效的JSON格式")

    def _on_analysis_complete(self, future, callback):
        try:
            result = future.result()
            if isinstance(result, Exception):
                raise result
            
            response, prompt_hash = result
            self.last_prompt_hash = prompt_hash
            self.cached_response = response
            callback(True, response)
        except Exception as e:
            callback(False, f"分析失败: {str(e)}")
