# 图片资源管理

## 概述

图片资源管理规范定义了游戏中各类图片的存放路径和命名规则。

## 目录结构

```
resources/
└── images/
    ├── evidence/          # 证据图片
    ├── witness/           # 证人图片
    ├── backgrounds/       # 背景图片
    ├── icons/             # 图标图片
    └── default/           # 默认图片
```

## 路径配置

图片路径在 `src/core/config.py` 中定义：

```python
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'images')
DEFAULT_EVIDENCE_IMAGE = os.path.join(IMAGES_DIR, 'default', 'default_evidence.png')
DEFAULT_WITNESS_IMAGE = os.path.join(IMAGES_DIR, 'default', 'default_witness.png')
```

## 命名规范

### 证据图片

```
evidence_{证据ID}.png
```

示例：
- `evidence_ev_001.png`
- `evidence_ev_002.png`

### 证人图片

```
witness_{证人姓名}.png
```

示例：
- `witness_张三.png`
- `witness_李四.png`

### 背景图片

```
bg_{场景名称}.png
```

示例：
- `bg_court.png`
- `bg_investigation.png`

### 图标图片

```
icon_{功能名称}.png
```

示例：
- `icon_evidence.png`
- `icon_law.png`

## 图片格式要求

| 属性 | 要求 |
|------|------|
| 格式 | PNG（推荐）或 JPG |
| 大小 | 建议不超过 512×512 |
| 透明 | 支持透明度 |
| 颜色 | RGB 色彩模式 |

## 默认图片处理

当指定路径的图片不存在时，使用默认图片：

```python
image_path = os.path.join(IMAGES_DIR, f'witness_{witness_name}.png')

if not os.path.exists(image_path):
    image_path = os.path.join(IMAGES_DIR, 'default', 'default_witness.png')
```

## 图片加载

使用 Pillow 库加载和处理图片：

```python
from PIL import Image, ImageTk

image = Image.open(image_path)
image = image.resize((width, height), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(image)
```

## 文件路径

- 图片资源目录: `resources/images/`
- 配置文件: `src/core/config.py`
