import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Canvas, Button, Label, Entry, Frame, Window, Toplevel, Text, Scrollbar, Checkbutton
import math

class PolygonAnalyzer(Window):
    
    def __init__(self):
        super().__init__()
        
        self.current_theme = 'cosmo' 
        
        self.title("Irregular Polygon Area Calculator)")
        self.geometry("1100x650")  # العرض 1100
        
        self.points = [] # قائمة النقاط المدخلة بالترتيب الأصلي
        self.scale_factor = 20 
        self.offset_x = 300 
        self.offset_y = 300
        self.polygon_id = None 
        
        self.last_x = 0
        self.last_y = 0
        self.is_panning = False 

        self.create_widgets()
    
    # --- دالة فرز النقاط المسترجعة ---
    def sort_points_by_angle(self, points):
        """
        يرتب النقاط حول محيط الشكل باستخدام الزاوية بالنسبة لمركز الكتلة.
        هذا يضمن رسم مضلع غير متقاطع (يعمل بشكل مثالي للمضلعات المحدبة).
        """
        if len(points) < 3:
            return points

        # حساب مركز الكتلة (Centroid)
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)

        # دالة مقارنة لحساب الزاوية (atan2)
        def get_angle(point):
            x, y = point
            return math.atan2(y - center_y, x - center_x)

        # فرز النقاط باستخدام الزاوية
        sorted_points = sorted(points, key=get_angle)
        return sorted_points
    
    def create_widgets(self):
        
        # --- 1. إعداد منطقة الرسم على اليمين ---
        canvas_container_frame = Frame(self, bootstyle="light")
        canvas_container_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas = Canvas(canvas_container_frame, bg='white', width=500, height=500)
        self.canvas.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.start_pan_or_click)
        self.canvas.bind("<B1-Motion>", self.pan_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.end_pan_or_click)
        
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel) 
        self.canvas.bind("<Button-4>", self.on_mouse_wheel) 
        self.canvas.bind("<Button-5>", self.on_mouse_wheel) 
        
        self.draw_axes()
        
        # --- 2. إعداد منطقة التحكم على اليسار مع شريط التمرير ---
        
        control_main_frame = Frame(self, padding=(10, 10)) 
        control_main_frame.pack(side="left", fill="y")
        
        control_scrollbar = Scrollbar(control_main_frame, orient="vertical")
        control_scrollbar.pack(side="right", fill="y")
        
        control_canvas = Canvas(control_main_frame, yscrollcommand=control_scrollbar.set, width=350) 
        control_canvas.pack(side="left", fill="both", expand=True)
        
        control_scrollbar.config(command=control_canvas.yview)
        
        control_inner_frame = Frame(control_canvas)
        
        control_canvas.create_window((0, 0), window=control_inner_frame, anchor="nw")
        
        control_inner_frame.bind("<Configure>", 
            lambda e: control_canvas.configure(
                scrollregion=control_canvas.bbox("all")
            )
        )

        # --- نقل جميع عناصر التحكم إلى control_inner_frame ---
        
        self.dark_mode_var = tk.BooleanVar(value=False)
        Checkbutton(
            control_inner_frame, 
            text="وضع داكن 🌙 / فاتح ☀️", 
            variable=self.dark_mode_var, 
            command=self.toggle_theme,
            bootstyle="round-toggle" 
        ).pack(pady=10, fill="x")
        
        Label(control_inner_frame, text="**إدخال الإحداثيات**", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        Label(control_inner_frame, text="إحداثي X:").pack(pady=2)
        self.x_entry = Entry(control_inner_frame, width=15)
        self.x_entry.pack(pady=2)
        
        Label(control_inner_frame, text="إحداثي Y:").pack(pady=2)
        self.y_entry = Entry(control_inner_frame, width=15)
        self.y_entry.pack(pady=2)
        
        Button(control_inner_frame, text="➕ إضافة نقطة", command=self.add_point, bootstyle="info").pack(pady=10, fill="x")
        
        Label(control_inner_frame, text="**النقاط المدخلة**").pack(pady=5)
        self.points_listbox = tk.Listbox(control_inner_frame, height=8, width=25) 
        self.points_listbox.pack(pady=5)
        
        Button(control_inner_frame, text="ℹ️ عرض خطوات حساب المساحة", command=self.show_calculation_method, bootstyle="primary-outline").pack(pady=10, fill="x")
        
        zoom_frame = Frame(control_inner_frame)
        zoom_frame.pack(pady=10)
        
        Label(zoom_frame, text="التحكم بالزوم:").pack(side="left", padx=5)
        Button(zoom_frame, text="🔎 Zoom In", command=lambda: self.zoom_in(None), bootstyle="secondary").pack(side="left", padx=5)
        Button(zoom_frame, text="🔍 Zoom Out", command=lambda: self.zoom_out(None), bootstyle="secondary").pack(side="left", padx=5)
        
        Button(control_inner_frame, text="✏️ رسم الشكل وحساب المساحة", command=self.draw_and_calculate, bootstyle="success").pack(pady=15, fill="x")
        
        self.area_label = Label(control_inner_frame, text="المساحة: 0.0 وحدة مربعة", font=('Helvetica', 10, 'bold'))
        self.area_label.pack(pady=5)
        
        Label(control_inner_frame, text="\n**تحقق من نقطة**", font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        Label(control_inner_frame, text="نقطة الاختبار X:").pack(pady=2)
        self.test_x_entry = Entry(control_inner_frame, width=15)
        self.test_x_entry.pack(pady=2)
        
        Label(control_inner_frame, text="نقطة الاختبار Y:").pack(pady=2)
        self.test_y_entry = Entry(control_inner_frame, width=15)
        self.test_y_entry.pack(pady=2)
        
        Button(control_inner_frame, text="🔍 تحقق", command=self.check_point_location, bootstyle="warning").pack(pady=10, fill="x")
        
        Button(control_inner_frame, 
               text="↩️ التحقق من نقطة البداية (P1)", 
               command=self.check_start_point, 
               bootstyle="secondary").pack(pady=5, fill="x")

        self.result_label = Label(control_inner_frame, text="النتيجة:", font=('Helvetica', 10, 'bold'))
        self.result_label.pack(pady=5)
        
        Button(control_inner_frame, text="🔄 إعادة تعيين", command=self.reset_app, bootstyle="danger").pack(pady=20, fill="x")
        
        # **تم إلغاء الملاحظة من هنا**


    def toggle_theme(self):
        
        if self.dark_mode_var.get():
            self.current_theme = 'superhero' 
            self.canvas.config(bg='#343a40') 
        else:
            self.current_theme = 'cosmo'
            self.canvas.config(bg='white') 
            
        self.style.theme_use(self.current_theme)
        
        self.redraw_canvas()
    
    def start_pan_or_click(self, event):
        self.last_x = event.x
        self.last_y = event.y
        self.is_panning = False 

    def pan_canvas(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        if abs(dx) > 3 or abs(dy) > 3: 
            self.is_panning = True
            self.offset_x += dx
            self.offset_y += dy
            
            self.last_x = event.x
            self.last_y = event.y
            
            self.redraw_canvas()

    def end_pan_or_click(self, event):
        if not self.is_panning:
            self.canvas_click_point(event)
        self.is_panning = False
        
    def redraw_canvas(self):
        self.draw_axes()
        if self.points:
            self.draw_and_calculate(calculate_area=False)
            
    def draw_axes(self):
        
        w = self.canvas.winfo_width() 
        h = self.canvas.winfo_height()
        self.canvas.delete("axes")
        
        axis_color = "dark gray" if self.current_theme == 'cosmo' else "light gray"
        text_color = "gray" if self.current_theme == 'cosmo' else "light gray"
        
        limit = int(max(w, h) / self.scale_factor) + 1 
        
        self.canvas.create_line(0, self.offset_y, w, self.offset_y, fill=axis_color, dash=(4, 4), tags="axes") 
        self.canvas.create_text(w - 15, self.offset_y + 15, text="X", fill=text_color, tags="axes")
        self.canvas.create_line(self.offset_x, 0, self.offset_x, h, fill=axis_color, dash=(4, 4), tags="axes") 
        self.canvas.create_text(self.offset_x + 15, 15, text="Y", fill=text_color, tags="axes")
        
        for i in range(-limit, limit + 1):
            x_coord = self.offset_x + i * self.scale_factor
            
            if 0 < x_coord < w:
                self.canvas.create_line(x_coord, self.offset_y - 3, x_coord, self.offset_y + 3, fill=axis_color, tags="axes")
                if i % 2 == 0 and i != 0:
                    text_y = max(3, min(h - 10, self.offset_y + 10))
                    self.canvas.create_text(x_coord, text_y, text=str(i), fill=text_color, tags="axes")

            y_coord = self.offset_y - i * self.scale_factor
            
            if 0 < y_coord < h:
                self.canvas.create_line(self.offset_x - 3, y_coord, self.offset_x + 3, y_coord, fill=axis_color, tags="axes")
                if i % 2 == 0 and i != 0:
                    text_x = max(10, min(w - 3, self.offset_x + 10))
                    self.canvas.create_text(text_x, y_coord, text=str(i), fill=text_color, tags="axes")
                

    def show_calculation_method(self):
        
        points = self.points
        # نستخدم النقاط المفروزة للعرض والحساب
        sorted_points = self.sort_points_by_angle(points) 

        if len(points) < 3:
            messagebox.showwarning("نقاط غير كافية", "الرجاء إدخال 3 نقاط على الأقل (رؤوس) لعرض خطوات الحساب.")
            return

        explain_window = Toplevel(self)
        explain_window.title("خطوات حساب المساحة التفصيلية")
        explain_window.geometry("700x480")
        
        explain_window.config(bg=self.style.lookup('.', 'background'))
        
        scroll_frame = Frame(explain_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        yscroll = Scrollbar(scroll_frame, orient="vertical")
        yscroll.pack(side="right", fill="y")

        text_widget = Text(
            scroll_frame, 
            wrap="word", 
            yscrollcommand=yscroll.set, 
            height=15, 
            width=70, 
            font=('Consolas', 10) 
        )
        text_widget.pack(side="left", fill="both", expand=True)
        yscroll.config(command=text_widget.yview)

        n = len(sorted_points)
        points_str = " -> ".join([f"P{i+1}({x:.2f}, {y:.2f})" for i, (x, y) in enumerate(sorted_points)])
        current_sum1, current_sum2 = 0, 0
        sum1_terms, sum2_terms = [], []
        
        # نستخدم النقاط المفروزة للحساب
        for i in range(n):
            x_i, y_i = sorted_points[i]
            x_next, y_next = sorted_points[(i + 1) % n]
            
            term1 = x_i * y_next
            term2 = y_i * x_next
            
            current_sum1 += term1
            current_sum2 += term2
            
            sum1_terms.append(f"({x_i:.2f} * {y_next:.2f}) = {term1:.2f}")
            sum2_terms.append(f"({y_i:.2f} * {x_next:.2f}) = {term2:.2f}")

        difference = current_sum1 - current_sum2
        area = 0.5 * abs(difference)
        
        explanation = "## خطوات حساب مساحة الشكل \n\n"
        explanation += "**النقاط المُستخدمة في الحساب (بعد الفرز لضمان الترتيب):**\n"
        explanation += f"   {points_str}\n"
        
        explanation += "\n### 1. حساب المجموع الأول (المجموع أ)\n"
        explanation += f"المجموع أ = {' + '.join(sum1_terms)}\n"
        explanation += f"   **القيمة النهائية للمجموع أ = {current_sum1:.2f}**\n"
        
        explanation += "\n### 2. حساب المجموع الثاني (المجموع ب)\n"
        explanation += f"المجموع ب = {' + '.join(sum2_terms)}\n"
        explanation += f"   **القيمة النهائية للمجموع ب = {current_sum2:.2f}**\n"
        
        explanation += "\n### 3. حساب المساحة النهائية\n"
        explanation += f"A = 0.5 * | {current_sum1:.2f} - {current_sum2:.2f} |\n"
        explanation += f"   A = 0.5 * {abs(difference):.2f}\n"
        explanation += f"   **المساحة النهائية = {area:.2f} وحدة مربعة**\n"
        
        text_widget.insert("1.0", explanation)
        
        text_widget.tag_config("h2", font=('Consolas', 14, 'bold'), foreground='navy')
        text_widget.tag_config("h3", font=('Consolas', 12, 'bold'), foreground='darkgreen')
        text_widget.tag_add("h2", "1.0", "1.end") 
        text_widget.tag_add("h3", "6.0", "6.end") 
        text_widget.tag_add("h3", "10.0", "10.end") 
        text_widget.tag_add("h3", "14.0", "14.end") 
        
        text_widget.config(state="disabled") 
        
        Button(explain_window, text="إغلاق", command=explain_window.destroy, bootstyle="primary").pack(pady=10)


    def convert_coords_to_canvas(self, x, y):
        canvas_x = self.offset_x + x * self.scale_factor
        canvas_y = self.offset_y - y * self.scale_factor 
        return canvas_x, canvas_y

    def convert_coords_from_canvas(self, canvas_x, canvas_y):
        x = (canvas_x - self.offset_x) / self.scale_factor
        y = (self.offset_y - canvas_y) / self.scale_factor
        return x, y

    def add_point(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.points.append((x, y))
            self.points_listbox.insert("end", f"({x:.2f}, {y:.2f})")
            self.x_entry.delete(0, "end")
            self.y_entry.delete(0, "end")
            self.x_entry.focus()
        except ValueError:
            messagebox.showerror("خطأ في الإدخال", "الرجاء إدخال أرقام صحيحة للإحداثيات.")

    def calculate_polygon_area(self, points):
        # صيغة شريط التمرير (Shoelace Formula) - تعمل على النقاط المرتبة
        n = len(points)
        if n < 3: return 0.0
        sum1, sum2 = 0, 0
        for i in range(n):
            x_i, y_i = points[i]
            x_next, y_next = points[(i + 1) % n]
            sum1 += x_i * y_next
            sum2 += y_i * x_next
        return 0.5 * abs(sum1 - sum2)

    def is_point_in_polygon(self, point_x, point_y, polygon_points):
        # دالة راي كاستنج (Ray casting) - تستخدم النقاط المرتبة للحصول على نتيجة صحيحة
        n = len(polygon_points)
        if n < 3: return False
        inside = False
        for i in range(n):
            (x1, y1) = polygon_points[i]
            (x2, y2) = polygon_points[(i + 1) % n] 
            if ((y1 <= point_y < y2) or (y2 <= point_y < y1)): 
                # تجنب القسمة على صفر
                if (y2 - y1) == 0:
                    continue
                x_intersect = (point_y - y1) * (x2 - x1) / (y2 - y1) + x1
                if (point_x < x_intersect):
                    inside = not inside
        return inside
        
    def draw_and_calculate(self, calculate_area=True):
        if len(self.points) < 3:
            if calculate_area:
                 messagebox.showwarning("نقاط غير كافية", "الرجاء إدخال 3 نقاط على الأقل لرسم شكل.")
            return

        # 1. فرز النقاط لضمان عدم تقاطع الشكل 
        sorted_points = self.sort_points_by_angle(self.points)
        
        self.canvas.delete("polygon_shape")
        self.canvas.delete("point_marker")
        
        # 2. حساب المساحة باستخدام النقاط المفروزة
        if calculate_area:
            area = self.calculate_polygon_area(sorted_points) 
            self.area_label.config(text=f"المساحة: {area:.2f} وحدة مربعة")
        
        canvas_coords = []
        for i, (x, y) in enumerate(sorted_points):
            cx, cy = self.convert_coords_to_canvas(x, y)
            canvas_coords.extend([cx, cy])
            
            # رسم النقطة وتسميتها (P1, P2...)
            self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="red", outline="red", tags="polygon_shape")
            self.canvas.create_text(cx+8, cy-8, text=f"P{i+1} ({x:.1f},{y:.1f})", fill="red", tags="polygon_shape")

        # 3. رسم المضلع باستخدام النقاط المفروزة
        self.polygon_id = self.canvas.create_polygon(
            canvas_coords, 
            outline='blue', 
            fill='lightblue', 
            width=2, 
            tags="polygon_shape"
        )
        
        try:
            test_x = float(self.test_x_entry.get())
            test_y = float(self.test_y_entry.get())
            self._perform_point_check(test_x, test_y)
        except ValueError:
            pass 

    def check_start_point(self):
        
        if len(self.points) < 3:
            messagebox.showwarning("خطأ", "يجب رسم شكل أولاً (3 نقاط على الأقل).")
            return
        
        # بعد الفرز، تكون النقطة P1 هي الأولى في القائمة المفروزة
        sorted_points = self.sort_points_by_angle(self.points)
        start_x, start_y = sorted_points[0]
        
        self.test_x_entry.delete(0, "end")
        self.test_x_entry.insert(0, f"{start_x:.2f}")
        self.test_y_entry.delete(0, "end")
        self.test_y_entry.insert(0, f"{start_y:.2f}")
        
        self._perform_point_check_on_sorted(start_x, start_y, sorted_points)

    def check_point_location(self):
        
        if len(self.points) < 3:
            messagebox.showwarning("خطأ", "يجب رسم شكل أولاً (3 نقاط على الأقل).")
            return
            
        try:
            test_x = float(self.test_x_entry.get())
            test_y = float(self.test_y_entry.get())
        except ValueError:
            messagebox.showerror("خطأ في الإدخال", "الرجاء إدخال أرقام صحيحة لنقطة الاختبار.")
            return
        
        # نستخدم النقاط المفروزة للتحقق
        sorted_points = self.sort_points_by_angle(self.points)
        self._perform_point_check_on_sorted(test_x, test_y, sorted_points)
        
    def _perform_point_check_on_sorted(self, test_x, test_y, sorted_points):
        
        is_inside = self.is_point_in_polygon(test_x, test_y, sorted_points)
        result_text = "✨ النقطة **داخل** الشكل!" if is_inside else "❌ النقطة **خارج** الشكل."
        result_color = "green" if is_inside else "darkred"
        self.result_label.config(text=f"النتيجة: {result_text}", foreground=result_color)
        self.draw_test_point(test_x, test_y, is_inside)

    def _perform_point_check(self, test_x, test_y):
         # هذا يستخدم فقط من check_point_location لتجنب إعادة الفرز مرتين
        sorted_points = self.sort_points_by_angle(self.points)
        self._perform_point_check_on_sorted(test_x, test_y, sorted_points)


    def draw_test_point(self, x, y, is_inside):
        self.canvas.delete("test_point")
        cx, cy = self.convert_coords_to_canvas(x, y)
        color = "lime green" if is_inside else "orange"
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=color, outline="black", width=1, tags="test_point")
        self.canvas.create_text(cx+15, cy, text=f"P({x:.1f},{y:.1f})", fill="black", tags="test_point")

    def canvas_click_point(self, event):
        x, y = self.convert_coords_from_canvas(event.x, event.y)
        self.test_x_entry.delete(0, "end")
        self.test_x_entry.insert(0, f"{x:.2f}")
        self.test_y_entry.delete(0, "end")
        self.test_y_entry.insert(0, f"{y:.2f}")
        self.check_point_location()

    def on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0: 
            self.zoom_in(event)
        elif event.num == 5 or event.delta < 0: 
            self.zoom_out(event)

    def zoom_in(self, event):
        self.scale_factor *= 1.25
        if self.scale_factor > 100:
             self.scale_factor = 100
        self.redraw_canvas()

    def zoom_out(self, event):
        self.scale_factor /= 1.25
        if self.scale_factor < 5:
            self.scale_factor = 5
        self.redraw_canvas()

    def reset_app(self):
        self.points = []
        self.scale_factor = 20 
        self.offset_x = 300 
        self.offset_y = 300 
        self.points_listbox.delete(0, "end")
        self.canvas.delete("polygon_shape")
        self.canvas.delete("test_point")
        self.area_label.config(text="المساحة: 0.0 وحدة مربعة")
        self.result_label.config(text="النتيجة:", foreground="black")
        self.x_entry.delete(0, "end")
        self.y_entry.delete(0, "end")
        self.test_x_entry.delete(0, "end")
        self.test_y_entry.delete(0, "end")
        self.draw_axes()

if __name__ == "__main__":
    app = PolygonAnalyzer()
    app.mainloop()