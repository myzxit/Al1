# Al1

PySide6로 만든 회원가입 / 로그인 데스크톱 앱입니다.
인증키·라이선스 키·서버 없이, 계정 정보를 사용자 PC의 로컬 SQLite 파일에만 저장합니다.

## 화면

| 화면 | 내용 |
| --- | --- |
| 로그인 | 아이디 또는 이메일 + 비밀번호, 로그인 상태 유지 |
| 회원가입 | 아이디 / 이메일 / 표시 이름(선택) / 비밀번호 + 확인, 비밀번호 강도 표시, 약관 동의 |
| 홈 | 계정 정보, 비밀번호 변경, 표시 이름 변경, 로그아웃, 회원탈퇴 |

## 실행

```bash
pip install -r requirements.txt
python main.py
```

Python 3.10 이상이 필요합니다 (개발·검증은 3.11에서 했습니다).

리눅스에서 실행할 때 Qt 런타임 라이브러리가 없다면:

```bash
sudo apt-get install -y libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1
```

## 테스트

```bash
pip install -r requirements-dev.txt
python -m pytest
```

계정 저장소·비밀번호 해싱·자동 로그인 토큰에 대한 61개 테스트가 들어 있습니다.
GUI 없이(headless) 돌아갑니다.

## 데이터 저장 위치

계정 DB(`accounts.db`)와 자동 로그인 토큰(`session.json`)이 저장되는 곳:

| OS | 경로 |
| --- | --- |
| Windows | `%APPDATA%\Al1\` |
| macOS | `~/Library/Application Support/Al1/` |
| Linux | `~/.local/share/Al1/` |

환경변수 `AL1_DATA_DIR`로 위치를 바꿀 수 있습니다. 테스트에서도 이 변수를 씁니다.

## 계정 처리 방식

- 비밀번호는 **PBKDF2-HMAC-SHA256(260,000회, 계정마다 다른 16바이트 솔트)** 로 해싱해 저장합니다. 평문은 저장하지 않습니다.
- 비밀번호 비교는 `hmac.compare_digest`로 합니다.
- 로그인 실패 문구는 "아이디 또는 비밀번호가 올바르지 않습니다."로 통일해, 계정 존재 여부가 드러나지 않게 했습니다.
- 아이디와 이메일은 대소문자를 구분하지 않고 중복을 막습니다(`COLLATE NOCASE`).
- "로그인 상태 유지"를 켜면 임의 토큰을 발급해 `session.json`(권한 0600)에 저장합니다. 기본 유효기간 14일이고, 로그아웃·비밀번호 변경·회원탈퇴 시 즉시 폐기됩니다.
- 회원탈퇴는 비밀번호 재확인을 거치며, 계정과 토큰을 함께 삭제합니다.

암호화 관련 코드는 모두 파이썬 표준 라이브러리(`hashlib`, `hmac`, `secrets`)만 사용합니다. 외부 의존성은 PySide6 하나뿐입니다.

## 구조

```
main.py                  진입점
app/
  config.py              앱 이름, 데이터 디렉터리 경로
  security.py            비밀번호 해싱·검증, 입력값 검사, 강도 계산
  database.py            SQLite 계정 저장소 (가입/로그인/변경/탈퇴/토큰)
  session.py             자동 로그인 토큰 파일 읽기·쓰기
  ui/
    main_window.py       QStackedWidget 화면 전환
    login_page.py        로그인 화면
    signup_page.py       회원가입 화면
    home_page.py         로그인 후 화면
    widgets.py           공용 위젯 helper
    styles.py            스타일시트
tests/                   pytest 테스트
```

UI 계층은 `app/database.py`의 `AccountError`만 잡아서 그대로 화면에 띄웁니다.
검증 규칙을 바꾸려면 `app/security.py` 한 곳만 고치면 됩니다.

## 배포용 실행 파일 만들기 (선택)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name Al1 main.py
```
