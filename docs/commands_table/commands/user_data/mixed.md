### Mixed Command

一个命令中存在多个操作的组合命令

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `generatePrompt`           | `genp`   | `GeneratePrompt`          | `MIXED`     | 4.3.7.5        | 生成提示词                     | 角色描述                                   | 生成提示词，并自动保存到用户提示词数据中 |
| `rewrite`                  | `rew`    | `Rewrite`                 | `MIXED`     | 4.6.6.2        | 重写                          | 自然语言文本                               | 撤回上一条并使用当前内容修改重新发送 |
| `regenerate`               | `reg`    | `Regenerate`              | `MIXED`     | 4.6.6.2        | 重新生成                       | 无                                        | 撤回上条并使用当前内容重新生成 |