# 澪地审判庭

一款法庭主题的文字冒险游戏，玩家扮演律师，通过收集证据、引用法律，在法庭上为被告辩护或代表原告诉讼。

## 功能特点

- **案件调查系统**: 收集和分析多种类型的证据（文档、视频、音频、物证、证言等）
- **法庭审判系统**: 在法庭上提出证据、引用法律条文、盘问证人
- **双角色玩法**: 可选择担任被告律师或原告律师，体验不同的游戏视角
- **双结局判定**: 根据证据链完整性和法庭表现决定案件胜负
- **成就系统**: 解锁各种游戏成就，记录你的律师生涯
- **等级系统**: 通过完成案件提升律师等级和声望
- **模组支持**: 支持自定义案件、法律和对话内容的模组扩展

## 安装步骤

### 环境要求

- Python 3.10 或更高版本
- Windows 10/11 操作系统

### 安装方法

1. **下载代码**

   ```bash
   git clone https://github.com/MiochiCourt/MiochiCourt.git
   cd MiochiCourt
   ```

2. **安装依赖**

   ```bash
   pip install pillow requests
   ```

3. **运行游戏**

   ```bash
   python run.py
   ```

## 使用方法

### 游戏流程

1. **开始游戏**: 点击主菜单的"开始游戏"按钮
2. **选择案件**: 在案件选择界面选择想要处理的案件
3. **调查阶段**: 收集证据、分析证据、与证人对话
4. **法庭阶段**: 在法庭上提出证据、引用法律、进行最终陈述
5. **判决结果**: 根据法庭表现获得判决结果和经验值

### 界面说明

- **主菜单**: 包含开始游戏、读取存档、设置、退出等选项
- **案件选择**: 显示所有可用案件及其进度状态
- **调查界面**: 显示调查地点、证据列表、证人对话选项
- **法庭界面**: 包含证据提出、法律引用、最终陈述等功能按钮
- **判决界面**: 显示判决结果和理由

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+C | 收集证据 |
| Ctrl+A | 分析证据 |
| Ctrl+I | 盘问证人 |
| Ctrl+L | 查询法律 |
| Ctrl+B | 返回上一级 |
| Ctrl+E | 进入法庭 |
| Esc | 退出当前界面 |

**自定义快捷键**: 在设置界面可以根据个人习惯修改快捷键配置。

## 常见问题解决

### PyInstaller打包错误

**问题**: `ERROR: Unable to find 'D:\a\MiochiCourt\MiochiCourt\spec\data' when adding binary and data files.`

**原因**: 使用命令行参数`--specpath spec`时，PyInstaller会切换工作目录到spec目录，导致相对路径`data`无法正确解析。

**解决方案**: 使用spec文件进行打包，并在spec文件中使用绝对路径引用数据目录：

```python
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

a = Analysis(
    [os.path.join(base_dir, 'run.py')],
    datas=[
        (os.path.join(base_dir, 'data'), 'data'),
        (os.path.join(base_dir, 'resources'), 'resources'),
    ],
    # ...
)
```

### 游戏运行时找不到数据文件

**问题**: 运行打包后的exe文件时，提示找不到data目录或json文件。

**原因**: 打包时数据文件没有正确包含到输出目录中。

**解决方案**: 
1. 确保spec文件中的datas配置正确
2. 使用`onedir`模式打包（在spec文件中移除`--onefile`参数）
3. 手动检查dist目录是否包含data文件夹

### 模组无法加载

**问题**: 安装的模组在游戏中不显示。

**原因**: 模组目录结构不正确或配置文件格式错误。

**解决方案**:
1. 检查模组目录名是否符合命名规范（小写字母+下划线）
2. 确保`module.json`文件存在且格式正确
3. 检查所有引用的文件是否存在于正确位置

## 项目结构

```
MiochiCourt/
├── src/                    # 源代码目录
│   ├── core/              # 核心逻辑模块
│   └── gui/               # 图形界面模块
├── data/                  # 游戏数据目录
│   ├── cases/             # 案件数据
│   ├── evidence/          # 证据数据
│   ├── laws/              # 法律数据
│   ├── dialogues/         # 对话数据
│   └── achievements/      # 成就数据
├── mods/                  # 模组目录
├── resources/             # 资源文件
│   └── images/            # 图片资源
├── docs/                  # 开发文档
├── tests/                 # 测试文件
├── city_qes.spec          # PyInstaller打包配置
├── run.py                 # 启动脚本
└── README.md              # 项目说明
```

## 开发

### 运行测试

```bash
python -m unittest discover -s tests
```

### 打包发布

```bash
python -m PyInstaller city_qes.spec --distpath dist --workpath build --specpath spec
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。