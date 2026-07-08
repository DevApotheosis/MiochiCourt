# 模组开发指南

## 概述

本指南介绍如何为《澪地审判庭》开发自定义模组。模组系统允许开发者扩展游戏内容，包括新增案件、法律条文、证据类型和对话内容。

## 文件结构规范

### 模组目录结构

```
my_module/                    # 模组根目录（目录名即为module_id）
├── module.json               # 模组配置文件（必填）
├── cases/                    # 案件数据目录
│   └── case_xxx.json         # 案件定义文件
├── evidence/                 # 证据数据目录
│   └── case_xxx.json         # 证据定义文件（与案件ID对应）
├── laws/                     # 法律数据目录
│   └── category_laws.json    # 法律定义文件
├── dialogues/                # 对话数据目录
│   └── case_xxx.json         # 对话定义文件（与案件ID对应）
├── images/                   # 图片资源目录（可选）
│   ├── evidence/             # 证据图片
│   └── witness/              # 证人图片
└── README.md                 # 模组说明文档（推荐）
```

### 命名约定

| 文件/目录 | 命名规则 | 示例 |
|-----------|----------|------|
| 模组目录 | 小写字母+下划线 | `cyber_crime_case` |
| 案件文件 | `case_{ID}.json` | `case_001.json` |
| 证据文件 | `{案件ID}.json` | `case_001.json` |
| 法律文件 | `{类别}_laws.json` | `cyber_laws.json` |
| 对话文件 | `{案件ID}.json` | `case_001.json` |
| 图片文件 | `evidence_{ID}.png` | `evidence_ev_001.png` |

## 模组配置文件

### module.json 格式

```json
{
    "module_id": "cyber_crime_case",
    "name": "网络犯罪案件包",
    "version": "1.0.0",
    "author": "开发者名称",
    "description": "包含3个网络犯罪相关案件和10条相关法律",
    "cases": ["case_001", "case_002", "case_003"],
    "laws": ["cyber_laws"],
    "evidence": ["case_001", "case_002", "case_003"],
    "dialogues": ["case_001", "case_002", "case_003"],
    "dependencies": [],
    "compatible_version": "1.0.0"
}
```

### 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| module_id | string | 是 | 模组唯一标识 |
| name | string | 是 | 模组显示名称 |
| version | string | 是 | 版本号（语义化版本） |
| author | string | 是 | 作者名称 |
| description | string | 是 | 模组描述 |
| cases | array | 否 | 包含的案件ID列表 |
| laws | array | 否 | 包含的法律文件列表 |
| evidence | array | 否 | 包含的证据文件列表 |
| dialogues | array | 否 | 包含的对话文件列表 |
| dependencies | array | 否 | 依赖的其他模组ID |
| compatible_version | string | 否 | 兼容的游戏版本 |

## 可扩展API

### Case API

#### 创建案件

```python
from src.core.case_manager import Case

case = Case(
    case_id='case_001',
    title='黑客入侵案',
    description='被告被指控非法入侵公司服务器...',
    defendant='张三',
    plaintiff='科技公司',
    location='北京市海淀区',
    time='2026-07-15',
    difficulty=2,
    required_evidence=['ev_001', 'ev_002'],
    key_laws=['law_001'],
    witnesses=['李四', '王五'],
    allow_roles=['defense', 'prosecution']
)
```

#### 案件数据格式

```json
{
    "case_id": "case_001",
    "title": "黑客入侵案",
    "description": "被告被指控非法入侵公司服务器...",
    "defendant": "张三",
    "plaintiff": "科技公司",
    "location": "北京市海淀区",
    "time": "2026-07-15",
    "difficulty": 2,
    "required_evidence": ["ev_001", "ev_002"],
    "key_laws": ["law_001"],
    "witnesses": ["李四", "王五"],
    "background": "案件背景故事...",
    "parties": {
        "defendant": {"name": "张三", "role": "被告"},
        "plaintiff": {"name": "科技公司", "role": "原告"}
    },
    "tags": ["网络犯罪", "刑事案件"],
    "allow_roles": ["defense", "prosecution"]
}
```

#### allow_roles 字段说明

`allow_roles` 字段用于限制玩家在该案件中可以担任的角色，增加游戏玩法多样性。

| 值 | 说明 |
|----|------|
| `defense` | 被告律师 |
| `prosecution` | 原告律师 |

**示例**:

- 仅允许担任被告律师：`"allow_roles": ["defense"]`
- 仅允许担任原告律师：`"allow_roles": ["prosecution"]`
- 两种角色都允许（默认）：`"allow_roles": ["defense", "prosecution"]`

如果玩家选择的角色不在案件的 `allow_roles` 列表中，系统会显示权限不足的提示，禁止进入该案件。

### Evidence API

#### 创建证据

```python
from src.core.evidence import Evidence

evidence = Evidence(
    evidence_id='ev_001',
    name='服务器日志',
    evidence_type='document',
    description='包含入侵记录的服务器日志',
    location='公司服务器机房',
    is_key=True,
    details={'format': 'JSON', 'size': '10MB'}
)
```

#### 证据类型

| 类型 | 说明 | 特点 |
|------|------|------|
| document | 文档证据 | 包含文本、数据表格 |
| video | 视频证据 | 包含监控录像 |
| audio | 音频证据 | 包含录音、语音 |
| physical | 物证 | 实物证据 |
| testimony | 证言 | 证人陈述 |
| digital | 数字证据 | 区块链/加密数据 |
| network | 网络证据 | 网络流量分析 |
| forensic | 取证证据 | 司法鉴定报告 |
| financial | 财务证据 | 资金流水 |
| expert | 专家证言 | 专家意见 |

### Law API

#### 创建法律条文

```python
from src.core.law_system import Law

law = Law(
    law_id='law_001',
    title='刑法第285条',
    category='刑事',
    severity='严重',
    content='违反国家规定，侵入国家事务、国防建设、尖端科学技术领域的计算机信息系统的，处三年以下有期徒刑或者拘役...',
    related_articles=['第286条', '第287条']
)
```

### Dialogue API

#### 创建对话

```python
from src.core.dialogue import Dialogue

dialogue = Dialogue(
    dialogue_id='dia_001',
    speaker='李四',
    text='我那天晚上确实看到有人在服务器机房附近...',
    case_id='case_001',
    choices=[
        {'text': '你能描述那个人的特征吗？', 'next_dialogue': 'dia_002', 'effect': {'trust': 5}},
        {'text': '你确定是那天晚上吗？', 'next_dialogue': 'dia_003', 'effect': {'trust': -5}}
    ]
)
```

## 开发工作流程

### 1. 创建模组项目

```bash
mkdir my_module
cd my_module
mkdir cases evidence laws dialogues images
touch module.json
```

### 2. 编写配置文件

编辑 `module.json`，填写模组基本信息。

### 3. 开发内容

按照需求开发案件、证据、法律和对话数据。

### 4. 测试模组

```python
from src.core.module_manager import ModuleManager

manager = ModuleManager()
manager.install_module('/path/to/my_module')
manager.load_modules()

modules = manager.get_all_modules()
print(f'已安装模组: {[m.name for m in modules]}')
```

### 5. 打包发布

将模组目录打包为 ZIP 文件：

```bash
zip -r my_module.zip my_module/
```

### 6. 发布渠道

- 游戏内置模组商店
- 第三方模组平台
- GitHub/Gitee 仓库

## 模组开发示例

### 示例1：新增案件模组

**module.json**

```json
{
    "module_id": "financial_fraud_case",
    "name": "金融诈骗案件",
    "version": "1.0.0",
    "author": "LegalDev",
    "description": "包含1个金融诈骗案件",
    "cases": ["case_fin_001"],
    "evidence": ["case_fin_001"],
    "dialogues": ["case_fin_001"]
}
```

**cases/case_fin_001.json**

```json
{
    "case_id": "case_fin_001",
    "title": "理财产品诈骗案",
    "description": "被告利用虚假理财产品骗取投资者资金...",
    "defendant": "赵六",
    "plaintiff": "投资者协会",
    "location": "上海市浦东新区",
    "time": "2026-06-20",
    "difficulty": 3,
    "required_evidence": ["ev_fin_001", "ev_fin_002"],
    "witnesses": ["钱七", "孙八"]
}
```

### 示例2：新增法律模组

**module.json**

```json
{
    "module_id": "financial_laws",
    "name": "金融法律包",
    "version": "1.0.0",
    "author": "LegalDev",
    "description": "包含金融相关法律条文",
    "laws": ["financial_laws"]
}
```

**laws/financial_laws.json**

```json
[
    {
        "law_id": "law_fin_001",
        "title": "刑法第192条",
        "category": "刑事",
        "severity": "严重",
        "content": "以非法占有为目的，使用诈骗方法非法集资，数额较大的，处五年以下有期徒刑或者拘役...",
        "related_articles": ["第193条", "第266条"]
    }
]
```

### 示例3：新增证据类型模组

**module.json**

```json
{
    "module_id": "digital_evidence_pack",
    "name": "数字证据包",
    "version": "1.0.0",
    "author": "TechDev",
    "description": "新增区块链和加密货币相关证据",
    "evidence": ["case_crypto_001"]
}
```

**evidence/case_crypto_001.json**

```json
[
    {
        "evidence_id": "ev_crypto_001",
        "name": "区块链交易记录",
        "evidence_type": "digital",
        "description": "包含被告钱包地址的区块链交易流水",
        "location": "区块链网络",
        "is_key": true,
        "details": {
            "format": "CSV",
            "blockchain": "Ethereum",
            "wallet_address": "0x7f3a..."
        }
    },
    {
        "evidence_id": "ev_crypto_002",
        "name": "智能合约代码",
        "evidence_type": "digital",
        "description": "可疑的智能合约源代码",
        "location": "区块链网络",
        "is_key": false,
        "details": {
            "format": "Solidity",
            "contract_address": "0x9e2b...",
            "verified": true
        }
    }
]
```

## 最佳实践

### 性能优化

1. 数据懒加载: 只在需要时加载案件数据
2. 图片压缩: 使用合适的图片格式和尺寸
3. 缓存机制: 缓存已加载的模组数据

### 兼容性

1. 版本检查: 在模组中声明兼容的游戏版本
2. 向后兼容: 确保旧版本存档能正常加载
3. 错误处理: 添加完善的错误处理和回退机制

### 安全性

1. 数据验证: 验证所有用户输入数据
2. 路径安全: 避免路径遍历攻击
3. 代码审查: 定期审查模组代码

## 常见问题

### Q: 模组安装后不显示怎么办？

**A:** 检查以下事项：
1. 模组目录名是否符合命名规范
2. `module.json` 是否存在且格式正确
3. 所有引用的文件是否存在

### Q: 如何调试模组？

**A:** 在模组代码中添加日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('模组加载成功')
```

### Q: 模组可以包含Python代码吗？

**A:** 当前版本的模组系统只支持JSON数据文件。如需自定义逻辑，需要修改游戏源代码。

## 文件路径

- 模组系统核心: `src/core/module_manager.py`
- 模组管理界面: `src/gui/module_manager_gui.py`
- 模组存储目录: `data/modules/`