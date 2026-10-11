import logging
import threading
import queue
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

from main import Bot

Window.clearcolor = (0.035, 0.025, 0.06, 1)

class QueueHandler(logging.Handler):
    def __init__(self, target):
        super().__init__()
        self.target = target
    def emit(self, record):
        try:
            self.target.put_nowait(self.format(record))
        except Exception:
            pass

class Panel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(18), spacing=dp(12), **kwargs)
        with self.canvas.before:
            Color(0.035, 0.025, 0.06, 1)
            self.bg = RoundedRectangle(radius=[dp(18)])
        self.bind(pos=self._update_bg, size=self._update_bg)
    def _update_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

class TCPBotApp(App):
    def build(self):
        self.title = "TeeXez TCP Bot"
        self.events = queue.Queue()
        self.bot = None
        self.bot_thread = None
        self.log_lines = []
        logging.getLogger().addHandler(QueueHandler(self.events))
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(72), spacing=dp(3))
        header.add_widget(Label(text="[b]TEEXEZ TCP BOT[/b]", markup=True, font_size="24sp", color=(0.85,0.65,1,1), halign="left", valign="middle"))
        self.status = Label(text="STATUS  •  STOPPED", size_hint_y=None, height=dp(24), color=(0.72,0.68,0.8,1), halign="left")
        header.add_widget(self.status)
        root.add_widget(header)

        panel = Panel(size_hint_y=None, height=dp(218))
        panel.add_widget(Label(text="ACCOUNT CREDENTIALS", size_hint_y=None, height=dp(26), color=(0.8,0.7,1,1), halign="left"))
        self.uid_input = TextInput(hint_text="Free Fire UID", multiline=False, size_hint_y=None, height=dp(48), input_filter="int", padding=[dp(12),dp(12)], background_color=(0.09,0.07,0.13,1), foreground_color=(1,1,1,1), hint_text_color=(0.58,0.54,0.65,1), cursor_color=(0.8,0.55,1,1))
        self.token_input = TextInput(hint_text="Guest token", multiline=False, password=True, size_hint_y=None, height=dp(48), padding=[dp(12),dp(12)], background_color=(0.09,0.07,0.13,1), foreground_color=(1,1,1,1), hint_text_color=(0.58,0.54,0.65,1), cursor_color=(0.8,0.55,1,1))
        panel.add_widget(self.uid_input)
        panel.add_widget(self.token_input)
        root.add_widget(panel)

        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        self.start_btn = Button(text="START BOT", background_normal="", background_color=(0.43,0.18,0.72,1), color=(1,1,1,1))
        self.stop_btn = Button(text="STOP BOT", background_normal="", background_color=(0.25,0.21,0.3,1), color=(0.9,0.88,0.93,1), disabled=True)
        self.start_btn.bind(on_release=self.start_bot)
        self.stop_btn.bind(on_release=self.stop_bot)
        actions.add_widget(self.start_btn); actions.add_widget(self.stop_btn)
        root.add_widget(actions)

        root.add_widget(Label(text="LIVE ACTIVITY LOG", size_hint_y=None, height=dp(25), color=(0.8,0.7,1,1), halign="left"))
        self.logs = Label(text="Logs will appear here when the bot starts.", size_hint_y=None, color=(0.82,0.8,0.88,1), font_size="12sp", halign="left", valign="top", text_size=(Window.width-dp(42), None))
        self.logs.bind(texture_size=self._resize_log)
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        scroll.add_widget(self.logs)
        root.add_widget(scroll)
        Clock.schedule_interval(self.flush_logs, 0.25)
        Window.bind(size=self._resize_text)
        return root

    def _resize_log(self, widget, size):
        widget.height = size[1] + dp(16)
    def _resize_text(self, *_):
        if hasattr(self, "logs"):
            self.logs.text_size = (max(dp(180), Window.width-dp(42)), None)

    def start_bot(self, *_):
        uid = self.uid_input.text.strip()
        token = self.token_input.text.strip()
        if not uid or not uid.isdigit() or not token:
            self.add_log("ERROR: Masukkan UID numerik dan guest token.")
            return
        if self.bot_thread and self.bot_thread.is_alive():
            return
        self.bot = Bot(uid, token)
        self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        self.bot_thread.start()
        self.status.text = "STATUS  •  CONNECTING"
        self.status.color = (1,0.75,0.3,1)
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.add_log("Bot starting. Credential tidak disimpan ke file.")

    def _run_bot(self):
        try:
            self.bot.run()
        except Exception as exc:
            logging.getLogger("TeeXezDevTCP").exception("Bot stopped unexpectedly: %s", exc)
        finally:
            Clock.schedule_once(self._bot_ended, 0)

    def _bot_ended(self, *_):
        self.status.text = "STATUS  •  STOPPED"
        self.status.color = (0.72,0.68,0.8,1)
        self.start_btn.disabled = False
        self.stop_btn.disabled = True

    def stop_bot(self, *_):
        if self.bot:
            self.bot.cleanup()
        self.status.text = "STATUS  •  STOPPING"
        self.add_log("Stop requested.")

    def add_log(self, message):
        self.log_lines.append(message)
        self.log_lines = self.log_lines[-180:]
        self.logs.text = "\n".join(self.log_lines)

    def flush_logs(self, _dt):
        changed = False
        while True:
            try:
                self.log_lines.append(self.events.get_nowait())
                changed = True
            except queue.Empty:
                break
        if changed:
            self.log_lines = self.log_lines[-180:]
            self.logs.text = "\n".join(self.log_lines)

    def on_stop(self):
        if self.bot:
            self.bot.cleanup()

if __name__ == "__main__":
    TCPBotApp().run()
