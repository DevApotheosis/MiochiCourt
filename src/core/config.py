import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CASES_DIR = os.path.join(DATA_DIR, 'cases')
LAWS_DIR = os.path.join(DATA_DIR, 'laws')
EVIDENCE_DIR = os.path.join(DATA_DIR, 'evidence')
DIALOGUES_DIR = os.path.join(DATA_DIR, 'dialogues')
MODULES_DIR = os.path.join(DATA_DIR, 'modules')
MODS_DIR = os.path.join(PROJECT_ROOT, 'mods')
SAVES_DIR = os.path.join(DATA_DIR, 'saves')
ACHIEVEMENTS_DIR = os.path.join(DATA_DIR, 'achievements')
DOSSIER_DIR = os.path.join(DATA_DIR, 'dossiers')

RESOURCES_DIR = os.path.join(PROJECT_ROOT, 'resources')
IMAGES_DIR = os.path.join(RESOURCES_DIR, 'images')

DEFAULT_EVIDENCE_IMAGE = os.path.join(IMAGES_DIR, 'default_evidence.png')

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
TITLE = '澪地审判庭'

EVIDENCE_TYPES = {
    'physical': '实物证据',
    'document': '文档证据',
    'audio': '音频证据',
    'video': '视频证据',
    'testimony': '证人证言'
}

CASE_STATUS = {
    'investigation': '调查中',
    'court': '庭审中',
    'completed': '已完成'
}

GUILT_LEVELS = {
    'innocent': '无罪',
    'minor': '轻罪',
    'major': '重罪',
    'capital': '极刑'
}

ACHIEVEMENT_TYPES = {
    'first_case': '初出茅庐',
    'all_cases': '审判大师',
    'perfect_evidence': '完美取证',
    'high_trust': '心灵捕手',
    'law_expert': '法律专家',
    'speed_run': '神速审判',
    'first_verdict': '初次裁决'
}