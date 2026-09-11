<div align="center">

# @复读机Repeater
**- Only Chat, Focus Chat. -**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-63b9ff.svg)](https://opensource.org/licenses/MIT) [![Protocol](https://img.shields.io/badge/Protocol-Repeater%20API-brightgreen.svg)](https://github.com/repeater-bot/repeater-ai-chatbot)

</div>

---

*注：本仓库仅为客户端实现，需要配合[后端项目](#相关仓库)使用*

一个基于[`NoneBot`](https://nonebot.dev/)和[`Repeater Server`](https://github.com/repeater-bot/repeater-ai-chatbot)开发的 AI QQ Bot
**此仓库仅为 Repeater 的 NoneBot OneBot v11 适配客户端**

---

## Length Score
长度评分系统，用于判断回复是否过长，过长则自动发送图片
长度评分的参数由`main_api.json/text_length_score_config`定义，其包含以下参数：
 - `max_lines`：回复的最大行数
 - `single_line_max`：单行的最大长度
 - `mean_line_max`：平均行的最大长度
 - `total_length`：总长度
 - `threshold`：长度评分阈值，包含`group`和`private`两个参数，分别表示群聊和私聊的阈值

长度评分系统通过以下公式计算：
```python
def length_score(text: str) -> float:
    if len(text) == 0:
        length_score = 0
    else:
        lines = text.splitlines()
        length_score = (
            len(lines) / max_lines +
            (
                max(len(line) for line in lines) / single_line_max +
                sum(len(line) for line in lines) / len(lines) / mean_line_max
            ) / 2 +
            len(text) / total_length
        ) / 3
    return length_score
```
PS: 此处的长度评分函数并非实际算法，仅为演示使用
如果长度评分超过阈值，则会向后端请求将文本渲染为图片，以保证不会影响其他用户正常聊天。

---

## ENV配置

| Name                         | Default                                                                    | Description |
|------------------------------|----------------------------------------------------------------------------|-------------|
| REPEATER_LOGGER_LEVEL        | "INFO"                                                                     | 日志等级，可选值：`TRACE`, `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |
| REPEATER_LOGGER_FORMAT       | "{time:YYYY-MM-DD HH:mm:ss.SSS} \| {level} \| {extra[module]} - {message}" | 到文件的日志格式，与控制台无关 |
| REPEATER_LOGGER_PATH         | "logs/repeater-log-{time:YYYY-MM-DD-HH-mm-ss}.log"                         | 日志文件的路径 |
| REPEATER_LOGGER_ENABLE_QUEUE | true                                                                       | 是否启用队列模式 |
| REPEATER_LOGGER_DELAY        | true                                                                       | 是否在第一条日志输出时才创建日志文件 |
| REPEATER_LOGGER_ROTATION     | "100 MB"                                                                   | 日志文件的轮换条件，可填时长、大小等数据 |
| REPEATER_LOGGER_RETENTION    | "1 month"                                                                  | 日志文件的保留条件，可填时长、大小等数据 |
| REPEATER_LOGGER_COMPRESSION  | "zip"                                                                      | 日志文件的处理方式 |
| STORAGE_BASE_PATH            | "./storage"                                                                | 存储文件的基础路径 |
| ENVIRONMENT                  | "dev"                                                                      | 该值的内容将决定了程序会进一步读取哪个环境变量文件，如`prod`就是读取`.env.prod`，`dev`就是读取`.env.dev` |
| HOST                         | "0.0.0.0"                                                                  | 主机地址 |
| PORT                         | 8080                                                                       | 端口号 |
| COMMAND_START                | ["/"]                                                                      | 用于触发命令的开始字符 |
| COMMAND_SEP                  | ["."]                                                                      | 用于触发命令的分隔符 |
| ONEBOT_ACCESS_TOKEN          | ""                                                                         | OneBot的访问令牌 |
| SUPERUSERS                   | [""]                                                                       | 超级用户列表 |

---

## License
这个项目基于[MIT License](LICENSE)发布。

---

## 依赖
| Name       | Version | License      | License Text Link                                                      | Where it is used              |
|------------|---------|--------------|------------------------------------------------------------------------|-------------------------------|
| httpx      | 0.28.1  | BSD License  | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) | *Entire Project*              |
| nonebot    | 2.4.3   | MIT License  | [MIT](https://github.com/nonebot/nonebot2/blob/master/LICENSE)         | Protocol docking              |
| pydantic   | 2.12.0  | MIT License  | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE)          | *Entire Project*              |
| aiofiles   | 25.1.0  | MIT License  | [Apache-2.0](https://github.com/Tinche/aiofiles/blob/main/LICENSE)     | `storage`                     |
| pyyaml     | 6.0.3   | MIT License  | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE)                | `storage`                     |
| orjson     | 3.11.3  | Apache Software License; MIT License | [Apache-2.0](https://github.com/ijl/orjson/blob/master/LICENSE-APACHE) / [MIT](https://github.com/ijl/orjson/blob/master/LICENSE-MIT) | `storage` |
| loguru     | 0.7.3   | MIT License  | [MIT](https://github.com/Delgan/loguru/blob/master/LICENSE)            | *Entire Project*              |
| curlify2   | 2.0.0   | MIT License  | [MIT](https://github.com/marcuxyz/curlify2/blob/master/LICENSE)        | *Entire Project*              |
| numpy      | 2.4.2   | BSD 3-Clause | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt)   | *Entire Project*              |
| cachetools | 7.1.4   | MIT License  | [MIT](https://github.com/tkem/cachetools/blob/master/LICENSE)          | *Entire Project*              |
| croniter   | 6.2.2   | MIT License  | [MIT](https://github.com/pallets-eco/croniter/blob/master/LICENSE)     | Hello Content                 |
| tokenizer  | 0.23.1  | MIT License  | [MIT](https://github.com/mideind/Tokenizer/blob/master/LICENSE.txt)    | Count tokens in a string      |

具体依赖的License请查看[LICENSES.md](LICENSES.md)

---

## 配置部署
**推荐 Python3.11 ~ Python3.12 的版本安装**
> PS: 复读机可能会兼容Python3.11以前的版本
> 但我们并未对其进行过测试
> 此处3.11为开发环境版本
> 同时由于 [`PEP 594`](https://peps.python.org/pep-0594/#imghdr) 移除了一些模块
> 因此在本组件迁移之前建议不要超过 Python3.12
> PS: 其他微服务组件不受影响

在目录下执行 `setup.bat` 或 `bash setup.sh`
#### 使用脚手架(nb-cli)创建项目环境
1. 选择simple模板
2. 给项目起个名字（比如`Repeater`）
3. 建议使用FastAPI驱动器
4. **至少必须选择OneBot V11适配器**
5. 输入Yes安装默认依赖
6. 输入Yes安装虚拟环境
7. 如果需要，可以选择内置插件，如echo，*但如果没记错的话我们好像有一个echo了*
8. 在项目目录下，找到`.env`文件
9. 填写 `PORT`(数字), `ONEBOT_ACCESS_TOKEN`(字符串) 等字段配置项
10. 将复读机的NoneBot插件放入项目目录下（通常是`plugins`文件夹下）

执行`{项目名称}/.venv/pip install httpx`安装唯一依赖（此处这个大括号要去掉）
运行`run.py`启动程序

---

## 连接

### 连接OneBot
1. 找到项目目录下的`.env`文件
2. 填写PORT(数字), ONEBOT_ACCESS_TOKEN(字符串) 等字段配置项
3. 执行`run.bat`或`bash run.sh`启动程序
4. 打开OneBot客户端，选择反向WebSocket(部分客户端上称为`WebSocket 客户端`)
5. 填写 `ws_url`(字符串，通常是`ws://127.0.0.1:PORT`，其中`PORT`是你在`.env`文件中填写的端口号)，`token`(字符串，需要与上面的`ONEBOT_ACCESS_TOKEN`一致)
6. 看到NoneBot日志输出中出现`connection open`时, 表示连接成功

### 链接后端
1. 找到项目目录下的`.env`文件
2. 填写`BACKEND_BASEURL`字段配置项 (需要你和后端配置中编写的一致)
3. 执行`run.bat`或`bash run.sh`启动程序

PS: 由于OneBot客户端通常为内网服务，所以默认情况下所有服务都不需要配置公网IP访问
但你需要保证后端可以连接到你设定的API端口，OneBot客户端可以连接到指定社交平台的服务器

---

## 配置文件

main_api.json
```json
{
    // Text Length Score 配置
    "text_length_score_configs":{

        // 最大长度阈值
        "max_lines": 5,

        // 每行最大字符数
        "single_line_max": 64,

        // 平均行最大字符数
        "mean_line_max": 24,

        // 总字符数
        "total_length": 400,

        // 评分阈值
        "threshold": {

            // 群聊阈值
            "group": 1.0,

            // 私聊阈值
            "private": 2.64
        }
    },

    // 在发现到有内容重复注册时
    // 是否抛出异常
    "throw_on_duplicate": {

        // 当发现 Trigger 重复时
        // 是否抛出异常
        "trigger": true,

        // 当发现 Handler 重复时
        // 是否抛出异常
        "handler": true,

        // 当发现 Matcher 重复时
        // 是否抛出异常
        "matcher": true,

        // 当发现 Type 重复时
        // 是否抛出异常
        "type": true,

        // 当发现 Component 重复时
        // 是否抛出异常
        "component": true,

        // 当发现 Class Name 重复时
        // 是否抛出异常
        "class_name": true
    },

    // 在发现命令模块注册失败时
    // 是否静默异常到模块级别
    // 而不是中断整个模块注册
    // 比如在 Chat 模块注册失败
    // 那么该模块已经注册的部分可以正常使用
    // 而出错与剩余部分则不会生效
    "continue_on_error": true,

    // 在仅@且没有任何文本的情况下
    // 返回的消息内容
    "hello_content": {

        // 基础内容
        // 可以让欢迎内容有相同的前缀
        "content": "Repeater is Online!",
        
        // 后缀内容
        "suffixs": [
            {
                // Cron 表达式
                // 此处建议填写范围大一些
                // 否则用户可能命中不到
                // 注意：此处 Cron 不代表后缀是主动触发的，而是作为时间验证器使用
                // 系统不会在到时间时主动触发后缀
                // 而是在用户发送一条验证消息时，系统会验证该消息是否在 Cron 表达式范围内
                "cron": "* * 1 1 *",

                // 后缀内容
                "content": "\nHappy New Year!"
            }
        ]
    },

    // 是否在群聊中让所有人使用同一个上下文
    "usage_group_context": false,

    // Repeater API超时时间
    "server_api_timeout": {

        // 聊天 API 超时
        "chat": 600.0,

        "image": 2400.0,

        // 上下文操作 API 超时
        "context": 10.0,

        // 提示词操作 API 超时
        "prompt": 10.0,

        // 配置操作 API 超时
        "config": 10.0,

        // 综合数据管理 API 超时
        "data_manager": 10.0,

        // 许可证 API 超时
        "licenses": 10.0,

        // 模型信息 API 超时
        "model_info": 10.0,

        // 状态 API 超时
        "status": 10.0,

        // 版本 API 超时
        "version": 10.0,

        // 请求统计 API 超时
        "request_log": 1200.0,

        // 变量展开 API 超时
        "variable_expansion": 40.0,

        // 图片渲染 API 超时
        "render": 600.0
    },
    
    // 伪装选项，可能会有一定的反风控效果
    "camouflage": {
        // 限制发送消息的频率
        "limit_speed_per_minute": {

            // 限制消息发送的频率
            // 默认 100 次/分钟
            // 如果想关闭可以设置为 null
            "send_msg": 100,

            // 限制文件发送的频率
            // 默认 50 次/分钟
            // 如果想关闭可以设置为 null
            "file": 50,

            // 限制戳一戳发送的频率
            // 默认 6 次/分钟
            // 如果想关闭可以设置为 null
            "poke": 6
        }
    },

    // 是否使用缩写来显示分支文件大小
    "branch_file_size_use_abbreviation": true,

    // 客户端限制
    "client_limits": {

        // 最大并发连接数
        "max_connections": 1000,

        // 最大存活连接数
        "max_keepalive_connections": 20,

        // 保持连接的时间
        "keepalive_expiry": 5
    },

    // 出错时，使用 markdown 渲染错误信息
    "render_error_message": {
        // 渲染错误信息的样式
        "style": null,

        // 渲染错误信息的模板
        "html_template": null
    },

    // 总计并收缩使用的默认消息内容
    "summarize_and_contract_default_message": "System Message: please sum up all the contents above.",

    // AI 生成内容提示
    "ai_generate_tip": "This content is generated by AI, be aware of authentication.",

    // Repeater Server 地址表
    "backends": {
        "repeater": "https://repeater.example.com"
    },

    // 默认使用的 Repeater Server
    "default_backend": "repeater",

    // Client Pool 的大小
    // 数量越多，缓存出现的概率越小
    // 但会增加内存消耗
    "client_pool_size": 10,

    // Namespace 字符串序列化时 hash 的掺盐内容
    "hash_namespace_salt": "",

    // Namespace 字符串序列化时 hash 的迭代次数
    // 为 0 时则不进行 hash
    "hash_namespace_iterations": 100000,

    // 是否允许用户构造任意消息发送
    "allow_send_any_message": false,

    // 模型生成的首字超时时间
    // 当到达该时间时，模型并没有生成任何内容
    // 缓冲区是空的
    // 则认为本次请求无法开始生成
    // Client 将向 Repeater Server 申请取消任务
    // 将其设置为 null 可以忽略超时检查
    "model_first_chunk_timeout": 90.0,

    // 是否在注册时打印 Handler 名称
    // 默认为 true
    "log_registed_handler_name": true,

    // 计算模型 Token 时，Tokenizer 缓存的大小上限
    "tokenizer_cache_size": 50,

    // 在计算模型 Token 时，会显示多少个最常用的 Token
    "tokenizer_most_frequent_tokens": 5,

    // 分析引用链时
    // 最大的引用链长度
    // 超过该长度后，即使仍然符合要求也不会继续分析
    // 默认为 5
    // 设置为 null 则不限制
    "max_reply_chain_length": 5,

    // 限制读取文本文件并展开时
    // 允许读取的最大文件大小
    "max_text_file_size": null,

    // 解析消息中的文本文件时
    // 使用的编码
    "text_file_encoding": "utf-8",

    // 入口忽略配置
    "ignore_enter": {
        // 忽略指定群聊的消息
        "group_ignore_enter_set": [],

        // 忽略指定用户的消息
        "user_ignore_enter_set": [],

        // 单独取消忽略的命令
        // 需要使用 component 而非 trigger
        "unignore_enter_commands": [],

        // 是否单独开启在线检查
        "allow_online_check": true
    },

    // 权限配置设置
    // 一些特殊功能可能会需要用到 super_permissions
    // 在此处配置权限设置
    "super_permissions": [

        // 只填写 group_id 可以表示在给定群聊内所有用户在给定群聊中持有权限
        {
            "group_id": "1234567890"
        },

        // 只填写 user_id 可以表示给定用户在所有群聊与私聊中均持有权限
        {
            "user_id": "1234567890"
        },

        // 同时填写 group_id 和 user_id 可以表示该用户仅在给定群聊内持有权限
        {
            "group_id": "1234567890",
            "user_id": "1234567890"
        },

        // 都不填，自动忽略
        {

        }
    ],
    
    // 平台接口配置
    "platform_interface": {
        // 是否缓存
        "cache": true,
        
        // 接口缓存大小
        "cache_size": 1000,
    
        // 接口缓存超时时间
        "cache_timeout": 60
    },

    // 生成图片所参考的文件的解析类型
    // 支持 url / path / base64
    // 具体请参考你的 OneBot 实现选择的方式
    "generate_image_file_type": "url",

    // Ciallo~ (∠・ω< )⌒★
    // 在执行 ciallo 命令时，发送的内容
    "ciallo_content": "Ciallo~ (∠・ω< )⌒★",

    // 无用的按钮文字
    // 在里面填写字符串
    // 无用的按钮将以 1% 的概率随机选择一个
    // 排序越靠前概率越高
    "useless_button_words": [...],

    // 当按钮未命中时，返回的内容
    "useless_button_missing": "The button buzzed away.",

    // 用户 ID 行为许可名单
    "behavioral_acts": {
        "1234567890": {
            // 允许的命令类型，可为 "ALL" 或命令类型列表
            "allowed_cmd_types": [],

            // 是否阻止该用户使用 Handler
            "block_handlers": true,

            // 是否阻止机器人对该用户输出内容
            "block_output": true
        }
    },

    // 默认的用户 ID 行为许可
    "default_behavioral_act": {
        "allowed_cmd_types": "ALL"
    },
}
```
配置了一些主要的参数，如文本长度评分、推理模型使用的UID、欢迎消息等。

tts.json
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
PS：该配置文件是专门用于对接ChatTTS的
如果不需要TTS功能，该部分可以忽略

---

## 命令表

### Echo Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `echo`                     | `echo`   | `Echo`                    | `ECHO`      | 4.0 Beta       | 重复消息                       | 要重复消息内容                             | 重复消息内容，包括特殊消息段，如果输入不跟内容，复读机会等待下一条消息 |
| `noPromptEcho`             | `npecho` | `NoPromptEcho`            | `ECHO`      | 4.3.16.0       | 无额外反应的 Echo              | 任何内容                                   | 与 `echo` 命令相同，但不在未找到参数时显示等待提示词 |
| `remoteEcho`               | `recho`  | `RemoteEcho`              | `ECHO`      | 4.9.1.0        | 远程 Echo                     | (group|private):id 要重复消息内容           | 与 echo 相同，但可以指定发送目标，**需要 super_permissions** |
| `remoteNoPromptEcho`       | `rnpecho`| `RemoteNoPromptEcho`      | `ECHO`      | 4.9.1.0        | 远程无额外反应的 Echo          | (group|private):id 任何内容                | 与 npecho 相同，但可以指定发送目标，**需要 super_permissions** |
| `removeReply`              | `rr`     | `RemoveReply`             | `ECHO`      | 4.9.1.0        | 移除回复消息                   | 消息内容                                   | 移除传入消息内容的回复消息 |

### Control Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `sleep`                    | `s`      | `Sleep`                   | `CONTROL`   | 4.8.0.0        | 休眠                          | 休眠时间（秒）                              | 休眠时间必须为一个有效数字且大于 0 |
| `serial`                   | `ser`    | `Serial`                  | `CONTROL`   | 4.8.0.0        | 串行执行命令                   | 每行一个命令，可嵌套                        | 每行一个命令，串行执行，支持转义字符与变量表达式 |
| `parallel`                 | `par`    | `Parallel`                | `CONTROL`   | 4.8.0.0        | 并行执行命令                   | 每行一个命令，可嵌套                        | 每行一个命令，并行执行，支持转义字符与变量表达式（注意：提交 Task 是串行的，任务调度在 Async 体系下，所以并不存在真正意义上同一时间内的并行调度） |
| `waitCall`                 | `wc`     | `WaitCall`                | `CONTROL`   | 4.8.0.0        | 等待用户输入消息后执行          | 格式为: 命令 参数                          | 等待一条当前会话的消息，并执行指定的命令 |
| `loop`                     | `l`      | `Loop`                    | `CONTROL`   | 4.8.0.0        | 循环执行命令                   | 格式为: 循环次数 命令 参数                  | 循环次数不填时，重复执行直到命令返回 0 值结束，当循环次数前面添加 `*` 时，循环直到命令返回 0 值或到达最大次数时结束 |
| `messageWithdrawn`         | `mw`     | `MessageWithdrawn`        | `CONTROL`   | 4.8.0.0        | 撤回机器人消息                 | 引用一个该机器人的消息                      | 撤回机器人发送的消息 |
| `poke`                     | `poke`   | `Poke`                    | `CONTROL`   | 4.8.3.2        | 戳一戳                        | @戳一戳的对象                              | 不填写参数时目标为自己 |
| `cancel`                   | `cl`     | `Cancel`                  | `CONTROL`   | 4.8.3.2        | 取消一个命令                   | 任务 ID                                   | 取消一个命令 |
| `taskList`                 | `tl`     | `TaskList`                | `CONTROL`   | 4.8.3.2        | 查看当前任务列表                | 无                                       | 查看当前用户所有正在运行的 Task 实例 |
| `cascade`                  | `cas`    | `Cascade`                 | `CONTROL`   | 4.8.5.0        | 级联执行命令                   | 格式为: 命令 参数                          | 每行一个命令，下一个命令执行时，会使用上一个命令的输出作为输入，最后一个直接输出，支持变量表达式 |
| `execute`                  | `e`      | `Execute`                 | `CONTROL`   | 4.9.1.0        | 使用 components 调用命令        | 格式为: components 参数                   | 当只知道 components 但不知道其 trigger 时，可以使用这种方法调用 |
| `cancel_all`               | `cla`    | `CancelAll`               | `CONTROL`   | 4.9.2.0        | 取消所有任务                   | component or trigger                      | 取消所有匹配的在运行任务 |
| `bypass`                   | `byp`    | `Bypass`                  | `CONTROL`   | 4.9.2.0        | 后台运行任务                   | 格式为: 命令 参数                          | 后台运行任务，不堵塞主流程 |
| `silence`                  | `sil`    | `Silence`                 | `CONTROL`   | 4.9.2.1        | 静默执行任务                   | 格式为: 命令 参数                          | 静默执行任务，不输出内容 |
| `timeout`                  | `t`      | `Timeout`                 | `CONTROL`   | 4.9.2.1        | 设置任务超时时间               | 格式为: 时间(秒): 命令 参数                 | 设置任务超时时间，超时后任务在后台继续运行 |
| `timeoutAndCancel`         | `tac`    | `TimeoutAndCancel`        | `CONTROL`   | 4.9.2.1        | 设置任务超时时间并在超时后取消  | 格式为: 时间(秒): 命令 参数                 | 设置任务超时时间，超时后自动取消任务 |
| `remoteWaitCall`           | `rwc`    | `RemoteWaitCall`          | `CONTROL`   | 4.9.2.1        | 远程等待调用                   | 格式为: Namespace 命令 参数                | 跨群或私聊等待一条消息，等待目标 Namespace 提供消息后执行命令，**需要 super_permissions** |
| `equal`                    | `eq`     | `Equal`                   | `CONTROL`   | 4.9.2.1        | 等于判断                       | 每行一个消息，可以添加标签                  | 所有消息在去掉收尾空格后都相等时，顺序执行 `true:` 标签，否则执行 `false:` 标签；标签必须独占一行，且允许不填，则表示空内容 |
| `flipResult`               | `fr`     | `FlipResult`              | `CONTROL`   | 4.9.3.0        | 反转结果                       | 格式为：命令 参数                          | 当命令执行结果为 0 时返回 1，否则返回 0 |
| `terminate`                | `ter`    | `Terminate`               | `CONTROL`   | 4.9.3.0        | 终止任务                       | 无                                        | 终止当前任务以及所在父级的整条任务树 |
| `debugMode`                | `dm`     | `DebugMode`               | `CONTROL`   | 4.9.3.0        | 调试模式                       | 格式为：命令 参数                          | 启用调试模式运行一个命令 |
| `scheduling`               | `scdl`   | `Scheduling`              | `CONTROL`   | 4.9.3.0        | 定时任务                       | 格式为：{cron 表达式} 命令 参数             | 创建一个定时任务，注意花括号需要保留以告知程序 cron 表达式的边界 |
| `similar`                  | `sml`    | `Similar`                 | `CONTROL`   | 4.9.7.0        | 相似度判断                     | 第一行为相似度，比较第二行与第三行，并执行标签 | 当高于阈值时，执行 `similar:` 标签，否则执行 `dissimilar:` 标签 |

### Variable Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---        | :---           | :---                          | :---                                      | :---    |
| `setVar`                   | `sv`     | `SetVar`                  | `VARIABLE`  | 4.9.2.1        | 设置变量值                     | 格式为: 变量名=变量值                      | 设置内存中的变量值，支持富媒体 |
| `getVar`                   | `gv`     | `GetVar`                  | `VARIABLE`  | 4.9.2.1        | 获取变量值                     | 格式为: 变量名                            | 获取内存中的变量值 |
| `removeVar`                | `rv`     | `RemoveVar`               | `VARIABLE`  | 4.9.2.1        | 删除变量                       | 格式为: 变量名                            | 删除内存中的变量 |
| `loadVar`                  | `lv`     | `LoadVar`                 | `VARIABLE`  | 4.9.2.1        | 加载变量                       | 格式为: 变量名                            | 从用户配置中加载变量 |
| `dumpVar`                  | `dv`     | `DumpVar`                 | `VARIABLE`  | 4.9.2.1        | 导出变量                       | 格式为: 变量名                            | 将内存中的变量导出到用户配置中 |

### Chat Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| ` `                        | ` `      | ` `                       | `CHAT`      | 4.0 Beta       | 默认命令，自然语言对话          | 自然语言输入                               | 当@复读机的时候，如果没有命中其他命令就会执行这个 Handler |
| `chat`                     | `c`      | `Chat`                    | `CHAT`      | 4.0 Beta       | 与机器人对话                   | 自然语言输入                               | 强制模型用文字输出，绕过 Markdown 渲染检查 (工具调用与推理内容仍渲染) |
| `keepAnswering`            | `ka`     | `KeepAnswering`           | `CHAT`      | 4.0 Beta       | 持续对话(常规)                 | 无                                        | 无须输入，AI再次回复 |
| `keepReasoning`            | `kr`     | `KeepReasoning`           | `CHAT`      | 4.0 Beta       | 持续对话(推理)                 | 无                                        | 无须输入，AI再次使用推理回复 |
| `renderChat`               | `rc`     | `RenderChat`              | `CHAT`      | 4.0 Beta       | 渲染Markdown回复               | 自然语言输入                              | 强制渲染图片输出 |
| `npChat`                   | `np`     | `NoPromptChat`            | `CHAT`      | 4.0 Beta       | 不加载提示词进行对话            | 自然语言输入                              | 使用常规模型 |
| `reason`                   | `r`      | `Reason`                  | `CHAT`      | 4.0 Beta       | 使用 Thinking 模式进行推理     | 自然语言输入                               | 开启 `thinking` 参数以激活 Thinking 模式 |
| `publicSpaceChat`          | `psc`    | `PublicSpaceChat`         | `CHAT`      | 4.0.2.1 Beta   | 公共空间聊天                   | 自然语言输入                               | 公共空间聊天 |
| `reference`                | `ref`    | `Reference`               | `CHAT`      | 4.1.2.0        | 引用上下文                     | @群成员并输入自然语言                      | 引用其他用户的上下文进行生成，并将结果保存到自己的聊天记录中 |
| `raw`                      | `raw`    | `Raw`                     | `CHAT`      | 4.2.5.1        | 发送消息且不包含任何元数据      | 自然语言输入                               | 发送消息且不包含任何元数据 |
| `noSaveChat`               | `nsc`    | `NoSaveChat`              | `CHAT`      | 4.2.6.6        | 不保存的聊天对话               | 无                                        | 聊天后不保存最新聊天记录 |
| `summarizeAndContract`     | `sac`    | `SummarizeAndContract`    | `CHAT`      | 4.3.7.6        | 摘要并压缩                     | 自定义提示词，可以为空                     | 摘要并压缩对话，并自动删除多余的历史记录 |
| `noReason`                 | `nr`     | `NoReason`                | `CHAT`      | 4.3.15.0       | 不使用 Thinking 进行对话       | 自然语言输入                               | 关闭 `thinking` 参数以阻止进入 Thinking 模式 |
| `generateCandidateAnswer`  | `gca`    | `GenerateCandidateAnswer` | `CHAT`      | 4.3.18.0       | 生成候选答案                   | 无                                        | 生成候选答案（生成内容不保存） |
| `generateCandidateReason`  | `gcr`    | `GenerateCandidateReason` | `CHAT`      | 4.3.23.1       | 生成候选推理                   | 无                                        | 生成候选回答并开启推理（生成内容不保存） |
| `toGroupChat`              | `tgc`    | `ToGroupChat`             | `CHAT`      | 4.7.5.0        | 使用群聊身份进行对话            | 群号 自然语言输入                          | 使用群聊身份进行对话 |
| `toPrivateChat`            | `tpc`    | `ToPrivateChat`           | `CHAT`      | 4.7.5.0        | 使用私聊身份进行对话            | 自然语言输入                               | 使用私聊身份进行对话 |
| `smartAt`                  | `smat`   | `SmartAT`                 | `CHAT`      | 4.8.1.3        | 默认命令的命令版本              | 自然语言输入                               | 使用该命令，可以用命令的方式触发默认 Handler |
| `textChat`                 | `txc`    | `TextChat`                | `CHAT`      | 4.9.4.0        | 强制让所有内容以文本方式显示     | 自然语言输入                               | 不建议用于直接输出，可以用于其他命令的输入 |

### FIM Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---        | :---           | :---                          | :---                                      | :---    |
| `fillInMiddle`             | `fim`    | `FillInTheMiddle`         | `FIM`       | 4.6.10.0       | FIM 内容生成                   | 自然语言输入                               | 用 `[fill_this]` 或 `___` 来填充空缺内容，一次只能填写一个空位 |
| `fillAtAfter`              | `faa`    | `FillAtAfter`             | `FIM`       | 4.6.10.0       | FIM 前缀续写                   | 自然语言前缀                               | 添入一个前缀，模型会自动尝试续写内容 |

### Gen Image Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---        | :---           | :---                          | :---                                      | :---    |
| `generateImage`            | `gi`     | `GenerateImage`           | `GENIMG`    | 4.8.0.0        | 使用模型生成图片               | 提示词                                     | 使用模型生成图片内容 |
| `generateImageWithSize`    | `giz`    | `GenerateImageWithSize`   | `GENIMG`    | 4.8.4.0        | 使用模型生成图片               | 宽x高 提示词                               | 使用模型生成图片内容，并指定画幅 |

### Context Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `deleteContext`            | `dc`     | `DeleteContext`           | `CONTEXT`   | 4.0 Beta       | 删除上下文                     | 无                                        | 删除上下文 |
| `getContextTotalLength`    | `gctl`   | `GetContextTotalLength`   | `CONTEXT`   | 4.0.1 Beta     | 获取上下文总长度                | 无                                       | 获取上下文总长度 |
| `deletePublicSpaceContext` | `dpsc`   | `DeletePublicSpaceContext`| `CONTEXT`   | 4.0.2.1 Beta   | 删除公共空间上下文              | 无                                       | 删除公共空间上下文 | 
| `withdraw`                 | `w`      | `Withdraw`                | `CONTEXT`   | 4.2.3.0        | 撤回消息                       | 无                                       | 删除复读机上下文中保存的最新一回合对话 |
| `checkRoleStructure`       | `crs`    | `CheckRoleStructure`      | `CONTEXT`   | 4.3.10.10      | 检查角色结构                   | 无                                        | 检查上下文中的角色结构是否符合 user-assistant 的规则 |
| `injectUserContent`        | `iuc`    | `InjectUserContent`       | `CONTEXT`   | 4.4.7.0        | 注入用户消息内容               | 消息内容                                   | 插入用户消息内容 |
| `injectAssistantContent`   | `iac`    | `InjectAssistantContent`  | `CONTEXT`   | 4.4.7.0        | 插入 AI 消息内容               | 消息内容                                   | 插入 AI 消息内容 |
| `injectSystemContent`      | `isc`    | `InjectSystemContent`     | `CONTEXT`   | 4.4.7.0        | 插入系统消息内容               | 消息内容                                   | 插入系统消息内容 |
| `getLastContent`           | `glc`    | `GetLastContent`          | `CONTEXT`   | 4.4.8.0        | 获取最后一条消息内容           | 无                                         | 获取当前会话的最后一条消息内容 |
| `singleWithdraw`           | `sw`     | `SingleWithdraw`          | `CONTEXT`   | 4.4.13.0       | 单条撤回                      | 消息条数                                   | 直接按条撤回消息（而不是按对撤回） |
| `sendContextFile`          | `scf`    | `SendContextFile`         | `CONTEXT`   | 4.5.5.0-beta   | 发送聊天记录文件               | 无                                        | 获取当前活动分支的聊天记录文件 |

### Prompt Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `setPrompt`                | `sp`     | `SetPrompt`               | `PROMPT`    | 4.0 Beta       | 设置提示词                     | 自然语言输入                               | 设置提示词 |
| `deletePrompt`             | `dp`     | `DeletePrompt`            | `PROMPT`    | 4.0 Beta       | 删除提示词                     | 无                                        | 删除提示词 |
| `getPrompt`                | `gp`     | `GetPrompt`               | `PROMPT`    | 4.4.8.0        | 获取提示词                     | 无                                        | 获取当前会话的提示词 |
| `sendPromptFile`           | `spf`    | `SendPromptFile`          | `PROMPT`    | 4.5.5.0-beta   | 获取提示词文件                 | 无                                        | 获取当前活动分支的提示词文件 |

### Config Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `setRenderStyle`           | `srs`    | `SetRenderStyle`          | `CONFIG`    | 4.0 Beta       | 设置渲染样式                   | 渲染样式名称                               | 设置Markdown图片渲染样式 |
| `setFrequencyPenalty`      | `sfp`    | `SetFrequencyPenalty`     | `CONFIG`    | 4.0 Beta       | 设置频率惩罚                   | `-2`\~`2`的浮点数<br/>或`-200%`\~`200%`的百分比 | 控制着模型输出重复相同内容的可能性 |
| `setPresencePenalty`       | `spp`    | `SetPresencePenalty`      | `CONFIG`    | 4.0 Beta       | 设置存在惩罚                   | `-2`\~`2`的浮点数<br/>或`-200%`\~`200%`的百分比 | 控制着模型谈论新主题的可能性 |
| `setTemperature`           | `st`     | `SetTemperature`          | `CONFIG`    | 4.0 Beta       | 设置温度                       | `0`\~`2`的浮点数<br/>或`0%`\~`200%`的百分比  | 控制着模型生成内容的不确定性 |
| `changeDefaultPersonality` | `cdp`    | `ChangeDefaultPersonality`| `CONFIG`    | 4.0 Beta       | 修改默认人格                   | 人格预设名称                               | 修改默认人格路由 |
| `setDefaultModel`          | `sdm`    | `SetDefaultModel`         | `CONFIG`    | 4.0 Beta       | 设置默认模型                   | 模型UID                                   | 设置默认使用的模型 |
| `setTopP`                  | `stp`    | `SetTopP`                 | `CONFIG`    | 4.0.1 Beta     | 设置Top_P参数                  | 0\~1的浮点数<br/>或`0%`\~`100%`的百分比    | 设置Top_P参数 |
| `setMaxTokens`             | `smt`    | `SetMaxTokens`            | `CONFIG`    | 4.0.1 Beta     | 设置最大生成tokens数           | 整数，通常最大可达模型上下文窗口长度的一半    | 设置最大生成tokens数 |
| `setAutoShrinkLength`      | `sasl`   | `SetAutoShrinkLength`     | `CONFIG`    | 4.2.4.0        | 设置自动缩减长度上限            | 目标消息字数                               | 如果你的聊天总字数超过该值，系统会尝试自动删除最旧的直到满足该值 |
| `setAutoLoadPrompt`        | `salp`   | `SetAutoLoadPrompt`       | `CONFIG`    | 4.3.1.0        | 设置自动加载提示词              | `true`/`false`                           | 设置请求时是否自动加载Prompt |
| `setAutoSaveContext`       | `sasc`   | `SetAutoSaveContext`      | `CONFIG`    | 4.3.1.0        | 设置自动保存上下文              | `true`/`false`                           | 设置生成完毕后是否自动保存Context |
| `setRenderTitle`           | `srt`    | `SetRenderTitle`          | `CONFIG`    | 4.3.2.1        | 设置渲染标题                   | 任意文本                                  | 渲染时显示的标题内容 |
| `setTimezone`              | `stz`    | `SetTimezone`             | `CONFIG`    | 4.3.3.3        | 设置时区                       | 时区名称(如`Asia/Shanghai`)               | 请使用确定的时区名称 |
| `writeUserProfile`         | `wup`    | `WriteUserProfile`        | `CONFIG`    | 4.3.3.6        | 写入用户人设数据                | 任意文本                                  | 该部分会被嵌入到用户提示词中，告诉AI用户的基础设定 |
| `setHtmlTemplate`          | `sht`    | `SetHtmlTemplate`         | `CONFIG`    | 4.3.3.6        | 设置HTML模板                   | 预设模板名称                              | 可以用于切换Markdown渲染时使用的HTML模板 |
| `setSaveTextOnly`          | `ssto`   | `SetSaveTextOnly`         | `CONFIG`    | 4.3.6.0        | 在保存时丢弃除文本以外的内容     | `true`/`false`                           | 设为`true`可以更快速的保存与读取，但模型将无法再获取到上下文中的附加数据 |
| `crossUserDataAccess`      | `cuda`   | `CrossUserDataAccess`     | `CONFIG`    | 4.3.10.3       | 允许跨用户数据访问              | `true`/`false`                            | 允许跨用户数据访问，如果设置为`false`则只能访问自己的数据 |
| `newRequestsTextOnly`      | `nrto`   | `NewRequestsTextOnly`     | `CONFIG`    | 4.3.10.7       | 忽略请求里的非文本数据          | `true`/`false`                            | 如果设置为`true`，复读机将把所有消息当成普通文本消息处理 |
| `setCustomName`            | `scn`    | `SetCustomName`           | `CONFIG`    | 4.3.12.1       | 设置个性化名称                 | 用户名                                     | 设置后模型看到的将是设置的名称而非用户名 |
| `thinkingMode`             | `tm`     | `ThinkingMode`            | `CONFIG`    | 4.3.14.0       | 设置思考模式                   | `true`/`false`/`null`                     | 用于在不指定 Thinking 参数时 启用/禁用/恢复默认 思考模式 |
| `setModelTimeout`          | `smto`   | `SetModelTimeout`         | `CONFIG`    | 4.3.25.0       | 设置模型超时时间               | 超时秒数                                   | 设置模型超时时间 |
| `removeReasoningPrompt`    | `rrp`    | `RemoveReasoningPrompt`   | `CONFIG`    | 4.3.26.0       | 删除推理内容                   | 删除推理内容 |                             | 设置是否在提交时移除模型输出的思考内容（不影响保存） |
| `renderDocBottomComment`   | `rdbc`   | `RenderDocBottomComment`  | `CONFIG`    | 4.4.4.0        | 渲染文档底部注释               | 文本内容                                   | 在渲染图片的底部添加一小段文本 |
| `fastStatisticsTemplate`   | `fst`    | `FastStatisticsTemplate`  | `CONFIG`    | 4.4.5.0        | 快速统计模板                   | 模板内容                                   | 可以在生成的图片结尾展示一些统计数据 |
| `setMultipleModel`         | `smm`    | `SetMultipleModel`        | `CONFIG`    | 4.4.6.0        | 设置多个模型                   | *多个模型名称*                             | 设置多个模型，当访问时随机选择一个模型 |
| `setStopKeywords`          | `ssk`    | `SetStopKeywords`         | `CONFIG`    | 4.4.6.0        | 设置停止关键词                 | *多个停止关键词*                           | 当模型生成出这个词时，暂停模型生成并即刻返回结果 |
| `getConfigs`               | `gcfg`   | `GetConfigs`              | `CONFIG`    | 4.4.8.0        | 获取配置                      | `JSON`/`YAML`                             | 获取当前会话的配置 |
| `setCustomAge`             | `sca`    | `SetCustomAge`            | `CONFIG`    | 4.4.9.0        | 设置自定义年龄                 | 年龄                                      | 设置自定义年龄 (需要提示词支持) |
| `setCustomGender`          | `scg`    | `SetCustomGender`         | `CONFIG`    | 4.4.9.0        | 设置自定义性别                 | 性别                                      | 设置自定义性别 (需要提示词支持) |
| `sendConfigFile`           | `scfgf`  | `SendConfigFile`          | `CONFIG`    | 4.5.5.0-beta   | 获取配置文件                   | 无                                        | 获取当前活动分支的配置文件 |
| `setReasoningEffort`       | `sre`    | `SetReasoningEffort`      | `CONFIG`    | 4.5.6.0        | 设置推理强度                   | `low`/`medium`/`high`/`xhigh`/`max`       | 设置推理强度 (需要模型支持) |
| `resetConfigField`         | `rcf`    | `ResetConfigField`        | `CONFIG`    | 4.5.6.0        | 重置配置字段                   | 配置字段名称                               | 设置指定配置字段到 null |
| `makeMultimodalMessage`    | `mmm`    | `MakeMultimodalMessage`   | `CONFIG`    | 4.5.8.0        | 是否创建多模态消息              | `true`/`false`                           | 设置是否创建多模态消息 |
| `allowedToolCalls`         | `atc`    | `AllowedToolCalls`        | `CONFIG`    | 4.5.8.0        | 批准使用工具                   | *\*多个工具注册名*                         | 指定 AI 能使用哪些工具 |
| `allowTools`               | `at`     | `AllowTools`              | `CONFIG`    | 4.5.8.0        | 允许使用工具                   | *\*多个工具注册名*                         | 增加工具使用权限 |
| `disallowTools`            | `dt`     | `DisallowTools`           | `CONFIG`    | 4.5.8.0        | 禁止使用工具                   | *\*多个工具注册名*                         | 移除工具使用权限 |
| `setPresetDirectives`      | `spd`    | `SetPresetDirectives`     | `CONFIG`    | 4.6.1.0        | 设置 Directive 预设           | *\*多个 Directive*                        | 添加 Directive |
| `addPresetDirectives`      | `apd`    | `AddPresetDirectives`     | `CONFIG`    | 4.6.1.0        | 添加 Directive 预设           | `<type>: <name>`                          | 添加 Directive |
| `removePresetDirectives`   | `rpd`    | `RemovePresetDirectives`  | `CONFIG`    | 4.6.1.0        | 移除 Directive 预设           | `<type>: <name>`                          | 移除 Directive |
| `setImageModel`            | `sim`    | `SetImageModel`           | `CONFIG`    | 4.8.0.0        | 设置 Image Model              | 模型名称                                  | 设置 Image Model |
| `horizontalAccessUserIDStrategy`| `hauids` | `HorizontalAccessUserIDStrategy` | `CONFIG`    | 4.9.6.0 | 设置水平访问用户 ID 策略 | `local_instance`, `separate` or `user`     | 当 Repeater 想要横向访问其他实例时，所使用的用户 ID 策略 |
| `setEmbeddingModel`        | `sem`    | `SetEmbeddingModel`       | `CONFIG`    | 4.9.7.0        | 设置 Embedding Model          | 模型名称                                  | 设置 Embedding Model |

### Branch Command

#### Context Branch Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changeContextBranch`      | `ccb`    | `ChangeContextBranch`     | `BRANCH`    | 4.1.2.0        | 切换上下文分支                 | 分支名称                                   | 切换上下文分支 |
| `contextBranchClone`       | `cbc`    | `ContextBranchClone`      | `BRANCH`    | 4.3.9.1        | 克隆上下文分支                 | 目标分支名称                               | 将当前活动分支复制到一个新的分支下 |
| `contextBranchCloneFrom`   | `cbcf`   | `ContextBranchCloneFrom`  | `BRANCH`    | 4.3.9.1        | 从分支克隆上下文               | 源分支名称                                 | 将指定分支复制到当前活动分支下 |
| `contextBranchBind`        | `cbb`    | `ContextBranchBind`       | `BRANCH`    | 4.3.9.1        | 绑定上下文分支                 | 目标分支名称                               | 创建一个新的分支，使其硬链接到当前活动分支 |
| `contextBranchBindFrom`    | `cbbf`   | `ContextBranchBindFrom`   | `BRANCH`    | 4.3.9.1        | 从分支绑定上下文               | 源分支名称                                 | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `contextBranchInfo`        | `cbi`    | `ContextBranchInfo`       | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getContextBranchsList`    | `gcbl`   | `GetContextBranchslist`   | `BRANCH`    | 4.3.16.7       | 获取上下文分支列表             | 无                                         | 返回当前用户的上下文分支列表 |

#### Prompt Branch Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changePromptBranch`       | `cppb`   | `ChangePromptBranch`      | `BRANCH`    | 4.1.2.0        | 切换提示词分支                 | 分支名称                                   | 切换提示词分支 |
| `promptBranchClone`        | `pbc`    | `PromptBranchClone`       | `BRANCH`    | 4.3.9.1        | 克隆提示词分支                 | 目标分支名称                                | 将当前活动分支复制到一个新的分支下 |
| `promptBranchCloneFrom`    | `pbcf`   | `PromptBranchCloneFrom`   | `BRANCH`    | 4.3.9.1        | 从分支克隆提示词               | 源分支名称                                  | 将指定分支复制到当前活动分支下 |
| `promptBranchBind`         | `pbb`    | `PromptBranchBind`        | `BRANCH`    | 4.3.9.1        | 绑定提示词分支                 | 目标分支名称                                | 创建一个新的分支，使其硬链接到当前活动分支 |
| `promptBranchBindFrom`     | `pbbf`   | `PromptBranchBindFrom`    | `BRANCH`    | 4.3.9.1        | 从分支绑定提示词               | 源分支名称                                  | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `promptBranchInfo`         | `pbi`    | `PromptBranchInfo`        | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getPromptBranchList`      | `gpbl`   | `GetPromptBranchList`     | `BRANCH`    | 4.3.16.7       | 获取提示词分支列表             | 无                                         | 返回当前用户的提示词分支列表 |

#### Config Branch Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changeConfigBranch`       | `ccfgb`  | `ChangeConfigBranch`      | `BRANCH`    | 4.1.2.0        | 切换配置分支                   | 分支名称                                   | 切换配置分支 |
| `configBranchClone`        | `cfgbc`  | `ConfigBranchClone`       | `BRANCH`    | 4.3.9.1        | 克隆配置分支                   | 目标分支名称                               | 将当前活动分支复制到一个新的分支下 |
| `configBranchCloneFrom`    | `cfgbcf` | `ConfigBranchCloneFrom`   | `BRANCH`    | 4.3.9.1        | 从分支克隆配置                 | 源分支名称                                 | 将指定分支复制到当前活动分支下 |
| `configBranchBind`         | `cfgbb`  | `ConfigBranchBind`        | `BRANCH`    | 4.3.9.1        | 绑定配置分支                   | 目标分支名称                               | 创建一个新的分支，使其硬链接到当前活动分支 |
| `configBranchBindFrom`     | `cfgbbf` | `ConfigBranchBindFrom`    | `BRANCH`    | 4.3.9.1        | 从分支绑定配置                 | 源分支名称                                 | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `configBranchInfo`         | `cfgbi`  | `ConfigBranchInfo`        | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getConfigBranchList`      | `gcfgbl` | `GetConfigBranchList`     | `BRANCH`    | 4.3.16.7       | 获取当前配置分支列表           | 无                                         | 返回当前配置分支列表 |

#### Mixed Branch Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `deleteSession`            | `ds`     | `DeleteSession`           | `BRANCH`    | 4.2.5.0        | 删除所有用户数据                | 无                                        | 删除所有用户数据 |
| `changeSession`            | `cs`     | `ChangeSession`           | `BRANCH`    | 4.2.5.1        | 让所有的数据同时切换到一个分支   | 分支名称                                   | 让`Context`、`Prompt`、`Config`同时切换到一个分支 |
| `sessionBranchClone`       | `sbc`    | `SessionBranchClone`      | `BRANCH`    | 4.3.9.3        | 克隆所有类型分支               | 目标分支名称                                | 将所有类型的当前活动分支复制到一个新的分支下 |
| `sessionBranchCloneFrom`   | `sbcf`   | `SessionBranchCloneFrom`  | `BRANCH`    | 4.3.9.3        | 所有类型从指定分支克隆          | 源分支名称                                 | 所有类型的当前活动分支从指定分支复制 |
| `sessionBranchBind`        | `sbb`    | `SessionBranchBind`       | `BRANCH`    | 4.3.9.3        | 所有类型绑定指定分支            | 目标分支名称                               | 所有类型同时创建一个新分支，硬链接到当前活动分支 |
| `sessionBranchBindFrom`    | `sbbf`   | `SessionBranchBindFrom`   | `BRANCH`    | 4.3.9.3        | 所有类型绑定指定分支            | 源分支名称                                 | 所有类型同时删除活动分支数据，并从指定分支硬链接一份活动分支文件 |

#### Mixed Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `generatePrompt`           | `genp`   | `GeneratePrompt`          | `MIXED`     | 4.3.7.5        | 生成提示词                     | 角色描述                                   | 生成提示词，并自动保存到用户提示词数据中 |
| `rewrite`                  | `rew`    | `Rewrite`                 | `MIXED`     | 4.6.6.2        | 重写                          | 自然语言文本                               | 撤回上一条并使用当前内容修改重新发送 |
| `regenerate`               | `reg`    | `Regenerate`              | `MIXED`     | 4.6.6.2        | 重新生成                       | 无                                        | 撤回上条并使用当前内容重新生成 |

### User File Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `sendUserDataFile`         | `sudf`   | `SendUserDataFile`        | `USERFILE`  | 4.0.2.1 Beta   | 发送用户数据文件               | 无                                        | 发送用户数据文件 |
| `packageUserSpace`         | `pus`    | `PackageUserSpace`        | `USERFILE`  | 4.5.5.0        | 打包用户空间                   | 无                                        | 与 `sendUserDataFile` 类似，但它会打包所有分支 |

### Template Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `templateRender`           | `tr`     | `TemplateRender`          | `TEMPLATE`  | 4.0 Beta       | 变量展开                       | 文本模板                                   | 变量展开 |
| `templateRenderText`       | `trt`    | `TemplateRenderText`      | `TEMPLATE`  | 4.2.7.0        | 变量展开(文本)                 | 文本模板                                   | 强制使用文本输出 |
| `templateRenderImage`      | `tri`    | `TemplateRenderImage`     | `TEMPLATE`  | 4.2.7.0        | 变量展开(图片)                 | 文本模板                                   | 强制使用图片输出 |

### Render Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `markdownRender`           | `mr`     | `MarkdownRender`          | `RENDER`    | 4.3.7.0        | Markdown 文本渲染              | Markdown 文本                             | 将 Markdown 文本渲染为图片 |

### Model Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getModelList`             | `gml`    | `GetModelList`            | `MODEL`     | 4.3.7.4        | 获取模型列表                   | 模型类型(目前只有`chat`)                    | 获取模型列表 |
| `pingProviderHost`         | `pph`    | `PingProviderHost`        | `MODEL`     | 4.6.4.0        | Ping 供应方主机                | 无                                        | 向模型供应方主机发送 Ping 请求 |

### Nexus Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `contextUploadToNexus`     | `cutn`   | `ContextUploadToNexus`    | `NEXUS`     | 4.3.11.0       | 上传上下文到 Nexus             | 超时秒数                                   | 上传上下文到Nexus共享 |
| `contextDownloadFromNexus` | `cdfn`   | `ContextDownloadFromNexus`| `NEXUS`     | 4.3.11.0       | 从 Nexus 下载上下文            | 资源 UUID                                  | 下载Nexus共享的上下文 |
| `promptUploadToNexus`      | `putn`   | `PromptUploadToNexus`     | `NEXUS`     | 4.3.11.0       | 上传提示词到 Nexus             | 超时秒数                                   | 上传提示词到Nexus共享 |
| `promptDownloadFromNexus`  | `pgetn`  | `PromptDownloadFromNexus` | `NEXUS`     | 4.3.11.0       | 从 Nexus 下载提示词            | 资源 UUID                                  | 获取Nexus共享的提示词 |
| `configUploadToNexus`      | `cfgutn` | `ConfigUploadToNexus`     | `NEXUS`     | 4.3.11.0       | 上传配置到 Nexus               | 超时秒数                                   | 个性配置上传到Nexus |
| `configDownloadFromNexus`  | `cfgdtn` | `ConfigDownloadFromNexus` | `NEXUS`     | 4.3.11.0       | 从 Nexus 下载配置              | 资源 UUID                                  | 从Nexus下载共享的个性配置 |
| `envUploadToNexus`         | `eutn`   | `EnvUploadToNexus`        | `NEXUS`     | 4.3.19.0       | 上传环境到 Nexus               | 超时秒数                                   | 同时上传所有用户数据到Nexus |
| `envDownloadFromNexus`     | `edfn`   | `EnvDownloadFromNexus`    | `NEXUS`     | 4.3.19.0       | 从 Nexus 下载环境              | 资源 UUID                                  | 从 Nexus 同时下载所有用户数据 |

### Client Config Command

| Command                    | Abridge  | Full Name                 | Type            | Joined Version | Description               | Parameter Description                     | Remarks |
| :---                       | :---     | :--                       | :--             | :--            | :--                       | :--                                       | :--     |
| `changeBackend`            | `cb`     | `ChangeBackend`           | `CLIENT_CONFIG` | 4.7.4.0        | 更改后端                   | 后端 ID                                   | 更换用于处理请求的后端 |
| `setHelloContent`          | `shc`    | `SetHelloContent`         | `CLIENT_CONFIG` | 4.8.0.0        | 设置欢迎内容               | 欢迎内容配置                               | 设置客户端启动时的欢迎内容 |

### Licenses Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getRequirementLicenses`   | `grl`    | `GetRequirementLicenses`  | `LICENSES`  | 4.3.10.8       | 获取依赖许可证                 | 依赖项名称                                 | 获取指定依赖的许可证信息 |
| `getRequirementList`       | `grls`   | `GetRequirementList`      | `LICENSES`  | 4.3.10.8       | 获取依赖列表                   | 无                                        | 获取所有记录了License的依赖项名称 |
| `getServerLicense`         | `gsl`    | `GetServerLicense`        | `LICENSES`  | 4.3.10.8       | 获取服务端许可证               | 无                                         | 获取服务端许可证信息 |

### Status Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getCoreTaskStatus`        | `gcts`   | `GetCoreTaskStatus`       | `STATUS`    | 4.3.17.0       | 获取当前任务状态               | 无                                         | 获取当前核心任务状态 (Free or Task Stack) |
| `breakChatTask`            | `bct`    | `BreakChatTask`           | `STATUS`    | 4.4.4.0        | 中止当前所有生成任务           | 任务 ID，不填中止所有任务                    | 中止当前所有生成任务，中止后模型已生成内容将不会保存和显示 |
| `getChatBuffer`            | `gcb`    | `GetChatBuffer`           | `STATUS`    | 4.4.8.0        | 获取聊天缓冲区                 | 无                                         | 获取当前会话的聊天缓冲区 |

### Statistic Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `tokenCount`               | `tc`     | `TokenCount`              | `STATISTIC` | 4.6.3.0        | 获取当前用户所消耗的 Token 数   | 无                                        | 获取当前用户所消耗的 Token 数量 |
| `tokenizer`                | `tiz`    | `Tokenizer`               | `STATISTIC` | 4.8.5.0        | 计算一个字符串的 Token 数       | 待计算的字符串                             | 计算一个字符串的 Token 数，需要引用一个 `tokenizer.json` 文件 |
| `tokenizerText`            | `tizt`   | `TokenizerText`           | `STATISTIC` | 4.8.5.0        | 计算一个字符串的 Token 数       | 待计算的字符串                             | 同上，但 `Most frequent` 部分将使用文本而不是图片输出 |

### Similarity Command

| Command                    | Abridge  | Full Name                 | Type         | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:        | :---           | :---                          | :---                                      | :---    |
| `similarity`               | `smrt`   | `Similarity`              | `SIMILARITY` | 4.7.5.0        | 获取相似度                     | `first_text` and `second_text` 包裹的文本  | 获取两段文本的相似度 |

### See Cmd Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `seeCmd`                   | `sc`     | `SeeCmd`                  | `SEE_CMD`   | 4.6.4.0        | 显示命令详细信息               | 命令名称                                   | 显示指定命令的详细帮助信息 |
| `cmdTypesList`             | `ctl`    | `CmdTypesList`            | `SEE_CMD`   | 4.6.4.0        | 列出命令类型                   | 无                                        | 列出所有命令类型 |
| `cmdType`                  | `ct`     | `CmdType`                 | `SEE_CMD`   | 4.6.5.0        | 列出命令类型下的所有命令        | 命令类型                                   | 列出命令类型下的所有命令 |
| `help`                     | `h`      | `Help`                    | `SEE_CMD`   | 4.9.1.0        | 显示帮助信息                   | 无                                        | 提供兼容生态习惯的入口，引导用户学习内容 |
| `seeComponents`            | `scmp`   | `SeeComponents`           | `SEE_CMD`   | 4.9.1.0        | 通过 component 显式命令详细信息 | 命令 component                            | 显示指定 component 的详细帮助信息 |
| `registedInfoTable`        | `rit`    | `RegistedInfoTable`       | `SEE_CMD`   | 4.9.2.1        | 显示注册信息表                 | 无                                        | 显示命令注册信息表 |

### Version Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `adaptationInfo`           | `adai`   | `AdaptationInfo`          | `VERSION`   | 4.3.10.7       | 版本适配信息                   | 无                                        | 展示服务端和客户端的版本信息 |

### Namespace Command
| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getNamespace`             | `gns`    | `GetNamespace`            | `NAMESPACE` | 4.2.4.4        | 获取命名空间                   | @目标用户 (不填就是自己)                    | 获取当前或指定用户的命名空间 |

### Reserved Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `#` or `/`                 | `anot`   | `Annotation`              | `RESERVED`  | 4.3.9.3        | 注释，不会执行任何操作          | 无                                        | 不执行任何操作，直接忽略内容，由于命令前缀的存在，触发需要 `/#` 或 `//` |

### Send Msg Command (Super Permissions Only)

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `sendMessage`              | `smsg`   | `SendMessage`             | `SENDMSG`   | 4.4.12.0       | 发送消息，使用结构体            | OneBot 消息结构                            | 发送一条自定义消息（需要 `allow_send_any_message` 字段为 `true`） |
| `sendMessageCQ`            | `smsgcq` | `SendMessageCQ`           | `SENDMSG`   | 4.9.1.0        | 发送消息，使用 CQ 码            | 包含 CQ 码的消息结构                       | 发送一条自定义消息（需要 `allow_send_any_message` 字段为 `true`） |
| `getCQ`                    | `gcq`    | `GetCQ`                   | `SENDMSG`   | 4.9.3.0        | 获取 CQ 码                     | 任意消息                                  | 获取当前 CQ 码 |

### Games Command

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `ciallo`                   | `ciallo` | `Ciallo`                  | `GAMES`     | 4.6.4.0        | Ciallo~(∠・ω< )⌒★           | 无                                        | 输出 `ciallo_content` 里的内容 |
| `randomFortune`            | `rf`     | `RandomFortune`           | `GAMES`     | 4.6.4.0        | 随机运势                       | @指定用户（可选）                          | 根据用户与时间生成每日固定的随机数 |
| `uselessButton`            | `ub`     | `UselessButton`           | `GAMES`     | 4.6.4.0        | 随机按钮                       | 次数（可选）                               | 多按几次或许会有意外收获 |
| `word`                     | `word`   | `Word`                    | `GAMES`     | 4.8.5.0        | 获取一句话，或是修改它          | 填充内容                                   | 如果有传入参数，则使用传入的内容覆盖之前的内容，否则返回上一次填充的内容 |

### Other Command
| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `chooseGroupMember`        | `cgm`    | `ChooseGroupMember`       | `OTHER`     | 4.1.2.0        | 抽取群组成员                   | 抽取数量                                   | 抽取群组成员 |
| `recentSpeakingRanking`    | `rsr`    | `RecentSpeakingRanking`   | `OTHER`     | 4.2.3.0        | 最近发言排行                   | 无                                        | 获取群组内最近发言的成员列表 |
| `summaryChatRecord`        | `scr`    | `SummaryChatRecord`       | `OTHER`     | 4.2.6.6        | 聊天记录总结                   | 整数，传入的消息数量                        | 获取当前群聊内指定数量的聊天记录摘要 |
| `calculateLengthScore`     | `cls`    | `CalculateLengthScore`    | `OTHER`     | 4.4.4.0        | 计算长度评分                   | 文本内容                                   | 计算给定文本的长度评分值 |
| `historyCharStatistics`    | `hcs`    | `HistoryCharStatistics`   | `OTHER`     | 4.8.3.2        | 聊天信息字符统计               | 消息数量，显示的排名数量                     | 获取当前群聊内指定数量的聊天记录字符统计 |

PS：`CHAT` 类型命令大部分都做到了支持视觉输入
默认命令已支持全模态输入
为了速度和减少本机网络开销，复读机会直接使用 QQ 传递的临时 URL
但想要 Repeater Server 不忽略附加数据需要主动设置 `NewRequestsTextOnly` 为 `false`
或是找管理员关闭 Repeater Server 的自动拦截

`CHAT` 类型命令支持解析引用消息链
可顺着引用消息一直展开，并读取其中的文本与图片视频音频文件等内容
其中文本文件会被展开到消息内容中，图片视频音频文件会被提交到附加数据

`MIXED` 类型命令是混合型命令
它的一条命令会执行多条后端请求
通常，它会从基础功能拼接出高级功能
或是同时操作多个数据内容

`NEXUS` 系列命令操作的是当前活动分支
所以在下载前请确保你的活动分支上没有重要数据

当命令需要传入多个参数时
参数需要通过指定分隔符进行拆分
支持的分隔符为 `|`, `,`, `;`, `/`, `\n`
分割时会按照最先出现的一个分隔符开始分割
即使后面出现了其他分隔符，也会作为子字符串的一部分
而不是也当成分隔符去切割子字符串

`CONTROL` 命令下的逐行命令
我们可以这样编写参数
```
/ser
/echo
  lines2
  lines3
    lines4
/echo finished
/sleep 2.7
```
它等同于这种写法
```
/ser
/echo lines2\nlines3\n  lines4
/echo finished
/sleep 2.7
```
其中嵌套开始的第一行不变
然后所有嵌套向内收缩一格
直到嵌套结束
同时你可以在这种多行输入的命令中
使用 `{var:<varname>}` 的方式来展开一个变量

当命令涉及到发送消息时，会受到全局消息限速器的限制
它会要求命令顺序执行，且发送间隔时间不能低于设定数目
这可能会导致执行调度时一些操作的意外延后
如果有无等待的需求，请尝试使用 `/bypass` 让等待让出执行权

所有命令都有变体
多单词的命令格式有：

- `lowerCamelCase`
- `UpperCamelCase`
- `snake_case`
- `Upper_Snake_Case`
- `UPPER_CASE`
- `ia` (Initials Abridge)
- `IA` (UPPER INITIALS ABRIDGE)

而单个单词的命令有些特殊：

- `lowercase`
- `Uppercase`
- `s` (Single Character)
- `S` (UPPER SINGLE CHARACTER)
- `slabv` (Syllabic abbreviations)
- `SLABV` (UPPER SYLLABIC ABBREVIATIONS)

---

## 相关仓库
- [Repeater Server](https://github.com/repeater-bot/repeater-ai-chatbot)