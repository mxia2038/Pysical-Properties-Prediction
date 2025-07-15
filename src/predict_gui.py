#!/usr/bin/env python3
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import joblib
from pathlib import Path

class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("物性预测器")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # 加载模型
        try:
            # 获取程序运行目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe文件
                base_path = Path(sys._MEIPASS)
            else:
                # 如果是源代码运行
                base_path = Path(__file__).parent.parent
            
            models_path = base_path / "models" / "pipelines_by_target.pkl"
            self.models = joblib.load(models_path)
        except Exception as e:
            messagebox.showerror("错误", f"加载模型失败：{str(e)}")
            self.root.destroy()
            return
        
        self.setup_ui()
    
    def convert_pressure_to_bar(self, pressure_value, unit):
        """将不同单位的压力转换为bar.A"""
        if unit == "bar.A":
            return pressure_value
        elif unit == "kPa.A":
            return pressure_value / 100  # 1 bar = 100 kPa
        elif unit == "MPa.A":
            return pressure_value * 10   # 1 MPa = 10 bar
        elif unit == "kg/cm2.A":
            return pressure_value * 0.980665  # 1 kg/cm2 = 0.980665 bar
        else:
            return pressure_value
    
    def setup_ui(self):
        # 标题
        title_label = tk.Label(self.root, text="物性预测器", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 输入框架
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=20, padx=20, fill="x")
        
        # 浓度输入 (所有模型都需要)
        ttk.Label(input_frame, text="浓度 (%NaOH):").grid(row=0, column=0, sticky="w", pady=5)
        self.x1_var = tk.StringVar()
        self.x1_entry = ttk.Entry(input_frame, textvariable=self.x1_var, width=15)
        self.x1_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # 温度输入 (用于大部分模型)
        ttk.Label(input_frame, text="温度 (°C):").grid(row=1, column=0, sticky="w", pady=5)
        self.x2_var = tk.StringVar()
        self.x2_entry = ttk.Entry(input_frame, textvariable=self.x2_var, width=15)
        self.x2_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # 压力输入 (用于bubble point模型)
        ttk.Label(input_frame, text="压力:").grid(row=2, column=0, sticky="w", pady=5)
        
        # 压力输入框架
        pressure_frame = ttk.Frame(input_frame)
        pressure_frame.grid(row=2, column=1, pady=5, padx=(10, 0), sticky="w")
        
        self.x3_var = tk.StringVar()
        self.x3_entry = ttk.Entry(pressure_frame, textvariable=self.x3_var, width=10)
        self.x3_entry.pack(side="left")
        
        # 压力单位下拉菜单
        self.pressure_unit_var = tk.StringVar(value="bar.A")
        pressure_units = ["bar.A", "kPa.A", "MPa.A", "kg/cm2.A"]
        self.pressure_unit_combo = ttk.Combobox(pressure_frame, textvariable=self.pressure_unit_var,
                                              values=pressure_units, width=8, state="readonly")
        self.pressure_unit_combo.pack(side="left", padx=(5, 0))
        
        # 预测按钮
        predict_btn = ttk.Button(self.root, text="开始预测", command=self.predict)
        predict_btn.pack(pady=20)
        
        # 结果显示框架
        result_frame = ttk.LabelFrame(self.root, text="预测结果", padding=10)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.result_text = tk.Text(result_frame, height=10, width=50, 
                                  font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", 
                                 command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def predict(self):
        try:
            # 获取输入值
            x1 = float(self.x1_var.get()) if self.x1_var.get() else None
            x2 = float(self.x2_var.get()) if self.x2_var.get() else None
            x3 = float(self.x3_var.get()) if self.x3_var.get() else None
            
            if x1 is None:
                messagebox.showerror("输入错误", "浓度 (X1) 是必填项")
                return
            
            # 清空结果显示
            self.result_text.delete(1.0, tk.END)
            
            # 进行预测
            self.result_text.insert(tk.END, "预测结果:\n")
            self.result_text.insert(tk.END, "=" * 40 + "\n")
            
            # 检查模型数据结构
            for stem, model_data in self.models.items():
                # 兼容旧版本模型格式
                if isinstance(model_data, dict):
                    pipe = model_data["model"]
                    features = model_data["features"]
                else:
                    # 旧格式：直接是pipeline对象
                    pipe = model_data
                    features = ["X1", "X2"]  # 默认特征
                
                # 根据模型所需特征创建输入样本
                if "bubblepoint" in stem:
                    if x3 is None:
                        self.result_text.insert(tk.END, f"跳过 {stem} (需要压力输入)\n")
                        continue
                    # 将压力转换为bar.A
                    pressure_unit = self.pressure_unit_var.get()
                    x3_bar = self.convert_pressure_to_bar(x3, pressure_unit)
                    sample = pd.DataFrame({"X1": [x1], "X3": [x3_bar]})
                else:
                    if x2 is None:
                        self.result_text.insert(tk.END, f"跳过 {stem} (需要温度输入)\n")
                        continue
                    sample = pd.DataFrame({"X1": [x1], "X2": [x2]})
                
                val = pipe.predict(sample)[0]
                label = stem.replace("_", " ").title()
                
                # 根据属性添加单位
                if stem == "vapor_pressure":
                    unit = "mmHg"
                elif stem == "viscosity":
                    unit = "cp"
                elif stem == "enthalpy":
                    unit = "kcal/kgNaOH"
                elif "bubblepoint" in stem:
                    unit = "°C"
                else:
                    unit = ""
                
                if unit:
                    result_line = f"{label:18s}: {val:8.4f} {unit}\n"
                else:
                    result_line = f"{label:18s}: {val:8.4f}\n"
                
                self.result_text.insert(tk.END, result_line)
            
            self.result_text.insert(tk.END, "=" * 40 + "\n")
            
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数值")
        except Exception as e:
            messagebox.showerror("预测错误", f"预测过程中出现错误：{str(e)}")

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()