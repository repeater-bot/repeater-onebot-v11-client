### Statistic Command

数据统计操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `tokenCount`               | `tc`     | `TokenCount`              | `STATISTIC` | 4.6.3.0        | 获取当前用户所消耗的 Token 数   | 无                                        | 获取当前用户所消耗的 Token 数量 |
| `tokenizer`                | `tiz`    | `Tokenizer`               | `STATISTIC` | 4.8.5.0        | 计算一个字符串的 Token 数       | 待计算的字符串                             | 计算一个字符串的 Token 数，需要引用一个 `tokenizer.json` 文件 |
| `tokenizerText`            | `tizt`   | `TokenizerText`           | `STATISTIC` | 4.8.5.0        | 计算一个字符串的 Token 数       | 待计算的字符串                             | 同上，但 `Most frequent` 部分将使用文本而不是图片输出 |