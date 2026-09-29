### Mixed Branch Command

同时对所有类型的分支进行操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `deleteSession`            | `ds`     | `DeleteSession`           | `BRANCH`    | 4.2.5.0        | 删除所有用户数据                | 无                                        | 删除所有用户数据 |
| `changeSession`            | `cs`     | `ChangeSession`           | `BRANCH`    | 4.2.5.1        | 让所有的数据同时切换到一个分支   | 分支名称                                   | 让`Context`、`Prompt`、`Config`同时切换到一个分支 |
| `sessionBranchClone`       | `sbc`    | `SessionBranchClone`      | `BRANCH`    | 4.3.9.3        | 克隆所有类型分支               | 目标分支名称                                | 将所有类型的当前活动分支复制到一个新的分支下 |
| `sessionBranchCloneFrom`   | `sbcf`   | `SessionBranchCloneFrom`  | `BRANCH`    | 4.3.9.3        | 所有类型从指定分支克隆          | 源分支名称                                 | 所有类型的当前活动分支从指定分支复制 |
| `sessionBranchBind`        | `sbb`    | `SessionBranchBind`       | `BRANCH`    | 4.3.9.3        | 所有类型绑定指定分支            | 目标分支名称                               | 所有类型同时创建一个新分支，硬链接到当前活动分支 |
| `sessionBranchBindFrom`    | `sbbf`   | `SessionBranchBindFrom`   | `BRANCH`    | 4.3.9.3        | 所有类型绑定指定分支            | 源分支名称                                 | 所有类型同时删除活动分支数据，并从指定分支硬链接一份活动分支文件 |