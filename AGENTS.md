# AGENTS.md

本仓是从本机 `droid` CLI 二进制提取的内置 skill 的中文版，没有 GitHub 上游。

- 类别目录是 catalog 真源，`README.md` 是投影：增删改 skill 后同步 README 的表格和总数。
- 翻译范围、必须保留的原文和术语表以 `docs/translation-profile.zh-CN.md` 为准；更新英文基线时先对比那里记录的基线 commit。
- 校验：`python3 -m unittest discover -s tests -p 'test_*.py'` 和 `python3 -m unittest discover -s test -p 'test_*.py'`。
