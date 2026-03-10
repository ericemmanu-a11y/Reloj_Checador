from zk import ZK
from datetime import datetime

class ZKService:
    def __init__(self, ip, port=4370):
        self.ip = ip
        self.port = port
        self.zk = ZK(self.ip, port=self.port, timeout=5)
        self.conn = None

    def connect(self):
        try:
            self.conn = self.zk.connect()
            return True, "Conectado"
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        if self.conn:
            try:
                self.conn.disconnect()
            except:
                pass
        self.conn = None

    def get_info(self):
        if not self.conn:
             return None
        return {
            "users": len(self.conn.get_users()),
            "attendance": len(self.conn.get_attendance()),
            "time": self.conn.get_time()
        }

    def get_users_list(self):
        if not self.conn:
             return []
        users = self.conn.get_users()
        res = []
        for u in users:
            uid = getattr(u, 'user_id', getattr(u, 'uid', str(u)))
            res.append({"uid": uid, "name": u.name, "privilege": u.privilege})
        return res

    def get_attendance_records(self, date_from=None, date_to=None):
        if not self.conn:
             return []
             
        users = self.get_users_list()
        user_dict = {str(u['uid']): u['name'] for u in users}
        
        attendances = self.conn.get_attendance()
        registros = []
        
        for att in attendances:
            uid_str = str(getattr(att, 'user_id', getattr(att, 'uid', 0)))
            nombre = user_dict.get(uid_str, f"Desconocido ({uid_str})")
            
            # Filtro fecha
            dt = att.timestamp
            if date_from and dt.date() < date_from.date():
                continue
            if date_to and dt.date() > date_to.date():
                continue
                
            registros.append({
                'ID': uid_str,
                'Nombre': nombre,
                'Fecha_Hora': dt
            })
            
        return registros

    def set_user(self, uid, name, privilege=0, password='', group_id='0', user_id=''):
        """Agrega o actualiza un usuario."""
        if not self.conn:
             return False, "No conectado"
        try:
            # En la librería pyzk, set_user suele recibir: uid, name, privilege, password, group_id, user_id
            self.conn.set_user(uid=int(uid), name=name, privilege=int(privilege), password=password, group_id=group_id, user_id=str(uid))
            return True, "Usuario guardado correctamente"
        except Exception as e:
            return False, str(e)

    def delete_user(self, uid):
        """Elimina un usuario por su UID."""
        if not self.conn:
             return False, "No conectado"
        try:
            self.conn.delete_user(uid=int(uid))
            return True, "Usuario eliminado correctamente"
        except Exception as e:
            return False, str(e)

