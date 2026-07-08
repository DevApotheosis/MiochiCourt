# 存档系统

## 概述

存档系统负责游戏进度的保存和加载，支持手动存档、自动存档和多存档管理。

## 类结构

### GameSave 类

#### 属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| save_id | str | 存档唯一标识 |
| player_name | str | 玩家名称 |
| current_case_id | str | 当前案件ID |
| case_status | str | 案件状态 |
| evidence_collected | list | 已收集证据ID列表 |
| evidence_analyzed | list | 已分析证据ID列表 |
| witness_trust | dict | 证人信任度 |
| dialogue_history | list | 对话历史 |
| game_time | int | 游戏时长（分钟） |
| player_data | dict | 玩家数据 |
| case_progress | dict | 案件进度 |
| created_at | str | 创建时间 |
| updated_at | str | 更新时间 |

#### 案件状态

| 状态值 | 说明 |
|--------|------|
| investigation | 调查中 |
| court | 庭审中 |
| completed | 已完成 |

### SaveManager 类

#### 常量

| 常量名 | 值 | 说明 |
|--------|------|------|
| AUTO_SAVE_ID | 'auto_save' | 自动存档ID |

#### 方法

```python
def create_save(player_name, current_case_id, case_status):
    # 创建新存档

def auto_save(player_name, current_case_id, case_status, ...):
    # 自动保存（覆盖auto_save）

def save_game(save_id, current_case_id, case_status, ...):
    # 手动保存

def load_game(save_id):
    # 加载存档

def delete_save(save_id):
    # 删除存档

def get_all_saves():
    # 获取所有存档列表

def get_save_by_id(save_id):
    # 根据ID获取存档
```

## 自动存档机制

自动存档在以下时机触发：

1. 玩家点击"开始游戏"按钮后
2. 玩家成功完成一个案件后
3. 玩家收集证据时
4. 玩家分析证据时

## 关卡数据隔离

每个案件的进度独立存储在 `case_progress` 字典中，格式如下：

```python
case_progress = {
    'case_001': {
        'status': 'completed',
        'verdict': 'innocent',
        'reason': '证据链完整...',
        'evidence_collected': ['ev_001', 'ev_002'],
        'evidence_analyzed': ['ev_001']
    },
    'case_002': {
        'status': 'investigation',
        'evidence_collected': [],
        'evidence_analyzed': []
    }
}
```

## 使用示例

```python
from src.core.save_system import SaveManager

save_manager = SaveManager()

save_manager.auto_save(
    player_name='林律师',
    current_case_id='case_001',
    case_status='investigation',
    evidence_collected=['ev_001'],
    evidence_analyzed=[],
    witness_trust={'张三': 50},
    dialogue_history=[],
    game_time=30,
    player_data=character.to_dict(),
    case_progress={'case_001': {'status': 'investigation'}}
)

save = save_manager.load_game('auto_save')
saves = save_manager.get_all_saves()
```

## 文件路径

`src/core/save_system.py`

## 存档文件位置

存档文件存储在 `data/saves/` 目录下，文件名格式为 `{save_id}.json`。