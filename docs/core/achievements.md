# 成就系统

## 概述

成就系统负责管理游戏中的成就解锁和进度追踪。

## 类结构

### Achievement 类

#### 属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| achievement_id | str | 成就唯一标识 |
| name | str | 成就名称 |
| description | str | 成就描述 |
| unlocked | bool | 是否已解锁 |
| unlocked_at | str | 解锁时间 |
| icon | str | 成就图标 |

### AchievementManager 类

#### 方法

```python
def unlock_achievement(achievement_id):
    # 解锁指定成就

def is_unlocked(achievement_id):
    # 检查成就是否已解锁

def get_unlocked_achievements():
    # 获取已解锁成就列表

def get_locked_achievements():
    # 获取未解锁成就列表

def get_progress():
    # 获取成就进度（已解锁数/总数）

def save_to_file(player_name):
    # 保存成就数据

def load_from_file(player_name):
    # 加载成就数据
```

## 成就列表

| 成就ID | 名称 | 描述 | 解锁条件 |
|--------|------|------|----------|
| first_case | 初出茅庐 | 完成第一个案件的调查 | 开始第一个案件 |
| first_verdict | 初次裁决 | 在法庭上完成第一次裁决 | 完成第一次审判 |
| all_cases | 审判大师 | 完成所有案件 | 完成所有案件 |
| perfect_evidence | 完美取证 | 在一个案件中收集所有证据 | 收集全部证据 |
| high_trust | 心灵捕手 | 将证人信任度提升到100 | 证人信任度达到100 |
| law_expert | 法律专家 | 熟悉所有法律条文 | 引用所有法律 |
| speed_run | 神速审判 | 在30分钟内完成一个案件 | 快速完成案件 |
| key_evidence | 关键突破 | 发现关键证据 | 收集关键证据 |
| analyst | 分析大师 | 分析所有收集的证据 | 分析全部证据 |
| module_master | 模组专家 | 安装第一个模组 | 安装模组 |

## 使用示例

```python
from src.core.achievements import AchievementManager

# 创建成就管理器
achievement_manager = AchievementManager()

# 加载玩家成就
achievement_manager.load_from_file('林律师')

# 解锁成就
achievement_manager.unlock_achievement('first_verdict')

# 保存成就
achievement_manager.save_to_file('林律师')

# 获取进度
unlocked, total = achievement_manager.get_progress()
```

## 文件路径

`src/core/achievements.py`

## 成就数据位置

成就数据存储在 `data/achievements/` 目录下，文件名格式为 `{player_name}_achievements.json`。
