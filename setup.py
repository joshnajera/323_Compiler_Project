from cx_Freeze import setup, Executable

base = None


executables = [Executable("syntax_analyzer.py", base=base)]

packages = ["codecs"]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "syntaxAnalyzer-JoshNajera",
    options = options,
    version = "1",
    description = 'Analyzes syntax of a rat17f program',
    executables = executables
)