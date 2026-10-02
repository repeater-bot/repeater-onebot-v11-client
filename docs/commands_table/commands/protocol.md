### Protocol Command

针对目标平台的协议命令

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `poke`                     | `poke`   | `Poke`                    | `PROTOCOL`  | 4.8.3.2        | 戳一戳                        | @戳一戳的对象                              | 不填写参数时目标为自己 |
| `sendZone`                 | `sz`     | `SendZone`                | `PROTOCOL`  | 4.9.10.0       | 向 QQ 空间发送一条动态         | 要发送的内容（可包含图片）                   | 发送到机器人自己的 QQ 空间，当 `zone_sender_need_permission` 为 `true` 时，则需要用户持有 `super_permission` 权限 |
| `deleteZone`               | `dz`     | `DeleteZone`              | `PROTOCOL`  | 4.9.10.0       | 删除 QQ 空间的动态             | 动态 ID                                   | 删除 QQ 空间的动态，当 `zone_sender_need_permission` 为 `true` 时，则需要用户持有 `super_permission` 权限 |
| `filterMessages`           | `fm`     | `FilterMessages`          | `PROTOCOL`  | 4.9.11.0       | 过滤消息                       | 格式：group/user:id message_id:count regex | 从历史消息中筛选关注的消息，当消息数量为负数时则表示向反方向查询，当消息 ID 不填或为 0 时，设为最新消息，此时反向查询将不可用 |
| `filterMessagesNow`        | `fmn`    | `FilterMessagesNow`       | `PROTOCOL`  | 4.9.11.0       | 过滤当前环境的消息              | 格式：message_id:count regex               | 与上条功能一致，但环境使用当前环境 |