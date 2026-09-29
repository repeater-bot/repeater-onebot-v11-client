### Variable Command

将消息存入内存中的变量
注意：当服务器停机时，未存储的变量将被删除

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---        | :---           | :---                          | :---                                      | :---    |
| `setVar`                   | `sv`     | `SetVar`                  | `VARIABLE`  | 4.9.2.1        | 设置变量值                     | 格式为: 变量名=变量值                      | 设置内存中的变量值，支持富媒体 |
| `getVar`                   | `gv`     | `GetVar`                  | `VARIABLE`  | 4.9.2.1        | 获取变量值                     | 格式为: 变量名                            | 获取内存中的变量值 |
| `removeVar`                | `rv`     | `RemoveVar`               | `VARIABLE`  | 4.9.2.1        | 删除变量                       | 格式为: 变量名                            | 删除内存中的变量 |
| `loadVar`                  | `lv`     | `LoadVar`                 | `VARIABLE`  | 4.9.2.1        | 加载变量                       | 格式为: 变量名                            | 从用户配置中加载变量 |
| `dumpVar`                  | `dv`     | `DumpVar`                 | `VARIABLE`  | 4.9.2.1        | 导出变量                       | 格式为: 变量名                            | 将内存中的变量导出到用户配置中 |