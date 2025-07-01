@echo off
echo 🔄 AR Sandbox RC - Camera Reset Utility
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️ WARNING: Not running as Administrator
    echo    Some operations may fail
    echo    Right-click and "Run as Administrator" for full reset
    echo.
)

echo 🛑 Step 1: Killing camera processes...
taskkill /f /im "Camera.exe" >nul 2>&1
taskkill /f /im "WindowsCamera.exe" >nul 2>&1
taskkill /f /im "opencv_videoio_msmf.exe" >nul 2>&1
echo    ✅ Camera processes terminated

echo.
echo 🔧 Step 2: Resetting Windows Camera Service...
net stop FrameServer >nul 2>&1
timeout /t 2 >nul
net start FrameServer >nul 2>&1
echo    ✅ Windows Camera Service reset

echo.
echo 🎯 Step 3: Resetting Kinect services...
net stop KinectManagement >nul 2>&1
net stop KinectService >nul 2>&1
timeout /t 2 >nul
net start KinectService >nul 2>&1
net start KinectManagement >nul 2>&1
echo    ✅ Kinect services reset

echo.
echo 📱 Step 4: Disabling and re-enabling cameras...
REM Use PowerShell to disable/enable camera devices
powershell -Command "Get-PnpDevice -Class Camera | Where-Object {$_.Status -eq 'OK'} | Disable-PnpDevice -Confirm:$false" >nul 2>&1
timeout /t 3 >nul
powershell -Command "Get-PnpDevice -Class Camera | Where-Object {$_.Status -eq 'Error'} | Enable-PnpDevice -Confirm:$false" >nul 2>&1
echo    ✅ Camera devices reset

echo.
echo ⏳ Step 5: Waiting for hardware stabilization...
timeout /t 5 >nul

echo.
echo 🧪 Step 6: Running Python camera test...
python reset_cameras.py

echo.
echo 🎉 Camera reset complete!
echo.
echo 💡 Manual steps if cameras still don't work:
echo    1. Unplug Kinect USB cable, wait 10 seconds, plug back in
echo    2. Open Device Manager ^> Cameras ^> Disable/Enable each camera
echo    3. Restart computer if all else fails
echo.
echo 📋 Next steps:
echo    1. Refresh your browser
echo    2. Open http://localhost:8000/debug_demo.html
echo    3. Click "🔄 Reset All Cameras" button
echo    4. Test the 4-camera system
echo.

pause
