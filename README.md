<!-- About 简介（推送后填写到仓库 About 栏）：
知产保护助手：类型判断→申请流程→维权清单 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-ip
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, ip-protection, trademark, copyright -->

# lhg-ip：知产保护助手，品牌保护一条龙

> ⚠️ **声明（首屏置顶）**：本插件是**知产保护助手**（非"专家"，弱化执业暗示），**非律师意见、仅供参考**；商标/专利审查标准与流程**以官方最新公告为准**，本插件不预测审查结果、不承诺"包过/包授权"。
>
> **一句话介绍**：给 AI 编程助手装上"知产保护助手"——商标/著作权/专利/商业秘密四象限判断 → 检索指引 → 申请流程 → 维权清单；**审查结果承诺写入即拦截，5 条确定性规则兜底**。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-ip
> /plugin install lhg-ip@lhg-plugs
> ```

## 它是什么

`lhg-ip` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **3 个命令**（小白入口）：`ip` 知产保护一条龙，`trademark` 商标专项（类别选择/驳回复审），`copyright` 著作权专项（登记流程/证据留存）
- **3 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：四象限判断框架、商标注册实务（尼斯分类三层选择法）、侵权取证与维权路径清单
- **2 个助手 agent**：知产顾问、知产材料审计员
- **1 个执业硬门 hook**：写入文件命中执业暗示/审查结果承诺（包授权/保证下证/律师意见等）直接拦截，"非律师意见"声明不被误拦，可一键关闭
- **5 条确定性审计规则**：纯 Python 标准库、零第三方依赖，含申请材料缺项、类别选择坑、时限节点、非律师意见声明检查

## 合规设计：三层防护

1. **声明置顶**：README 首屏、每个 SKILL.md 开头、每条命令输出末尾，都有显著的"非律师意见"声明。
2. **写入硬门**：hook 在文件写入前扫描执业暗示/承诺性表述关键词，命中即拦截（exit 2）；`LHG_IP_ADVICE_OFF=1` 可关闭。
3. **审计兜底**：`ip_audit.py` 的 5 条规则（3 blocker + 2 warning），`trademark`/`copyright` 命令逐条清零。

## 3 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-ip:ip` | 类型判断→检索→申请→维权一条龙 | `/lhg-ip:ip "我的咖啡品牌'山野'"` |
| `/lhg-ip:trademark` | 商标专项：类别/驳回复审 | `/lhg-ip:trademark "'山野' 咖啡"` |
| `/lhg-ip:copyright` | 著作权专项：登记/证据留存 | `/lhg-ip:copyright "一套 UI 设计稿"` |

## 目录结构

```
lhg-ip/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 3 个命令：ip / trademark / copyright
├── skills/                  # 3 个平台中立 skill（四象限/商标实务/维权清单，声明置顶）
├── agents/                  # 2 个助手 agent（ip-advisor / ip-checker）
├── hooks/                   # 执业暗示/承诺性表述拦截 hook（fail-open，可一键关闭）
├── scripts/audit/           # 确定性审计：ip_audit.py（零第三方依赖）
├── fixtures/                # 好/坏对照用例
├── smoke_test.py            # 冒烟测试
├── ATTRIBUTION.md           # 灵感来源声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用**
- 有了品牌名/产品，不知道该注册商标还是登记版权 → `ip` 跑四象限判断
- 商标类别不知道选哪几类 → `trademark` 三层选择法
- 收到商标驳回通知 → `trademark` 驳回复审决策框架
- 作品被搬运/抄袭，不知道保留哪些证据 → `copyright` + 维权清单
- 申请前想体检材料齐不齐 → 审计脚本逐条清零

**什么时候不用**
- 想要"这个商标一定能注册"的结论 → 本插件**不给**，审查结果由官方判定
- 想要代理机构"包过"服务 → 本插件不承诺，承诺包过的代理本身就不靠谱
- 涉外申请（马德里/ PCT）→ 超出本插件范围，请咨询专业代理机构
- 想伪造证据"让维权更稳" → **直接拒绝**，这是违法的

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、5 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-ip/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 组织插件矩阵（互链）

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-startup-legal](https://github.com/lhg-plugs/lhg-startup-legal) | 创业法务助手：选型→注册→股权→协议一条龙 | `/plugin install lhg-startup-legal@lhg-plugs` |
| [lhg-contract](https://github.com/lhg-plugs/lhg-contract) | 合同审查助手：风险条款标红+修改建议 | `/plugin install lhg-contract@lhg-plugs` |
| [lhg-labor-rights](https://github.com/lhg-plugs/lhg-labor-rights) | 劳动维权助手：仲裁维权一条龙 | `/plugin install lhg-labor-rights@lhg-plugs` |
| [lhg-bp](https://github.com/lhg-plugs/lhg-bp) | 商业计划书专家：九章BP→投资人自检→路演版 | `/plugin install lhg-bp@lhg-plugs` |
| [lhg-fullstack](https://github.com/lhg-plugs/lhg-fullstack) | 小白一句话 → 高质量全栈应用 | `/plugin install lhg-fullstack@lhg-plugs` |

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
