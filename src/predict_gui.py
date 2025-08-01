#!/usr/bin/env python3
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import joblib
from pathlib import Path
from PIL import Image, ImageTk

class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("氯碱工业理化常数计算软件V1.0")
        self.root.geometry("800x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")  # 设置窗口背景色
        
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
    
    def format_property_name(self, stem):
        """格式化属性名称，保持正确的化学式大小写"""
        # 将下划线转为空格并首字母大写
        formatted = stem.replace("_", " ").title()
        
        # 修正化学式的大小写
        formatted = formatted.replace("Naoh", "NaOH")
        formatted = formatted.replace("Nacl", "NaCl")
        formatted = formatted.replace("Hcl", "HCl")
        
        # 修正术语
        formatted = formatted.replace("Bubblepoint", "Bubble Point Temperature")
        
        return formatted
    
    def convert_vapor_pressure_from_mmhg(self, pressure_mmhg, target_unit):
        """将蒸汽压从mmHg转换为目标单位"""
        if target_unit == "mmHg":
            return pressure_mmhg
        elif target_unit == "kPa":
            return pressure_mmhg * 0.133322  # 1 mmHg = 0.133322 kPa
        elif target_unit == "bar":
            return pressure_mmhg * 0.00133322  # 1 mmHg = 0.00133322 bar
        elif target_unit == "atm":
            return pressure_mmhg * 0.00131579  # 1 mmHg = 0.00131579 atm
        elif target_unit == "psi":
            return pressure_mmhg * 0.0193368  # 1 mmHg = 0.0193368 psi
        elif target_unit == "torr":
            return pressure_mmhg * 1.0  # 1 mmHg = 1 torr
        else:
            return pressure_mmhg
    
    def setup_ui(self):
        # 添加公司Logo (独立行)
        try:
            # 获取logo路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe文件
                base_path = Path(sys._MEIPASS)
            else:
                # 如果是源代码运行
                base_path = Path(__file__).parent.parent
            
            logo_path = base_path / "fig" / "logo.jpg"
            if logo_path.exists():
                # 加载和调整logo大小 (适中尺寸，保持原始比例)
                logo_image = Image.open(logo_path)
                # 获取原始尺寸
                original_width, original_height = logo_image.size
                # 计算合适的宽高比，保持原始比例
                target_height = 60  # 减小高度
                aspect_ratio = original_width / original_height
                target_width = int(target_height * aspect_ratio)  # 保持原始比例
                logo_image = logo_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # 显示logo (单独一行，居中)
                logo_label = tk.Label(self.root, image=self.logo_photo)
                logo_label.pack(pady=5)
        except Exception as e:
            print(f"无法加载logo: {e}")
        
        # 标题 (独立行)
        title_label = tk.Label(self.root, text="氯碱工业理化常数计算软件V1.0", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(2, 8))
        
        # 输入框架
        input_frame = ttk.LabelFrame(self.root, text="输入参数", padding=10)
        input_frame.pack(pady=8, padx=20, fill="x")
        
        # 使用两列布局
        # 左列
        # 溶液类型选择
        ttk.Label(input_frame, text="溶液类型:").grid(row=0, column=0, sticky="w", pady=3)
        self.solution_type_var = tk.StringVar(value="NaOH")
        solution_types = ["NaOH", "NaCl", "HCl"]
        self.solution_type_combo = ttk.Combobox(input_frame, textvariable=self.solution_type_var,
                                              values=solution_types, width=12, state="readonly")
        self.solution_type_combo.grid(row=0, column=1, pady=3, padx=(5, 20))
        self.solution_type_combo.bind("<<ComboboxSelected>>", self.on_solution_type_change)
        
        # 浓度输入 (所有模型都需要)
        self.concentration_label = ttk.Label(input_frame, text="浓度 (%NaOH):")
        self.concentration_label.grid(row=1, column=0, sticky="w", pady=3)
        self.x1_var = tk.StringVar()
        self.x1_entry = ttk.Entry(input_frame, textvariable=self.x1_var, width=12)
        self.x1_entry.grid(row=1, column=1, pady=3, padx=(5, 20))
        
        # 温度输入 (用于大部分模型)
        ttk.Label(input_frame, text="温度 (°C):").grid(row=2, column=0, sticky="w", pady=3)
        self.x2_var = tk.StringVar()
        self.x2_entry = ttk.Entry(input_frame, textvariable=self.x2_var, width=12)
        self.x2_entry.grid(row=2, column=1, pady=3, padx=(5, 20))
        
        # 右列
        # 密度输入 (用于NaCl浓度预测)
        ttk.Label(input_frame, text="密度 (kg/m³):").grid(row=0, column=2, sticky="w", pady=3)
        self.x4_var = tk.StringVar()
        self.x4_entry = ttk.Entry(input_frame, textvariable=self.x4_var, width=12)
        self.x4_entry.grid(row=0, column=3, pady=3, padx=(5, 0))
        
        # 压力输入 (用于bubble point模型)
        ttk.Label(input_frame, text="压力:").grid(row=1, column=2, sticky="w", pady=3)
        
        # 压力输入框架
        pressure_frame = ttk.Frame(input_frame)
        pressure_frame.grid(row=1, column=3, pady=3, padx=(5, 0), sticky="w")
        
        self.x3_var = tk.StringVar()
        self.x3_entry = ttk.Entry(pressure_frame, textvariable=self.x3_var, width=8)
        self.x3_entry.pack(side="left")
        
        # 压力单位下拉菜单
        self.pressure_unit_var = tk.StringVar(value="bar.A")
        pressure_units = ["bar.A", "kPa.A", "MPa.A", "kg/cm2.A"]
        self.pressure_unit_combo = ttk.Combobox(pressure_frame, textvariable=self.pressure_unit_var,
                                              values=pressure_units, width=6, state="readonly")
        self.pressure_unit_combo.pack(side="left", padx=(3, 0))
        
        # 蒸汽压结果单位选择
        ttk.Label(input_frame, text="蒸汽压结果单位:").grid(row=2, column=2, sticky="w", pady=3)
        self.vapor_pressure_unit_var = tk.StringVar(value="mmHg")
        vapor_pressure_units = ["mmHg", "kPa", "bar", "atm", "psi", "torr"]
        self.vapor_pressure_unit_combo = ttk.Combobox(input_frame, textvariable=self.vapor_pressure_unit_var,
                                                    values=vapor_pressure_units, width=12, state="readonly")
        self.vapor_pressure_unit_combo.grid(row=2, column=3, pady=3, padx=(5, 0))
        
        # 预测按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        predict_btn = ttk.Button(button_frame, text="🚀 开始计算", command=self.predict,
                               style="Accent.TButton")
        predict_btn.pack()
        
        # 配置按钮样式
        style = ttk.Style()
        style.configure("Accent.TButton", 
                       font=("Arial", 11, "bold"),
                       padding=(20, 10))
        
        # 结果显示框架
        result_frame = ttk.LabelFrame(self.root, text="计算结果", padding=10)
        result_frame.pack(pady=8, padx=20, fill="both", expand=True)
        
        # 创建结果显示的表格样式框架
        self.result_text = tk.Text(result_frame, height=10, width=70, 
                                  font=("Consolas", 12), 
                                  bg="white", 
                                  relief="solid", 
                                  borderwidth=1,
                                  padx=8, pady=8)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", 
                                 command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 配置文本标签样式
        self.result_text.tag_configure("header", font=("Arial", 12, "bold"))
        self.result_text.tag_configure("separator")
        self.result_text.tag_configure("property", font=("Arial", 12))
        self.result_text.tag_configure("value", font=("Arial", 12))
        self.result_text.tag_configure("unit", font=("Arial", 12))
        self.result_text.tag_configure("skip", font=("Arial", 12, "italic"))
    
    def on_solution_type_change(self, event=None):
        """更新浓度标签根据溶液类型"""
        solution_type = self.solution_type_var.get()
        if solution_type == "NaOH":
            self.concentration_label.config(text="浓度 (%NaOH):")
        elif solution_type == "NaCl":
            self.concentration_label.config(text="浓度 (%NaCl):")
        else:  # HCl
            self.concentration_label.config(text="浓度 (%HCl):")
    
    def validate_inputs(self, x1, x2, x3, x4, solution_type):
        """验证输入值的合理性"""
        errors = []
        
        # 浓度范围验证
        if x1 is not None:
            if x1 < 0 or x1 > 100:
                errors.append("浓度应在 0-100% 之间")
        
        # 温度范围验证  
        if x2 is not None:
            if x2 < -50 or x2 > 500:
                errors.append("温度应在 -50°C 到 500°C 之间")
        
        # 压力验证
        if x3 is not None:
            if x3 <= 0:
                errors.append("压力必须为正值")
        
        # 密度验证
        if x4 is not None:
            if x4 <= 0 or x4 > 5000:
                errors.append("密度应在 0-5000 kg/m³ 之间")
        
        return errors

    def predict(self):
        try:
            # 清空之前的结果
            self.result_text.delete(1.0, tk.END)
            
            # 显示加载状态
            self.result_text.insert(tk.END, "正在计算中...\n")
            self.root.update()
            
            # 获取输入值
            x1 = float(self.x1_var.get()) if self.x1_var.get() else None
            x2 = float(self.x2_var.get()) if self.x2_var.get() else None
            x3 = float(self.x3_var.get()) if self.x3_var.get() else None
            x4 = float(self.x4_var.get()) if self.x4_var.get() else None
            solution_type = self.solution_type_var.get()
            
            # 输入验证
            validation_errors = self.validate_inputs(x1, x2, x3, x4, solution_type)
            if validation_errors:
                self.result_text.delete(1.0, tk.END)
                error_msg = "输入验证失败:\n"
                for error in validation_errors:
                    error_msg += f"  {error}\n"
                self.result_text.insert(tk.END, error_msg)
                return
            
            # 验证必要输入 (根据模型类型不同)
            # 对于浓度预测模型，不需要X1
            has_concentration_model = any("concentration" in stem for stem in self.models.keys() if solution_type in stem)
            
            if not has_concentration_model and x1 is None:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "浓度 (X1) 是必填项\n")
                return
            
            # 清空加载状态，显示结果
            self.result_text.delete(1.0, tk.END)
            header_text = f"计算结果 ({solution_type}):\n"
            self.result_text.insert(tk.END, header_text, "header")
            separator_line = "-" * 40 + "\n"
            self.result_text.insert(tk.END, separator_line)
            
            # 根据溶液类型过滤模型
            filtered_models = {}
            for stem, model_data in self.models.items():
                if solution_type == "NaOH" and stem.startswith("NaOH"):
                    filtered_models[stem] = model_data
                elif solution_type == "NaCl" and stem.startswith("NaCl"):
                    filtered_models[stem] = model_data
                elif solution_type == "HCl" and stem.startswith("HCl"):
                    filtered_models[stem] = model_data
            
            if not filtered_models:
                error_msg = f"没有找到 {solution_type} 的预测模型\n"
                self.result_text.insert(tk.END, error_msg)
                return
            
            # 检查模型数据结构
            for stem, model_data in filtered_models.items():
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
                        formatted_name = self.format_property_name(stem)
                        skip_msg = f"跳过 {formatted_name} (需要压力输入)\n"
                        self.result_text.insert(tk.END, skip_msg)
                        continue
                    # 将压力转换为bar.A
                    pressure_unit = self.pressure_unit_var.get()
                    x3_bar = self.convert_pressure_to_bar(x3, pressure_unit)
                    sample = pd.DataFrame({"X1": [x1], "X3": [x3_bar]})
                elif "concentration" in stem:
                    if x2 is None or x4 is None:
                        formatted_name = self.format_property_name(stem)
                        skip_msg = f"跳过 {formatted_name} (需要温度和密度输入)\n"
                        self.result_text.insert(tk.END, skip_msg)
                        continue
                    # NaCl浓度预测使用温度和密度
                    sample = pd.DataFrame({"X2": [x2], "X4": [x4]})
                elif "HCl" in stem and "vapor_pressure" in stem:
                    if x2 is None:
                        formatted_name = self.format_property_name(stem)
                        skip_msg = f"跳过 {formatted_name} (需要温度输入)\n"
                        self.result_text.insert(tk.END, skip_msg)
                        continue
                    # Create advanced features for Neural Network
                    import numpy as np
                    T_K = x2 + 273.15
                    
                    # Create all advanced features
                    feature_dict = {
                        "X1": [x1],
                        "X2": [x2],
                        "inv_T": [1 / T_K],
                        "log_T": [np.log(T_K)],
                        "sqrt_T": [np.sqrt(T_K)],
                        "log_X1": [np.log(x1 + 1)],
                        "sqrt_X1": [np.sqrt(x1)],
                        "X1_squared": [x1 ** 2],
                        "X1_inv_T": [x1 / T_K],
                        "X1_log_T": [x1 * np.log(T_K)],
                        "X1_sqrt_T": [x1 * np.sqrt(T_K)],
                        "X1_X2": [x1 * x2],
                        "X1_X2_inv_T": [x1 * x2 / T_K],
                        "exp_inv_T": [np.exp(1 / T_K)],
                        "X1_exp_inv_T": [x1 * np.exp(1 / T_K)]
                    }
                    sample = pd.DataFrame(feature_dict)
                else:
                    if x2 is None:
                        formatted_name = self.format_property_name(stem)
                        skip_msg = f"跳过 {formatted_name} (需要温度输入)\n"
                        self.result_text.insert(tk.END, skip_msg)
                        continue
                    sample = pd.DataFrame({"X1": [x1], "X2": [x2]})
                
                val = pipe.predict(sample)[0]
                label = self.format_property_name(stem)
                
                # 根据属性添加单位和转换
                if "vapor_pressure" in stem:
                    # 获取用户选择的蒸汽压单位
                    selected_unit = self.vapor_pressure_unit_var.get()
                    # 模型预测的是mmHg，转换为用户选择的单位
                    converted_val = self.convert_vapor_pressure_from_mmhg(val, selected_unit)
                    
                    # 格式化显示结果（对齐列显示）
                    result_line = f"{label:<25}: {converted_val:>10.4f} {selected_unit}\n"
                    self.result_text.insert(tk.END, result_line)
                    
                    # 如果用户选择的不是mmHg，也显示常用单位供参考
                    if selected_unit != "mmHg":
                        other_units = ["kPa", "bar", "atm", "psi"]
                        if selected_unit in other_units:
                            other_units.remove(selected_unit)
                        
                        for other_unit in other_units[:2]:  # 显示前两个其他单位
                            other_val = self.convert_vapor_pressure_from_mmhg(val, other_unit)
                            ref_text = f"{'':<25}  ({other_val:>10.4f} {other_unit})\n"
                            self.result_text.insert(tk.END, ref_text)
                    
                    continue  # 已经处理了vapor_pressure，跳过后续处理
                    
                elif "viscosity" in stem:
                    unit = "cp"
                elif "enthalpy" in stem:
                    unit = "kcal/kgNaOH"
                elif "bubblepoint" in stem:
                    unit = "°C"
                elif "density" in stem:
                    unit = "kg/m³"
                elif "concentration" in stem:
                    unit = "g/L"
                elif "thermal_conductivity" in stem:
                    unit = "kcal/m.hr.°C"
                else:
                    unit = ""
                
                # 格式化其他属性的显示（对齐列显示）
                if unit:
                    result_line = f"{label:<25}: {val:>10.4f} {unit}\n"
                else:
                    result_line = f"{label:<25}: {val:>10.4f}\n"
                
                self.result_text.insert(tk.END, result_line)
            
            # 结束分隔线
            end_separator = "-" * 40 + "\n"
            self.result_text.insert(tk.END, end_separator)
            
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数值")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中出现错误：{str(e)}")

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()