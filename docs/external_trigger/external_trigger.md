## External Trigger

这是一个可以直接用 HTTP 请求触发并使用对应的 Bot API 输出执行的接入口

### API

`GET /repeater/api/external_trigger/bots_list`

获取所有已注册的 Bot

`POST /repeater/api/external_trigger/call`

发送消息并指定一个 Handler 执行

#### 参数

| Parameter | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `bot_id` | str | Yes | The Bot id. |
| `handler` | str | Yes | The target Handler that needs to be executed uses a Trigger match if it starts with a slash and a component ID match if it starts without a slash. |
| `namespace` | str  | Yes | The namespace now user is using. |
| `message` | str | Yes | The cq.code message. |
| `args` | str | No | Optionally, the message data will be overwritten when args is present. |
| `message_id` | int | Yes | Message ID, which identifies the ID of the current message. |
| `font` | int | No | The font of the message. |
| `nickname` | str | No | The nickname of the user. |
| `sex` | str | No | The gender of the user. |
| `age` | int | No | The age of the user. |
| `card` | str | No | The card of the user. |
| `area` | str | No | The area of the user. |
| `level` | str | No | The level of the user. |
| `role` | str | No | The role of the user. |
| `title` | str | No | The title of the user. |
| `to_me` | bool | No | Whether the message is directed to me. |
| `sub_type` | str | No | The sub type of the message. |