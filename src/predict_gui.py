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
        self.root.geometry("780x500")  # 更紧凑的窗口尺寸，适合笔记本电脑
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
        """格式化属性名称，保持正确的化学式大小写，并确保对齐"""
        # 将下划线转为空格并首字母大写
        formatted = stem.replace("_", " ").title()
        
        # 修正化学式的大小写
        formatted = formatted.replace("Naoh", "NaOH")
        formatted = formatted.replace("Nacl", "NaCl")
        formatted = formatted.replace("Hcl", "HCl")
        
        # 修正术语
        formatted = formatted.replace("Bubblepoint", "Bubble Point Temperature")
        
        # 缩短长属性名以确保完美对齐 (最多22个字符)
        formatted = formatted.replace("Thermal Conductivity", "Thermal Cond.")
        formatted = formatted.replace("Bubble Point Temperature", "Bubble Point Temp")
        formatted = formatted.replace("Vapor Pressure", "Vapor Press.")
        
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
        """设置主界面"""
        # 设置现代化背景色
        self.root.configure(bg="#f8f9fa")
        self._setup_header()
        self._setup_input_section()
        self._setup_result_section()
    
    def _setup_header(self):
        """设置头部logo和标题 - Apple风格紧凑设计"""
        # 创建现代化头部区域
        header_frame = tk.Frame(self.root, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(8, 10))
        
        # 添加公司Logo
        try:
            # 获取logo路径
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent.parent
            
            logo_path = base_path / "fig" / "logo.jpg"
            if logo_path.exists():
                logo_image = Image.open(logo_path)
                original_width, original_height = logo_image.size
                target_height = 45  # 减小logo尺寸以节省空间
                aspect_ratio = original_width / original_height
                target_width = int(target_height * aspect_ratio)
                logo_image = logo_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = tk.Label(header_frame, image=self.logo_photo, bg="#f8f9fa")
                logo_label.pack(pady=2)
        except Exception as e:
            print(f"无法加载logo: {e}")
        
        # 现代化标题 - 更小字体以节省空间
        title_label = tk.Label(header_frame, text="氯碱工业理化常数计算软件V1.0", 
                              font=("Segoe UI", 13, "bold"), bg="#f8f9fa", fg="#1d1d1f")
        title_label.pack(pady=(2, 0))
    
    def _setup_input_section(self):
        # 创建现代化容器 - Apple风格紧凑布局
        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        
        # 输入参数卡片 - 减少内边距
        input_card = tk.Frame(main_container, bg="white", relief="flat", bd=0)
        input_card.pack(fill="x", pady=(0, 8))
        
        # 卡片标题 - 更紧凑
        title_frame = tk.Frame(input_card, bg="white")
        title_frame.pack(fill="x", padx=16, pady=(12, 8))
        
        title_label = tk.Label(title_frame, text="输入参数", 
                              font=("Segoe UI", 12, "bold"), 
                              bg="white", fg="#1d1d1f")
        title_label.pack(anchor="w")
        
        # 输入区域 - 减少内边距
        input_frame = tk.Frame(input_card, bg="white")
        input_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        # Apple风格紧凑网格布局
        # 左列
        # 溶液类型选择
        solution_label = tk.Label(input_frame, text="溶液类型:", 
                                 font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        solution_label.grid(row=0, column=0, sticky="w", pady=4)
        self.solution_type_var = tk.StringVar(value="NaOH")
        solution_types = ["NaOH", "NaCl", "HCl"]
        self.solution_type_combo = ttk.Combobox(input_frame, textvariable=self.solution_type_var,
                                              values=solution_types, width=11, state="readonly",
                                              font=("Segoe UI", 9))
        self.solution_type_combo.grid(row=0, column=1, pady=4, padx=(6, 16))
        self.solution_type_combo.bind("<<ComboboxSelected>>", self.on_solution_type_change)
        
        # 浓度输入
        self.concentration_label = tk.Label(input_frame, text="浓度 (%NaOH):", 
                                           font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        self.concentration_label.grid(row=1, column=0, sticky="w", pady=4)
        self.x1_var = tk.StringVar()
        self.x1_entry = ttk.Entry(input_frame, textvariable=self.x1_var, width=11,
                                 font=("Segoe UI", 9))
        self.x1_entry.grid(row=1, column=1, pady=4, padx=(6, 16))
        
        # 温度输入
        temp_label = tk.Label(input_frame, text="温度 (°C):", 
                             font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        temp_label.grid(row=2, column=0, sticky="w", pady=4)
        self.x2_var = tk.StringVar()
        self.x2_entry = ttk.Entry(input_frame, textvariable=self.x2_var, width=11,
                                 font=("Segoe UI", 9))
        self.x2_entry.grid(row=2, column=1, pady=4, padx=(6, 16))
        
        # 右列
        # 密度输入
        density_label = tk.Label(input_frame, text="密度 (kg/m³):", 
                                font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        density_label.grid(row=0, column=2, sticky="w", pady=4)
        self.x4_var = tk.StringVar()
        self.x4_entry = ttk.Entry(input_frame, textvariable=self.x4_var, width=11,
                                 font=("Segoe UI", 9))
        self.x4_entry.grid(row=0, column=3, pady=4, padx=(6, 0))
        
        # 压力输入
        pressure_label = tk.Label(input_frame, text="压力:", 
                                 font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        pressure_label.grid(row=1, column=2, sticky="w", pady=4)
        
        # 压力输入框架
        pressure_frame = tk.Frame(input_frame, bg="white")
        pressure_frame.grid(row=1, column=3, pady=4, padx=(6, 0), sticky="w")
        
        self.x3_var = tk.StringVar()
        self.x3_entry = ttk.Entry(pressure_frame, textvariable=self.x3_var, width=6,
                                 font=("Segoe UI", 9))
        self.x3_entry.pack(side="left")
        
        # 压力单位下拉菜单
        self.pressure_unit_var = tk.StringVar(value="bar.A")
        pressure_units = ["bar.A", "kPa.A", "MPa.A", "kg/cm2.A"]
        self.pressure_unit_combo = ttk.Combobox(pressure_frame, textvariable=self.pressure_unit_var,
                                              values=pressure_units, width=5, state="readonly",
                                              font=("Segoe UI", 8))
        self.pressure_unit_combo.pack(side="left", padx=(2, 0))
        
        # 蒸汽压结果单位选择
        vapor_label = tk.Label(input_frame, text="蒸汽压单位:", 
                              font=("Segoe UI", 9), bg="white", fg="#2c2c2c")
        vapor_label.grid(row=2, column=2, sticky="w", pady=4)
        self.vapor_pressure_unit_var = tk.StringVar(value="mmHg")
        vapor_pressure_units = ["mmHg", "kPa", "bar", "atm", "psi", "torr"]
        self.vapor_pressure_unit_combo = ttk.Combobox(input_frame, textvariable=self.vapor_pressure_unit_var,
                                                    values=vapor_pressure_units, width=11, state="readonly",
                                                    font=("Segoe UI", 9))
        self.vapor_pressure_unit_combo.grid(row=2, column=3, pady=4, padx=(6, 0))
    
    def _setup_result_section(self):
        """设置结果显示区域和操作按钮 - Apple风格横向布局"""
        # 获取主容器
        main_container = self.root.children[list(self.root.children.keys())[-1]]
        
        # Apple风格控制面板 - 按钮和结果在同一行
        control_panel = tk.Frame(main_container, bg="white", relief="flat", bd=0)
        control_panel.pack(fill="both", expand=True, pady=(0, 8))
        
        # 左侧控制区域 - 按钮和控制
        control_left = tk.Frame(control_panel, bg="white", width=200)
        control_left.pack(side="left", fill="y", padx=(16, 8), pady=12)
        control_left.pack_propagate(False)  # 固定宽度
        
        # 控制区标题
        control_title = tk.Label(control_left, text="操作", 
                               font=("Segoe UI", 12, "bold"), 
                               bg="white", fg="#1d1d1f")
        control_title.pack(anchor="w", pady=(0, 8))
        
        # 现代化紧凑按钮
        predict_btn = tk.Button(control_left, text="🚀 开始计算", command=self.predict,
                              font=("Segoe UI", 10, "bold"), 
                              bg="#007aff", fg="white",
                              relief="flat", bd=0, padx=20, pady=8,
                              cursor="hand2", activebackground="#0056b3")
        predict_btn.pack(fill="x", pady=(0, 6))
        
        # 公式按钮
        formula_btn = tk.Button(control_left, text="📊 显示公式", command=self.show_formula_selector,
                               font=("Segoe UI", 10), 
                               bg="white", fg="#007aff",
                               relief="solid", bd=1, padx=20, pady=8,
                               cursor="hand2", activebackground="#f0f0f0")
        formula_btn.pack(fill="x")
        
        # 右侧结果区域
        result_right = tk.Frame(control_panel, bg="white")
        result_right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=12)
        
        # 结果区标题
        result_title = tk.Label(result_right, text="计算结果", 
                               font=("Segoe UI", 12, "bold"), 
                               bg="white", fg="#1d1d1f")
        result_title.pack(anchor="w", pady=(0, 8))
        
        # 结果显示区域
        result_content_frame = tk.Frame(result_right, bg="white")
        result_content_frame.pack(fill="both", expand=True)
        
        # 创建现代化结果文本框 - 更紧凑
        self.result_text = tk.Text(result_content_frame, height=8, 
                                  font=("Consolas", 10),  # 使用等宽字体确保完美对齐
                                  bg="#f8f9fa", 
                                  relief="flat", 
                                  borderwidth=0,
                                  padx=12, pady=12)
        scrollbar = ttk.Scrollbar(result_content_frame, orient="vertical", 
                                 command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 配置现代化文本样式
        self.result_text.tag_configure("header", font=("Segoe UI", 11, "bold"), foreground="#1d1d1f")
        self.result_text.tag_configure("separator")
        self.result_text.tag_configure("property", font=("Segoe UI", 10), foreground="#2c2c2c")
        self.result_text.tag_configure("value", font=("Segoe UI", 10, "bold"), foreground="#007aff")
        self.result_text.tag_configure("unit", font=("Segoe UI", 10), foreground="#666666")
        self.result_text.tag_configure("skip", font=("Segoe UI", 10, "italic"), foreground="#999999")
    
    def _validate_and_prepare_inputs(self):
        """验证输入并准备计算所需的数据"""
        try:
            # 获取输入值
            x1 = float(self.x1_var.get()) if self.x1_var.get() else None
            x2 = float(self.x2_var.get()) if self.x2_var.get() else None
            x3 = float(self.x3_var.get()) if self.x3_var.get() else None
            x4 = float(self.x4_var.get()) if self.x4_var.get() else None
            solution_type = self.solution_type_var.get()
            
            # 输入验证
            validation_errors = self.validate_inputs(x1, x2, x3, x4, solution_type)
            if validation_errors:
                return None, f"输入验证失败:\n" + "\n".join(f"  {error}" for error in validation_errors)
            
            # 验证必要输入 (根据模型类型不同)
            has_concentration_model = any("concentration" in stem for stem in self.models.keys() if solution_type in stem)
            if not has_concentration_model and x1 is None:
                return None, "浓度 (X1) 是必填项"
                
            return {"x1": x1, "x2": x2, "x3": x3, "x4": x4, "solution_type": solution_type}, None
            
        except ValueError:
            return None, "请输入有效的数值"
    
    def _run_model_predictions(self, inputs):
        """运行模型预测计算"""
        x1, x2, x3, x4, solution_type = inputs["x1"], inputs["x2"], inputs["x3"], inputs["x4"], inputs["solution_type"]
        
        # 获取当前溶液类型的模型
        filtered_models = {k: v for k, v in self.models.items() if solution_type in k}
        predictions = {}
        
        for stem, model_data in filtered_models.items():
            # 兼容旧版本模型格式
            if isinstance(model_data, dict):
                pipe = model_data["model"]
                features = model_data["features"]
            else:
                pipe = model_data
                features = ["X1", "X2"]
            
            # 根据模型所需特征创建输入样本
            sample = self._create_model_sample(stem, x1, x2, x3, x4)
            if sample is None:
                continue  # 跳过无法创建样本的模型
                
            # 执行预测
            prediction = pipe.predict(sample)[0]
            predictions[stem] = prediction
            
        return predictions
    
    def _create_model_sample(self, stem, x1, x2, x3, x4):
        """根据模型类型创建输入样本"""
        if "bubblepoint" in stem:
            if x3 is None:
                return None
            pressure_unit = self.pressure_unit_var.get()
            x3_bar = self.convert_pressure_to_bar(x3, pressure_unit)
            return pd.DataFrame({"X1": [x1], "X3": [x3_bar]})
            
        elif "concentration" in stem:
            if x2 is None or x4 is None:
                return None
            return pd.DataFrame({"X2": [x2], "X4": [x4]})
            
        elif "HCl" in stem and "vapor_pressure" in stem:
            if x2 is None:
                return None
            # Create advanced features for Neural Network
            import numpy as np
            T_K = x2 + 273.15
            feature_dict = {
                'X1': [x1], 'X2': [x2], 'inv_T': [1 / T_K], 'log_T': [np.log(T_K)], 'sqrt_T': [np.sqrt(T_K)],
                'log_X1': [np.log(x1 + 1)], 'sqrt_X1': [np.sqrt(x1)], 'X1_squared': [x1 ** 2],
                'X1_inv_T': [x1 * (1 / T_K)], 'X1_log_T': [x1 * np.log(T_K)], 'X1_sqrt_T': [x1 * np.sqrt(T_K)],
                'X1_X2': [x1 * x2], 'X1_X2_inv_T': [x1 * x2 * (1 / T_K)],
                'exp_inv_T': [np.exp(1 / T_K)], 'X1_exp_inv_T': [x1 * np.exp(1 / T_K)]
            }
            return pd.DataFrame(feature_dict)
            
        else:
            # 标准模型使用浓度和温度
            if x1 is None or x2 is None:
                return None
            return pd.DataFrame({"X1": [x1], "X2": [x2]})
    
    def _format_and_display_results(self, predictions, solution_type):
        """格式化并显示预测结果"""
        self.result_text.delete(1.0, tk.END)
        header_text = f"计算结果 ({solution_type}):\n"
        self.result_text.insert(tk.END, header_text, "header")
        separator_line = "-" * 40 + "\n"
        self.result_text.insert(tk.END, separator_line, "separator")
        
        for stem, prediction in predictions.items():
            formatted_name = self.format_property_name(stem)
            
            # 处理蒸汽压单位转换
            if "vapor_pressure" in stem:
                target_unit = self.vapor_pressure_unit_var.get()
                if target_unit != "mmHg":
                    val = self.convert_vapor_pressure_from_mmhg(prediction, target_unit)
                    unit = target_unit
                else:
                    val = prediction
                    unit = "mmHg"
                # 完美对齐：固定宽度的属性名 + 冒号 + 右对齐的数值 + 单位
                result_line = f"{formatted_name:<22} : {val:>10.4f} {unit}\n"
            else:
                # 其他属性的单位处理 - 完美对齐
                val = prediction
                unit = self._get_property_unit(stem)
                if unit:
                    result_line = f"{formatted_name:<22} : {val:>10.4f} {unit}\n"
                else:
                    result_line = f"{formatted_name:<22} : {val:>10.4f}\n"
                    
            self.result_text.insert(tk.END, result_line)
        
        end_separator = "-" * 40 + "\n"
        self.result_text.insert(tk.END, end_separator)
    
    def _get_property_unit(self, stem):
        """获取属性单位"""
        if "viscosity" in stem:
            return "cP"
        elif "density" in stem:
            return "kg/m³"
        elif "concentration" in stem:
            return "g/L"
        elif "thermal_conductivity" in stem:
            return "kcal/m.hr.°C"
        elif "enthalpy" in stem:
            return "kcal/kgNaOH"
        elif "bubblepoint" in stem:
            return "°C"
        else:
            return ""
    
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
        """主预测方法 - 简化版本，使用辅助方法"""
        try:
            # 清空之前的结果并显示加载状态
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "正在计算中...\n")
            self.root.update()
            
            # 验证输入并准备数据
            inputs, error = self._validate_and_prepare_inputs()
            if error:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error)
                return
            
            # 运行预测计算
            predictions = self._run_model_predictions(inputs)
            
            # 格式化并显示结果
            self._format_and_display_results(predictions, inputs["solution_type"])
            
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数值")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中出现错误：{str(e)}")
    
    def extract_model_formula(self, model_name):
        """提取指定模型的数学公式"""
        try:
            model_data = self.models[model_name]
            if isinstance(model_data, dict):
                pipe = model_data["model"]
            else:
                pipe = model_data
            
            # 检查模型类型
            if hasattr(pipe, 'named_steps'):
                if 'poly' in pipe.named_steps:
                    # Ridge regression with polynomial features
                    return self.extract_polynomial_formula(pipe, model_name)
                elif hasattr(pipe.named_steps.get('reg'), 'regressor_'):
                    # TransformedTargetRegressor - could be Neural Network with log transformation
                    if "HCl" in model_name and "vapor_pressure" in model_name:
                        return self.extract_hcl_neural_network_formula(pipe, model_name)
                    else:
                        return self.extract_log_transformed_formula(pipe, model_name)
                elif hasattr(pipe.named_steps.get('reg'), 'hidden_layer_sizes'):
                    # Neural Network without log transformation
                    return self.extract_neural_network_formula(pipe, model_name)
            
            return None
        except Exception as e:
            return f"无法提取公式: {str(e)}"
    
    def extract_polynomial_formula(self, pipe, model_name):
        """提取多项式回归公式"""
        try:
            # Check for different step names (scale vs scaler)
            if 'scale' in pipe.named_steps:
                scaler = pipe.named_steps['scale']
            else:
                scaler = pipe.named_steps['scaler']
            poly = pipe.named_steps['poly']
            regressor = pipe.named_steps['reg']
            
            # 处理TransformedTargetRegressor
            if hasattr(regressor, 'regressor_'):
                actual_regressor = regressor.regressor_
            else:
                actual_regressor = regressor
            
            scale_mean = scaler.mean_
            scale_std = scaler.scale_
            coefficients = actual_regressor.coef_
            intercept = actual_regressor.intercept_
            
            # 获取变量名称
            if "bubblepoint" in model_name:
                var_names = ["X1 (浓度%)", "X3 (压力bar)"]
            elif "concentration" in model_name:
                var_names = ["X2 (温度°C)", "X4 (密度kg/m³)"]
            else:
                var_names = ["X1 (浓度%)", "X2 (温度°C)"]
            
            # 获取单位
            if "density" in model_name:
                unit = "kg/m³"
            elif "viscosity" in model_name:
                unit = "cp"
            elif "vapor_pressure" in model_name:
                unit = "kPa"
            elif "enthalpy" in model_name:
                unit = "kcal/kgNaOH"
            elif "bubblepoint" in model_name:
                unit = "°C"
            elif "concentration" in model_name:
                unit = "g/L"
            elif "thermal_conductivity" in model_name:
                unit = "kcal/m.hr.°C"
            else:
                unit = ""
            
            # 计算展开后的系数
            if len(scale_mean) == 2:
                mean1, mean2 = scale_mean[0], scale_mean[1]
                std1, std2 = scale_std[0], scale_std[1]
                
                c0 = intercept
                c1 = coefficients[0] if len(coefficients) > 0 else 0
                c2 = coefficients[1] if len(coefficients) > 1 else 0
                c3 = coefficients[2] if len(coefficients) > 2 else 0
                c4 = coefficients[3] if len(coefficients) > 3 else 0
                c5 = coefficients[4] if len(coefficients) > 4 else 0
                
                # 展开公式系数
                coeff_constant = c0 - (c1*mean1/std1) - (c2*mean2/std2) + (c3*mean1**2/std1**2) + (c4*mean1*mean2/(std1*std2)) + (c5*mean2**2/std2**2)
                coeff_X1 = (c1/std1) - (2*c3*mean1/std1**2) - (c4*mean2/(std1*std2))
                coeff_X2 = (c2/std2) - (c4*mean1/(std1*std2)) - (2*c5*mean2/std2**2)
                coeff_X1_sq = c3/std1**2 if abs(c3) > 1e-10 else 0
                coeff_X1_X2 = c4/(std1*std2) if abs(c4) > 1e-10 else 0
                coeff_X2_sq = c5/std2**2 if abs(c5) > 1e-10 else 0
                
                formula = f"Y = {coeff_constant:.6f}"
                if abs(coeff_X1) > 1e-10:
                    formula += f" + {coeff_X1:.6f}*X1"
                if abs(coeff_X2) > 1e-10:
                    formula += f" + {coeff_X2:.6f}*X2"
                if abs(coeff_X1_sq) > 1e-10:
                    formula += f" + {coeff_X1_sq:.6f}*X1^2"
                if abs(coeff_X1_X2) > 1e-10:
                    formula += f" + {coeff_X1_X2:.6f}*X1*X2"
                if abs(coeff_X2_sq) > 1e-10:
                    formula += f" + {coeff_X2_sq:.6f}*X2^2"
                
                # 清理公式格式
                formula = formula.replace(" + -", " - ")
                
                return {
                    'formula': formula,
                    'variables': var_names,
                    'unit': unit,
                    'type': 'polynomial',
                    'degree': poly.degree,
                    'r2': 'N/A',  # 需要从验证数据计算
                    'coefficients': {
                        'constant': coeff_constant,
                        'X1': coeff_X1,
                        'X2': coeff_X2,
                        'X1^2': coeff_X1_sq,
                        'X1*X2': coeff_X1_X2,
                        'X2^2': coeff_X2_sq
                    }
                }
            
        except Exception as e:
            return f"提取多项式公式时出错: {str(e)}"
    
    def extract_hcl_neural_network_formula(self, pipe, model_name):
        """提取HCl蒸气压神经网络模型的公式描述"""
        try:
            regressor = pipe.named_steps['reg'].regressor_  # MLPRegressor
            
            # 获取神经网络架构
            hidden_layers = regressor.hidden_layer_sizes
            
            # 特征工程描述
            feature_engineering = """
特征工程 (Advanced Feature Engineering):
• T_K = X2 + 273.15 (温度转换为开尔文)
• inv_T = 1 / T_K (温度倒数 - 符合Clausius-Clapeyron方程)
• log_T = ln(T_K) (对数温度)
• sqrt_T = T_K^0.5 (平方根温度)
• log_X1 = ln(X1 + 1) (对数浓度)
• sqrt_X1 = X1^0.5 (平方根浓度)
• X1_squared = X1^2 (浓度平方)
• X1_inv_T = X1 * (1/T_K) (浓度与温度倒数的交互项)
• X1_log_T = X1 * ln(T_K) (浓度与对数温度的交互项)
• X1_sqrt_T = X1 * T_K^0.5 (浓度与平方根温度的交互项)
• X1_X2 = X1 * X2 (浓度与温度的交互项)
• X1_X2_inv_T = X1 * X2 * (1/T_K) (三元交互项)
• exp_inv_T = exp(1/T_K) (指数温度倒数项)
• X1_exp_inv_T = X1 * exp(1/T_K) (浓度与指数温度倒数交互项)
            """
            
            return {
                'type': 'neural_network_log',
                'formula': f'log(Y) = NeuralNetwork(特征工程后的15个特征)',
                'final_formula': 'Y = exp(NeuralNetwork输出)',
                'variables': ["X1 (HCl浓度%)", "X2 (温度°C)"],
                'unit': 'kPa',
                'architecture': f"神经网络架构: {hidden_layers}",
                'feature_count': 15,
                'feature_engineering': feature_engineering,
                'activation': 'ReLU',
                'note': '基于物理定律的复杂非线性模型，使用对数变换确保正值输出'
            }
        except Exception as e:
            return f"提取HCl神经网络公式时出错: {str(e)}"
    
    def extract_neural_network_formula(self, pipe, model_name):
        """提取普通神经网络模型的公式描述"""
        try:
            regressor = pipe.named_steps['reg']
            hidden_layers = regressor.hidden_layer_sizes
            
            return {
                'type': 'neural_network',
                'formula': f'Y = NeuralNetwork(标准化后的输入特征)',
                'variables': ["X1 (浓度%)", "X2 (温度°C)"],
                'unit': self.get_unit_for_property(model_name),
                'architecture': f"神经网络架构: {hidden_layers}",
                'activation': 'ReLU',
                'note': '多层感知器神经网络模型'
            }
        except Exception as e:
            return f"提取神经网络公式时出错: {str(e)}"
    
    def extract_log_transformed_formula(self, pipe, model_name):
        """提取对数变换模型的公式"""
        return {
            'formula': '复杂对数变换模型 - 请参考软件内部算法',
            'variables': ["X1 (浓度%)", "X2 (温度°C)"],
            'unit': 'cp' if 'viscosity' in model_name else self.get_unit_for_property(model_name),
            'type': 'log_transformed',
            'note': '此模型使用对数变换，公式较为复杂'
        }
    
    def get_unit_for_property(self, model_name):
        """获取属性的单位"""
        if "density" in model_name:
            return "kg/m³"
        elif "viscosity" in model_name:
            return "cp"
        elif "vapor_pressure" in model_name:
            return "kPa"
        elif "enthalpy" in model_name:
            return "kcal/kgNaOH"
        elif "bubblepoint" in model_name:
            return "°C"
        elif "concentration" in model_name:
            return "g/L"
        elif "thermal_conductivity" in model_name:
            return "kcal/m.hr.°C"
        else:
            return ""
    
    def _create_formula_selector_window(self):
        """创建并配置公式选择器窗口"""
        selector_window = tk.Toplevel(self.root)
        selector_window.title("Formula Selection")
        selector_window.geometry("550x400")
        selector_window.resizable(True, True)
        selector_window.configure(bg="#f8f9fa")
        
        # 现代化窗口设置
        selector_window.transient(self.root)
        selector_window.grab_set()
        selector_window.focus_set()
        selector_window.lift()
        
        # 居中显示
        selector_window.update_idletasks()
        x = (selector_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (selector_window.winfo_screenheight() // 2) - (400 // 2)
        selector_window.geometry(f"550x400+{x}+{y}")
        
        return selector_window
    
    def _setup_formula_selector_ui(self, selector_window):
        """设置公式选择器的用户界面"""
        # 主容器 - 现代化设计，更大的边距和更好的背景
        main_container = tk.Frame(selector_window, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=16)  # 减少边距
        
        # 标题区域 - 紧凑设计
        header_frame = tk.Frame(main_container, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(0, 16))  # 大幅减少间距
        
        title_label = tk.Label(header_frame, text="Select Formula", 
                              font=("Segoe UI", 16, "bold"), 
                              bg="#f8f9fa", fg="#1d1d1f")
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(header_frame, text="Choose a solution type and property to view the formula", 
                                 font=("Segoe UI", 10, "normal"), 
                                 bg="#f8f9fa", fg="#6e6e73")
        subtitle_label.pack(anchor="w", pady=(2, 0))  # 减少间距
        
        return main_container
    
    def _setup_solution_type_dropdown(self, main_container):
        """设置溶液类型下拉选择器"""
        # 溶液类型选择 - 紧凑设计
        solution_section = tk.Frame(main_container, bg="#f8f9fa")
        solution_section.pack(fill="x", pady=(0, 12))  # 大幅减少间距
        
        solution_title = tk.Label(solution_section, text="Solution Type", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg="#f8f9fa", fg="#1d1d1f")
        solution_title.pack(anchor="w", pady=(0, 6))  # 减少间距
        
        # 下拉选择器容器
        dropdown_container = tk.Frame(solution_section, bg="#f8f9fa")
        dropdown_container.pack(fill="x", pady=(0, 4))  # 减少间距
        
        # 溶液类型下拉选择器
        self.solution_type_var = tk.StringVar()
        self.solution_type_var.set("NaOH")  # 默认选择NaOH
        
        solutions = ["NaOH", "NaCl", "HCl"]
        self.solution_combo = ttk.Combobox(dropdown_container, 
                                          textvariable=self.solution_type_var,
                                          values=solutions,
                                          font=("Segoe UI", 11),
                                          state="readonly",
                                          width=30)
        self.solution_combo.pack(fill="x", pady=(0, 4))  # 减少间距
        
        # 绑定选择事件
        self.solution_combo.bind("<<ComboboxSelected>>", self.on_solution_type_selected)
        
        # 溶液类型描述标签
        self.solution_desc_label = tk.Label(solution_section, 
                                           text="Select the solution type to view available properties",
                                           font=("Segoe UI", 9, "italic"),
                                           bg="#f8f9fa", fg="#6e6e73")
        self.solution_desc_label.pack(anchor="w", pady=(2, 0))
    
    def _setup_property_dropdown(self, main_container):
        """设置属性下拉选择器 - 更适合大量数据"""
        # 物理性质选择 - 紧凑设计
        property_section = tk.Frame(main_container, bg="#f8f9fa")
        property_section.pack(fill="x", pady=(0, 12))  # 大幅减少间距
        
        property_title = tk.Label(property_section, text="Select Property", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg="#f8f9fa", fg="#1d1d1f")
        property_title.pack(anchor="w", pady=(0, 6))  # 减少间距
        
        # 下拉选择器容器 - 紧凑样式
        dropdown_container = tk.Frame(property_section, bg="#f8f9fa")
        dropdown_container.pack(fill="x", pady=(0, 4))  # 减少间距
        
        # 属性下拉选择器
        self.property_var = tk.StringVar()
        self.property_var.set("Choose a property...")  # 默认提示文本
        
        self.property_combo = ttk.Combobox(dropdown_container, 
                                          textvariable=self.property_var,
                                          font=("Segoe UI", 11),
                                          state="readonly",
                                          width=50)
        self.property_combo.pack(fill="x", pady=(0, 4))  # 减少间距
        
        # 绑定选择事件
        self.property_combo.bind("<<ComboboxSelected>>", self.on_property_selected)
        
        # 配置现代化样式
        style = ttk.Style()
        style.configure("TCombobox", 
                       fieldbackground="#ffffff",
                       background="#ffffff",
                       borderwidth=1,
                       relief="solid")
        
        # 属性描述标签（可选显示更多信息）
        self.property_desc_label = tk.Label(property_section, 
                                           text="Select a property to view its prediction formula",
                                           font=("Segoe UI", 9, "italic"),
                                           bg="#f8f9fa", fg="#6e6e73")
        self.property_desc_label.pack(anchor="w", pady=(2, 0))
    
    def _setup_continue_button(self, main_container):
        """设置继续按钮"""
        # Continue按钮区域 - 紧凑设计
        button_frame = tk.Frame(main_container, bg="#f8f9fa")
        button_frame.pack(fill="x", pady=(8, 0))  # 大幅减少顶部间距
        
        # 现代化Continue按钮 - 更紧凑
        self.continue_btn = tk.Button(button_frame, text="Continue", 
                                     font=("Segoe UI", 11, "bold"),
                                     bg="#007aff", fg="white", 
                                     relief="flat", bd=0, padx=24, pady=8,  # 减少按钮padding
                                     command=self.show_selected_formula, state="disabled")
        self.continue_btn.pack(anchor="center")
    
    def show_formula_selector(self):
        """显示现代化的公式选择器 - 重构版本"""
        # 创建并配置窗口
        selector_window = self._create_formula_selector_window()
        self.selector_window = selector_window  # Store reference for later use
        
        # 设置UI组件
        main_container = self._setup_formula_selector_ui(selector_window)
        self._setup_solution_type_dropdown(main_container)
        self._setup_property_dropdown(main_container)
        self._setup_continue_button(main_container)
        
        # 初始化选择状态变量
        self.formula_solution_var = tk.StringVar()
        self.selected_model_var = tk.StringVar()
        self.property_model_map = {}  # 映射显示名称到模型名称
        self.selected_solution = None
        self.selected_property = None
        
        # 选择默认的NaOH并更新属性列表
        # 初始化默认选择并更新属性列表
        self.on_solution_type_selected()
    
    def on_solution_type_selected(self, event=None):
        """处理溶液类型下拉选择器的选择事件"""
        solution_type = self.solution_type_var.get()
        self.formula_solution_var.set(solution_type)
        
        # 更新属性下拉选择器
        self.update_property_dropdown()
        
        # 更新溶液类型描述
        property_count = len(self.property_combo['values']) if hasattr(self, 'property_combo') else 0
        desc_text = f"Selected: {solution_type} ({property_count} properties available)"
        self.solution_desc_label.config(text=desc_text)
    
    
    def on_property_selected(self, event=None):
        """处理下拉选择器的属性选择事件"""
        selected_text = self.property_var.get()
        if selected_text == "Choose a property..." or not selected_text:
            # 禁用继续按钮
            if hasattr(self, 'continue_btn'):
                self.continue_btn.config(state="disabled", bg="#cccccc", fg="#666666", text="Continue")
            return
        
        # 从显示文本中提取模型名称（存储在属性映射中）
        if hasattr(self, 'property_model_map') and selected_text in self.property_model_map:
            model_name = self.property_model_map[selected_text]
            self.selected_model_var.set(model_name)
            
            # 启用继续按钮
            if hasattr(self, 'continue_btn'):
                self.continue_btn.config(state="normal", bg="#007aff", fg="white", 
                                        text="Continue →", cursor="hand2")
    
    def get_property_name(self, model_name):
        """获取属性显示名称"""
        display_name = self.format_property_name(model_name)
        # 移除溶液类型前缀
        for solution in ["NaOH", "NaCl", "HCl"]:
            if model_name.startswith(solution):
                property_name = display_name.replace(f"{solution} ", "").replace(f"{solution}", "")
                if property_name.startswith(" "):
                    property_name = property_name[1:]
                return property_name
        return display_name
    
    def update_property_dropdown(self):
        """根据选择的溶液类型更新属性下拉选择器"""
        selected_solution = self.formula_solution_var.get()
        
        # 获取当前溶液类型的可用属性
        available_properties = []
        self.property_model_map = {}  # 存储显示名称到模型名称的映射
        
        for model_name in self.models.keys():
            if model_name.startswith(selected_solution):
                display_name = self.format_property_name(model_name)
                property_name = display_name.replace(f"{selected_solution} ", "").replace(f"{selected_solution}", "")
                property_name = property_name.strip()
                if property_name:
                    available_properties.append(property_name)
                    self.property_model_map[property_name] = model_name
        
        # 按属性名称排序
        available_properties.sort()
        
        # 更新下拉选择器的值
        if hasattr(self, 'property_combo'):
            self.property_combo['values'] = available_properties
            self.property_var.set("Choose a property...")  # 重置选择
            
            # 更新描述文本
            if available_properties:
                desc_text = f"Available properties: {len(available_properties)} options"
                self.property_desc_label.config(text=desc_text)
            else:
                self.property_desc_label.config(text="No properties available for this solution type")
        
        # 重置选择状态
        if hasattr(self, 'selected_model_var'):
            self.selected_model_var.set("")
            
        # 禁用继续按钮
        if hasattr(self, 'continue_btn'):
            self.continue_btn.config(state="disabled", bg="#cccccc", fg="#666666", text="Continue")
    
    def select_property(self, model_name, property_name):
        """选择属性 - 现代化选择样式"""
        if not hasattr(self, 'selected_model_var'):
            return
            
        self.selected_model_var.set(model_name)
        
        # 更新所有列表项样式 - 现代化选择状态
        if hasattr(self, 'property_buttons'):
            for mn, btn_info in self.property_buttons.items():
                btn = btn_info['button']
                container = btn_info['container']
                if mn == model_name:
                    # 选中状态 - 现代化蓝色主题
                    btn.configure(bg="#007aff", fg="white", relief="flat")
                    container.configure(relief="solid", bd=2, highlightbackground="#007aff")
                else:
                    # 未选中状态 - 恢复默认样式
                    btn.configure(bg="#fafafa", fg="#2c2c2c", relief="flat")
                    container.configure(relief="flat", bd=0)
        
        # 启用继续按钮
        if hasattr(self, 'continue_btn'):
            self.continue_btn.config(state="normal", bg="#007aff", fg="white", 
                                    text="Continue →", cursor="hand2")
    
    
    def show_selected_formula(self):
        """显示选中的公式"""
        model_name = self.selected_model_var.get()
        if not model_name:
            return
        
        display_name = self.format_property_name(model_name)
        self.show_model_formula(model_name, display_name, self.selector_window)
    
    def show_model_formula(self, model_name, display_name, parent_window):
        """显示特定模型的公式"""
        # 隐藏选择器窗口而不是销毁它
        parent_window.withdraw()
        
        formula_window = tk.Toplevel(self.root)
        formula_window.title(f"{display_name} - 预测公式")
        formula_window.geometry("800x600")
        formula_window.resizable(True, True)
        formula_window.configure(bg="#ffffff")
        
        # 确保窗口显示在最前面
        formula_window.transient(self.root)
        formula_window.grab_set()
        formula_window.focus_set()
        formula_window.lift()
        formula_window.attributes('-topmost', True)
        formula_window.after(100, lambda: formula_window.attributes('-topmost', False))
        
        # 创建标题框架
        title_frame = tk.Frame(formula_window, bg="#2E86AB", height=60)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=f"{display_name} - 预测公式", 
                              font=("Arial", 16, "bold"), fg="white", bg="#2E86AB")
        title_label.pack(expand=True)
        
        # 创建滚动文本框
        main_frame = tk.Frame(formula_window, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        text_frame = tk.Frame(main_frame, bg="#ffffff")
        text_frame.pack(fill="both", expand=True)
        
        formula_text = tk.Text(text_frame, font=("Consolas", 12), wrap=tk.WORD,
                              bg="#ffffff", fg="#333333", padx=15, pady=15,
                              relief="solid", borderwidth=1)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=formula_text.yview)
        formula_text.configure(yscrollcommand=scrollbar.set)
        
        formula_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 提取公式
        formula_info = self.extract_model_formula(model_name)
        
        if isinstance(formula_info, str):
            # 错误信息
            formula_content = f"{display_name}\n" + "="*50 + f"\n\n{formula_info}"
        elif formula_info is None:
            # 无法提取公式
            formula_content = f"{display_name}\n" + "="*50 + f"\n\n无法提取该模型的公式，可能是不支持的模型类型。"
        else:
            # 生成公式内容
            formula_content = f"{display_name} 预测公式\n"
            formula_content += "="*50 + "\n\n"
            
            if formula_info['type'] == 'polynomial':
                formula_content += f"数学公式:\n{formula_info['formula']}\n\n"
                formula_content += "变量说明:\n"
                for i, var in enumerate(formula_info['variables']):
                    formula_content += f"• {var}\n"
                formula_content += f"• Y = {display_name} ({formula_info['unit']})\n\n"
                
                formula_content += "系数详情:\n"
                for term, coeff in formula_info['coefficients'].items():
                    if abs(coeff) > 1e-10:
                        formula_content += f"• {term}: {coeff:.6f}\n"
                
                formula_content += f"\n模型信息:\n"
                formula_content += f"• 类型: {formula_info['degree']}次多项式回归\n"
                formula_content += f"• 算法: Ridge回归 + 正则化\n"
            
            elif formula_info['type'] == 'neural_network_log':
                # HCl vapor pressure neural network with log transformation
                formula_content += f"预测公式:\n{formula_info['formula']}\n"
                formula_content += f"最终输出: {formula_info['final_formula']}\n\n"
                
                formula_content += "变量说明:\n"
                for var in formula_info['variables']:
                    formula_content += f"• {var}\n"
                formula_content += f"• Y = {display_name} ({formula_info['unit']})\n\n"
                
                formula_content += f"神经网络架构:\n• {formula_info['architecture']}\n"
                formula_content += f"• 激活函数: {formula_info['activation']}\n"
                formula_content += f"• 输入特征数量: {formula_info['feature_count']}个\n\n"
                
                formula_content += formula_info['feature_engineering'] + "\n"
                
                formula_content += f"模型说明:\n• {formula_info['note']}\n"
                formula_content += "• 该模型基于Clausius-Clapeyron方程和物理化学原理\n"
                formula_content += "• 使用对数变换确保蒸气压预测结果为正值\n"
            
            elif formula_info['type'] == 'neural_network':
                formula_content += f"预测公式:\n{formula_info['formula']}\n\n"
                
                formula_content += "变量说明:\n"
                for var in formula_info['variables']:
                    formula_content += f"• {var}\n"
                formula_content += f"• Y = {display_name} ({formula_info['unit']})\n\n"
                
                formula_content += f"神经网络架构:\n• {formula_info['architecture']}\n"
                formula_content += f"• 激活函数: {formula_info['activation']}\n\n"
                formula_content += f"模型说明:\n• {formula_info['note']}\n"
            
            else:
                formula_content += f"模型类型: {formula_info['type']}\n"
                formula_content += f"说明: {formula_info.get('note', '复杂非线性模型')}\n\n"
                formula_content += "变量说明:\n"
                for var in formula_info['variables']:
                    formula_content += f"• {var}\n"
                formula_content += f"• Y = {display_name} ({formula_info['unit']})\n"
        
        formula_text.insert("1.0", formula_content)
        formula_text.configure(state="disabled")  # 只读
        
        # 配置文本样式
        formula_text.tag_add("title", "1.0", "1.end")
        formula_text.tag_config("title", font=("Arial", 14, "bold"), foreground="#2E86AB")
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.pack(fill="x", pady=(15, 0))
        
        # 返回按钮 - Apple风格
        def return_to_selector():
            formula_window.destroy()
            parent_window.deiconify()  # 重新显示选择器窗口
            parent_window.lift()
            parent_window.focus_set()
        
        close_btn = tk.Button(button_frame, text="← Back to Selection", 
                             command=return_to_selector,
                             bg="#007aff", fg="white", font=("Segoe UI", 12, "bold"),
                             padx=24, pady=12, relief="flat", bd=0, cursor="hand2")
        close_btn.pack(anchor="center")
        
        # 设置窗口关闭协议，确保关闭时返回到选择器
        formula_window.protocol("WM_DELETE_WINDOW", return_to_selector)

def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()