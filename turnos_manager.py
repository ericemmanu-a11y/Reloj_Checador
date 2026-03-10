import json
import os
from datetime import time

class TurnosManager:
    """Clase para gestionar la persistencia local de Turnos y asignaciones de Usuarios."""
    def __init__(self):
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'turnos.json')
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            # Formato Default
            data = {
                "turnos": {
                    "1": {"nombre": "Administrativo", "entrada": "09:00", "salida": "18:00"},
                    "2": {"nombre": "Operativo", "entrada": "08:00", "salida": "17:00"}
                },
                "usuarios_turnos": {} # Mapeo de "ID_Usuario" -> "ID_Turno"
            }
            self._save(data)
            return data
            
        with open(self.filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"turnos": {}, "usuarios_turnos": {}}

    def _save(self, data=None):
        if data is None:
            data = self.data
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    # --- Gestión de Turnos ---
    def obtener_turnos(self):
        return self.data.get('turnos', {})

    def agregar_turno(self, nombre, entrada, salida):
        turnos = self.data.setdefault('turnos', {})
        # Generar ID
        nuevo_id = str(max([int(k) for k in turnos.keys()] + [0]) + 1)
        turnos[nuevo_id] = {
            "nombre": nombre,
            "entrada": entrada,
            "salida": salida
        }
        self._save()
        return True, "Turno creado."

    def editar_turno(self, id_turno, nombre, entrada, salida):
        id_turno = str(id_turno)
        if id_turno in self.data.get('turnos', {}):
            self.data['turnos'][id_turno] = {
                "nombre": nombre,
                "entrada": entrada,
                "salida": salida
            }
            self._save()
            return True, "Turno actualizado."
        return False, "El turno no existe."

    def eliminar_turno(self, id_turno):
        id_turno = str(id_turno)
        if id_turno in self.data.get('turnos', {}):
            del self.data['turnos'][id_turno]
            
            # Limpiar re-asignaciones que hayan quedado huérfanas
            uas = self.data.get('usuarios_turnos', {})
            usuarios_a_limpiar = [uid for uid, tid in uas.items() if tid == id_turno]
            for uid in usuarios_a_limpiar:
                del uas[uid]
                
            self._save()
            return True, "Turno eliminado."
        return False, "El turno no existe."

    # --- Asignación de Usuarios ---
    def asignar_turno_a_usuario(self, uid_usuario, id_turno):
        uid_usuario = str(uid_usuario)
        id_turno = str(id_turno)
        self.data.setdefault('usuarios_turnos', {})[uid_usuario] = id_turno
        self._save()

    def obtener_asignacion(self, uid_usuario):
        return self.data.get('usuarios_turnos', {}).get(str(uid_usuario))
        
    def eliminar_asignacion(self, uid_usuario):
        uid_usuario = str(uid_usuario)
        if uid_usuario in self.data.get('usuarios_turnos', {}):
            del self.data['usuarios_turnos'][uid_usuario]
            self._save()

    def get_turno_por_usuario(self, uid_usuario):
        # Devuelve obj time(hh,mm) para entrada y salida
        id_turno = self.obtener_asignacion(uid_usuario)
        if not id_turno:
             return None, None
        
        turno_info = self.data.get('turnos', {}).get(id_turno)
        if not turno_info:
             return None, None
             
        try:
            h_in, m_in = map(int, turno_info['entrada'].split(':'))
            h_out, m_out = map(int, turno_info['salida'].split(':'))
            return time(h_in, m_in), time(h_out, m_out)
        except:
             return None, None
