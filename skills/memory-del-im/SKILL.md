---
name: memory-del-im
description: memory.del 的社交软件部分。在微信、QQ、企业微信、钉钉、飞书、微博、小红书、抖音、快手、哔哩哔哩、知乎、豆瓣、即刻、Soul、陌陌、探探、网易云音乐、QQ音乐，以及支付宝、淘宝、外卖、地图、出行等国产 App 里，找出并清理和 ta 的聊天记录、好友 / 关注关系、收藏、动态、地址等痕迹。由 memory-del 在问询完成后调用。
---

# 社交软件：聊天记录、好友和其他痕迹

前提：已经按 `memory-del` 完成范围问询和 ta 档案，并取得本对话的 READY。只处理用户选中的范围和 App，规则以 `memory-del` 的安全规则为准。

各 App 的界面经常改版，参考文件里的路径是写作时的常见入口，**以实际观察为准**。找不到入口时先截图观察，可以用 App 内搜索；仍然找不到就停下来告诉用户，不要乱点。

## 先确定涉及哪些 App

1. 用户在问询时说过的 App 先列上。
2. 用户说不清时，用 `pua_apps(source="installed", query=...)` 逐个查询下表里的 App 是否安装（只返回匹配项，不会读出整份安装清单），把已安装的列给用户，问和 ta 在哪些上面有交集。
3. 启动 App 时，下表给出 bundle ID 的直接使用；标「查询」的用 `pua_apps(source="auto", query="名称")` 查到并核对后再启动，不要猜 ID。

| App | bundle ID | 参考 |
| --- | --- | --- |
| 微信 | `com.tencent.xin` | [wechat.md](references/wechat.md) |
| QQ | `com.tencent.mqq` | [qq.md](references/qq.md) |
| 企业微信 | `com.tencent.ww` | [work-im.md](references/work-im.md) |
| 钉钉 | `com.laiwang.DingTalk` | [work-im.md](references/work-im.md) |
| 飞书 | `com.bytedance.ee.lark` | [work-im.md](references/work-im.md) |
| 微博 | `com.sina.weibo` | [social.md](references/social.md) |
| 小红书 | `com.xingin.discover` | [social.md](references/social.md) |
| 抖音 | `com.ss.iphone.ugc.Aweme` | [social.md](references/social.md) |
| 快手 | `com.jiangjia.gif` | [social.md](references/social.md) |
| 哔哩哔哩 | `tv.danmaku.bilianime` | [social.md](references/social.md) |
| 知乎、豆瓣、即刻 | 查询 | [social.md](references/social.md) |
| Soul、陌陌、探探 | 查询 | [social.md](references/social.md) |
| 网易云音乐 | `com.netease.cloudmusic` | [social.md](references/social.md) |
| QQ音乐 | `com.tencent.QQMusic` | [social.md](references/social.md) |
| 支付宝 | `com.alipay.iphoneclient` | [life.md](references/life.md) |
| 淘宝 | `com.taobao.taobao4iphone` | [life.md](references/life.md) |
| 京东 | `com.360buy.jdmobile` | [life.md](references/life.md) |
| 拼多多 | `com.xunmeng.pinduoduo` | [life.md](references/life.md) |
| 美团 | `com.meituan.imeituan` | [life.md](references/life.md) |
| 饿了么 | `me.ele.ios.eleme` | [life.md](references/life.md) |
| 高德地图 | `com.autonavi.amap` | [life.md](references/life.md) |
| 百度地图 | `com.baidu.map` | [life.md](references/life.md) |
| 铁路12306 | `cn.12306.rails12306` | [life.md](references/life.md) |
| 携程旅行 | `ctrip.com` | [life.md](references/life.md) |
| 飞猪 | `com.taobao.travel` | [life.md](references/life.md) |
| 滴滴出行 | `com.xiaojukeji.didi` | [life.md](references/life.md) |

已列出的 bundle ID 来自 iPhone Use 的已核验目录。上表没有的 App，同样先用 `pua_apps` 查询，再参照最接近的同类参考处理。

## 每个 App 的通用步骤

1. **找到 ta（只读）**：在 App 内搜索档案里的备注名 / 昵称 / 账号，打开资料页核对。候选不唯一或对不上时停下来问。
2. **盘点（只读）**：按用户范围逐项看这个 App 里有哪些痕迹：单聊会话、群聊里的消息、好友 / 关注 / 粉丝关系、特别关心或星标、收藏、自己发过的相关动态、共享或绑定关系、地址等。记下数量和位置，不点任何删除。
3. **列清单**：按 `memory-del` 的清单格式，每项标级别（L2 本机不可撤回 / L3 ta 可能察觉）。
4. **确认后执行**：L2 按类别确认；L3 每项单独确认，说明 ta 那边会看到什么。
5. **核对**：删除后回到列表或资料页观察，确认会话已不在、关系已变化、数量对得上。

## 几个要讲清楚的事实

- **删除聊天记录只删本机。** ta 手机上的记录、电脑版和平板上的记录、聊天记录备份都不受影响。用户希望连电脑版也清，告诉用户需要在电脑上自己处理。
- **删好友、拉黑、取关大多不通知对方，但对方可能察觉。** 例如 ta 给你发消息会失败或需要验证、ta 看不到你的动态、关注数变化。每个 App 的具体表现写在参考文件里；不确定时如实说「ta 可能会发现」。
- **群聊里 ta 的消息通常只能逐条删，而且也只删本机。** 默认不做，用户明确要求时才做，并先告诉用户数量和大概耗时。
- **转账、红包、订单等资金和交易记录不处理**，多数也无法删除。
- 处理自己发过的动态时，优先提供「设为仅自己可见」这种更温和的选项，由用户选择删除还是隐藏。

## 遇到这些情况停下来

- 需要登录或登录已过期、需要短信验证码、需要支付密码：按 `iphone-use` 的认证接管交给用户。
- 确认弹窗里出现「同时删除」「无法恢复」「对方将」「通知」等之前没说明过的后果。
- App 弹出风控提示、操作频繁提示：立即停止这个 App 的操作，告诉用户，过一段时间再说。批量操作之间留出正常的间隔，不要连续高速点击。
- 一个按钮同时做两件事（例如删除好友时默认勾选「同时删除聊天记录」），而用户只同意了其中一件。
