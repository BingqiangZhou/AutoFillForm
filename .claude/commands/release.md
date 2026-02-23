---
name: /release
description: 发布新版本 - 生成CHANGELOG、更新版本号、创建tag并推送
usage: /release <version>
example: /release 5.1.0
---

# Release Workflow Command

当收到 `/release <版本号>` 命令时，按以下步骤自动执行发布流程：

## 步骤1: 生成 CHANGELOG
使用 `git-cliff --tag v<版本号> -o CHANGELOG.md` 生成 CHANGELOG.md

## 步骤1.5: 更新 README.md
使用 Edit 工具直接更新 README.md 中的版本信息和日期：
1. 更新版本号徽章
2. 更新版本历史部分，添加新版本条目

## 步骤2: 更新版本号
更新 `Codes/version.py` 中的版本信息：
- 文件位置: `E:\Projects\PythonTools\AutoFillForm\Codes\version.py`
- 更新 `__version__` 变量为新版本号 (例如: "5.1.0")
- 所有其他文件会自动使用新版本号（已集中管理，无需修改其他文件）

## 步骤3: 创建提交
创建 commit，message 格式为：
```
chore(release): update version to <版本号> and generate changelog

- Update version in version.py

- Generate CHANGELOG.md for v<版本号>

- Update README.md version history
```

## 步骤4: 推送提交
将提交推送到远程仓库

## 步骤5: 创建并推送 Tag
创建 tag（格式: v<版本号>），例如: v5.1.0
推送到远程仓库

## 示例
输入: `/release 5.1.0`
- 新版本: 5.1.0
- Tag: v5.1.0
- Commit message:
  ```
  chore(release): update version to 5.1.0 and generate changelog

  - Update version in version.py

  - Generate CHANGELOG.md for v5.1.0

  - Update README.md version history
  ```

## 版本号规范
遵循语义化版本 (Semantic Versioning):
- **主版本号 (Major)**: 不兼容的 API 修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

示例:
- `5.0.0` → `5.1.0` (新功能)
- `5.1.0` → `5.1.1` (Bug 修复)
- `5.1.1` → `6.0.0` (重大变更)
