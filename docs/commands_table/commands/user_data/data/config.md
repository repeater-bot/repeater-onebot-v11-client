### Config Command

用户配置设置

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `setRenderStyle`           | `srs`    | `SetRenderStyle`          | `CONFIG`    | 4.0 Beta       | 设置渲染样式                   | 渲染样式名称                               | 设置Markdown图片渲染样式 |
| `setFrequencyPenalty`      | `sfp`    | `SetFrequencyPenalty`     | `CONFIG`    | 4.0 Beta       | 设置频率惩罚                   | `-2`\~`2`的浮点数<br/>或`-200%`\~`200%`的百分比 | 控制着模型输出重复相同内容的可能性 |
| `setPresencePenalty`       | `spp`    | `SetPresencePenalty`      | `CONFIG`    | 4.0 Beta       | 设置存在惩罚                   | `-2`\~`2`的浮点数<br/>或`-200%`\~`200%`的百分比 | 控制着模型谈论新主题的可能性 |
| `setTemperature`           | `st`     | `SetTemperature`          | `CONFIG`    | 4.0 Beta       | 设置温度                       | `0`\~`2`的浮点数<br/>或`0%`\~`200%`的百分比  | 控制着模型生成内容的不确定性 |
| `changeDefaultPersonality` | `cdp`    | `ChangeDefaultPersonality`| `CONFIG`    | 4.0 Beta       | 修改默认人格                   | 人格预设名称                               | 修改默认人格路由 |
| `setDefaultModel`          | `sdm`    | `SetDefaultModel`         | `CONFIG`    | 4.0 Beta       | 设置默认模型                   | 模型UID                                   | 设置默认使用的模型 |
| `setTopP`                  | `stp`    | `SetTopP`                 | `CONFIG`    | 4.0.1 Beta     | 设置Top_P参数                  | 0\~1的浮点数<br/>或`0%`\~`100%`的百分比    | 设置Top_P参数 |
| `setMaxTokens`             | `smt`    | `SetMaxTokens`            | `CONFIG`    | 4.0.1 Beta     | 设置最大生成tokens数           | 整数，通常最大可达模型上下文窗口长度的一半    | 设置最大生成tokens数 |
| `setAutoShrinkLength`      | `sasl`   | `SetAutoShrinkLength`     | `CONFIG`    | 4.2.4.0        | 设置自动缩减长度上限            | 目标消息字数                               | 如果你的聊天总字数超过该值，系统会尝试自动删除最旧的直到满足该值 |
| `setAutoLoadPrompt`        | `salp`   | `SetAutoLoadPrompt`       | `CONFIG`    | 4.3.1.0        | 设置自动加载提示词              | `true`/`false`                           | 设置请求时是否自动加载Prompt |
| `setAutoSaveContext`       | `sasc`   | `SetAutoSaveContext`      | `CONFIG`    | 4.3.1.0        | 设置自动保存上下文              | `true`/`false`                           | 设置生成完毕后是否自动保存Context |
| `setRenderTitle`           | `srt`    | `SetRenderTitle`          | `CONFIG`    | 4.3.2.1        | 设置渲染标题                   | 任意文本                                  | 渲染时显示的标题内容 |
| `setTimezone`              | `stz`    | `SetTimezone`             | `CONFIG`    | 4.3.3.3        | 设置时区                       | 时区名称(如`Asia/Shanghai`)               | 请使用确定的时区名称 |
| `writeUserProfile`         | `wup`    | `WriteUserProfile`        | `CONFIG`    | 4.3.3.6        | 写入用户人设数据                | 任意文本                                  | 该部分会被嵌入到用户提示词中，告诉AI用户的基础设定 |
| `setHtmlTemplate`          | `sht`    | `SetHtmlTemplate`         | `CONFIG`    | 4.3.3.6        | 设置HTML模板                   | 预设模板名称                              | 可以用于切换Markdown渲染时使用的HTML模板 |
| `setSaveTextOnly`          | `ssto`   | `SetSaveTextOnly`         | `CONFIG`    | 4.3.6.0        | 在保存时丢弃除文本以外的内容     | `true`/`false`                           | 设为`true`可以更快速的保存与读取，但模型将无法再获取到上下文中的附加数据 |
| `crossUserDataAccess`      | `cuda`   | `CrossUserDataAccess`     | `CONFIG`    | 4.3.10.3       | 允许跨用户数据访问              | `true`/`false`                            | 允许跨用户数据访问，如果设置为`false`则只能访问自己的数据 |
| `newRequestsTextOnly`      | `nrto`   | `NewRequestsTextOnly`     | `CONFIG`    | 4.3.10.7       | 忽略请求里的非文本数据          | `true`/`false`                            | 如果设置为`true`，复读机将把所有消息当成普通文本消息处理 |
| `setCustomName`            | `scn`    | `SetCustomName`           | `CONFIG`    | 4.3.12.1       | 设置个性化名称                 | 用户名                                     | 设置后模型看到的将是设置的名称而非用户名 |
| `thinkingMode`             | `tm`     | `ThinkingMode`            | `CONFIG`    | 4.3.14.0       | 设置思考模式                   | `true`/`false`/`null`                     | 用于在不指定 Thinking 参数时 启用/禁用/恢复默认 思考模式 |
| `setModelTimeout`          | `smto`   | `SetModelTimeout`         | `CONFIG`    | 4.3.25.0       | 设置模型超时时间               | 超时秒数                                   | 设置模型超时时间 |
| `removeReasoningPrompt`    | `rrp`    | `RemoveReasoningPrompt`   | `CONFIG`    | 4.3.26.0       | 删除推理内容                   | 删除推理内容 |                             | 设置是否在提交时移除模型输出的思考内容（不影响保存） |
| `renderDocBottomComment`   | `rdbc`   | `RenderDocBottomComment`  | `CONFIG`    | 4.4.4.0        | 渲染文档底部注释               | 文本内容                                   | 在渲染图片的底部添加一小段文本 |
| `fastStatisticsTemplate`   | `fst`    | `FastStatisticsTemplate`  | `CONFIG`    | 4.4.5.0        | 快速统计模板                   | 模板内容                                   | 可以在生成的图片结尾展示一些统计数据 |
| `setMultipleModel`         | `smm`    | `SetMultipleModel`        | `CONFIG`    | 4.4.6.0        | 设置多个模型                   | *多个模型名称*                             | 设置多个模型，当访问时随机选择一个模型 |
| `setStopKeywords`          | `ssk`    | `SetStopKeywords`         | `CONFIG`    | 4.4.6.0        | 设置停止关键词                 | *多个停止关键词*                           | 当模型生成出这个词时，暂停模型生成并即刻返回结果 |
| `getConfigs`               | `gcfg`   | `GetConfigs`              | `CONFIG`    | 4.4.8.0        | 获取配置                      | `JSON`/`YAML`                             | 获取当前会话的配置 |
| `setCustomAge`             | `sca`    | `SetCustomAge`            | `CONFIG`    | 4.4.9.0        | 设置自定义年龄                 | 年龄                                      | 设置自定义年龄 (需要提示词支持) |
| `setCustomGender`          | `scg`    | `SetCustomGender`         | `CONFIG`    | 4.4.9.0        | 设置自定义性别                 | 性别                                      | 设置自定义性别 (需要提示词支持) |
| `sendConfigFile`           | `scfgf`  | `SendConfigFile`          | `CONFIG`    | 4.5.5.0-beta   | 获取配置文件                   | 无                                        | 获取当前活动分支的配置文件 |
| `setReasoningEffort`       | `sre`    | `SetReasoningEffort`      | `CONFIG`    | 4.5.6.0        | 设置推理强度                   | `low`/`medium`/`high`/`xhigh`/`max`       | 设置推理强度 (需要模型支持) |
| `resetConfigField`         | `rcf`    | `ResetConfigField`        | `CONFIG`    | 4.5.6.0        | 重置配置字段                   | 配置字段名称                               | 设置指定配置字段到 null |
| `makeMultimodalMessage`    | `mmm`    | `MakeMultimodalMessage`   | `CONFIG`    | 4.5.8.0        | 是否创建多模态消息              | `true`/`false`                           | 设置是否创建多模态消息 |
| `allowedToolCalls`         | `atc`    | `AllowedToolCalls`        | `CONFIG`    | 4.5.8.0        | 批准使用工具                   | *\*多个工具注册名*                         | 指定 AI 能使用哪些工具 |
| `allowTools`               | `at`     | `AllowTools`              | `CONFIG`    | 4.5.8.0        | 允许使用工具                   | *\*多个工具注册名*                         | 增加工具使用权限 |
| `disallowTools`            | `dt`     | `DisallowTools`           | `CONFIG`    | 4.5.8.0        | 禁止使用工具                   | *\*多个工具注册名*                         | 移除工具使用权限 |
| `setPresetDirectives`      | `spd`    | `SetPresetDirectives`     | `CONFIG`    | 4.6.1.0        | 设置 Directive 预设           | *\*多个 Directive*                        | 添加 Directive |
| `addPresetDirectives`      | `apd`    | `AddPresetDirectives`     | `CONFIG`    | 4.6.1.0        | 添加 Directive 预设           | `<type>: <name>`                          | 添加 Directive |
| `removePresetDirectives`   | `rpd`    | `RemovePresetDirectives`  | `CONFIG`    | 4.6.1.0        | 移除 Directive 预设           | `<type>: <name>`                          | 移除 Directive |
| `setImageModel`            | `sim`    | `SetImageModel`           | `CONFIG`    | 4.8.0.0        | 设置 Image Model              | 模型名称                                  | 设置 Image Model |
| `horizontalAccessUserIDStrategy`| `hauids` | `HorizontalAccessUserIDStrategy` | `CONFIG`    | 4.9.6.0 | 设置水平访问用户 ID 策略 | `local_instance`, `separate` or `user`     | 当 Repeater 想要横向访问其他实例时，所使用的用户 ID 策略 |
| `setEmbeddingModel`        | `sem`    | `SetEmbeddingModel`       | `CONFIG`    | 4.9.7.0        | 设置 Embedding Model          | 模型名称                                  | 设置 Embedding Model |