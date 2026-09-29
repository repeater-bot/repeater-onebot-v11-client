### Control Command

调度其他命令
实现组合功能

| Command                    | Abridge  | Full Name                 | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---           | :---                          | :---                                      | :---    |
| `sleep`                    | `s`      | `Sleep`                   | 4.8.0.0        | 休眠                          | 休眠时间（秒）                              | 休眠时间必须为一个有效数字且大于 0 |
| `serial`                   | `ser`    | `Serial`                  | 4.8.0.0        | 串行执行命令                   | 每行一个命令，可嵌套                        | 每行一个命令，串行执行，支持转义字符与变量表达式 |
| `parallel`                 | `par`    | `Parallel`                | 4.8.0.0        | 并行执行命令                   | 每行一个命令，可嵌套                        | 每行一个命令，并行执行，支持转义字符与变量表达式（注意：提交 Task 是串行的，任务调度在 Async 体系下，所以并不存在真正意义上同一时间内的并行调度） |
| `waitCall`                 | `wc`     | `WaitCall`                | 4.8.0.0        | 等待用户输入消息后执行          | 格式为: 命令 参数                          | 等待一条当前会话的消息，并执行指定的命令 |
| `loop`                     | `l`      | `Loop`                    | 4.8.0.0        | 循环执行命令                   | 格式为: 循环次数 命令 参数                  | 循环次数不填时，重复执行直到命令返回 0 值结束，当循环次数前面添加 `*` 时，循环直到命令返回 0 值或到达最大次数时结束 |
| `messageWithdrawn`         | `mw`     | `MessageWithdrawn`        | 4.8.0.0        | 撤回机器人消息                 | 引用一个该机器人的消息                      | 撤回机器人发送的消息 |
| `cancel`                   | `cl`     | `Cancel`                  | 4.8.3.2        | 取消一个命令                   | 任务 ID                                   | 取消一个命令 |
| `taskList`                 | `tl`     | `TaskList`                | 4.8.3.2        | 查看当前任务列表                | 无                                       | 查看当前用户所有正在运行的 Task 实例 |
| `cascade`                  | `cas`    | `Cascade`                 | 4.8.5.0        | 级联执行命令                   | 格式为: 命令 参数                          | 每行一个命令，下一个命令执行时，会使用上一个命令的输出作为输入，最后一个直接输出，支持变量表达式 |
| `execute`                  | `e`      | `Execute`                 | 4.9.1.0        | 使用 components 调用命令        | 格式为: components 参数                   | 当只知道 components 但不知道其 trigger 时，可以使用这种方法调用 |
| `cancel_all`               | `cla`    | `CancelAll`               | 4.9.2.0        | 取消所有任务                   | component or trigger                      | 取消所有匹配的在运行任务 |
| `bypass`                   | `byp`    | `Bypass`                  | 4.9.2.0        | 后台运行任务                   | 格式为: 命令 参数                          | 后台运行任务，不堵塞主流程 |
| `silence`                  | `sil`    | `Silence`                 | 4.9.2.1        | 静默执行任务                   | 格式为: 命令 参数                          | 静默执行任务，不输出内容 |
| `timeout`                  | `t`      | `Timeout`                 | 4.9.2.1        | 设置任务超时时间               | 格式为: 时间(秒): 命令 参数                 | 设置任务超时时间，超时后任务在后台继续运行 |
| `timeoutAndCancel`         | `tac`    | `TimeoutAndCancel`        | 4.9.2.1        | 设置任务超时时间并在超时后取消  | 格式为: 时间(秒): 命令 参数                 | 设置任务超时时间，超时后自动取消任务 |
| `remoteWaitCall`           | `rwc`    | `RemoteWaitCall`          | 4.9.2.1        | 远程等待调用                   | 格式为: Namespace 命令 参数                | 跨群或私聊等待一条消息，等待目标 Namespace 提供消息后执行命令，**需要 super_permissions** |
| `equal`                    | `eq`     | `Equal`                   | 4.9.2.1        | 等于判断                       | 每行一个消息，可以添加标签                  | 所有消息在去掉收尾空格后都相等时，顺序执行 `true:` 标签，否则执行 `false:` 标签；标签必须独占一行，且允许不填，则表示空内容 |
| `flipResult`               | `fr`     | `FlipResult`              | 4.9.3.0        | 反转结果                       | 格式为：命令 参数                          | 当命令执行结果为 0 时返回 1，否则返回 0 |
| `terminate`                | `ter`    | `Terminate`               | 4.9.3.0        | 终止任务                       | 无                                        | 终止当前任务以及所在父级的整条任务树 |
| `debugMode`                | `dm`     | `DebugMode`               | 4.9.3.0        | 调试模式                       | 格式为：命令 参数                          | 启用调试模式运行一个命令 |
| `scheduling`               | `scdl`   | `Scheduling`              | 4.9.3.0        | 定时任务                       | 格式为：{cron 表达式} 命令 参数             | 创建一个定时任务，注意花括号需要保留以告知程序 cron 表达式的边界 |
| `similar`                  | `sml`    | `Similar`                 | 4.9.7.0        | 相似度判断                     | 第一行为相似度，比较第二行与第三行，并执行标签 | 当高于阈值时，执行 `similar:` 标签，否则执行 `dissimilar:` 标签 |
| `textTrigger`              | `tt`     | `TextTrigger`             | 4.9.10.2       | 文本触发器                     | 第一行为正则表达式，后面一行一个命令          | 监控自己的消息输入，当匹配正则表达式时，顺序执行后面的命令，并将 `{message}` 替换为接受到的文本 |
| `horizontalTree`           | `ht`     | `HorizontalTree`          | 4.9.10.2       | 横向调用树                     | 任务 ID (可选)                              | 输出树结构，当不输入任何参数时，逆向查找根并输出整棵调用树 |