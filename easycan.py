import can
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Vertical

class CanReceiveWidget(Static):
    def __init__(self, bus):
        super().__init__()
        self.bus = bus
        self.can_messages = []

    async def on_mount(self):
        asyncio.create_task(self.refresh_can_messages())

    async def refresh_can_messages(self):
        while True:
            msg = self.bus.recv(1.0)  # 超时时间为1秒
            if msg:
                self.can_messages.append(f"Received: {msg}")
                self.update('\n'.join(self.can_messages))
            await asyncio.sleep(1)

class CanSendWidget(Input):
    def __init__(self, bus):
        super().__init__(placeholder="Enter CAN message data and press Enter")
        self.bus = bus

    async def on_blur(self, event: Input.blur):
        data = [int(x) for x in self.value.split()]
        msg = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
        self.bus.send(msg)
        self.value = ""  # 发送后清空输入框

class CanApp(App):
    def compose(self) -> ComposeResult:
        bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
        receive_widget = CanReceiveWidget(bus)
        send_widget = CanSendWidget(bus)
        container = Vertical(send_widget, receive_widget)
        yield container

if __name__ == "__main__":
    app = CanApp()
    app.run()
