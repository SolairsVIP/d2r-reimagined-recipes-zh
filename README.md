# 赫拉迪姆中文配方图鉴

暗黑破坏神重构版的非官方中文配方查询页，整理了方块合成、装备附魔和物品制作。可按材料、结果和类型搜索；数据来自[原始配方页面](https://wiki.d2r-reimagined.com/en/recipes/recipes)。

直接用浏览器打开 `index.html` 即可使用，也可以部署到 GitHub Pages。所有网页文件和配方数据均使用相对路径，无需安装依赖或运行服务器。

当前数据基于原始资料 2026-11-02（世界协调时）的版本，保留原表中材料相同但结果有差异的记录。游戏内容可能更新，请以模组当前版本与原始资料为准。

## 检查

```text
python -m unittest discover -s tests -v
node --test tests/search.test.js
```

## 更新数据

将官方配方 Markdown 保存为 `source_recipes.tmp`，运行 `python tools/build_data.py source_recipes.tmp` 生成 `data/recipes.json` 和 `data/recipes.js`。脚本中的术语表须随原始资料的新术语一起更新；生成后运行上述检查并人工核对配方限制。数据测试中的原始配方数量也需要在确认新增或删除后更新。

## GitHub Pages

工作流位于 `.github/workflows/pages.yml`。将项目推送到 GitHub 仓库的 `main` 分支，并在仓库的 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**；后续推送会触发验证与发布。发布需要仓库具备 Pages 功能及相应权限。
