import sys
import os
import subprocess
import shutil
import time


def install_pyinstaller():
    print('正在安装 PyInstaller...')
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
        check=True,
        capture_output=True,
        text=True
    )
    print('PyInstaller 安装完成')


def get_include_files(base_dir):
    include_files = []
    
    data_dir = os.path.join(base_dir, 'data')
    if os.path.exists(data_dir):
        include_files.append((data_dir, 'data'))
    
    resources_dir = os.path.join(base_dir, 'resources')
    if os.path.exists(resources_dir):
        include_files.append((resources_dir, 'resources'))
    
    mods_dir = os.path.join(base_dir, 'mods')
    if os.path.exists(mods_dir):
        include_files.append((mods_dir, 'mods'))
    
    return include_files


def build_executable():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_script = os.path.join(base_dir, 'run.py')
    output_dir = os.path.join(base_dir, 'dist')
    build_dir = os.path.join(base_dir, 'build')
    spec_dir = os.path.join(base_dir, 'spec')
    
    for d in [output_dir, build_dir, spec_dir]:
        os.makedirs(d, exist_ok=True)
    
    include_files = get_include_files(base_dir)
    
    spec_content = f'''import sys
import os

sys.setrecursionlimit(5000)

base_dir = r'{base_dir}'

a = Analysis(
    [os.path.join(base_dir, 'run.py')],
    pathex=[base_dir],
    binaries=[],
    datas={include_files},

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
    hooksconfig={{}},
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
'''
    
    spec_file = os.path.join(spec_dir, 'city_qes.spec')
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f'开始打包，输出目录: {output_dir}')
    
    start_time = time.time()
    
    args = [
        sys.executable, '-m', 'PyInstaller',
        spec_file,
        '--distpath', output_dir,
        '--workpath', build_dir,
    ]
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f'\\n打包成功!')
            print(f'耗时: {elapsed_time:.2f}秒')
            print(f'输出文件位于: {output_dir}')
            
            output_app_dir = os.path.join(output_dir, '澪地审判庭')
            if os.path.exists(output_app_dir):
                exe_path = os.path.join(output_app_dir, '澪地审判庭.exe')
                if os.path.exists(exe_path):
                    file_size = os.path.getsize(exe_path) / (1024 * 1024)
                    print(f'主程序大小: {file_size:.2f} MB')
                    
                    total_size = 0
                    for root, dirs, files in os.walk(output_app_dir):
                        for f in files:
                            total_size += os.path.getsize(os.path.join(root, f))
                    total_size_mb = total_size / (1024 * 1024)
                    print(f'总大小: {total_size_mb:.2f} MB')
            
            return True
        else:
            print(f'\\n打包失败!')
            print('错误信息:')
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f'\\n打包超时!')
        return False
    except Exception as e:
        print(f'\\n打包异常: {e}')
        return False


def cleanup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(base_dir, 'build')
    spec_dir = os.path.join(base_dir, 'spec')
    
    for d in [build_dir, spec_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f'清理目录: {d}')


if __name__ == '__main__':
    print('=' * 50)
    print('澪地审判庭 - 打包脚本')
    print('=' * 50)
    
    try:
        import PyInstaller
        print('PyInstaller 已安装')
    except ImportError:
        install_pyinstaller()
    
    success = build_executable()
    
    if success:
        cleanup()
        print('\\n打包完成!')
    else:
        print('\\n打包失败，请检查错误信息')