# Claude Code Environment Setup

## Environment Details
- Platform: WSL2 (Windows Subsystem for Linux)
- Python Virtual Environment: `D:\Prediction\.venv` (Windows) / `/mnt/d/Prediction/.venv` (WSL)
- Working Directory: `/mnt/d/Prediction`

## Commands to Run Python
```bash
# From WSL2 bash terminal
/mnt/d/Prediction/.venv/Scripts/python.exe <script.py>

# Or with PyInstaller
/mnt/d/Prediction/.venv/Scripts/pyinstaller.exe build.spec
```

## Common Tasks
- **Train models**: `/mnt/d/Prediction/.venv/Scripts/python.exe src/train.py`
- **Run GUI**: `/mnt/d/Prediction/.venv/Scripts/python.exe src/predict_gui.py`
- **Build executable**: `/mnt/d/Prediction/.venv/Scripts/pyinstaller.exe build.spec`
- **Test functionality**: `/mnt/d/Prediction/.venv/Scripts/python.exe src/predict.py`

## Project Structure
- `src/` - Source code (GUI, training, prediction)
- `data/` - CSV datasets (NaOH_*, NaCl_*)
- `models/` - Trained ML models
- `dist/` - Built executable
- `requirements.txt` - Python dependencies

## Notes
- Virtual environment contains all required packages
- Use Windows Python executable from WSL2
- Unicode issues may occur - use ASCII characters in console output