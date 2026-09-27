# Episode 配置约定

配置用于把一期内容与渲染实现分开。示例见 [../assets/episode.example.json](../assets/episode.example.json)。

## 顶层字段

| 字段 | 要求 |
|---|---|
| `slug` | 必填；小写字母、数字和连字符，最长 64 字符 |
| `fileStem` | 可选；最终文件名前缀 |
| `outputDirectory` | 可选；相对当前工作区或绝对输出目录 |
| `title` | 必填；视频标题 |
| `coverText` | 必填；封面文案，不超过 10 个字、每行不超过 5 个字，用换行分行 |
| `coverSource` | 可选；封面底图，字段同 `source`，只接受图片；`focusX`（0–100）决定竖版和 4:3 裁切时的水平焦点 |
| `subtitle` | 可选；系列或内容类型 |
| `hook.statement` | 必填；一句话钩子 |
| `hook.beats` | 必填；正好 3 个观看理由 |
| `callToAction` | 必填；结尾自然问题或下一步 |
| `style` | 可选；本期视觉方向，不应写死其他品牌 |
| `scenes` | 必填；六段母版正好 6 项 |

所有文字字段超出上限都会报错，不会被截断。

## Scene 字段

| 字段 | 要求 |
|---|---|
| `heading` | 必填；镜头核心判断 |
| `body` | 必填；画面说明或辅助解释 |
| `bullets` | 必填；最多 4 项，写可观察事实 |
| `narration` | 必填；最终口播 |
| `durationSeconds` | 可选；2–30 秒，最终应由音频校准 |
| `visualDirection` | 可选；本期具体画面设计 |
| `recipe` | 可选；换用其他镜头卡，默认按段落顺序；另有证据卡 `focus-zoom`、`scan-annotate` |
| `focusRegions` | 两张证据卡必填；`[{x,y,w,h,label}]`，按 16:9 画面的百分比；`focus-zoom` 1 个区域，`scan-annotate` 1–4 个且每个都要 `label`（不超过 16 字） |
| `source` | 除 `deck-deal-flyin` 外的镜头卡必填 |
| `compareSource` | 可选；只用于 `before-after-slider-scrub`，作为左侧“以前”画面 |
| `delivery` | 可选；情绪、强调、停顿和语速 |
| `pronunciation` | 可选；品牌和多音字发音规则 |
| `shotCopy` | 可选；镜头内短标签，不改变口播 |

## Source 字段

- `path`：本地最高画质素材路径；相对路径按配置文件所在目录解析。
- `label`：画面显示或制作记录使用的简短来源名。
- `sourceUrl`：完整 HTTP/HTTPS 官方网址。
- `capturedAt`：必填，真实的 ISO 8601 采集时间；占位时间会报错。
- `kind`：`official`（默认）/ `own-product` / `illustration` / `media`，决定画面角标。示意图必须用 `illustration`。
- 路径只接受 MP4、PNG、JPG、WebP。

第三段可以完全由信息卡构成，因此默认不强制官方媒体；其中的事实仍需在来源清单里有依据。

## Delivery 与发音

`delivery.emphasis` 和 `delivery.breakAfter` 中的短语必须真实出现在 `narration` 中，否则报错。`pronunciation` 每项格式为：

```json
{
  "key": "藏",
  "value": "cang2",
  "caseSensitive": false
}
```

不同 TTS 服务的音素或声调格式不同。配置进入服务前要做适配，不要默认所有服务都接受拼音加声调数字。

## ShotCopy

支持的键由实现决定，常见键包括：

- `sourceBadge`
- `comparisonCodes`、`comparisonLabels`
- `cardLabels`、`cardFooter`
- `resultSummary`、`resultStatus`、`panelTitle`
- `flipLabels`、`flipFooter`
- `columnAnchor`、`columnBridge`、`columnFinal`

未知键直接报错。没填的标签应隐藏或显示中性文字，不能沿用上一期的文案。

## 验证

在 Skill 目录中运行：

```bash
python3 scripts/validate_episode.py /absolute/path/to/episode.json
```

使用 `--schema-only` 只验证结构；使用 `--json` 输出机器可读结果。正式渲染前不要使用 `--schema-only` 代替素材检查。
