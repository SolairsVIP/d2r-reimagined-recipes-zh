# D2R Reimagined 中文配方与符文之语图鉴

**在线访问：[https://solairsvip.github.io/d2r-reimagined-recipes-zh/](https://solairsvip.github.io/d2r-reimagined-recipes-zh/)**

[D2R Reimagined](https://www.d2r-reimagined.com/) 模组的非官方中文图鉴，整理了方块合成、装备附魔、物品制作及符文之语。可按材料、结果、属性和底材等条件查询。

- [配方图鉴](https://solairsvip.github.io/d2r-reimagined-recipes-zh/) · [原始配方资料](https://wiki.d2r-reimagined.com/en/recipes/recipes)
- [符文之语图鉴](https://solairsvip.github.io/d2r-reimagined-recipes-zh/runewords.html) · [原始符文之语资料](https://www.d2r-reimagined.com/data/runewords)

直接用浏览器打开 `index.html` 即可使用，也可以部署到 GitHub Pages。所有网页文件和配方数据均使用相对路径，无需安装依赖或运行服务器。

配方数据基于原始资料 2026-11-02（世界协调时）的版本；符文之语基于官网 2026-10-29 的数据及简体中文游戏文本。本站保留材料相同但结果不同的配方，以及底材或属性不同的同名符文之语。模组新增符文名称采用音译；游戏内容可能更新，请以当前模组版本与原始资料为准。

## 检查

```text
python -m unittest discover -s tests -v
node --test tests/search.test.js tests/runewords-search.test.js
```

## 更新数据

将官方配方 Markdown 保存为 `source_recipes.tmp`，运行 `python tools/build_data.py source_recipes.tmp` 生成 `data/recipes.json` 和 `data/recipes.js`。脚本中的术语表须随原始资料的新术语一起更新；生成后运行上述检查并人工核对配方限制。数据测试中的原始配方数量也需要在确认新增或删除后更新。

更新符文之语时，将官网的 `data/keyed/runewords.json`、`data/strings/zhCN.json` 和 `data/strings/enUS.json` 分别保存为 `source_runewords_json.tmp`、`source_zhcn.tmp` 和 `source_enus.tmp`，再运行：

```text
python tools/build_runewords.py source_runewords_json.tmp source_zhcn.tmp source_enus.tmp --source-updated 2026-10-29T14:10:11Z
```

将 `--source-updated` 改为对应数据版本的更新时间，核对新增本地化文本与原始数据，然后运行检查。

## GitHub Pages

工作流位于 `.github/workflows/pages.yml`。将项目推送到 GitHub 仓库的 `main` 分支，并在仓库的 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**；后续推送会触发验证与发布。发布需要仓库具备 Pages 功能及相应权限。
