### Program Branch Command

对程序数据分支进行操作

| Command                    | Abridge  | Full Name                 | Type        | Joined Version | Description                   | Parameter Description                     | Remarks |
| :---                       | :---     | :---                      | :---:       | :---           | :---                          | :---                                      | :---    |
| `changeProgramBranch`      | `cpgmb`  | `ChangeProgramBranch`     | `BRANCH`    | 4.10.7.0       | 切换程序数据分支                | 分支名称                                  | 切换程序数据分支 |
| `programBranchClone`       | `pgmbc`  | `ProgramBranchClone`      | `BRANCH`    | 4.10.7.0       | 克隆程序数据分支                | 目标分支名称                               | 将当前活动分支复制到一个新的分支下 |
| `programBranchCloneFrom`   | `pgmbcf` | `ProgramBranchCloneFrom`  | `BRANCH`    | 4.10.7.0       | 从分支克隆程序数据              | 源分支名称                                 | 将指定分支复制到当前活动分支下 |
| `programBranchBind`        | `pgmbb`  | `ProgramBranchBind`       | `BRANCH`    | 4.10.7.0       | 绑定程序数据分支                | 目标分支名称                               | 创建一个新的分支，使其硬链接到当前活动分支 |
| `programBranchBindFrom`    | `pgmbbf` | `ProgramBranchBindFrom`   | `BRANCH`    | 4.10.7.0       | 从分支绑定程序数据              | 源分支名称                                 | 删除当前活动分支的内容，并作为指定分支的硬链接 |
| `programBranchInfo`        | `pgmbi`  | `ProgramBranchInfo`       | `BRANCH`    | 4.10.7.0       | 获取分支元数据信息              | 无                                        | 获取当前活动分支的元数据信息 |
| `getProgramBranchList`     | `gpgmbl` | `GetProgramBranchList`    | `BRANCH`    | 4.10.7.0       | 获取程序数据分支列表             | 无                                        | 返回当前用户的程序数据分支列表 |
| `getProgramActiveBranch`   | `gpgmba` | `GetProgramActiveBranch`  | `BRANCH`    | 4.10.7.0       | 获取当前活动程序数据分支         | 无                                        | 获取当前活动程序数据分支 |