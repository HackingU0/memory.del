# memory.del

帮你快速清理一个人在你手机里的痕迹。

memory.del 是一套给 AI 助手用的技能（skills）。它基于 [iPhone Use](https://github.com/HackingU0/iPhone-use)（PUA，Phone Use Agent）通过 USB 操作**你自己的** iPhone，在「照片」、微信、QQ、微博、小红书、抖音等国产 IM 和社交软件，以及系统 App 里找出和 ta 有关的东西，列清单给你过目，你点头之后再删。

目前适配 **Claude**（Claude Code、Claude 桌面端）和 **Codex**。只支持 iPhone，暂不支持安卓。

## 它会先问你删什么

开始之前，助手一定会先问范围，不会上来就删：

| 选项 | 包括 |
| --- | --- |
| 截图 | 和 ta 的聊天截图、ta 的朋友圈 / 主页截图、转账和通话记录截图 |
| ta 的样子 | 只有 ta 的照片、自拍、视频 |
| 合影 | 你们的合照；有 ta 的多人照算不算，你说了算 |
| 聊天记录 | 微信、QQ 等里和 ta 的对话 |
| 好友 | 删好友、拉黑、取关，或者只屏蔽朋友圈 |
| 绝情模式 | 以上全部，再加上通讯录、通话记录、备忘录、日历、收藏、收货地址、常用乘车人、共享位置等所有能找到的痕迹 |

然后再问：ta 在各个 App 里叫什么、大概的时间段和地点、删除方式（删到「最近删除」留 30 天后悔期 / 先备份到 Mac / 只隐藏 / 彻底删除）、哪些要留下。

## 怎么找到「和 ta 有关」的照片

「照片」App 在手机本地做了人脸识别、文字识别、场景识别和地点索引，memory.del 把这些都用上，再由模型逐张看图判断：

| 信号 | 用来找 | 可靠程度 |
| --- | --- | --- |
| **人物**：「人物与宠物」里 ta 的人物（你标记过名字的，或者现场让你指认） | ta 的样子、合影 | 高 |
| **人物组合**：ta 和「我」同时出现的照片 | 合影 | 高 |
| **截图文字**：搜索 ta 的备注名、昵称、微信号 / QQ 号、手机号（实况文本 OCR） | 截图 | 高 |
| **聊天截图标题**：截图顶部的聊天对象名字 | 截图 | 高 |
| **照片说明**：你给照片写过的说明文字 | 全部 | 高 |
| **头像比对**：截图里的头像和 ta 当前的头像对比 | 截图 | 中 |
| **地点**：城市、景点、ta 家或学校附近的地名，地图视图 | ta 的样子、合影 | 中 |
| **时间**：在一起的时间段、纪念日、生日、「旅行」和「回忆」 | 全部，用于缩小范围 | 中 |
| **来源**：微信 / QQ 保存的图片相簿、「与你共享」、AirDrop 收到的、共享相簿 | ta 的样子、截图 | 中 |
| **时空邻近**：一张已确认照片前后几分钟、同一地点的连拍 | ta 的样子、合影 | 中 |
| **描述搜索**：一句话描述画面（需要系统支持自然语言搜索），或场景词（海边、蛋糕、电影票） | 补漏 | 低 |
| **媒体类型 / 宠物 / 礼物**：自拍、人像、屏幕录制；ta 的宠物；ta 送的东西 | 补漏，宠物和礼物要先问你 | 低 |

每个候选都会标上「确定 / 很可能 / 存疑」。「存疑」的会一张张让你在手机上看，由你决定。删完之后还可以顺手处理：减少精选 ta（不再在回忆和小组件里出现）、删掉以 ta 为主的回忆、退出共享相簿、检查「隐藏」和「重复项」。

详细做法见 [匹配方法](skills/memory-del-photos/references/matching.md) 和 [截图识别](skills/memory-del-photos/references/screenshots.md)。

## 支持的 App

| 类别 | App |
| --- | --- |
| 相册 | 照片 |
| IM | 微信、QQ；企业微信、钉钉、飞书（默认不动，点名才处理） |
| 社交 | 微博、小红书、抖音、快手、哔哩哔哩、知乎、豆瓣、即刻、Soul、陌陌、探探 |
| 音乐 | 网易云音乐、QQ音乐 |
| 生活 | 支付宝、淘宝、京东、拼多多、美团、饿了么、高德地图、百度地图、铁路12306、携程、飞猪、滴滴 |
| 系统 | 通讯录、电话、信息、FaceTime、备忘录、日历、提醒事项、查找、健康（紧急联系人）、文件、语音备忘录、键盘文本替换 |

## 安全设计

- **先问范围，再碰手机**；**先找，再删**。只读侦察阶段不会点任何删除。
- **不确定就停下来问**：同名、身份对不上、把握不足、数量对不上、界面出现没见过的弹窗、涉及共享内容，都会停手问你。
- **分级确认**：照片删到「最近删除」这类可撤回操作按类别确认；删好友、拉黑、取关、停止共享位置这类 ta 可能察觉的动作**每项单独确认**；从「最近删除」永久删除需要再确认一次，并且只清本次删掉的那些，绝不点「全部删除」。
- **只动你自己的手机和账号**：不会给 ta 或任何人发消息，不发帖，不碰资金，不代输密码和验证码。
- **照片不外传**：照片和截图只用来在本机判断，不上传、不另存。收尾时会提醒你清掉 iPhone Use 留在电脑上的观察截图。
- **如实汇报**：删除聊天记录只删本机，ta 那边、电脑版、备份里的都还在，会直接告诉你。

## 安装

前提和 iPhone Use 一样：一台 Mac（macOS、完整 Xcode、Python 3.9+、Node.js），一部用 USB 连接的 iPhone，以及能在这台 Mac 上运行命令的助手（Claude Code 或 Codex；Claude 桌面端用户可以在桌面端的 Code 标签页里发这句话）。

### 一句话安装

把下面这句话丢给你的助手：

```text
请帮我在这台 Mac 上安装 memory.del：先按 https://github.com/HackingU0/iPhone-use 的 README 为你自己安装并配置 iPhone Use，直到 pua_ready 返回 ready=true（已经能用就跳过）；再把 https://github.com/HackingU0/memory.del 克隆到 iPhone-use 旁边，运行 sh scripts/install.sh，把需要我手动完成的步骤（重开会话、在 Claude 桌面端上传技能 ZIP 等）一条条告诉我，遇到需要我操作或不确定的地方先停下来问我。
```

### 手动安装

```sh
git clone https://github.com/HackingU0/iPhone-use.git
git clone https://github.com/HackingU0/memory.del.git
cd memory.del
sh scripts/install.sh                 # 自动识别 Claude Code / Codex / Claude 桌面端
```

`install.sh` 会做这些事：

| 宿主 | 做了什么 | 你还需要做的 |
| --- | --- | --- |
| Claude Code | 把 4 个技能复制到 `~/.claude/skills/`。如果还没注册 `iphone_use` MCP：复用 Claude 桌面端已有的配置，或者运行 iPhone Use 自带的 Claude 安装器（会先验证服务能启动），再用 `claude mcp add-json` 注册；同时复制 iPhone Use 的两个技能 | 新开 Claude Code 会话 |
| Codex | 把 4 个技能复制到 `~/.codex/skills/`；检查 `codex mcp list` 里有没有 `iphone_use`，没有时提示你运行 iPhone Use 的 `sh scripts/install.sh` | 重连或新开 Codex 聊天 |
| Claude 桌面端 | 在 `dist/skill-uploads/` 生成 4 个技能 ZIP | 先在 iPhone Use 目录运行 `python3 claude/install.py`；然后在「自定义 > 技能」上传这 4 个 ZIP 并打开；⌘Q 完全退出再打开 Claude |

常用参数：`--hosts claude-code,codex,claude-desktop` 指定宿主；`--iphone-use /path/to/iPhone-use` 指定 iPhone Use 的位置；`--skip-mcp` 只装 memory.del 的技能；`--uninstall` 卸载（只删除本脚本装过的技能文件夹，不动 MCP 注册）。脚本不会覆盖不是它装的同名文件夹，除非加 `--force`。

Claude Code 也可以只装技能、不走脚本：`/plugin marketplace add HackingU0/memory.del`，再 `/plugin install memory-del@memory-del`。这种方式不会注册 iPhone Use 的 MCP 服务，需要你另外配置。

### 开始用

新开一个会话，说：

> 用 memory.del 帮我清理和 ta 有关的东西

助手会先问你范围。使用期间手机保持解锁亮屏；遇到 Face ID、密码、App 登录，助手会停下来请你在手机上完成。

## 目录

```text
skills/
  memory-del/          入口：范围问询、ta 档案、安全规则、清单、各宿主提问方式
  memory-del-photos/   相册：截图、ta 的样子、合影；匹配方法与删除步骤
  memory-del-im/       IM 与社交软件：微信、QQ、工作 IM、社交 / 音乐、生活类 App
  memory-del-system/   系统 App：通讯录、通话、信息、备忘录、日历、查找等
scripts/
  install.sh / install.py   安装到 Claude Code、Codex，生成 Claude 桌面端 ZIP
  check.py                  校验技能格式和文档链接
.claude-plugin/        Claude Code 插件与 marketplace 清单
```

开发检查：

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

## 已知限制

- 各 App 的界面路径来自常见版本，App 改版后可能对不上。技能要求模型以实际观察到的界面为准，找不到入口时停下来，而不是乱点。这些流程还没有在大量真机和版本上逐一验证过，欢迎反馈。
- 「照片」的识别依赖本机索引：刚导入大量照片、索引还没完成时会搜不全；自然语言描述搜索取决于系统版本、语言和地区是否支持。
- 聊天记录删除只影响这部手机。ta 的手机、电脑版、平板、云端或本地备份不受影响。
- iCloud 照片会把删除同步到所有设备；iCloud 共享图库里的照片删除后其他参与者也看不到，涉及时会先问你。
- 不支持安卓设备。

## 致谢

手机操作能力来自 [iPhone Use](https://github.com/HackingU0/iPhone-use)（ZHONG XIN 原作，MIT License），底层依赖 [Appium](https://github.com/appium/appium) 生态与 [WebDriverAgent](https://github.com/appium/WebDriverAgent)。
