# ch01 一键自测：按顺序跑三个实验并检查关键输出
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
Set-Location $PSScriptRoot

Write-Host "== 1. hello.py" -ForegroundColor Cyan
python hello.py

Write-Host "`n== 2. score.py（及格）" -ForegroundColor Cyan
python score.py --name 李明 --scores 85 92 78

Write-Host "`n== 3. score.py（不及格）" -ForegroundColor Cyan
python score.py --name 张三 --scores 40 55 58

Write-Host "`n== 4. score.py（非法输入）" -ForegroundColor Cyan
python score.py --name 李四 --scores 40 55 abc
Write-Host "   （退出码应为 2，实际：$LASTEXITCODE）"

Write-Host "`n== 5. ai_generate.py" -ForegroundColor Cyan
python ai_generate.py
python generated\hello_ai.py

Write-Host "`n== 6. errors/b_indent.py" -ForegroundColor Cyan
python errors\b_indent.py
