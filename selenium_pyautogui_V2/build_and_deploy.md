下面是批处理脚本的更新版本，其中包括对 Python 脚本文件名的参数化处理：

```bat
@echo off
setlocal

:: 检查是否提供了足够的参数
if "%~1"=="" (
    echo Please provide a version name.
    exit /b 1
)
if "%~2"=="" (
    echo Please provide a script file name.
    exit /b 1
)

:: 设置版本名称和脚本文件名
set VERSION_NAME=%~1
set SCRIPT_NAME=%~2

:: 切换到项目目录
cd /d E:\Projects\AutoFillForm\selenium_pyautogui_V2

:: 使用 PyInstaller 构建项目
pyinstaller --onefile --name %VERSION_NAME% --distpath=./releases/%VERSION_NAME%/dist --workpath=./releases/%VERSION_NAME%/build --specpath=./releases/%VERSION_NAME%  %SCRIPT_NAME%

:: 复制 rules 文件夹
xcopy "./rules" "./releases/%VERSION_NAME%/dist/rules" /E /H /C /I

:: 复制 README 文件
copy ".\releases\ReadMe\README.pdf" "./releases/%VERSION_NAME%/dist"

:: 结束
echo Build and deployment complete.
endlocal
```

### 使用说明：

- 运行此批处理文件时，你需要提供两个参数：版本名称和 Python 脚本的文件名。例如：
  ```bash
  build_and_deploy.bat AutoFillForm_v9 v9.py
  ```
- 这将构建名为 `AutoFillForm_v9` 的版本，使用名为 `v9.py` 的脚本。

这种方法提高了脚本的灵活性和通用性，使你能够针对不同的脚本和版本轻松地构建和部署。



------


在 Windows 中，你可以使用命令行工具如 PowerShell 来将文件打包成 ZIP 文件。这是一个简单而强大的方法，特别是当你想自动化文件打包过程时。以下是如何使用 PowerShell 创建 ZIP 文件的步骤：

### 使用 PowerShell 压缩文件

1. 打开 PowerShell。
2. 使用以下命令来压缩文件夹或文件：

   ```powershell
   Compress-Archive -Path 'C:\path\to\your\files' -DestinationPath 'C:\path\to\your\output.zip'
   ```

   - `-Path` 参数指定了要压缩的文件或文件夹的路径。你可以列出多个文件或文件夹，用逗号隔开。
   - `-DestinationPath` 参数指定了生成的 ZIP 文件的存储路径。

### 示例

假设你想将 `C:\Users\Example\Documents` 目录中的所有文件压缩到 `C:\Users\Example\Documents.zip` 中，你可以使用如下命令：

```powershell
Compress-Archive -Path 'C:\Users\Example\Documents\*' -DestinationPath 'C:\Users\Example\Documents.zip'
```

### 压缩指定的多个文件

如果你只想压缩某个文件夹中的特定文件，你可以具体指定这些文件的名称：

```powershell
Compress-Archive -Path 'C:\Users\Example\Documents\File1.txt', 'C:\Users\Example\Documents\File2.txt' -DestinationPath 'C:\Users\Example\SelectedFiles.zip'
```

### 使用选项

PowerShell 的 `Compress-Archive` 命令还有一些有用的选项，比如：

- `-Update`：如果 ZIP 文件已经存在，这个选项允许你向其中添加或更新文件。
- `-CompressionLevel`：允许你设置压缩级别（Optimal, Fastest, NoCompression）。

### 扩展用法

如果需要在一个批处理脚本中使用 PowerShell 命令，你可以在 CMD 或批处理文件中调用 PowerShell：

```bat
powershell -command "Compress-Archive -Path 'C:\path\to\files' -DestinationPath 'C:\path\to\output.zip'"
```

这些方法提供了一个强大的工具来自动化和简化文件管理任务。