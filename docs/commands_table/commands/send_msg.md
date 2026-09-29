### Send Msg Command (Super Permissions Only)

从零构建一条消息并发送

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `sendMessage`              | `smsg`   | `SendMessage`             | `SENDMSG`   | 4.4.12.0       | 发送消息，使用结构体            | OneBot 消息结构                            | 发送一条自定义消息（需要 `allow_send_any_message` 字段为 `true`） |
| `sendMessageCQ`            | `smsgcq` | `SendMessageCQ`           | `SENDMSG`   | 4.9.1.0        | 发送消息，使用 CQ 码            | 包含 CQ 码的消息结构                       | 发送一条自定义消息（需要 `allow_send_any_message` 字段为 `true`） |
| `getCQ`                    | `gcq`    | `GetCQ`                   | `SENDMSG`   | 4.9.3.0        | 获取 CQ 码                     | 任意消息                                  | 获取当前 CQ 码 |