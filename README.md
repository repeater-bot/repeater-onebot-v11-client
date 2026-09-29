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

## 详细文档

从[此处](./docs/index.md)开始详细了解该项目

---

## License

这个项目基于[MIT License](LICENSE)发布。

---

## 相关仓库

- [Repeater Server](https://github.com/repeater-bot/repeater-ai-chatbot)