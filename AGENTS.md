# memory.del 开发说明

这个仓库是一组 Agent Skills（每个技能一个文件夹，里面是带 `name` / `description` frontmatter 的 `SKILL.md` 和按需读取的 `references/`），供 Claude Code、Claude 桌面端和 Codex 使用。手机操作依赖 [iPhone Use](https://github.com/HackingU0/iPhone-use) 的 `pua_*` MCP 工具。

- 用户要清理手机里某个人的痕迹时，从 `skills/memory-del/SKILL.md` 开始。
- 修改技能时保持宿主中立：提问方式和工具名差异写在 `skills/memory-del/references/hosts.md`，不要在其他文件里写死某个宿主的工具。
- 新增 App 时放进 `skills/memory-del-im/references/` 里最接近的分类文件，在 `memory-del-im/SKILL.md` 的表格里加一行；bundle ID 只写经过核验的，其余写「查询」。
- 界面路径一律标注为参考，要求以实际观察为准；任何删除类动作都要写明级别（见 `skills/memory-del/references/safety.md`）。
- 文档里不要写入真实的人名、聊天内容、手机号或设备信息。
- 提交前运行 `python3 scripts/check.py` 和 `python3 -m unittest discover -s tests -v`。
