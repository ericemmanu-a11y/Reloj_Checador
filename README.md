# 🏢 ZKManager Elite - Reloj Checador (V6)

Sistema integral todo-en-uno de Gestión, Control de Asistencia y Reporteo automatizado (Excel) conectado vía Red a un Reloj Biométrico ZKTeco (Modelo K40 / K14 o compatibles con firmware UDP/TCP ZK). 

---

## 📸 Características Modulares de la Versión 6:
* **Escalabilidad Offline:** Soporta conexión y extracción de marcajes (Attlogs) sin interrumpir el funcionamiento continuo del Reloj.
* **Turnos Corporativos y Tolerancias:** Motor de Base de Datos local JSON para crear "Horarios de Turnos" (`08:00 a 17:00`) evitando el hardcode general.
* **Auto-Identificación y CRUD:** Asignación automática de IDs, y posibilidad de Editar Datos y nombres con guardado directo en la Terminal ZK.
* **Generación Robusta en Excel (Elite):** Autoapertura de hojas nativas de Pandas + Openpyxl subdivididas en *Turnos, Asistencias, Estadísticas y Excepciones* en Formato Ejecutivo.

---

## 🛠 Instalación Rápida y Requisitos (Modo USB)

Para utilizar esta aplicación **no es necesario saber Python ni programar**. Basta con descargar este proyecto desde GitHub ("Download ZIP") e ir al archivo ejecutable.

### Pasos Rápidos en Windows:
1. En GitHub, dale a **`Code` -> `Download ZIP`** y extraelo donde gustes.
2. Adentro de los archivos, dirígete a la carpeta exclusiva del sistema: `ZKManager/Ejecutable_Windows/`.
3. Dale doble clic al archivo de la aplicación principal **`ZKManager.exe`**.
4. ¡El Gestor Elite comenzará!

*(Nota: En el primer arranque, la aplicación buscará conectarse al Reloj por default, el cual puedes renombrar desde la sección Ajustes de Red).*

---

## 🔌 Guía de Configuración Física: Red, Router y Terminal ZKTeco

Para que ZKManager haga la "magia" en los Excels interactivos, **EL RELOJ DEBE ESTAR CONECTADO A LA MISMA RED DEL PC**.

### 1. Preparación del Router y Repetidor 🌐
1. Asegúrate de conectar el Cable Ethernet Remoto (RJ45) a la roseta / modem / repetidor del corporativo.
2. Identifica el rango de Segmentos de IP en donde trabaja la red del negocio (usualmente empieza con `192.168.1.X` o `192.168.0.X`).

### 2. Configuración en el Aparato (ZKTeco K40) ⏰
Dirígete a la Pantalla de tu Reloj:
1. Toca `M/OK` (para entrar al Menú) e ingresa huella de super-administrador.
2. Ve al menú de **`Opciones de Red`** -> **`Ethernet`** o **`IP`**.
3. **Apaga** la casilla del `DHCP` (Para que el módem no le ande cambiando la IP por las mañanas).
4. Dale una **Dirección IP Fija** en el mismo rango de tu módem pero libre, por ejemplo: `192.168.X.201` (Asegúrate de configurar igual la Puerta de Enlace / Gateway).
5. Ve a **`Ajustes de Sistema`** -> **`Asistencia`**.
6. Activa imperativamente la opción **`Estado Requerido` (Punch State Required)** para que al poner el dedo, la terminal exija presionar primero los físicos F1 (Llegada), F2, F3 y F4 (Salida).

### 3. Sincronización de ZKManager 💻
1. Enciende la aplicación `ZKManager.exe`.
2. Dirígete a la quinta pestaña (la rueda dentada de Configuraciones) **`Ajustes de Red`**.
3. Ingresa la Dirección IP Fija que acuestas de introducirle a tu Reloj Biométrico.
4. Presiona Guardar y en la pestaña `Dashboard` haz un "Ping" o presiona **Conectar**.

---

## 👨‍💼 Operación en el Trabajo Diario

El ciclo de una incorporación será:
1. Registra su **Turno Predeterminado** en la ventana de GUI de Turnos (`[09:00 a 14:00]`).
2. Entra a "Empleados y Contratación". Haz Sincronizar.
3. Agrégale un Empleado con ID Automática y asocia su **Turno Creado**.
4. Párate frente al Reloj Físico; y registra su dedo / rostro en el Dispositivo (M/OK -> Usuarios), escribiendo la misma `ID` que el programa te arrojó, pero no re-edites nombres desde el reloj.
5. Cada fin de semana entra a **Reportes**, selecciona un rango de Fechas Largos... !Y disfruta del Excel!
