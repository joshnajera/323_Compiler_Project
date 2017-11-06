# -*- mode: python -*-

block_cipher = None


a = Analysis(['syntax_analyzer.py'],
             pathex=['C:\\Users\\ap0c\\Documents\\Git\\323_Compiler_Project'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='syntax_analyzer',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
