### Config Branch Command

对配置分支进行操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changeConfigBranch`       | `ccfgb`  | `ChangeConfigBranch`      | `BRANCH`    | 4.1.2.0        | 切换配置分支                   | 分支名称                                   | 切换配置分支 |
| `configBranchClone`        | `cfgbc`  | `ConfigBranchClone`       | `BRANCH`    | 4.3.9.1        | 克隆配置分支                   | 目标分支名称                               | 将当前活动分支复制到一个新的分支下 |
| `configBranchCloneFrom`    | `cfgbcf` | `ConfigBranchCloneFrom`   | `BRANCH`    | 4.3.9.1        | 从分支克隆配置                 | 源分支名称                                 | 将指定分支复制到当前活动分支下 |
| `configBranchBind`         | `cfgbb`  | `ConfigBranchBind`        | `BRANCH`    | 4.3.9.1        | 绑定配置分支                   | 目标分支名称                               | 创建一个新的分支，使其硬链接到当前活动分支 |
| `configBranchBindFrom`     | `cfgbbf` | `ConfigBranchBindFrom`    | `BRANCH`    | 4.3.9.1        | 从分支绑定配置                 | 源分支名称                                 | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `configBranchInfo`         | `cfgbi`  | `ConfigBranchInfo`        | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getConfigBranchList`      | `gcfgbl` | `GetConfigBranchList`     | `BRANCH`    | 4.3.16.7       | 获取当前配置分支列表           | 无                                         | 返回当前配置分支列表 |