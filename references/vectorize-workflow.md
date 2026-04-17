# Vectorize Workflow

AI 生成图 → 可编辑 SVG 矢量图的开源流水线。

## 适用场景

将 Gemini 等 AI 生成的 Logo、图标、示意图转为可编辑矢量图，用于 PPT 排版或论文插图。

不适用于：照片级图像（矢量化效果差）、纯文字（直接在 PPT 中输入更清晰）。

## 前置依赖

```bash
# Python 包
pip install py-gemini-watermark-remover vtracer "rembg[cpu]"

# 超分辨率二进制（从 GitHub Releases 下载对应平台版本）
# https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan/releases
# macOS: 下载后解压，放入 $PATH 或用 --realesrgan-bin 指定路径
# 首次运行可能需要：xattr -cr realesrgan-ncnn-vulkan（解除 macOS 安全限制）

# 可选：裁剪功能需要 Pillow
pip install Pillow
```

注意：`rembg` 首次运行会自动下载 U2-Net 模型（~170MB），存放在 `~/.u2net/`。

## 流水线四阶段

```
输入图 → [1] 去水印 → [2] 超分辨率 → [3] 去背景 → [4] 矢量化 → SVG
```

| 阶段 | 工具 | 作用 | 输出 |
|------|------|------|------|
| 去水印 | py-gemini-watermark-remover | 反向 Alpha 混合去除 Gemini 隐形水印 | `*-1-dewatermark.png` |
| 超分辨率 | realesrgan-ncnn-vulkan | 4x 放大，提升矢量化精度 | `*-2-upscale.png` |
| 去背景 | rembg (U2-Net) | AI 去除白色/彩色背景 | `*-3-nobg.png` |
| 矢量化 | vtracer | 光栅图转 SVG 曲线 | `*-4-vector.svg` |

## 使用示例

```bash
# 完整流水线
python3 scripts/vectorize_image.py gemini_output.png

# 非 Gemini 图片，跳过去水印
python3 scripts/vectorize_image.py logo.png --skip dewatermark

# 只做矢量化（已有透明背景的 PNG）
python3 scripts/vectorize_image.py transparent_logo.png --only vectorize

# 裁剪单个元素后处理
python3 scripts/vectorize_image.py full_image.png --crop 100,200,300,300

# 调整矢量化参数
python3 scripts/vectorize_image.py logo.png --vtracer-mode polygon --color-precision 8

# 预览步骤
python3 scripts/vectorize_image.py input.png --dry-run
```

## 最佳实践

1. **单元素裁剪**：永远只对单个 Logo/图标操作，不要整图导入。用 `--crop` 或提前裁好。
2. **文字后加**：图里的文字能去就去，在 PPT 中重新输入最清晰。
3. **基础图形用原生**：圆、框、箭头等简单几何图形，PPT 自带图形画的最完美，不必矢量化。
4. **二值模式**：纯黑白 Logo 用 `--vtracer-colormode binary`，输出更简洁。
5. **跳过不需要的步骤**：非 Gemini 图片跳过去水印，已经高清的图片跳过超分辨率。

## 闭源 vs 开源对照

| 步骤 | 原闭源方案 | 开源替代 |
|------|-----------|---------|
| 高清重绘 | imagen.apiyi.com | realesrgan-ncnn-vulkan |
| 矢量化 + 去背景 | Vector Magic (PC) | vtracer + rembg |
| 去水印 | gemini-watermark-remover (JS) | py-gemini-watermark-remover (Python) |

## 常见问题

**macOS 提示"无法验证开发者"**
```bash
xattr -cr /path/to/realesrgan-ncnn-vulkan
```

**rembg 首次运行很慢**
正在下载 U2-Net 模型（~170MB），后续运行会使用缓存。

**opencv-python 冲突**
如果已安装 `opencv-python-headless`，`py-gemini-watermark-remover` 的 `opencv-python` 依赖可能冲突。解决：
```bash
pip install opencv-python-headless
```

**矢量化效果不理想**
- 提高 `--color-precision`（默认 6，最高 8）
- 降低 `--filter-speckle`（默认 4，设为 1 保留更多细节）
- 对于线条图尝试 `--vtracer-colormode binary`
