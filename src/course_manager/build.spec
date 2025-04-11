# build.spec
block_cipher = None

# 需要打包的附加文件
added_files = [
    ('data/*', 'data'),          # 数据文件夹
    ('assets/icon.ico', '.'),    # 程序图标
    ('config/*.ini', 'config')   # 配置文件
]

a = Analysis(
    ['src/course_manager/gui/main.py'],
    pathex=['.'], 
    binaries=[],
    datas=added_files,  # 关键配置项
    hiddenimports=[
        'pandas',       # 显式声明隐藏依赖
        'openpyxl',
        'tkinter.filedialog'
    ],  
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts, 
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CourseManager',
    debug=False,         # 发布时设为 False
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # 启用压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # 程序图标路径
)