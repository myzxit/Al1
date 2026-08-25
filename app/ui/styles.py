"""앱 전체 스타일시트."""

STYLESHEET = """
/* 배경은 창과 다이얼로그에만 칠한다. 카드 안의 컨테이너 위젯은 카드 색을 그대로 쓴다. */
QWidget {
    color: #e6e8ee;
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    font-size: 14px;
}

QMainWindow, QDialog, QStackedWidget {
    background-color: #0f1117;
}

QStackedWidget > QWidget {
    background-color: #0f1117;
}

QLabel, QCheckBox {
    background: transparent;
}

QLabel#Value {
    color: #e6e8ee;
}

QFrame#Card {
    background-color: #171a23;
    border: 1px solid #262b38;
    border-radius: 14px;
}

QLabel#Title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#Subtitle {
    font-size: 13px;
    color: #8d94a6;
}

QLabel#FieldLabel {
    font-size: 12px;
    color: #a6adbf;
}

QLabel#Error {
    color: #ff6b6b;
    font-size: 12px;
}

QLabel#Success {
    color: #4ade80;
    font-size: 12px;
}

QLineEdit {
    background-color: #10131b;
    border: 1px solid #2c3243;
    border-radius: 8px;
    padding: 9px 11px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QLineEdit[invalid="true"] {
    border: 1px solid #ff6b6b;
}

QPushButton#Primary {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
}

QPushButton#Primary:hover  { background-color: #2f74e0; }
QPushButton#Primary:pressed{ background-color: #2764c4; }
QPushButton#Primary:disabled {
    background-color: #2a3243;
    color: #6c7488;
}

QPushButton#Secondary {
    background-color: transparent;
    color: #e6e8ee;
    border: 1px solid #2c3243;
    border-radius: 8px;
    padding: 9px 16px;
}

QPushButton#Secondary:hover { border-color: #3b82f6; color: #ffffff; }

QPushButton#Danger {
    background-color: transparent;
    color: #ff6b6b;
    border: 1px solid #4a2b31;
    border-radius: 8px;
    padding: 9px 16px;
}

QPushButton#Danger:hover { border-color: #ff6b6b; }

QPushButton#Link {
    background: transparent;
    border: none;
    color: #7aa7ff;
    padding: 2px;
    text-align: left;
}

QPushButton#Link:hover { color: #a9c6ff; text-decoration: underline; }

QCheckBox { color: #a6adbf; spacing: 8px; }

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2c3243;
    border-radius: 4px;
    background-color: #10131b;
}

QCheckBox::indicator:hover { border-color: #3b82f6; }

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
    image: none;
}

QProgressBar {
    background-color: #10131b;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk { border-radius: 3px; }
"""

STRENGTH_COLORS = {
    0: "#3a4152",
    1: "#ff6b6b",
    2: "#f7b955",
    3: "#4ade80",
    4: "#22c55e",
}
