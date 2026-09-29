### Chat Command

与 Repeater 进行对话

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