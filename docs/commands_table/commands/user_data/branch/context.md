### Context Branch Command

对上下文分支进行操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changeContextBranch`      | `ccb`    | `ChangeContextBranch`     | `BRANCH`    | 4.1.2.0        | 切换上下文分支                 | 分支名称                                   | 切换上下文分支 |
| `contextBranchClone`       | `cbc`    | `ContextBranchClone`      | `BRANCH`    | 4.3.9.1        | 克隆上下文分支                 | 目标分支名称                               | 将当前活动分支复制到一个新的分支下 |
| `contextBranchCloneFrom`   | `cbcf`   | `ContextBranchCloneFrom`  | `BRANCH`    | 4.3.9.1        | 从分支克隆上下文               | 源分支名称                                 | 将指定分支复制到当前活动分支下 |
| `contextBranchBind`        | `cbb`    | `ContextBranchBind`       | `BRANCH`    | 4.3.9.1        | 绑定上下文分支                 | 目标分支名称                               | 创建一个新的分支，使其硬链接到当前活动分支 |
| `contextBranchBindFrom`    | `cbbf`   | `ContextBranchBindFrom`   | `BRANCH`    | 4.3.9.1        | 从分支绑定上下文               | 源分支名称                                 | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `contextBranchInfo`        | `cbi`    | `ContextBranchInfo`       | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getContextBranchsList`    | `gcbl`   | `GetContextBranchslist`   | `BRANCH`    | 4.3.16.7       | 获取上下文分支列表             | 无                                         | 返回当前用户的上下文分支列表 |