@echo off
echo ================================================
echo    DANG BUILD BAN TAY MA THUAT cho Windows
echo ================================================
echo.

REM Kiểm tra Python có cài không
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long tai Python tai: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Cai dat thu vien...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/4] Xoa cache cu...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

echo.
echo [3/4] Bat dau build...
pyinstaller --name=BanTayMaThuat ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data=font.ttf;. ^
    --add-data=slide.jpg;. ^
    --add-data=core;core ^
    --hidden-import=mediapipe ^
    --hidden-import=cv2 ^
    --hidden-import=pygame ^
    --hidden-import=pymunk ^
    --hidden-import=numpy ^
    --hidden-import=mediapipe.python ^
    --hidden-import=mediapipe.python.solutions ^
    --hidden-import=mediapipe.python.solutions.hands ^
    --hidden-import=google.protobuf ^
    --collect-data=mediapipe ^
    --collect-all=mediapipe ^
    --clean ^
    --noconfirm ^
    main.py

echo.
echo [4/4] Sao chep resources vao dist...
xcopy /Y font.ttf dist\
xcopy /Y slide.jpg dist\

echo.
echo ================================================
echo    BUILD HOAN THANH!
echo ================================================
echo File game: dist\BanTayMaThuat.exe
echo Kich thuoc: Du kien 150-300 MB (bao gom MediaPipe models)
echo.
pause