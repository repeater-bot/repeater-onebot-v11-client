### Cards Command

卡牌卡图检索。命令实现在 `repeater/plugins/repeater_main/commands/cards/` 子包，
`cmd_type` 为 `CARDS`。

> 本命令由 [watermellonkitten](https://github.com/watermellonkitten) 设计，
> 并使用 DeepSeek Harness 辅助开发。

| Command                    | Abridge  | Full Name     | Type        | Joined Version | Description            | Parameter Description                                   | Remarks |
| :---                       | :---     | :---          | :---:       | :---           | :---                    | :---                                                    | :---    |
| `FindCards`                | `FC`     | `FindCards`   | `CARDS`     | 4.10.4.0       | 按名称检索卡牌卡图        | 名称（留空则随机抽一张）                                   | 名称与卡图放在**同一条消息**里发出 |
| `FindCards -a`             | `FC -a`  | `FindCards`   | `CARDS`     | 4.10.4.0       | 添加一张卡图             | `{"zh": "中文名", "en": "English"}` + 卡图               | `-a` / `-add` / `--add` 等价；卡图可随消息发送，或 60 秒内补发 |

别名：`FindCards` / `FC` / `fc` / `findcards` / `Findcards`。
群聊触发遵循框架默认 `rule = to_me()`，即需要 @ 机器人。

#### 检索规则

1. **精确**：归一化后与中文名 / 英文名 / card_id / 别名完全相等；
2. **包含**：归一化后是某个名称的子串。只命中一个名称时在名称前加一行
   `输入未完全，但找到唯一符合规则`；命中多个名称时只列举名称、**不发图**：
   ```
   检测到多个符合条件的卡：
   · 近卫步兵第 1 团
   · 近卫步兵第 99 团
   ```
3. **模糊**：用 `assist.fuzzy.FuzzyMatch` 的 `WRatio` 取最相近的一个名称，
   低于阈值返回无结果；命中时加一行 `没有完全匹配，最相近的是：`。

归一化为 NFKC + 去掉全部空白 + casefold，因此全角/半角、空格、大小写差异都不影响命中
（`霍尔姆第99团` 与 `霍尔姆第 99 团` 等价）。

`card_names.jsonl` 里没有官方英文名的卡，玩家提供的译名作为**别名**参与检索，
回复中显示的仍是卡面名称（见 `commands/cards/aliases.py`）。

#### 同名处理

同一展示名下的多张卡（基础版 / 老兵版）会一起发出，例如 `步兵第 252 团` 返回 2 张。
同名达到 `SAME_NAME_LIMIT`（默认 3）张时：

- **群聊**：只提示数量过多、建议转到私聊，不发图；
- **私聊**：正常发出全部卡图（例如 `惩戒` 的 12 张）。

#### 增卡

```
/FC -a {"zh": "中文名", "en": "English"}
/FC -a {"zh": "中文名", "en": "English"} + 卡图
```

- 中英文至少填一个；中文引号、全角冒号/等号也能识别；
- 卡图随消息附图，或命令发出后 **60 秒内**补发一张；
- 一律转成 PNG，按 `custom_N`（最小未占用编号）落盘，名称写入索引；
- 中文名或英文名任一与已有卡牌冲突 → `已经有同名卡图了，请重新命名`；
- 没有卡图 → `你似乎需要再发送一张卡图`；
- 写索引失败会删掉刚存的图并回滚内存，不留孤儿文件。

#### 数据与依赖

数据全部相对于框架的 `STORAGE_BASE_PATH`：

```
<STORAGE_BASE_PATH>/card_names.jsonl         索引，JSONL，一行一张卡
<STORAGE_BASE_PATH>/images/<card_id>.png     卡图
```

转码依赖系统里的 `ffmpeg`（异步子进程，只在增卡时调用；`http(s)` URL 直接作为其输入，
不预先下载；已经是 PNG 的原样落盘）。找不到 `ffmpeg` 时只影响增卡，检索不受影响。
