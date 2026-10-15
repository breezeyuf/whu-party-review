# whu-party-review

武汉大学团队协作项目仓库。（项目简介待补充）

## 分支模型

| 分支   | 用途                             | 保护规则                       |
| ------ | -------------------------------- | ------------------------------ |
| `main` | 生产/稳定分支，随时可交付        | 仅可通过 PR 合并，需 1 人评审  |
| `dev`  | 开发集成主分支，日常开发汇合于此 | 仅可通过 PR 合并                |

## 协作流程

1. 从 `dev` 拉取功能分支：

   ```bash
   git checkout dev && git pull
   git checkout -b feature/xxx
   ```

2. 开发并提交（提交信息参考 Conventional Commits：`feat:` / `fix:` / `docs:` / `refactor:` …）
3. 推送功能分支并提 PR 合入 `dev`
4. 功能稳定后，由负责人发起 `dev → main` 的 PR 完成发布

## 快速开始

```bash
git clone https://github.com/breezeyuf/whu-party-review.git
cd whu-party-review
git checkout dev
```

## 队友须知

- 所有改动走 PR，**不要直接向 `main` / `dev` 推送**
- 提交前先 `git pull --rebase origin dev` 保持分支同步
- 遇到冲突，先沟通再解决，不要强推（force push）
