---
name: official-ai-explainer-shotcraft
description: Create evidence-backed, high-quality 16:9 explainer videos about AI or technical products from official docs, blogs, screenshots, and demos. Use when the user wants a Chinese or multilingual product explainer that ordinary viewers can understand, including research, plain-language narration, real-source visuals, Shotcraft-style motion, TTS pronunciation control, subtitles, rendering, and final audiovisual QA. Do not use for general sports promos or unrelated advertising unless the user explicitly asks to adapt the method.
metadata:
  short-description: Official-source AI explainers for general audiences
---

# 官网实证型 AI 解释视频

把官方文档、博客、截图和演示视频，做成普通人看得懂、愿意看完、每个关键说法都能追溯来源的横屏解释视频。

这个 Skill 是独立方法包，不依赖任何特定业务项目或绝对路径。不要从最初抽离它的项目中 import 代码、读取私有素材或假设固定接口。目标仓库已有视频链路时就适配；没有时，在用户指定的工作区建立隔离的视频工程。

## 先判断交付范围

- 用户只要标题、文案或分镜时，只交付对应内容，不擅自渲染或调用付费配音。
- 用户明确要成片时，默认推进到可播放 MP4，并同时交付封面、最终脚本和来源清单。
- 用户给了网址、项目或素材时，先做只读检查；不要修改无关业务代码。
- 信息足够时直接执行。只有缺少会实质改变事实、版权范围或成片方向的输入时才询问。

## 默认成片合同

除非用户另有要求：

- 画幅：16:9，1920×1080，30fps。
- 时长：45–90 秒。
- 编码：H.264，高质量交付，优先 CRF 14–18。
- 受众：没有专业背景的普通观众。
- 观看场景：同时发小红书、视频号、抖音等手机平台时，横版常被放在竖屏里小窗播放（约缩到 0.2 倍）。主要信息必须靠标题和字幕看懂，正文小字和整页截图只能当佐证。
- 开场：第一帧就出现本期核心判断，前 2 秒说出来，0 秒就有声音；不要从黑屏、模糊或空画面淡入，也不以自我介绍或系列介绍开头。
- 语气：大白话、具体、克制，不吹成“万能 AI”。
- 素材：官方来源优先，始终使用可获得的最高画质版本。

## 核心流程

1. **建立事实底稿。** 阅读官方介绍、文档、博客、演示和限制说明，为每个准备写入口播的事实记录来源。开始研究和写稿前读 [references/editorial-and-evidence.md](references/editorial-and-evidence.md)。
2. **把专业概念翻译成人话。** 先说明“它替谁做什么、结果有什么不同”，再补术语和原理。不要把官网术语原样堆给观众。
3. **用六段母版组织内容。** 默认使用下方六段结构；如果证据不足，删减或改写，不要为了凑结构编造内容。
4. **采集最高画质素材并留下来源。** 优先官方原视频或原图，其次才是高分辨率网页截图。每项素材保留 URL、采集时间、用途和来源类型（官方、自有产品实录、示意、媒体报道）。整页截图在手机上看不清时，改用放大后的局部截图。
5. **按语义设计镜头。** 镜头服务于信息，不为了炫技。制作成片时完整阅读 [references/production-workflow.md](references/production-workflow.md)。
6. **先出静帧，确认画面再配音。** 配音和渲染会产生费用，先按估算时长渲出每镜开头、定格、结尾三张静帧和两种比例的封面，按手机小窗大小检查一遍。
7. **生成并校对声音。** 检查品牌名、英文缩写、数字和多音字；支持发音字典时写显式规则，不支持时改成不会误读的等价口语。
8. **按音频重排时间线。** 字幕、画面停留和转场以最终音频时长为准，不用估算时长硬切。只重配口播改过的镜头；复用旧音频前核对它与当前口播完全一致。
9. **渲染并做独立终检。** 交付前完整阅读 [references/quality-gates.md](references/quality-gates.md)，实际看完、听完最终文件，而不是只确认渲染命令成功。

## 六段母版

1. **一句话说清它是什么**：明确对象、动作和结果；适合轻推近或 `cursor-flyover`。
2. **和原来方式差在哪**：用同一任务做具体对比；适合 `before-after-slider-scrub`。
3. **普通人最容易遇到的场景**：通常列 2–3 个“输入 → 结果”；适合 `deck-deal-flyin`。
4. **把核心能力翻译成人话**：术语与口语解释同屏；适合 `ai-stream-response`。
5. **主动讲清能力边界**：限制、前提和不适用场景；适合 `card-flip-reveal`。
6. **说明它会在哪里出现并收束**：回到普通人的日常体验和一个自然问题；适合 `text-column-converge`。

### 三种变体

默认六段适合“讲清一个产品或模型”。另外两种内容按下面改写，镜头卡可以换位，但每镜仍只做一件事：

- **事件型**（发布、事故、封禁、政策）：1 发生了什么，并给出判断 → 2 和以前相比变了什么 → 3 牵涉到谁 → 4 背后的机制翻成人话 → 5 还不确定、不能下结论的部分 → 6 对观众意味着什么。
- **自有产品型**（作者自己搭的系统）：素材用真实录屏或截图，来源类型标“自有产品实录”；第 5 段必须讲清还没验证或还没做到的部分，不把试运行说成已交付。

作者有自己的账号口吻时，第 1 段先给出作者判断，第 6 段讲判断和理由；判断必须标明是观点，第一人称经历只能用作者提供的真实经历。

这些卡名是运动语义，不是必须照抄的视觉皮肤。如果本机安装了 `video-shotcraft`，使用某张卡前读取对应卡片和准确示例实现；如果没有，按 [references/production-workflow.md](references/production-workflow.md) 中的语义实现，不要声称复刻了原卡参数。

## 不可妥协的约束

- 不编造官网没有证明的能力、性能数字、发布日期、客户或使用场景。
- 不用低清截图放大冒充高清素材；没有合格素材时改镜头方案。
- 不把模拟 UI 当成产品真实界面。必须模拟时，画面角标和制作记录都要标“示意”。
- 不采集或展示密钥、客户数据、个人信息、内部页面和其他敏感内容。
- 字幕必须逐句对应最终配音；不能在配音修改后继续使用旧字幕或旧时长。
- 动画必须逐帧可复现；不要在渲染路径中使用未固定种子的随机数或当前时间。
- 涉及比赛片段、音乐、肖像、队徽或第三方品牌时，单独核验授权；本 Skill 不替代版权许可。

## 配置化制作

需要批量或可复用生产时，复制 [assets/episode.example.json](assets/episode.example.json)，并读 [references/episode-schema.md](references/episode-schema.md)。完成后运行：

```bash
python3 scripts/validate_episode.py path/to/episode.json
```

只想先验证结构、不检查本地素材是否存在时加 `--schema-only`。

## 最低交付清单

- 最终 MP4。
- 封面 PNG 或 JPG：3:4 一张（各平台信息流）和 4:3 一张（抖音电脑端横竖双封面）。封面用清晰明亮的真实素材作底图，只放一句不超过 10 个字、每行不超过 5 个字的封面文案和署名，与标题互补不重复。
- 多平台发布时，每个平台的标题、简介和话题各一份，内容与口播一致；热点内容每份都写明来源。
- 配音核对报告（转写与口播的比对结果）。
- 最终口播和分镜脚本。
- 素材来源清单，包括 URL、用途和采集时间。
- 多音字与品牌发音规则。
- QA 结果，以及仍需用户自行确认的版权或事实风险。

Shotcraft 镜头词汇受 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) 启发。复制其代码或资产时遵守仓库许可证并保留相应声明；本 Skill 自身不打包该仓库代码。
