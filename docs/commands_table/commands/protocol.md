### Protocol Command

针对目标平台的协议命令

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `poke`                     | `poke`   | `Poke`                    | `PROTOCOL`  | 4.8.3.2        | 戳一戳                        | @戳一戳的对象                              | 不填写参数时目标为自己 |
| `sendZone`                 | `sz`     | `SendZone`                | `PROTOCOL`  | 4.9.10.0       | 向 QQ 空间发送一条动态         | 要发送的内容（可包含图片）                   | 发送到机器人自己的 QQ 空间，当 `zone_sender_need_permission` 为 `true` 时，则需要用户持有 `super_permission` 权限 |