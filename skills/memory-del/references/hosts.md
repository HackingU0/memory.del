# 各宿主的提问方式和工具名

## 提问

| 宿主 | 提问工具 | 注意 |
| --- | --- | --- |
| Claude Code | `AskUserQuestion` | 每次最多 4 题，每题 2–4 个选项，可设 `multiSelect`；用户总能选「其他」自由输入。第一问按 [范围问询](intake.md) 的拆分方式问。 |
| Codex | `request_user_input`（Plan 模式）或 `request_user_input_async`（Default 模式，与 `iphone-use` 的认证接管一致） | 异步提问会立即返回，那不是用户的回答；等用户实际提交。选项放不下时改用文字。 |
| Claude 桌面端 | 通常没有提问工具 | 直接在回复里提问并结束本回合，等用户下一条消息。 |
| 其他宿主 | 按实际提供的工具 | 没有就用文字。 |

无论哪个宿主：

- 认证接管的提问按 `iphone-use` 的约定，第一个选项是「已完成继续」。
- 删除确认的提问，第一个选项写清楚动作和数量，例如「删除这 24 张（进最近删除）」，不要只写「确认」。
- 不要把用户没选的预设选项当作回答。

## 工具名

`iphone-use` 的 MCP 服务名是 `iphone_use`，工具在不同宿主里的显示名不同：

| 宿主 | 工具名示例 |
| --- | --- |
| Claude Code | `mcp__iphone_use__pua_ready` |
| Codex | `mcp__iphone_use__pua_ready`（或通过 `tools.mcp__iphone_use__pua_ready` 调用） |
| Claude 桌面端 | `pua_ready` |

本技能文中统一写 `pua_ready` 这样的短名。

## 截图查看

- Claude Code、Claude 桌面端：工具结果里的图片块直接可见。
- Codex 通过 `functions.exec` 调工具时，要把图片块转发给模型，见 `iphone-use` 技能的说明。
- 判断照片和截图内容时，必须真正看过返回的图片，不能只凭元数据下结论。
- Claude Code 在终端里看不到手机实时预览，需要用户看的时候请用户直接看手机。
