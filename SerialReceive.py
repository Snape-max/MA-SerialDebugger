import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox

class CheckBoxExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout()

        # 创建 QCheckBox 部件
        check_box = QCheckBox('Enable Feature')

        # 连接信号槽，当开关状态发生变化时调用 on_checkbox_changed 方法
        check_box.stateChanged.connect(self.on_checkbox_changed)

        layout.addWidget(check_box)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('Check Box Example')
        self.setGeometry(100, 100, 300, 200)

    def on_checkbox_changed(self, state):
        if state == 2:  # 2 表示选中状态
            print('Feature is enabled')
        else:
            print('Feature is disabled')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CheckBoxExample()
    window.show()
    sys.exit(app.exec_())
