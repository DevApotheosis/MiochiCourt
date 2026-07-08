# 双结局判定系统

## 概述

双结局判定系统负责在法庭最终陈述阶段决定案件的判决结果，支持辩护成功/失败和诉讼成功/失败两种结果分支。

## 判定逻辑

### 判定条件

判决结果基于以下因素综合判定：

| 因素 | 权重 | 说明 |
|------|------|------|
| 证据分 | 30% | 提出证据获得的分数 |
| 法律分 | 30% | 引用法律获得的分数 |
| 证言分 | 20% | 盘问证人获得的分数 |
| 法官态度 | 20% | 法庭过程中法官的态度变化 |

### 成功条件

```
总分 >= 40 且 法官态度 >= 40
```

如果收集了至少一半的关键证据，成功阈值降低为 30。

### 失败条件

```
总分 < 40 或 法官态度 < 40
```

## 结局类型

### 辩护场景

| 判决结果 | 结局类型 | 说明 |
|----------|----------|------|
| 无罪 | defense_success | 辩护成功，被告无罪释放 |
| 有罪 | defense_failure | 辩护失败，被告有罪判决 |

### 诉讼场景

| 判决结果 | 结局类型 | 说明 |
|----------|----------|------|
| 胜诉 | prosecution_success | 诉讼成功，原告胜诉 |
| 败诉 | prosecution_failure | 诉讼失败，原告败诉 |

## 评分计算

### 证据分

```python
if evidence.is_key:
    points = 15
    judge_mood += 10
else:
    points = 5
    judge_mood -= 5
```

### 法律分

```python
points = 15
judge_mood += 5
```

### 证言分

```python
points = 10
```

## 判决理由生成

系统会随机选择判决理由，增加游戏的多样性：

### 成功理由

| 序号 | 理由 |
|------|------|
| 1 | 证据链完整，能够证明被告无罪 |
| 2 | 辩方提供的证据和法律依据充分，足以推翻指控 |
| 3 | 证人证言与物证相互印证，形成完整的证据体系 |
| 4 | 控方证据存在重大瑕疵，无法排除合理怀疑 |
| 5 | 被告的行为符合法律规定的免责情形 |

### 失败理由

| 序号 | 理由 |
|------|------|
| 1 | 现有证据无法证明被告无罪，存在重大嫌疑 |
| 2 | 辩方未能提供充分证据反驳控方指控 |
| 3 | 证人证言存在矛盾，可信度不足 |
| 4 | 法律适用不当，未能有效辩护 |
| 5 | 综合全案证据，无法排除被告作案嫌疑 |

## 经验值奖励

案件完成后根据判决结果给予经验值奖励：

| 判决结果 | 基础奖励 | 难度加成 |
|----------|----------|----------|
| 成功 | 50 | difficulty × 10 |
| 失败 | 25 | difficulty × 10 |

## 关键代码位置

```python
# 最终陈述判定逻辑
def on_final_statement(self):
    total_score = self.evidence_points + self.law_points + self.witness_points
    key_collected = len(self.current_case.evidence_manager.get_key_evidence())
    total_key = len(self.current_case.required_evidence)
    
    success_threshold = 40
    if key_collected >= total_key // 2:
        success_threshold = 30
    
    if total_score >= success_threshold and self.judge_mood >= 40:
        verdict = 'innocent'
        outcome_type = 'defense_success' if self.current_case.defendant else 'prosecution_success'
    else:
        verdict = 'major'
        outcome_type = 'defense_failure' if self.current_case.defendant else 'prosecution_failure'
```

## 文件路径

`src/gui/court_view.py`
