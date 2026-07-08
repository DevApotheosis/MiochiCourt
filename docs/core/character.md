# 角色系统

## 概述

角色系统负责管理玩家角色的数据，包括名称、等级、经验值、技能和统计数据。

## 类结构

### Character 类

#### 属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | str | 玩家角色名称 |
| level | int | 角色等级 |
| experience | int | 当前经验值 |
| skills | dict | 技能字典，key为技能ID |
| stats | dict | 游戏统计数据 |

#### 等级体系

| 等级名称 | 经验范围 | 说明 |
|----------|----------|------|
| 实习律师 | 0-100 | 初始等级 |
| 初级律师 | 100-300 | 完成2-3个案件 |
| 三级律师 | 300-600 | 完成5-6个案件 |
| 二级律师 | 600-1000 | 完成8-10个案件 |
| 一级律师 | 1000+ | 最高等级 |

#### 方法

```python
def add_experience(amount):
    # 添加经验值，自动升级

def get_lawyer_rank():
    # 获取当前律师等级名称

def get_rank_index():
    # 获取等级索引（0-4）

def upgrade_skill(skill_id):
    # 升级指定技能

def update_stat(stat_name, value):
    # 更新统计数据

def to_dict():
    # 序列化为字典

@classmethod
def from_dict(data):
    # 从字典反序列化
```

### Skill 类

#### 属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| skill_id | str | 技能唯一标识 |
| name | str | 技能名称 |
| description | str | 技能描述 |
| level | int | 当前等级 |
| max_level | int | 最高等级 |

#### 技能列表

| 技能ID | 名称 | 效果 |
|--------|------|------|
| investigation | 调查技巧 | 提高证据收集效率 |
| persuasion | 说服能力 | 提高证人信任度获取 |
| analysis | 分析能力 | 提高证据分析速度 |
| law_knowledge | 法律知识 | 提高法律引用效果 |
| tech_skill | 技术能力 | 提高技术证据处理能力 |

## 使用示例

```python
from src.core.character import Character

# 创建角色
character = Character(name='林律师')

# 添加经验
character.add_experience(50)

# 获取等级
rank = character.get_lawyer_rank()  # '实习律师'

# 升级技能
character.upgrade_skill('investigation')

# 保存角色数据
data = character.to_dict()
```

## 文件路径

`src/core/character.py`
