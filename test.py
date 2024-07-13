import serial
import time

serial_port = serial.Serial('COM2', 115200)  # Replace 'COM3' with your serial port
frame_b_1 = b'\xfa\xaf'
data = 0
while True:
    serial_port.write(frame_b_1 + data.to_bytes(2, byteorder='little'))  # Send data to the serial port
    data += 1
    if data > 3000:
        data = -3000
    time.sleep(0.01)  # Adjust the delay as needed





