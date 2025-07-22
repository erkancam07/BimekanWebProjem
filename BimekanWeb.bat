@echo off
cd C:\Users\Erkan\Desktop\proje-adi

REM Sanal ortamı aktif et
call myenv\Scripts\activate

if not exist "myenv\Scripts\activate.bat" (
    echo Sanal ortam bulunamadı. Lütfen 'myenv' klasörünün varlığını kontrol edin.
    pause
    exit
)

REM Tarayıcıyı aç (isteğe bağlı)
start http://127.0.0.1:8000/

REM Django sunucusunu başlat
python manage.py runserver
pause