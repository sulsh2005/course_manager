# build.spec
block_cipher = None

# ��Ҫ����ĸ����ļ�
added_files = [
    ('data/*', 'data'),          # �����ļ���
    ('assets/icon.ico', '.'),    # ����ͼ��
    ('config/*.ini', 'config')   # �����ļ�
]

a = Analysis(
    ['src/course_manager/gui/main.py'],
    pathex=['.'], 
    binaries=[],
    datas=added_files,  # �ؼ�������
    hiddenimports=[
        'pandas',       # ��ʽ������������
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
    debug=False,         # ����ʱ��Ϊ False
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # ����ѹ��
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # ����ʾ����̨����
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # ����ͼ��·��
)