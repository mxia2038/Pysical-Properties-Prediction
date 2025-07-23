@echo off
echo 正在构建物性预测器...
echo.

echo 1. 安装依赖...
.venv\Scripts\pip.exe install -r requirements.txt

echo.
echo 2. 检查模型文件...
if not exist "models\pipelines_by_target.pkl" (
    echo 错误：未找到训练好的模型文件！
    echo 请先运行 .venv\Scripts\python.exe src/train.py 训练模型
    pause
    exit /b 1
)

echo.
echo 3. 开始打包...
.venv\Scripts\pyinstaller.exe build.spec

echo.
echo 4. 打包完成！
echo 可执行文件位置：dist\氯碱工业理化常数计算软件V1.0.exe
echo.

echo 5. 清理临时文件...
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__
if exist "src\__pycache__" rmdir /s /q src\__pycache__

echo.
echo 构建完成！可执行文件已保存到 dist 目录
pause