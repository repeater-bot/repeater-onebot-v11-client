# cards — 卡牌卡图检索命令

`/FindCards` 与 `/FC`。按中文名 / 英文名 / card_id / 别名检索本地卡图，
一张卡只发一条消息（名称 + 卡图），支持随机抽卡，并允许把新卡图加进卡牌库。

## 位置与加载方式

```
repeater/plugins/repeater_main/commands/cards/
├── __init__.py      SubmoduleImporter 递归导入本目录所有模块
├── command.py       FindCards（CommandPackage）
├── library.py       索引加载、卡图扫描、增卡（持锁 + 回滚）
├── matching.py      精确 → 包含 → 模糊（纯 CPU，调用方交给 to_thread）
├── models.py        Card 与 normalize()
├── aliases.py       玩家提供的备选译名（只参与检索）
└── constants.py     全部路径与阈值（唯一改动点）
```

**不是 NoneBot 插件**，而是 `repeater_main.commands` 的子包，由
`commands/__init__.py` 的 `SubmoduleImporter().import_pkgs()` 递归导入。
因此本包内任何模块级异常都会让 `repeater_main` 导入失败，
`client_configs.main_configs.loading.continue_on_error` 默认为 `False`，客户端会直接起不来。

框架能力一律走现成接口：`@CommandCaller.register` + `CommandPackage`、
`SendMsg`、`PersonaInfo.get_images_url()` / `make_message()`、
`assist.FuzzyMatch`、`storage` 的异步读写、`logger`、`CommandCaller.message_future()`。

## 命令

| 触发 | 行为 | 卡图 |
| --- | --- | --- |
| `/FC` | 从有卡图的卡牌里随机抽一张 | 1 张 |
| `/FC 霍尔姆第99团` | 精确命中 | 该名下全部 |
| `/FC 第99团` | 包含但唯一：前缀「输入未完全，但找到唯一符合规则」 | 该名下全部 |
| `/FC 近卫步兵` | 命中多个名称：`检测到多个符合条件的卡：` + 列举 | 不发图 |
| `/FC 惩戒`（群聊，≥3 张） | 提示数量过多、建议转私聊 | 不发图 |
| `/FC 惩戒`（私聊） | 名称 | 12 张 |
| `/FC -a {"zh": "…", "en": "…"}` | 加卡：随消息附图，或 60 秒内补发 | — |

- 匹配顺序：精确 → 包含 → 模糊（`FuzzyMatch.most_similar_n`，`to_thread` 内执行）。
- 归一化：NFKC + 去全部空白 + casefold，写法的全半角/空格/大小写差异都不影响命中。
- 同名按 `SAME_NAME_LIMIT`（默认 3）分档：达到阈值且是群聊时提示转私聊。
- 群聊触发遵循框架默认 `rule = to_me()`，即**需要 @ 机器人**。

## 数据

全部相对于框架的 `STORAGE_BASE_PATH`（本机 `.env` 为 `../storage`）：

```
<STORAGE_BASE_PATH>/card_names.jsonl   索引，UTF-8，一行一张卡
<STORAGE_BASE_PATH>/images/<card_id>.png   卡图
```

索引记录格式：

```json
{"card_id": "1005th_rifles", "zh": "步兵第 1005 团", "en": "1005th RIFLES"}
```

- 读：`async_json_storage.load_line_stream` 逐行解析，**单行坏掉只跳过并告警**，不拖垮整库。
- 写：`async_json_storage.save_jsonl(append = True)` 追加一行，不重写全量。
- 迁移：旧的对象式 `card_names.json` 用工作区里的
  `repeater_plugins/cards/migrate_index.py` 转成 JSONL（校验条数与逐条 zh/en 一致，旧文件保留）。

## 依赖

| 项目 | 说明 |
| --- | --- |
| Python | ≥ 3.10（`dataclass(slots=True)`、`X \| Y`） |
| 框架 | `repeater_main`（assist / cmd_info / command_register / storage / logger） |
| 第三方 Python 包 | **无**。不需要 Pillow、不需要 rapidfuzz 之外的任何东西（rapidfuzz 由框架依赖带入） |
| 外部可执行文件 | `ffmpeg`（PATH 上即可）——只在 `-a` 增卡时用来把图片转成 PNG |

`ffmpeg` 的用法是异步子进程（`asyncio.create_subprocess_exec`），不占事件循环：

- **`http(s)://` URL 直接作为 ffmpeg 输入**，不预先下载（附 `-user_agent` 与 `-rw_timeout`）；
- `base64://` / `file://` / 本地路径先取成字节再转；
- 已经是 PNG 的字节原样落盘，不启动子进程。

找不到 `ffmpeg` 时命令回「系统里找不到 ffmpeg，无法把卡图转成 PNG。」，
检索功能完全不受影响。

> 注意：ffmpeg 的 HTTP 由它自己发起，**不会**继承框架 `Downloader` 的 httpx 配置
> （连接池、SSL 上下文、代理环境变量）。如果部署环境必须走代理，
> 需要额外给 ffmpeg 传 `-http_proxy`。

## 命令分类

```python
cmd_type = CmdTypes.CARDS
```

框架现在支持 `cmd_type: str | CmdTypes`，两种都能注册。本包用枚举成员，因为
`commands/see_cmd` 下的 `/cmd_types`、`/see_cmd`、`/cmd_type` 是按 `.value` 渲染、
并按 `CmdTypes(输入)` 反查的，只有枚举成员能被它们正确显示。

代价是 `cmd_info/cmd_types.py` 里要有 `CARDS = "CARDS"` 这一行。
不想改那个文件的话，换成字符串 `"CARDS"` 也能注册（`component` 会正确拼成
`Repeater.CARDS.FindCards`），但上面三个命令会在遍历到该分组时抛 `AttributeError`。

## 命令触发词按配置渲染

`CommandPackage.cmd` 允许是 `str | tuple[str, ...]`，nonebot 的 `on_command` 原生支持
多段命令。所以所有面向用户的调用提示都经 `invoke_text()` 生成，前缀与分隔符取自
`CommandCaller.cmd_prefixs()` / `CommandCaller.delimiters()`，避免把元组的 repr 甩给用户。
`description` 也因此改成运行时生成的 `documents()`。

## 增卡的落盘策略

1. 先转 PNG（URL 直读 / 字节转换 / 已是 PNG 则原样），再按 `custom_N`（找到最小未占用编号）落盘到 `images/`；
2. 然后追加一行索引；
3. 索引写失败 → 删掉刚存的图并抛出，内存与索引都不变（`storage.remove` 同时清掉缓存）。

## 测试

工作区 `repeater_plugins/cards/` 下两个脚本，都跑在临时树里，**不碰真实 storage**：

- `boot_check.py`：真实框架启动 + 1613 条真实数据（索引复制、卡图硬链接），20 项检索断言；
- `add_check.py`：空临时库，19 项增卡断言（含真实 ffmpeg 转换、回滚、缓存清理）。

跑之前需先把 `commands/games/find_cards.py` 移出框架：
它和本包的类名 / 触发词 / component 三处相同，`ThrowOnDuplicate` 默认为真，会在注册期抛 `ValueError`。

## 来源与许可

本命令由 [watermellonkitten](https://github.com/watermellonkitten) 设计，
并使用 DeepSeek Harness 辅助开发。

- 许可证遵循本项目许可：仓库根目录 `LICENSE` —— MIT License，Copyright (c) 2025 Qeggs。

卡名与卡图数据来自 Kards 官方卡图 CDN 与 qwq.wards.mom 卡牌图鉴；
本插件只使用其中的名称与图片，不含费用、效果等游戏数据。
