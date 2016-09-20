from cx_Freeze import setup, Executable

exe = Executable(
    script="cocomud.py",
    base="Win32GUI",
)

includefiles = [
    "translations",
    "../dolapi.dll",
    "../jfwapi.dll",
    "../nvdaControllerClient.dll",
    "../SAAPI32.dll",
    "../UniversalSpeech.dll",
    "../settings",
]

setup(
    name = "CocoMUD client",
    version = "0.1",
    description = "The CocoMUD client.",
    options = {'build_exe': {'include_files': includefiles}},
    executables = [exe]
)
