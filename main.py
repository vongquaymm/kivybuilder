import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import threading
import time
from threading import Thread
from jnius import autoclass

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
uuid = autoclass('java.util.UUID').fromString("00001101-0000-1000-8000-00805F9B34FB")
socket = None
recv_stream = None
send_stream = None
bt_adapter = BluetoothAdapter.getDefaultAdapter()
devices = bt_adapter.getBondedDevices().toArray()

for device in devices:
    if device.getName() == "TLCT":
        socket = device.createRfcommSocketToServiceRecord(uuid)
        socket.connect()
        print(f'connected to {device.getName()}')
        recv_stream = socket.getInputStream()
        send_stream = socket.getOutputStream()


def send_signal(signal):
    send_stream.write(signal.decode("utf-8"))
    send_stream.flush()
def receive_signal():
    while True:
        buffer = bytearray(1024)
        data = recv_stream.read(buffer, 0, len(buffer))
        message = bytes(buffer[:data]).decode("utf-8").strip()
        print(message)
        if message == "0":
            AppRoot.stop_timer()



class AppRoot(BoxLayout):
    def __init__(self, **kwargs):
        super(AppRoot, self).__init__(**kwargs)
        self.orientation = "vertical"
        
        # Biến lưu trữ thời gian và trạng thái chạy
        self.elapsed_time = 0.0
        self.start_time = 0.0
        self.running = False
        self.timer_thread = None

        # Label hiển thị thời gian (ban đầu là 0.000 giây)
        self.time_displayed = Label(text="0.000 giây", font_size=100)
        self.add_widget(self.time_displayed)

        # Layout chứa các nút điều khiển
        button_layout = BoxLayout(orientation="horizontal", spacing=10, padding=(0, 100, 0, 50))
        self.start_btn = Button(text="Start")
        self.stop_btn  = Button(text="Stop")
        self.reset_btn = Button(text="Reset")

        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.stop_btn)
        button_layout.add_widget(self.reset_btn)
        self.add_widget(button_layout)

        # Gán sự kiện cho các nút
        self.start_btn.bind(on_press=self.start_timer)
        self.stop_btn.bind(on_press=self.stop_timer)
        self.reset_btn.bind(on_press=self.reset_timer)
    def update_timer(self):
        while self.running:
            self.elapsed_time = time.time() - self.start_time
            self.time_displayed.text = f"{self.elapsed_time:.3f} giây"
            time.sleep(0.01)
    def start_timer(self):
        if not self.running:
            send_signal("1")
            self.running = True
            self.start_time = time.time()
            Thread(target=self.update_timer, daemon=True).start()
    def stop_timer(self):
        self.running = False
        send_signal("0")
    def reset_timer(self):
        self.running = False
        self.elapsed_time = 0.0
        self.time_displayed.text = "0.000 giây"


class AppGui(App):
    def build(self):
        return AppRoot()

if __name__ == "__main__":
    Thread(target=receive_signal, daemon=True).start()
    AppGui().run()
