# 物性预测器打包说明

## 概述
本项目提供了将Python物性预测程序打包成独立exe文件的完整解决方案，方便没有Python环境的用户使用。

## 文件说明

### 新增文件
- `src/predict_gui.py` - GUI界面版本的预测程序
- `build.spec` - PyInstaller打包配置文件
- `build.bat` - Windows打包批处理脚本
- `BUILD_README.md` - 本说明文档

### 修改文件
- `requirements.txt` - 添加了pyinstaller和tkinter依赖

## 打包步骤

### 1. 准备工作
确保您的系统已安装Python 3.7+

### 2. 训练模型（如果尚未训练）
```bash
python src/train.py
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 开始打包
在Windows系统中，双击运行 `build.bat` 文件，或者在命令行中执行：
```bash
build.bat
```

或者手动执行PyInstaller命令：
```bash
pyinstaller build.spec
```

### 5. 获取可执行文件
打包完成后，可执行文件将位于 `dist/物性预测器.exe`

## GUI程序使用说明

### 功能特点
- 友好的图形界面
- 实时输入验证
- 清晰的结果显示
- 错误提示和异常处理

### 使用方法
1. 运行 `物性预测器.exe`
2. 在界面中输入浓度(X1)和温度(X2)值
3. 点击"开始预测"按钮
4. 查看预测结果显示区域的结果

### 输入要求
- 浓度(X1): 数值类型
- 温度(X2): 数值类型（摄氏度）

## 技术细节

### 打包配置
- 使用PyInstaller进行打包
- 包含所有必要的数据文件（models/, data/）
- 添加了sklearn相关的隐式导入
- 生成单文件可执行程序

### 依赖库
- pandas: 数据处理
- numpy: 数值计算
- scikit-learn: 机器学习模型
- joblib: 模型序列化
- tkinter: GUI界面
- pyinstaller: 打包工具

## 故障排除

### 常见问题
1. **模型文件未找到**: 确保先运行train.py训练模型
2. **依赖安装失败**: 检查Python版本和网络连接
3. **打包失败**: 查看错误信息，可能需要更新PyInstaller

### 兼容性
- Windows 7/8/10/11
- 不需要目标机器安装Python
- exe文件大小约50-100MB

## 分发说明
分发时只需要提供 `dist/物性预测器.exe` 文件即可，无需其他依赖。