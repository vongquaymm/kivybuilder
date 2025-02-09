import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import time
from kivy.clock import Clock
from jnius import autoclass
class Myroot(BoxLayout):
    def __init__(self, **kwargs):
        self.elapsed_time = 0.0
        self.start_time = 0.0
        self.running = False
        super().__init__(orientation="vertical", spacing=20, padding=20, **kwargs)

        # Hiển thị thời gian
        self.time_displayed = Label(text="0.000s", font_size=80, size_hint=(1, 0.5))

        # Layout chứa các nút
        self.BtnLayout = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.3))

        # Các nút điều khiển
        self.btn_start = Button(text="Start", font_size=30, size_hint=(1, 1), on_press = self.Start_timer)
        self.btn_stop = Button(text="Stop", font_size=30, size_hint=(1, 1), on_press = self.Stop_timer)
        self.btn_reset = Button(text="Reset", font_size=30, size_hint=(1, 1), on_press = self.Reset_timer)

        # Thêm nút vào layout
        self.BtnLayout.add_widget(self.btn_start)
        self.BtnLayout.add_widget(self.btn_stop)
        self.BtnLayout.add_widget(self.btn_reset)

        # Thêm các phần vào giao diện chính
        self.add_widget(self.time_displayed)
        self.add_widget(self.BtnLayout)
    
    def update_time(self, instance):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.time_displayed.text = f"{self.elapsed_time:.3f} giây"

    def Start_timer(self, instance):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            Clock.schedule_interval(self.update_time, 0.01)
            sendsignal("1")
    def Stop_timer(self, instance):
        self.running = False
        Clock.unschedule(self.update_time)
        sendsignal("0")
    def Reset_timer(self, instance):
        self.running = False
        self.elapsed_time = 0.0
        self.start_time = 0.0
        self.time_displayed.text = "0.000 giây"
        Clock.unschedule(self.update_time)
        sendsignal("0")

class MyApp(App):
    def build(self):
        return Myroot()

if __name__ == '__main__':
    BluetoohAdapter = autoclass("android.bluetooth.BlueToothAdapter")
    BluetoohDevice = autoclass("android.bluetooth.BlueToothDevice")
    BluetoohSocket = autoclass("android.bluetooth.BlueToothSocket")
    socket = None
    send_stream = None
    recv_stream = None
    uuid = autoclass('java.util.UUID').fromString("00001101-0000-1000-8000-00805F9B34FB")
    bt_adapter = BluetoohAdapter.getDefaultApdapter()
    devices = bt_adapter.getBondedDevices().toArray()
    
    for device in devices:
        if device.getName() == "TLCT":
            socket = device.createRfCommSocketToServiceRecord(uuid)
            socket.conect()
            send_stream =socket.getOutputStream()
            recv_stream = socket.getInputStream()
    def sendsignal(signal):
        send_stream.write(signal.encode("utf-8"))
        send_stream.flush()
    def recvsignal(data):
        while True:
            buffer = bytearray(1024)
            data = recv_stream.read(buffer, 0, len(buffer))
            message = bytes(buffer[:data]).decode("utf-8").strip()
            print(message)
            if message == "0":
                Myroot.Stop_timer()
    MyApp().run()
    Clock.schedule_interval(recvsignal, 0.01)
