"""卡牌卡图检索命令包（/FindCards、/FC）。

放在 commands/cards/ 下，由 commands 包的 SubmoduleImporter 递归导入，
不经过 NoneBot 插件系统，因此也没有插件级的加载失败隔离：
本包内任何模块级的异常都会让 repeater_main 导入失败。

模块划分：
- constants.py 全部固定参数与相对路径（唯一改动点）
- models.py    Card 数据类与 normalize()
- aliases.py   玩家提供的译名备选写法（只参与检索）
- matching.py  精确 -> 包含 -> 模糊 三级匹配（纯 CPU）
- library.py   索引加载、卡图扫描、增卡（持锁、失败回滚）
- command.py   FindCards 命令本体
"""

from ...import_assist import SubmoduleImporter as _SubmoduleImporter

_importer = _SubmoduleImporter()
_importer.import_pkgs()
__all__ = _importer.all_list()  # type: ignore
