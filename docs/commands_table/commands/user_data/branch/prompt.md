### Prompt Branch Command

对提示词分支进行操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changePromptBranch`       | `cppb`   | `ChangePromptBranch`      | `BRANCH`    | 4.1.2.0        | 切换提示词分支                 | 分支名称                                   | 切换提示词分支 |
| `promptBranchClone`        | `pbc`    | `PromptBranchClone`       | `BRANCH`    | 4.3.9.1        | 克隆提示词分支                 | 目标分支名称                                | 将当前活动分支复制到一个新的分支下 |
| `promptBranchCloneFrom`    | `pbcf`   | `PromptBranchCloneFrom`   | `BRANCH`    | 4.3.9.1        | 从分支克隆提示词               | 源分支名称                                  | 将指定分支复制到当前活动分支下 |
| `promptBranchBind`         | `pbb`    | `PromptBranchBind`        | `BRANCH`    | 4.3.9.1        | 绑定提示词分支                 | 目标分支名称                                | 创建一个新的分支，使其硬链接到当前活动分支 |
| `promptBranchBindFrom`     | `pbbf`   | `PromptBranchBindFrom`    | `BRANCH`    | 4.3.9.1        | 从分支绑定提示词               | 源分支名称                                  | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `promptBranchInfo`         | `pbi`    | `PromptBranchInfo`        | `BRANCH`    | 4.3.9.1        | 获取分支元数据信息             | 无                                         | 获取当前活动分支的元数据信息 |
| `getPromptBranchList`      | `gpbl`   | `GetPromptBranchList`     | `BRANCH`    | 4.3.16.7       | 获取提示词分支列表             | 无                                         | 返回当前用户的提示词分支列表 |