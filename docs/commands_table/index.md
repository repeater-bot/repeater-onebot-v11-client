# 命令表

通过命令来操作程序

现有命令分类：
- [Echo](./commands/echo.md)
- [Control](./commands/control.md)
- [Variable](./commands/variable.md)
- [Chat](./commands/chat.md)
- [FIM](./commands/fim.md)
- [GenImage](./commands/gen_image.md)
- [UserData](./commands/user_data/index.md)
- [Template](./commands/template.md)
- [Render](./commands/render.md)
- [ClientConfig](./commands/client_config.md)
- [Licenses](./commands/licenses.md)
- [Status](./commands/status.md)
- [Statistic](./commands/statistic.md)
- [Similarity](./commands/similarity.md)
- [SeeCmd](./commands/see_cmd.md)
- [Version](./commands/version.md)
- [Namespace](./commands/namespace.md)
- [Reserved](./commands/reserved.md)
- [SendMsg](./commands/send_msg.md)
- [Protocol](./commands/protocol.md)
- [Games](./commands/games.md)
- [Other](./commands/other.md)

PS：`CHAT` 类型命令大部分都做到了支持视觉输入
默认命令已支持全模态输入
为了速度和减少本机网络开销，复读机会直接使用 QQ 传递的临时 URL
但想要 Repeater Server 不忽略附加数据需要主动设置 `NewRequestsTextOnly` 为 `false`
或是找管理员关闭 Repeater Server 的自动拦截

`CHAT` 类型命令支持解析引用消息链
可顺着引用消息一直展开，并读取其中的文本与图片视频音频文件等内容
其中文本文件会被展开到消息内容中，图片视频音频文件会被提交到附加数据

`MIXED` 类型命令是混合型命令
它的一条命令会执行多条后端请求
通常，它会从基础功能拼接出高级功能
或是同时操作多个数据内容

`NEXUS` 系列命令操作的是当前活动分支
所以在下载前请确保你的活动分支上没有重要数据

当命令需要传入多个参数时
参数需要通过指定分隔符进行拆分
支持的分隔符为 `|`, `,`, `;`, `/`, `\n`
分割时会按照最先出现的一个分隔符开始分割
即使后面出现了其他分隔符，也会作为子字符串的一部分
而不是也当成分隔符去切割子字符串

`CONTROL` 命令下的逐行命令
我们可以这样编写参数
```
/ser
/echo
  lines2
  lines3
    lines4
/echo finished
/sleep 2.7
```
它等同于这种写法
```
/ser
/echo lines2\nlines3\n  lines4
/echo finished
/sleep 2.7
```
其中嵌套开始的第一行不变
然后所有嵌套向内收缩一格
直到嵌套结束
同时你可以在这种多行输入的命令中
使用 `{var:<varname>}` 的方式来展开一个变量

当命令涉及到发送消息时，会受到全局消息限速器的限制
它会要求命令顺序执行，且发送间隔时间不能低于设定数目
这可能会导致执行调度时一些操作的意外延后
如果有无等待的需求，请尝试使用 `/bypass` 让等待让出执行权

所有命令都有变体
多单词的命令格式有：

- `lowerCamelCase`
- `UpperCamelCase`
- `snake_case`
- `Upper_Snake_Case`
- `UPPER_CASE`
- `ia` (Initials Abridge)
- `IA` (UPPER INITIALS ABRIDGE)

而单个单词的命令有些特殊：

- `lowercase`
- `Uppercase`
- `s` (Single Character)
- `S` (UPPER SINGLE CHARACTER)
- `slabv` (Syllabic abbreviations)
- `SLABV` (UPPER SYLLABIC ABBREVIATIONS)