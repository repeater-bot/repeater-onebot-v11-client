## ChatTTS Configs

PS：该配置文件是专门用于对接ChatTTS的
如果不需要TTS功能，该部分可以忽略

```json
{
    // ChatTTS API 地址
    "base_url": "http://127.0.0.1:9966",

    // ChatTTS API 参数
    "api_args": {

        // 模型名称
        "voice": "265.pt",

        // TTS 语速
        "speed": 6,

        // TTS 模型提示词
        "tts_prompt": "[break_6]",

        // TTS 模型温度
        "temperature": 0.2,

        // TTS 模型Top_P
        "top_p": 0.701,

        // TTS 模型Top_K
        "top_k": 20,

        // TTS 模型生成的最大优化Token数
        "refine_max_new_token": 384,

        // TTS 模型生成最大推理Token数
        "infer_max_new_token": 2048,

        // 文本种子（我不确定这里是文本修饰种子还是TTS种子，不填则随机生成）
        "text_seed": 42,

        // 是否跳过输入优化
        "skip_refine": true,

        // 是否为流式输出
        "is_stream": false,

        // 自定义语音
        "custom_voice": 0
    },
    "timeout": 300.0
}
```