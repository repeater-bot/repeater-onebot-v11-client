### Model Command

与模型管理相关的命令

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `getModelList`             | `gml`    | `GetModelList`            | `MODEL`     | 4.3.7.4        | 获取模型列表                   | 模型类型(目前只有`chat`)                    | 获取模型列表 |
| `pingProviderHost`         | `pph`    | `PingProviderHost`        | `MODEL`     | 4.6.4.0        | Ping 供应方主机                | 无                                        | 向模型供应方主机发送 Ping 请求 |
| `refreshModels`            | `rm`     | `RefreshModels`           | `MODEL`     | 4.3.7.4        | 刷新模型列表                   | 模型供应商(可选)                           | 刷新模型列表 |