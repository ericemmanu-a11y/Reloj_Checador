@echo off
echo ========================================================
echo        Empaquetando ZKManager en EXE...
echo ========================================================
pyinstaller --noconfirm --onedir --windowed --collect-all customtkinter main.py --name ZKManager
pause
