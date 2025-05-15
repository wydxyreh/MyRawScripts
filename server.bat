@echo off
REM 切换到当前批处理文件所在目录
cd /d "%~dp0%"

REM 运行 Python 脚本
python Network\sample_server.py

REM 暂停以便查看输出结果（可选）
pause