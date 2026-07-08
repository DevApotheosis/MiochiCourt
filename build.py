import sys
import os
import subprocess
import shutil
import time
import threading

def install_pyinstaller():
    print('正在安装 PyInstaller...')
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
        check=True,
        capture_output=True,
        text=True
    )
    print('PyInstaller 安装完成')

def collect_data_files(base_dir):
    data_files = []
    data_dir = os.path.join(base_dir, 'data')
    
    if os.path.exists(data_dir):
        for root, dirs, files in os.walk(data_dir):
            for filename in files:
                if filename.endswith('.json'):
                    src_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(root, base_dir)
                    data_files.append((src_path, rel_path))
    
    return data_files

def build_executable():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_script = os.path.join(base_dir, 'run.py')
    output_dir = os.path.join(base_dir, 'dist')
    build_dir = os.path.join(base_dir, 'build')
    spec_dir = os.path.join(base_dir, 'spec')
    
    for d in [output_dir, build_dir, spec_dir]:
        os.makedirs(d, exist_ok=True)
    
    data_files = collect_data_files(base_dir)
    
    args = [
        sys.executable, '-m', 'PyInstaller',
        '--name', '澪地审判庭',
        '--onefile',
        '--windowed',
        '--distpath', output_dir,
        '--workpath', build_dir,
        '--specpath', spec_dir,
        '--add-data', f'{os.path.join(base_dir, "data")}{os.pathsep}data',
        entry_script
    ]
    
    print(f'开始打包，输出目录: {output_dir}')
    
    def progress_printer():
        while True:
            print('打包中...')
            time.sleep(0.5)
    
    progress_thread = threading.Thread(target=progress_printer, daemon=True)
    progress_thread.start()
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        progress_thread.join(timeout=1)
        
        if result.returncode == 0:
            print('\n打包成功!')
            print(f'输出文件位于: {output_dir}')
            return True
        else:
            print('\n打包失败!')
            print('错误信息:')
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print('\n打包超时!')
        return False
    except Exception as e:
        print(f'\n打包异常: {e}')
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
        print('\n打包完成!')
    else:
        print('\n打包失败，请检查错误信息')