from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine-tuning.
build_options = {
    'packages': [],
    'excludes': [],
    'include_files': [
        ("ui/", "ui/"),
    ]}

base = 'gui'

executables = [
    Executable('main.py', base=base, target_name = 'LangtonsAnt')
]

setup(name="Langton's Ant",
      version = '1.0',
      description = "Implementation of famous Langton's ant in Python with Qt GUI framework PySide6",
      options = {'build_exe': build_options},
      executables = executables)
