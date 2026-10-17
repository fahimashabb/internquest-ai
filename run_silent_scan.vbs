Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\CV hunter Webapp"
WshShell.Run """E:\CV hunter Webapp\.venv\Scripts\python.exe"" ""E:\CV hunter Webapp\daily_runner.py""", 0, False
