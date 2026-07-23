# fake-star 风格指南 · Yuki Design System

> 利兹与青鸟 × 蜡笔颗粒感 × 玻璃童话
> 此方 & Yuki · 2026  
> 最后更新: 2026-07-23
> 已应用站点: 主站 · 音乐站 · 书签站

---

## 🎨 配色系统

| 名称 | 色值 | 用途 |
|------|------|------|
| 青蓝 | `#4A7A9A` | 主色，按钮/标题 |
| 浅青蓝 | `#7DAEC8` | 辅助色，次要元素 |
| 深青蓝 | `#2E5F78` | 强调色，深色文字 |
| 夕阳橙红 | `#E8683A` | 暖点缀，CTA 按钮 |
| 草绿 | `#7EB87E` | 自然色，标签/装饰 |
| 麦秆黄 | `#E8C87A` | 暖点缀，标签/装饰 |
| 珊瑚粉 | `#C4716E` | 辅助点缀色 |
| 画纸底色 | `#C4DFF0` | 页面背景（利兹与青鸟童话淡蓝） |
| 深灰文字 | `#2D2D2D` | 正文 |
| 浅灰文字 | `#6A6A6A` | 辅助文字 |

> **原则：** 青蓝为基底，夕阳橙红、草绿、麦秆黄注入温暖与生命力。蓝色不孤，冷暖平衡。

---

## 📄 纹理

- **颗粒噪点：** 全页覆盖 SVG 噪点滤镜（opacity 0.035），模拟蜡笔画纸粗糙感
- **CSS 实现：** 使用 feTurbulence 滤镜，不依赖外部图片

---

## 📝 字体

| 用途 | 字体 | fallback |
|------|------|----------|
| 标题 | `Noto Serif SC` | FangSong, 仿宋, FZFS, serif |
| 正文 | `Noto Serif SC` | FangSong, 仿宋, FZFS, serif |

- 字重：标题 600，正文 500
- 行高：2.1
- 抗锯齿：`-webkit-font-smoothing: antialiased`
- 渲染：`text-rendering: optimizeLegibility`

---

## 🧊 组件样式

### 毛玻璃卡片 (Glass Card)

```css
.glass-card {
  background: rgba(255,255,255,0.45);
  backdrop-filter: blur(28px) saturate(1.3);
  border-radius: 24px;
  padding: var(--sp6) var(--sp6) 80px;
  margin-bottom: 112px;
  border: 1px solid rgba(255,255,255,0.6);
  border-bottom: 1px solid rgba(255,255,255,0.3);
  box-shadow:
    0 2px 4px rgba(0,0,0,0.02),
    0 8px 24px rgba(0,0,0,0.04),
    0 20px 60px rgba(0,0,0,0.04),
    inset 0 1px 0 rgba(255,255,255,0.6);
}
```

### 按钮 (Button)

```css
.btn {
  padding: 12px 34px;
  border-radius: 30px;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.25s;
}

.btn-primary {
  background: var(--c-blue);
  color: white;
  box-shadow: 0 2px 8px rgba(74,122,154,0.2);
}
.btn-primary:hover {
  background: var(--c-blue-dk);
  transform: translateY(-2px);
}

.btn-warm {
  background: var(--c-warm);
  color: white;
}
.btn-warm:hover {
  background: #D45A2E;
  transform: translateY(-2px);
}
```

### 毛玻璃 Hero 按钮

```css
.hero-btn {
  padding: 10px 28px;
  border-radius: 30px;
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
}
```

### 标签页 (Tab)

```css
.tab {
  padding: 6px 18px; border-radius: 30px; font-size: 0.8rem;
  border: 1px solid rgba(74,122,154,0.15);
  background: rgba(255,255,255,0.3); color: var(--c-text-lt);
  transition: all 0.25s;
}
.tab.active {
  background: var(--c-blue); color: #fff; border-color: var(--c-blue);
  box-shadow: 0 2px 8px rgba(74,122,154,0.2);
}
```

### 浮动弹窗 (Modal)

```css
.modal-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(0,0,0,0.3); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
}
.modal-box {
  background: rgba(255,255,255,0.92); backdrop-filter: blur(28px);
  border-radius: 20px; padding: var(--sp4); max-width: 400px;
  border: 1px solid rgba(255,255,255,0.6);
}
```

### 链接行 (Link Item)

```css
.link-item {
  display: flex; align-items: center; gap: 14px; padding: 12px 16px;
  background: rgba(255,255,255,0.35); backdrop-filter: blur(12px);
  border-radius: 14px; border: 1px solid rgba(255,255,255,0.4);
  transition: all 0.2s;
}
.link-item:hover {
  background: rgba(255,255,255,0.55); transform: translateY(-2px);
}
```

---

## 📐 间距系统

```css
--sp: 8px;
--sp2: calc(var(--sp)*2);   /* 16px */
--sp3: calc(var(--sp)*3);   /* 24px */
--sp4: calc(var(--sp)*4);   /* 32px */
--sp6: calc(var(--sp)*6);   /* 48px */
--sp8: calc(var(--sp)*8);   /* 64px */

/* 关键间距 */
卡片上下间距:     112px
三栏卡片内部间距: 48px (gap)
内容侧边距:       48px
内容顶部内边距:   32px
内容底部内边距:   120px
三栏→按钮间距:   80px (margin-top)
```

---

## 🌅 整体氛围

- **背景：** Pixiv 画师插画作为固定壁纸（z-index: 0）
- **内容层：** 透明，壁纸透上，backdrop-filter 极淡模糊
- **风格：** 清透明亮、童话感、冷中带暖
- **布局：** Hero 全屏大图 → 毛玻璃内容区 → Footer

---

## 🐦 装饰主题

- **青鸟：** SVG 内嵌几何剪影（主站/音乐站已应用）
- **勿忘我：** SVG 内嵌五瓣小花藤蔓（主站已应用）
- **壁纸：** Pixiv 画师插画，三站各用不同图

---

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `预览.html` | 视觉预览页面（打开浏览器查看效果） |
| `STYLE_GUIDE.md` | Claude Code 设计规范参考 |
| `素材参考/` | Pixiv 壁纸原图存放 |

---

_此风格指南供 Claude Code 在开发功能站时参考。所有功能站应统一使用此设计语言。_
