import customtkinter
import threading
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta

from config import load_config, save_config
from zk_service import ZKService
from reporter import export_to_excel
from turnos_manager import TurnosManager

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class DatePickerModal(customtkinter.CTkToplevel):
    """Modal enorme y seguro para seleccionar fechas sin bugs visuales."""
    def __init__(self, master, initial_date=None, title="Seleccionar Fecha", callback=None):
        super().__init__(master)
        self.title(title)
        self.geometry("400x350")
        self.transient(master)
        self.grab_set()
        
        self.callback = callback
        
        self.cal = Calendar(self, selectmode='day', locale='es_ES', 
                            font="Arial 14", cursor="hand2", 
                            background="#1e1e1e", foreground="white", 
                            headersbackground="#3484F0", headersforeground="white",
                            normalbackground="#2a2d2e", normalforeground="white",
                            weekendbackground="#2a2d2e", weekendforeground="red")
        self.cal.pack(fill="both", expand=True, padx=20, pady=20)
        
        if initial_date:
            self.cal.selection_set(initial_date)
            
        btn_ok = customtkinter.CTkButton(self, text="Confirmar Selección", height=40, font=customtkinter.CTkFont(size=16, weight="bold"), command=self.on_ok)
        btn_ok.pack(pady=(0, 20))
        
    def on_ok(self):
        sel = self.cal.selection_get()
        if self.callback:
            self.callback(sel)
        self.destroy()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ZKManager - Panel de Asistencia Inteligente V5")
        self.geometry("1050x700")

        # Config & Services
        self.config_data = load_config()
        self.zk = ZKService(self.config_data['ip'], self.config_data['port'])
        self.turnos_manager = TurnosManager()
        
        # Grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # UI Aesthetics
        btn_font = customtkinter.CTkFont(size=16, weight="bold")
        title_font = customtkinter.CTkFont(size=26, weight="bold")

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="ZKManager", font=title_font)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_dashboard = customtkinter.CTkButton(self.sidebar_frame, text="Dashboard", font=btn_font, height=50, command=self.show_dashboard_frame)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_users = customtkinter.CTkButton(self.sidebar_frame, text="Gestión Empleados", font=btn_font, height=50, command=self.show_users_frame)
        self.btn_users.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_shifts = customtkinter.CTkButton(self.sidebar_frame, text="Configurar Turnos", font=btn_font, height=50, fg_color="#8e44ad", hover_color="#9b59b6", command=self.show_shifts_frame)
        self.btn_shifts.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_reports = customtkinter.CTkButton(self.sidebar_frame, text="Reportes", font=btn_font, height=50, command=self.show_reports_frame)
        self.btn_reports.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_config = customtkinter.CTkButton(self.sidebar_frame, text="Ajustes de Red", font=btn_font, height=50, command=self.show_config_frame)
        self.btn_config.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Main Frame containers
        self.dashboard_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.users_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.shifts_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.reports_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.config_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self._setup_dashboard()
        self._setup_users()
        self._setup_shifts()
        self._setup_reports()
        self._setup_config()

        # Select Dashboard by default
        self.show_dashboard_frame()

    def _setup_dashboard(self):
        title_font = customtkinter.CTkFont(size=24, weight="bold")
        info_font = customtkinter.CTkFont(size=18)
        
        self.lbl_dash_title = customtkinter.CTkLabel(self.dashboard_frame, text="Panel de Control Principal", font=title_font)
        self.lbl_dash_title.grid(row=0, column=0, padx=30, pady=30, sticky="w")
        
        self.lbl_status = customtkinter.CTkLabel(self.dashboard_frame, text="Estatus del Reloj: Desconectado", text_color="red", font=info_font)
        self.lbl_status.grid(row=1, column=0, padx=30, pady=15, sticky="w")
        
        self.lbl_info = customtkinter.CTkLabel(self.dashboard_frame, text="Presiona 'Conectar' para validar la comunicación de red.", font=info_font)
        self.lbl_info.grid(row=2, column=0, padx=30, pady=15, sticky="w")

        self.btn_connect = customtkinter.CTkButton(self.dashboard_frame, text="Conectar al Dispositivo", height=50, font=customtkinter.CTkFont(size=16, weight="bold"), command=self.connect_and_refresh)
        self.btn_connect.grid(row=3, column=0, padx=30, pady=30, sticky="w")

    def _setup_users(self):
        self.users_frame.grid_rowconfigure(2, weight=1)
        self.users_frame.grid_columnconfigure(0, weight=1)
        self.lbl_users_title = customtkinter.CTkLabel(self.users_frame, text="Administración de Empleados", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.lbl_users_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.users_toolbar = customtkinter.CTkFrame(self.users_frame, fg_color="transparent")
        self.users_toolbar.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        btn_font = customtkinter.CTkFont(size=14, weight="bold")
        
        self.btn_load_users = customtkinter.CTkButton(self.users_toolbar, text="Sincronizar Reloj", font=btn_font, height=40, command=self.load_users_from_device, width=130)
        self.btn_load_users.pack(side="left", padx=(0, 15))
        
        self.btn_add_user = customtkinter.CTkButton(self.users_toolbar, text="+ Registrar Nuevo", font=btn_font, height=40, command=self.add_user_dialog, width=130, fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_add_user.pack(side="left", padx=15)
        
        self.btn_edit_user = customtkinter.CTkButton(self.users_toolbar, text="✎ Editar Datos", font=btn_font, height=40, command=self.edit_user_dialog, width=130, fg_color="#f39c12", hover_color="#e67e22")
        self.btn_edit_user.pack(side="left", padx=15)
        
        self.btn_delete_user = customtkinter.CTkButton(self.users_toolbar, text="- Dar de Baja", font=btn_font, height=40, command=self.delete_user_action, width=130, fg_color="#c0392b", hover_color="#e74c3c")
        self.btn_delete_user.pack(side="left", padx=15)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=35, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=('Arial', 12))
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=('Arial', 12, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])
        
        self.tree_users = ttk.Treeview(self.users_frame, columns=("uid", "name", "privilege", "turno"), show="headings")
        self.tree_users.heading("uid", text="ID Único")
        self.tree_users.heading("name", text="Nombre del Trabajador")
        self.tree_users.heading("privilege", text="Nivel de Acceso")
        self.tree_users.heading("turno", text="Turno Asignado")
        self.tree_users.column("uid", width=120, anchor="center")
        self.tree_users.column("name", width=300)
        self.tree_users.column("privilege", width=150, anchor="center")
        self.tree_users.column("turno", width=150, anchor="center")
        self.tree_users.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def _setup_shifts(self):
        self.shifts_frame.grid_rowconfigure(2, weight=1)
        self.shifts_frame.grid_columnconfigure(0, weight=1)
        self.lbl_shifts_title = customtkinter.CTkLabel(self.shifts_frame, text="Gestor de Horarios y Turnos", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.lbl_shifts_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        toolbar = customtkinter.CTkFrame(self.shifts_frame, fg_color="transparent")
        toolbar.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        btn_font = customtkinter.CTkFont(size=14, weight="bold")
        btn_add = customtkinter.CTkButton(toolbar, text="+ Generar Turno", font=btn_font, height=40, command=self.add_shift_dialog, width=130, fg_color="#27ae60", hover_color="#2ecc71")
        btn_add.pack(side="left", padx=(0, 15))
        
        btn_edit = customtkinter.CTkButton(toolbar, text="✎ Editar Turno", font=btn_font, height=40, command=self.edit_shift_dialog, width=130, fg_color="#f39c12", hover_color="#e67e22")
        btn_edit.pack(side="left", padx=15)
        
        btn_del = customtkinter.CTkButton(toolbar, text="- Borrar Turno", font=btn_font, height=40, command=self.delete_shift_action, width=130, fg_color="#c0392b", hover_color="#e74c3c")
        btn_del.pack(side="left", padx=15)
        
        self.tree_shifts = ttk.Treeview(self.shifts_frame, columns=("id", "nombre", "entrada", "salida"), show="headings")
        self.tree_shifts.heading("id", text="ID")
        self.tree_shifts.heading("nombre", text="Nombre del Turno")
        self.tree_shifts.heading("entrada", text="Hora Entrada")
        self.tree_shifts.heading("salida", text="Hora Salida")
        self.tree_shifts.column("id", width=80, anchor="center")
        self.tree_shifts.column("nombre", width=300)
        self.tree_shifts.column("entrada", width=150, anchor="center")
        self.tree_shifts.column("salida", width=150, anchor="center")
        self.tree_shifts.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.load_shifts()

    def _setup_reports(self):
        title_font = customtkinter.CTkFont(size=24, weight="bold")
        info_font = customtkinter.CTkFont(size=16)
        
        self.lbl_rep_title = customtkinter.CTkLabel(self.reports_frame, text="Generador Avanzado de Reportes", font=title_font)
        self.lbl_rep_title.grid(row=0, column=0, padx=30, pady=30, sticky="w")
        
        self.lbl_rep_desc = customtkinter.CTkLabel(self.reports_frame, text="Selecciona un rango de fechas para exportar el registro a hojas de cálculo analíticas.", font=info_font)
        self.lbl_rep_desc.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        
        # Filtros Fecha - Modal UI Style
        self.date_frame = customtkinter.CTkFrame(self.reports_frame, fg_color="transparent")
        self.date_frame.grid(row=2, column=0, padx=30, pady=20, sticky="w")
        
        today = datetime.now()
        first_day = today.replace(day=1)
        
        # State variables for dates
        self.d_desde = first_day.date()
        self.d_hasta = today.date()
        
        btn_font = customtkinter.CTkFont(size=14, weight="bold")
        
        self.lbl_desde = customtkinter.CTkLabel(self.date_frame, text="Día Inicial:", font=info_font)
        self.lbl_desde.grid(row=0, column=0, padx=(0,10))
        self.btn_cal_desde = customtkinter.CTkButton(self.date_frame, text=self.d_desde.strftime("%Y-%m-%d"), height=40, font=btn_font, command=lambda: self.open_calendar_modal('desde'))
        self.btn_cal_desde.grid(row=0, column=1, padx=(0,30))
        
        self.lbl_hasta = customtkinter.CTkLabel(self.date_frame, text="Día Final:", font=info_font)
        self.lbl_hasta.grid(row=0, column=2, padx=(0,10))
        self.btn_cal_hasta = customtkinter.CTkButton(self.date_frame, text=self.d_hasta.strftime("%Y-%m-%d"), height=40, font=btn_font, command=lambda: self.open_calendar_modal('hasta'))
        self.btn_cal_hasta.grid(row=0, column=3)

        self.btn_gen_rep = customtkinter.CTkButton(self.reports_frame, text="Generar Resumen Corporativo (Excel)", height=60, font=customtkinter.CTkFont(size=18, weight="bold"), command=self.generate_report, fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_gen_rep.grid(row=3, column=0, padx=30, pady=30, sticky="w")

        self.lbl_rep_status = customtkinter.CTkLabel(self.reports_frame, text="", text_color="yellow", font=info_font)
        self.lbl_rep_status.grid(row=4, column=0, padx=30, pady=10, sticky="w")

    def _setup_config(self):
        self.lbl_conf_title = customtkinter.CTkLabel(self.config_frame, text="Parámetros de Red", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.lbl_conf_title.grid(row=0, column=0, padx=30, pady=30, sticky="w")
        
        lbl_info = customtkinter.CTkLabel(self.config_frame, text="Dirección IP del Reloj Biométrico ZKTeco:", font=customtkinter.CTkFont(size=16))
        lbl_info.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="w")
        
        self.entry_ip = customtkinter.CTkEntry(self.config_frame, placeholder_text="Ej. 192.168.1.200", width=300, height=50, font=customtkinter.CTkFont(size=18))
        self.entry_ip.insert(0, self.config_data['ip'])
        self.entry_ip.grid(row=2, column=0, padx=30, pady=10, sticky="w")
        
        self.btn_save_conf = customtkinter.CTkButton(self.config_frame, text="Guardar Parámetros", height=50, font=customtkinter.CTkFont(size=16, weight="bold"), command=self.save_configuration)
        self.btn_save_conf.grid(row=3, column=0, padx=30, pady=30, sticky="w")

    # --- ROUTING ---
    def select_frame_by_name(self, name):
        self.btn_dashboard.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.btn_users.configure(fg_color=("gray75", "gray25") if name == "users" else "transparent")
        self.btn_shifts.configure(fg_color=("gray75", "gray25") if name == "shifts" else "transparent")
        self.btn_reports.configure(fg_color=("gray75", "gray25") if name == "reports" else "transparent")
        self.btn_config.configure(fg_color=("gray75", "gray25") if name == "config" else "transparent")

        frames = {
            "dashboard": self.dashboard_frame,
            "users": self.users_frame,
            "shifts": self.shifts_frame,
            "reports": self.reports_frame,
            "config": self.config_frame
        }
        
        for k, v in frames.items():
            if name == k:
                v.grid(row=0, column=1, sticky="nsew")
            else:
                v.grid_forget()

    def show_dashboard_frame(self): self.select_frame_by_name("dashboard")
    def show_users_frame(self): self.select_frame_by_name("users")
    def show_shifts_frame(self): self.select_frame_by_name("shifts")
    def show_reports_frame(self): self.select_frame_by_name("reports")
    def show_config_frame(self): self.select_frame_by_name("config")

    # --- DASH ---
    def connect_and_refresh(self):
        self.lbl_status.configure(text="Sincronizando... por favor espera.", text_color="yellow")
        self.update()
        
        def task():
            success, msg = self.zk.connect()
            if success:
                info = self.zk.get_info()
                self.zk.disconnect()
                
                if info:
                    self.lbl_status.configure(text="ESTADO: Online - Vinculado exitosamente", text_color="#2ecc71")
                    infotxt = f"Capacidad Usuarios: {info['users']} vigentes\nBóveda de Asistencias: {info['attendance']} checadas\nHora Dispositivo: {info['time']}"
                    self.lbl_info.configure(text=infotxt)
            else:
                self.lbl_status.configure(text=f"ERROR: Fallo de conexión de red. ({msg})", text_color="red")
        
        threading.Thread(target=task).start()

    # --- SHIFTS ---
    def load_shifts(self):
        for item in self.tree_shifts.get_children():
            self.tree_shifts.delete(item)
        turnos = self.turnos_manager.obtener_turnos()
        for k, v in turnos.items():
            self.tree_shifts.insert("", "end", values=(k, v['nombre'], v['entrada'], v['salida']))

    def add_shift_dialog(self):
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Añadir Horario / Turno")
        dialog.geometry("400x350")
        dialog.transient(self)
        
        font_lbl = customtkinter.CTkFont(size=14)
        
        lbl_n = customtkinter.CTkLabel(dialog, text="Nombre del Turno (Ej. Operativo):", font=font_lbl)
        lbl_n.pack(pady=(20, 5))
        e_n = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_n.pack()
        
        lbl_in = customtkinter.CTkLabel(dialog, text="Hora Entrada (HH:MM):", font=font_lbl)
        lbl_in.pack(pady=(15, 5))
        e_in = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_in.insert(0, "08:00")
        e_in.pack()
        
        lbl_out = customtkinter.CTkLabel(dialog, text="Hora Salida (HH:MM):", font=font_lbl)
        lbl_out.pack(pady=(15, 5))
        e_out = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_out.insert(0, "17:00")
        e_out.pack()
        
        def save():
            n = e_n.get().strip()
            tin = e_in.get().strip()
            tout = e_out.get().strip()
            if not n or not tin or not tout:
                messagebox.showerror("Error", "Campos vacíos")
                return
            # Validar hora
            try:
                datetime.strptime(tin, "%H:%M")
                datetime.strptime(tout, "%H:%M")
            except:
                messagebox.showerror("Error formato", "Usa reloj de 24 horas Ej: 14:30")
                return
                
            self.turnos_manager.agregar_turno(n, tin, tout)
            self.load_shifts()
            dialog.destroy()
            
        btn_save = customtkinter.CTkButton(dialog, text="Guardar Turno", height=40, font=customtkinter.CTkFont(size=14, weight="bold"), command=save)
        btn_save.pack(pady=25)

    def edit_shift_dialog(self):
        selected = self.tree_shifts.focus()
        if not selected:
            messagebox.showwarning("Atención", "Toca el turno que deseas modificar.")
            return
            
        t_data = self.tree_shifts.item(selected, 'values')
        t_id, t_nom, t_ent, t_sal = t_data[0], t_data[1], t_data[2], t_data[3]
        
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Editando Turno {t_id}")
        dialog.geometry("400x350")
        dialog.transient(self)
        
        font_lbl = customtkinter.CTkFont(size=14)
        
        lbl_n = customtkinter.CTkLabel(dialog, text="Nombre del Turno:", font=font_lbl)
        lbl_n.pack(pady=(20, 5))
        e_n = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_n.insert(0, t_nom)
        e_n.pack()
        
        lbl_in = customtkinter.CTkLabel(dialog, text="Nueva Hora Entrada (HH:MM):", font=font_lbl)
        lbl_in.pack(pady=(15, 5))
        e_in = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_in.insert(0, t_ent)
        e_in.pack()
        
        lbl_out = customtkinter.CTkLabel(dialog, text="Nueva Hora Salida (HH:MM):", font=font_lbl)
        lbl_out.pack(pady=(15, 5))
        e_out = customtkinter.CTkEntry(dialog, width=250, height=35)
        e_out.insert(0, t_sal)
        e_out.pack()
        
        def save():
            n = e_n.get().strip()
            tin = e_in.get().strip()
            tout = e_out.get().strip()
            if not n or not tin or not tout:
                messagebox.showerror("Error", "No puedes dejar configuraciones vacías.")
                return
            try:
                datetime.strptime(tin, "%H:%M")
                datetime.strptime(tout, "%H:%M")
            except:
                messagebox.showerror("Error formato", "Usa reloj de 24 horas Ej: 14:30")
                return
                
            self.turnos_manager.editar_turno(t_id, n, tin, tout)
            self.load_shifts()
            self.load_users_from_device()
            dialog.destroy()
            
        btn_save = customtkinter.CTkButton(dialog, text="Sobreescribir Turno", height=40, font=customtkinter.CTkFont(size=14, weight="bold"), command=save, fg_color="#f39c12", hover_color="#e67e22")
        btn_save.pack(pady=25)

    def delete_shift_action(self):
        selected = self.tree_shifts.focus()
        if not selected:
            messagebox.showwarning("Atención", "Toca un turno primero.")
            return
        t_data = self.tree_shifts.item(selected, 'values')
        if messagebox.askyesno("Confirmar", f"¿Eliminar el turno {t_data[1]}? Los empleados amarrados quedarán sin turno."):
            self.turnos_manager.eliminar_turno(t_data[0])
            self.load_shifts()
            self.load_users_from_device() # Refresh if needed

    # --- USERS ---
    def load_users_from_device(self):
        self.btn_load_users.configure(state="disabled", text="Sincronizando...")
        for item in self.tree_users.get_children():
            self.tree_users.delete(item)
            
        def task():
            success, _ = self.zk.connect()
            if success:
                users = self.zk.get_users_list()
                self.zk.disconnect()
                self.after(0, self._populate_tree, users)
            else:
                self.after(0, lambda: messagebox.showerror("Error", "El reloj no responde por red."))
            self.after(0, lambda: self.btn_load_users.configure(state="normal", text="Sincronizar Reloj"))
        threading.Thread(target=task).start()

    def _populate_tree(self, users):
        turnos = self.turnos_manager.obtener_turnos()
        for u in users:
            priv = "Admin" if str(u['privilege']) == '14' else "Normal"
            tid = self.turnos_manager.obtener_asignacion(u['uid'])
            t_nom = turnos.get(str(tid), {}).get("nombre", "Sin Turno")
            self.tree_users.insert("", "end", values=(u['uid'], u['name'], priv, t_nom))

    def add_user_dialog(self):
        max_id = 0
        for item in self.tree_users.get_children():
            try:
                uid = int(self.tree_users.item(item, 'values')[0])
                if uid > max_id:
                    max_id = uid
            except ValueError:
                pass
        next_id = str(max_id + 1)
        
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Registro de Empleado")
        dialog.geometry("400x450")
        dialog.transient(self) 

        font_lbl = customtkinter.CTkFont(size=14)
        
        lbl_id = customtkinter.CTkLabel(dialog, text="ID de Empleado (Inmodificable, Secuencial):", font=font_lbl)
        lbl_id.pack(pady=(20, 5))
        entry_id = customtkinter.CTkEntry(dialog, width=250, height=35)
        entry_id.insert(0, next_id)
        entry_id.pack()
        
        lbl_name = customtkinter.CTkLabel(dialog, text="Nombre del Empleado Completo:", font=font_lbl)
        lbl_name.pack(pady=(15, 5))
        entry_name = customtkinter.CTkEntry(dialog, width=250, height=35)
        entry_name.pack()
        
        lbl_ti = customtkinter.CTkLabel(dialog, text="Asignar a Turno Laboral:", font=font_lbl, text_color="#3498db")
        lbl_ti.pack(pady=(20, 5))
        
        turnos = self.turnos_manager.obtener_turnos()
        opciones_turnos = [f"{k} - {v['nombre']}" for k, v in turnos.items()]
        opciones_turnos.insert(0, "Sin Turno Asignado")
        
        combo_turnos = customtkinter.CTkComboBox(dialog, values=opciones_turnos, width=250, height=35)
        combo_turnos.pack()
        
        def save():
            uid = entry_id.get().strip()
            name = entry_name.get().strip()
            sel_turno = combo_turnos.get()
            
            if not uid or not name:
                messagebox.showerror("Rechazado", "Nombre e ID son obligatorios.")
                return
                
            # Guardar en reloj
            success, _ = self.zk.connect()
            if success:
                ok, msg = self.zk.set_user(uid, name)
                self.zk.disconnect()
                if ok:
                    # Guardar turno localmente
                    if sel_turno != "Sin Turno Asignado":
                        tid = sel_turno.split(" - ")[0]
                        self.turnos_manager.asignar_turno_a_usuario(uid, tid)
                    else:
                        self.turnos_manager.eliminar_asignacion(uid)
                        
                    messagebox.showinfo("Operación limpia", f"Trabajador guardado. Ahora pidele que ponga su dedo en el reloj en el usuario ID {uid}.")
                    dialog.destroy()
                    self.load_users_from_device()
                else:
                    messagebox.showerror("Error Dispositivo", msg)
            else:
                messagebox.showerror("Caída de Red", "Reloj inaccesible.")

        btn_save = customtkinter.CTkButton(dialog, text="Inyectar al Servidor/Reloj", height=45, font=customtkinter.CTkFont(size=14, weight="bold"), command=save)
        btn_save.pack(pady=30)

    def edit_user_dialog(self):
        selected = self.tree_users.focus()
        if not selected:
            messagebox.showwarning("Atención", "Toca a un trabajador en la lista para editar su nombre o tuno.")
            return
            
        user_data = self.tree_users.item(selected, 'values')
        uid, old_name = user_data[0], user_data[1]
        
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Re-Asignar Datos o Turno a ID {uid}")
        dialog.geometry("400x350")
        dialog.transient(self) 

        font_lbl = customtkinter.CTkFont(size=14)
        
        lbl_name = customtkinter.CTkLabel(dialog, text="Modificar Nombre del Empleado:", font=font_lbl)
        lbl_name.pack(pady=(20, 5))
        entry_name = customtkinter.CTkEntry(dialog, width=250, height=35)
        entry_name.insert(0, old_name)
        entry_name.pack()
        
        lbl_ti = customtkinter.CTkLabel(dialog, text="Cambiar / Asignar nuevo Turno Laboral:", font=font_lbl, text_color="#3498db")
        lbl_ti.pack(pady=(20, 5))
        
        turnos = self.turnos_manager.obtener_turnos()
        opciones_turnos = [f"{k} - {v['nombre']}" for k, v in turnos.items()]
        opciones_turnos.insert(0, "Sin Turno Asignado")
        
        combo_turnos = customtkinter.CTkComboBox(dialog, values=opciones_turnos, width=250, height=35)
        
        # Select current mapping if exists
        curr_tid = self.turnos_manager.obtener_asignacion(uid)
        if curr_tid and str(curr_tid) in turnos:
            combo_turnos.set(f"{curr_tid} - {turnos[str(curr_tid)]['nombre']}")
        else:
            combo_turnos.set("Sin Turno Asignado")
            
        combo_turnos.pack()
        
        def update_usr():
            name = entry_name.get().strip()
            sel_turno = combo_turnos.get()
            
            if not name:
                messagebox.showerror("Rechazado", "Defina el Nombre.")
                return
                
            success, _ = self.zk.connect()
            if success:
                ok, msg = self.zk.set_user(uid, name) # Sobre-escribe
                self.zk.disconnect()
                if ok:
                    # Update Shift DB
                    if sel_turno != "Sin Turno Asignado":
                        tid = sel_turno.split(" - ")[0]
                        self.turnos_manager.asignar_turno_a_usuario(uid, tid)
                    else:
                        self.turnos_manager.eliminar_asignacion(uid)
                        
                    messagebox.showinfo("Limpieza General", "Reajustes de empleado y turno actualizados.")
                    dialog.destroy()
                    self.load_users_from_device()
                else:
                    messagebox.showerror("Fallo Memoria Reloj", msg)
            else:
                messagebox.showerror("Caída de Red", "Dispositivo biométrico inalcanzable.")

        btn_save = customtkinter.CTkButton(dialog, text="Sobreescribir y Cambiar", height=45, font=customtkinter.CTkFont(size=14, weight="bold"), fg_color="#f39c12", hover_color="#e67e22", command=update_usr)
        btn_save.pack(pady=30)

    def delete_user_action(self):
        selected = self.tree_users.focus()
        if not selected:
            messagebox.showwarning("Foco", "Selecciona una fila primero.")
            return
            
        user_data = self.tree_users.item(selected, 'values')
        uid, name = user_data[0], user_data[1]
        
        if messagebox.askyesno("Alerta de Seguridad", f"¿Estudiaste bien purgar a {name} (ID: {uid})? Sus huellas morirán en el reloj físico."):
            success, _ = self.zk.connect()
            if success:
                ok, msg = self.zk.delete_user(uid)
                self.zk.disconnect()
                if ok:
                    self.turnos_manager.eliminar_asignacion(uid) # Clean local mapping
                    messagebox.showinfo("Limpieza Exitosa", "Registro erradicado.")
                    self.tree_users.delete(selected)
                else:
                    messagebox.showerror("Error de Firmware", msg)
            else:
                messagebox.showerror("Caída de Red", "El hardware está offline.")

    # --- REPORTS ---
    def open_calendar_modal(self, who):
        init_val = self.d_desde if who == 'desde' else self.d_hasta
        def set_date_cb(selected_date):
            if who == 'desde':
                self.d_desde = selected_date
                self.btn_cal_desde.configure(text=selected_date.strftime("%Y-%m-%d"))
            else:
                self.d_hasta = selected_date
                self.btn_cal_hasta.configure(text=selected_date.strftime("%Y-%m-%d"))
                
        DatePickerModal(self, initial_date=init_val, title="Configuración de Rango", callback=set_date_cb)

    def generate_report(self):
        if self.d_desde > self.d_hasta:
            messagebox.showerror("Error lógico", "El periodo inicial sobrepasa al final.")
            return

        self.btn_gen_rep.configure(state="disabled")
        self.lbl_rep_status.configure(text=f"Analizando big data del {self.d_desde} al {self.d_hasta}... aguarda.")
        self.update()

        def task():
            active_uids = [str(self.tree_users.item(i, 'values')[0]) for i in self.tree_users.get_children()]
            if not active_uids:
                self.lbl_rep_status.configure(text="Advertencia: No veo usuarios cargados. Carga la vista de Empleados primero.", text_color="orange")
                self.btn_gen_rep.configure(state="normal")
                return
                
            success, msg = self.zk.connect()
            if not success:
                self.lbl_rep_status.configure(text="Fallo de capa de red. Reloj bloqueado o apagado.", text_color="red")
                self.btn_gen_rep.configure(state="normal")
                return

            try:
                dfrom = datetime.combine(self.d_desde, datetime.min.time())
                dto = datetime.combine(self.d_hasta, datetime.max.time())
                
                registros = self.zk.get_attendance_records(date_from=dfrom, date_to=dto)
                self.zk.disconnect()
                
                if not registros:
                    self.lbl_rep_status.configure(text="No hay movimientos registrados por los dedos en este periodo.", text_color="orange")
                    self.btn_gen_rep.configure(state="normal")
                    return
                
                self.lbl_rep_status.configure(text="Compilando Motor Elite de Cálculo (Dinamismo de Turnos)...")
                ts = datetime.now().strftime('%H%M%S')
                filename = f"Reporte_Empresarial_del_{self.d_desde.strftime('%y%m%d')}_al_{self.d_hasta.strftime('%y%m%d')}_{ts}.xlsx"
                
                ok, res_msg = export_to_excel(registros, filename, active_uids, self.turnos_manager)
                
                if ok:
                    import os
                    self.lbl_rep_status.configure(text=f"EXCEL CREADO EXITOSAMENTE EN: Reportes/{filename}", text_color="#2ecc71")
                    # AUTO OPEN
                    try:
                        os.startfile(res_msg)
                    except AttributeError:
                        import subprocess
                        subprocess.call(['open', res_msg])
                else:
                    self.lbl_rep_status.configure(text=f"Excepción en Pandas: {res_msg}", text_color="red")
            
            except Exception as e:
                self.lbl_rep_status.configure(text=f"Pánico nativo: {str(e)}", text_color="red")
            finally:
                self.btn_gen_rep.configure(state="normal")
                self.zk.disconnect()

        threading.Thread(target=task).start()

    def save_configuration(self):
        new_ip = self.entry_ip.get().strip()
        if new_ip:
            save_config(new_ip)
            self.zk = ZKService(new_ip, self.config_data['port'])
            messagebox.showinfo("Red Ajustada", f"Se conectará siempre a: {new_ip}")
        else:
            messagebox.showerror("Inválido", "Asigna una ruta IPv4.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
