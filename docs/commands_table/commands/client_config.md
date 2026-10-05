### Client Config Command

本程序相关的用户配置数据操作命令
请勿与 Config 命令混淆
Config 命令的作用域是 环境 + 用户
Client Config 命令的作用域是 用户

| Command                    | Abridge  | Full Name                 | Type            | Joined Version | Description               | Parameter Description                     | Remarks |
| :---                       | :---     | :--                       | :--             | :--            | :--                       | :--                                       | :--     |
| `changeBackend`            | `cb`     | `ChangeBackend`           | `CLIENT_CONFIG` | 4.7.4.0        | 更改后端                   | 后端 ID                                   | 更换用于处理请求的后端 |
| `setHelloContent`          | `shc`    | `SetHelloContent`         | `CLIENT_CONFIG` | 4.8.0.0        | 设置欢迎内容               | 欢迎内容配置                               | 设置客户端启动时的欢迎内容 |
| `chatOutput`               | `co`     | `ChatOutput`              | `CLIENT_CONFIG` | 4.9.12.0       | 修改 `CHAT` 命令的输出模式  | 三个参数，通过分隔符分隔                    | 三个参数分别表示 推理，工具，正文 三个部分的输出，可选模式：`auto`/`text`/`image`/`null`/`default`，该设置对部分固定模式的 CHAT 命令不生效 |