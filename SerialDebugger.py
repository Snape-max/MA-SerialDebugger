import datetime
import sys
import struct
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QPushButton, QGridLayout, QComboBox,
    QLineEdit, QMessageBox, QTextEdit, QLabel, QCheckBox
)
import serial
import serial.tools.list_ports as port_find

# 帧头
frame_b_1 = b'\xfa'
frame_b_2 = b'\xac'

# 帧尾
frame_e_1 = b'\xcc'
frame_e_2 = b'\xff'


def get_serial_com():
    portlist = list(port_find.comports())
    return [port[0] for port in portlist]


class SerialThread(QThread):
    data_received = pyqtSignal(bytes)

    def __init__(self, port, baud_rate):
        super().__init__()
        self.new_data = None
        self.port = port
        self.baud_rate = baud_rate
        self.running = True

    def run(self):
        with serial.Serial(
                port=self.port, baudrate=self.baud_rate,
                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None
        ) as ser:
            while self.running:
                self.new_data = ser.read(10)
                self.data_received.emit(self.new_data)

    def stop(self):
        self.running = False


class SerialDebugger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_frame = None
        self.poltch = None
        self.bound_rate = None
        self.plot_widget = None
        self.ser = None
        self.serialbox = None
        self.data_buffer = b''
        self.init_ui()
        self.plot_data = [[], [], [], []]
        self.serial_thread = None

    def open_serial(self):
        port = self.serialbox.currentText()
        bound_str = self.bound_rate.text()
        try:
            bound = int(bound_str)
            self.serial_thread = SerialThread(port, bound)
            self.serial_thread.data_received.connect(self.process_received_data)
            self.serial_thread.start()
            QMessageBox.information(None, 'Success', '串口已打开')
        except ValueError:
            QMessageBox.critical(None, 'Error', '波特率为整数')

    def process_received_data(self, new_data):
        self.data_buffer += new_data
        self.process_data_buffer()

        current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        data_str = f'<b><font size="4" color="blue">[{current_time}]</font> <font size="4" color="green">\
            {" ".join(format(byte, "02x").upper() for byte in new_data)}</font><b><br>'

        if self.rx_show.isChecked():
            self.text_edit.insertHtml(data_str)
            self.scroll_to_bottom()

    def closeEvent(self, event):
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread.wait()

        super().closeEvent(event)

    def init_ui(self):
        central_widget = QWidget(self)
        grid = QGridLayout()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Serial Debugger")
        self.setWindowIcon(QIcon('main.png'))
        self.setGeometry(200, 100, 1200, 720)
        grid.setSpacing(10)

        self.serialbox = QComboBox()
        self.serialbox.addItems(get_serial_com())

        button = QPushButton("打开串口")
        button.clicked.connect(self.open_serial)

        self.bound_rate = QLineEdit()
        self.bound_rate.setPlaceholderText("波特率")

        for i in range(15):
            grid.setColumnStretch(i, 1)

        for i in range(10):
            grid.setRowStretch(i, 1)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')

        self.poltch = QComboBox()
        self.poltch.addItems(["0", "1", "2", "3", "4"])

        chlabel = QLabel()
        chtxt = f'<font >选择数据通道数</font>'
        chlabel.setText(chtxt)
        chlabel.setAlignment(Qt.AlignBottom)

        self.rx_show = QCheckBox('RX ON')
        self.tx_show = QCheckBox('TX ON')

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        self.tx_edit = QLineEdit()

        button_tx = QPushButton("发送")
        button_tx.clicked.connect(self.serial_send)

        self.sendtypebox = QComboBox()
        self.sendtypebox.addItems(["ABC", "HEX"])

        grid.addWidget(self.sendtypebox, *[9, 13], 1, 1)
        grid.addWidget(button_tx, *[9, 14], 1, 1)
        grid.addWidget(self.text_edit, *[7, 1], 2, 14)
        grid.addWidget(self.tx_edit, *[9, 1], 1, 12)
        grid.addWidget(self.plot_widget, *[0, 1], 7, 14)
        grid.addWidget(self.serialbox, *[0, 0])
        grid.addWidget(self.bound_rate, *[1, 0])

        grid.addWidget(button, *[2, 0])
        grid.addWidget(self.poltch, *[4, 0])
        grid.addWidget(chlabel, *[3, 0])
        grid.addWidget(self.rx_show, *[7, 0])
        grid.addWidget(self.tx_show, *[9, 0])

        self.ch1 = self.plot_widget.getPlotItem()
        self.ch2 = self.plot_widget.getPlotItem()
        self.ch3 = self.plot_widget.getPlotItem()
        self.ch4 = self.plot_widget.getPlotItem()

        self.plot_data = [[], [], [], []]
        self.plot_curve1 = self.ch1.plot(self.plot_data[0])
        self.plot_curve1.setPen(pg.mkPen(color='red', width=2, style=pg.QtCore.Qt.SolidLine))
        self.plot_curve2 = self.ch2.plot(self.plot_data[1])
        self.plot_curve2.setPen(pg.mkPen(color='blue', width=2, style=pg.QtCore.Qt.SolidLine))
        self.plot_curve3 = self.ch3.plot(self.plot_data[2])
        self.plot_curve3.setPen(pg.mkPen(color='green', width=2, style=pg.QtCore.Qt.SolidLine))
        self.plot_curve4 = self.ch4.plot(self.plot_data[3])
        self.plot_curve4.setPen(pg.mkPen(color='black', width=2, style=pg.QtCore.Qt.SolidLine))

        self.show()
        self.timer = self.startTimer(10)
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.plot_update)
        self.plot_timer.start(100)

    def scroll_to_bottom(self):
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_data_buffer(self):
        start_index_1 = self.data_buffer.find(frame_b_1)
        start_index_2 = self.data_buffer.find(frame_b_2)
        end_index_1 = self.data_buffer.find(frame_e_1)
        end_index_2 = self.data_buffer.find(frame_e_2)

        if start_index_2 - start_index_1 == 1 and end_index_2 - end_index_1 == 1:
            self.data_frame = self.data_buffer[start_index_2 + 1:end_index_1]
            self.data_buffer = self.data_buffer[end_index_2 + 1:]
        else:
            self.data_buffer = self.data_buffer[end_index_2 + 1:]
        if len(self.data_buffer) > 1000:
            self.data_buffer = b''

    def serial_send(self):
        if self.ser != None:
            if self.ser.isOpen():
                txtype = self.sendtypebox.currentText()
                txcontent = self.tx_edit.text()
                if txtype == "HEX":
                    content = bytes.fromhex(txcontent)
                    self.ser.write(content)
                    current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    data_str = f'<b><font size="4" color="red">[{current_time}]</font> <font size="4" color="black">\
                                    {" ".join(format(byte, "02x").upper() for byte in content)}</font></b><br>'
                    if self.tx_show.isChecked():
                        self.text_edit.insertHtml(data_str)
                    print(content)
                if txtype == "ABC":
                    content = bytes(txcontent, "UTF-8")
                    self.ser.write(content)
                    current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    data_str = f'<b><font size="4" color="red">[{current_time}]</font> <font size="4" color="black">\
                                    {" ".join(format(byte, "02x").upper() for byte in content)}</font></b><br>'
                    if self.tx_show.isChecked():
                        self.text_edit.insertHtml(data_str)
                    print(content)
        else:
            QMessageBox.information(None, "ATTITION", '先打开串口哦')

    def plot_update(self):
        ch = self.poltch.currentIndex()
        if ch != 0 and self.data_frame != None:
            if len(self.data_frame) != 0:
                data = struct.unpack("h" * ch, self.data_frame[:ch * 2])
                data_len = len(data)
                for i in range(data_len):
                    self.plot_data[i].insert(0, data[i])

                self.plot_curve1.setData(self.plot_data[0])
                self.plot_curve2.setData(self.plot_data[1])
                self.plot_curve3.setData(self.plot_data[2])
                self.plot_curve4.setData(self.plot_data[3])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sd = SerialDebugger()
    sys.exit(app.exec_())
