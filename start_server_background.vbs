Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\project"
WshShell.Run """C:\Users\HP\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" ""C:\project\live_detection_server.py"" --no-browser", 0, False
