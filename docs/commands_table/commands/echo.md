### Echo Command

接受消息，并将消息原样返回
没有传递消息时，等待一条消息，并将其原样返回

| Command                    | Abridge  | Full Name                 | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---           | :---                          | :---                                      | :---    |
| `echo`                     | `echo`   | `Echo`                    | 4.0 Beta       | 重复消息                       | 要重复消息内容                             | 重复消息内容，包括特殊消息段，如果输入不跟内容，复读机会等待下一条消息 |
| `noPromptEcho`             | `npecho` | `NoPromptEcho`            | 4.3.16.0       | 无额外反应的 Echo              | 任何内容                                   | 与 `echo` 命令相同，但不在未找到参数时显示等待提示词 |
| `remoteEcho`               | `recho`  | `RemoteEcho`              | 4.9.1.0        | 远程 Echo                     | (group|private):id 要重复消息内容           | 与 echo 相同，但可以指定发送目标，**需要 super_permissions** |
| `remoteNoPromptEcho`       | `rnpecho`| `RemoteNoPromptEcho`      | 4.9.1.0        | 远程无额外反应的 Echo          | (group|private):id 任何内容                | 与 npecho 相同，但可以指定发送目标，**需要 super_permissions** |
| `removeReply`              | `rr`     | `RemoveReply`             | 4.9.1.0        | 移除回复消息                   | 消息内容                                   | 移除传入消息内容的回复消息 |