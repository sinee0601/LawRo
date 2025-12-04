PowerShell (관리자 권한으로 실행)
# Frontend 포트 5173 열기
New-NetFirewallRule -DisplayName "LawRo Frontend (5173)" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow

# Backend 포트 8000 열기
New-NetFirewallRule -DisplayName "LawRo Backend (8000)" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
실행 방법
PowerShell 관리자 권한으로 열기:
Windows 검색 → "PowerShell" 입력
우클릭 → "관리자 권한으로 실행"
위 명령어 복사 & 붙여넣기
확인:
# 방화벽 규칙 확인
Get-NetFirewallRule -DisplayName "LawRo*"
나중에 규칙 삭제하려면
Remove-NetFirewallRule -DisplayName "LawRo Frontend (5173)"
Remove-NetFirewallRule -DisplayName "LawRo Backend (8000)"
GUI로 확인
제어판 → Windows Defender 방화벽 → 고급 설정 → 인바운드 규칙
"LawRo Frontend", "LawRo Backend" 규칙이 생성되어 있어야 함