import sys
import os

sys.setrecursionlimit(5000)

base_dir = os.path.dirname(os.path.abspath(__file__))

a = Analysis(
    [os.path.join(base_dir, 'run.py')],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'data'), 'data'),
        (os.path.join(base_dir, 'resources'), 'resources'),
        (os.path.join(base_dir, 'mods'), 'mods'),
    ],
    hiddenimports=[
        'src.core',
        'src.gui',
        'src.core.case_manager',
        'src.core.evidence',
        'src.core.law_system',
        'src.core.dialogue',
        'src.core.save_system',
        'src.core.character',
        'src.core.achievements',
        'src.core.config_manager',
        'src.core.module_manager',
        'src.core.dossier_system',
        'src.gui.main_frame',
        'src.gui.main_menu',
        'src.gui.case_selection',
        'src.gui.investigation_view',
        'src.gui.court_view',
        'src.gui.verdict_view',
        'src.gui.law_viewer',
        'src.gui.profile_view',
        'src.gui.achievement_view',
        'src.gui.shortcuts_settings',
        'src.gui.module_manager_gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='澪地审判庭',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='澪地审判庭',
)