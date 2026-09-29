### Context Command

对上下文数据进行操作

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