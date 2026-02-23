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
cd /d E:\Projects\AutoFillForm\V2_selenium_pyautogui

:: 使用 PyInstaller 构建项目
pyinstaller --onefile --name %VERSION_NAME% --distpath=./releases/%VERSION_NAME%/dist --workpath=./releases/%VERSION_NAME%/build --specpath=./releases/%VERSION_NAME% %SCRIPT_NAME%

echo Build complete.

:: 复制 rules 文件夹
xcopy "./releases/RuleExamples" "./releases/%VERSION_NAME%/dist/rules" /E /H /C /I

:: 复制 README 文件
copy ".\releases\ReadMe\README.pdf" "./releases/%VERSION_NAME%/dist"

:: tar -acf "%VERSION_NAME%.tar" "./releases/%VERSION_NAME%/dist"
:: 打包成zip压缩文件
powershell Compress-Archive -Path "./releases/%VERSION_NAME%/dist/*" -DestinationPath "./releases/ReleasePakeages/%VERSION_NAME%.zip"

:: 结束
echo deployment complete.
endlocal