使用 PyInstaller 打包 Python 脚本并指定输出的可执行文件（EXE）的名称，你可以使用 `--name` 参数来设置。以下是用来打包代码并设置 EXE 名称为 `AutoFillForm_v7` 的 PyInstaller 命令：

```bash
pyinstaller --onefile --name AutoFillForm_v7 your_script.py
```

### 命令解释：

1. `--onefile`: 这个选项告诉 PyInstaller 将所有必要的文件打包成一个单独的可执行文件。没有这个参数，PyInstaller 会创建一个包含依赖和库的文件夹。

2. `--name AutoFillForm_v7`: 设置生成的 EXE 文件的名称为 `AutoFillForm_v7`。

3. `your_script.py`: 这应该替换为你要打包的 Python 脚本的文件名。

确保在运行此命令之前已经安装了 PyInstaller。如果未安装，可以通过以下 pip 命令进行安装：

```bash
pip install pyinstaller
```

### 附加选项：

- 如果你的脚本依赖于特定的文件夹或数据文件，你可能还需要使用 `--add-data` 选项指定这些资源。
- 对于图形界面应用，你可能想使用 `--windowed` 或 `--noconsole` 选项，这可以防止在应用运行时显示命令行窗口。

使用这条命令后，PyInstaller 将生成一个 `dist` 文件夹，在这个文件夹中你会找到名为 `AutoFillForm_v7.exe` 的可执行文件。