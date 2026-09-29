## 环境变量配置

通过环境变量来配置项目

| Name                         | Default                                                                    | Description |
|------------------------------|----------------------------------------------------------------------------|-------------|
| REPEATER_LOGGER_LEVEL        | "INFO"                                                                     | 日志等级，可选值：`TRACE`, `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |
| REPEATER_LOGGER_FORMAT       | "{time:YYYY-MM-DD HH:mm:ss.SSS} \| {level} \| {extra[module]} - {message}" | 到文件的日志格式，与控制台无关 |
| REPEATER_LOGGER_PATH         | "logs/repeater-log-{time:YYYY-MM-DD-HH-mm-ss}.log"                         | 日志文件的路径 |
| REPEATER_LOGGER_ENABLE_QUEUE | true                                                                       | 是否启用队列模式 |
| REPEATER_LOGGER_DELAY        | true                                                                       | 是否在第一条日志输出时才创建日志文件 |
| REPEATER_LOGGER_ROTATION     | "100 MB"                                                                   | 日志文件的轮换条件，可填时长、大小等数据 |
| REPEATER_LOGGER_RETENTION    | "1 month"                                                                  | 日志文件的保留条件，可填时长、大小等数据 |
| REPEATER_LOGGER_COMPRESSION  | "zip"                                                                      | 日志文件的处理方式 |
| STORAGE_BASE_PATH            | "./storage"                                                                | 存储文件的基础路径 |
| ENVIRONMENT                  | "dev"                                                                      | 该值的内容将决定了程序会进一步读取哪个环境变量文件，如`prod`就是读取`.env.prod`，`dev`就是读取`.env.dev` |
| HOST                         | "0.0.0.0"                                                                  | 主机地址 |
| PORT                         | 8080                                                                       | 端口号 |
| COMMAND_START                | ["/"]                                                                      | 用于触发命令的开始字符 |
| COMMAND_SEP                  | ["."]                                                                      | 用于触发命令的分隔符 |
| ONEBOT_ACCESS_TOKEN          | ""                                                                         | OneBot的访问令牌 |
| SUPERUSERS                   | [""]                                                                       | 超级用户列表 |