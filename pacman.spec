a = Analysis(['pac-man.py'])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='pacman',
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='pacman',
)
