### Status Command

检查后端服务状态

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getCoreTaskStatus`        | `gcts`   | `GetCoreTaskStatus`       | `STATUS`    | 4.3.17.0       | 获取当前任务状态               | 无                                         | 获取当前核心任务状态 (Free or Task Stack) |
| `breakChatTask`            | `bct`    | `BreakChatTask`           | `STATUS`    | 4.4.4.0        | 中止当前所有生成任务           | 任务 ID，不填中止所有任务                    | 中止当前所有生成任务，中止后模型已生成内容将不会保存和显示 |
| `getChatBuffer`            | `gcb`    | `GetChatBuffer`           | `STATUS`    | 4.4.8.0        | 获取聊天缓冲区                 | 无                                         | 获取当前会话的聊天缓冲区 |