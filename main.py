# -- coding utf-8 --
import threading
import requests
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from plyer import notification as plyer_notify

NOTIFY_ID = 1001

STOCKS_FILE = 'stocks.txt'


def normalize_code(code)
    600519 - sh600519 ; 000001 - sz000001
    code = code.strip().lower()
    if code.startswith(('sh', 'sz', 'hk', 'us'))
        return code
    if code.startswith(('6', '9'))
        return 'sh' + code
    return 'sz' + code


def in_trade_time(now=None)
    now = now or datetime.now()
    if now.weekday() = 5          # 周末
        return False
    t = now.hour  60 + now.minute
    return (9  60 + 15 = t = 11  60 + 35) or 
           (12  60 + 55 = t = 15  60 + 30)


def fetch_quotes(codes)
    腾讯财经API，返回 [(name, pct), ...]
    url = 'httpsqt.gtimg.cnq=' + ','.join(codes)
    r = requests.get(url, timeout=8)
    r.encoding = 'gbk'
    result = []
    for line in r.text.split(';')
        line = line.strip()
        if '=' not in line or '~' not in line
            continue
        data = line.split('~')
        if len(data)  33
            continue
        name = data[1]
        pct = data[32]              # 第33个字段为涨跌幅
        try
            pct = float(pct)
        except ValueError
            continue
        result.append((name, pct))
    return result


def build_text(quotes, ok, show_name=True)
    正常 ✅  贵州茅台 🔴1.23%  -  平安银行 🟢0.85%
       故障 ❌ 获取失败
    if not ok
        return '❌ 获取失败', '请检查网络或股票代码'
    parts = []
    for name, pct in quotes
        val = f'{abs(pct).2f}%'
        if pct  0
            marker = f'🔴{val}'      # 红 = 涨
        elif pct  0
            marker = f'🟢{val}'      # 绿 = 跌
        else
            marker = f'⚪{val}'      # 灰 = 平
        if show_name
            parts.append(f'{name} {marker}')
        else
            parts.append(marker)     # 只显示 🔴1.23%
    return '✅', '  -  '.join(parts)


# ---------- 界面 ----------

class StockApp(App)
    def __init__(self, kw)
        super().__init__(kw)
        self.stocks = self._load_stocks()
        self.interval = 10          # 秒
        self.all_day = False
        self.show_name = False      # 默认不显示股票名称
        self._event = None
        self.status_label = None

    def _load_stocks(self)
        try
            with open(STOCKS_FILE) as f
                return [l.strip() for l in f if l.strip()]
        except OSError
            return ['sh600519', 'sz000001']

    def _save_stocks(self)
        with open(STOCKS_FILE, 'w') as f
            f.write('n'.join(self.stocks))

    def build(self)
        root = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # 状态与股票列表
        self.status_label = Label(text='等待刷新…', size_hint_y=None, height=36)
        root.add_widget(self.status_label)
        self.list_label = Label(text='', size_hint_y=None, height=120,
                                valign='top')
        self.list_label.bind(texture_size=self.list_label.setter('size'))
        sv = ScrollView()
        sv.add_widget(self.list_label)
        root.add_widget(sv)

        # 添加删除股票
        row1 = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.code_input = TextInput(hint_text='如 600519  sz000001',
                                    multiline=False)
        row1.add_widget(self.code_input)
        row1.add_widget(Button(text='添加', on_press=self.add_stock))
        row1.add_widget(Button(text='删除', on_press=self.del_stock))
        root.add_widget(row1)

        # 更新间隔
        row2 = BoxLayout(size_hint_y=None, height=48, spacing=8)
        row2.add_widget(Label(text='更新间隔(秒)'))
        self.interval_input = TextInput(text='10', multiline=False,
                                        input_filter='int')
        row2.add_widget(self.interval_input)
        row2.add_widget(Button(text='应用间隔', on_press=self.apply_interval))
        root.add_widget(row2)

        # 全天显示
        row3 = BoxLayout(size_hint_y=None, height=44)
        self.all_day_cb = CheckBox(active=False, size_hint_x=None, width=40)
        self.all_day_cb.bind(active=self.toggle_all_day)
        row3.add_widget(self.all_day_cb)
        row3.add_widget(Label(text='全天显示（不勾选则只在交易时间显示）'))
        root.add_widget(row3)

        # 显示股票名称
        row4 = BoxLayout(size_hint_y=None, height=44)
        self.name_cb = CheckBox(active=False, size_hint_x=None, width=40)
        self.name_cb.bind(active=self.toggle_name)
        row4.add_widget(self.name_cb)
        row4.add_widget(Label(text='显示股票名称（不勾选则只显示涨跌幅）'))
        root.add_widget(row4)

        self._schedule(10)
        self.refresh_list_label()
        return root

    # ----- 控件回调 -----
    def add_stock(self, _)
        code = self.code_input.text.strip()
        if not code
            return
        code = normalize_code(code)
        if code not in self.stocks and len(self.stocks)  3
            self.stocks.append(code)
            self._save_stocks()
            self.refresh_list_label()

    def del_stock(self, _)
        code = normalize_code(self.code_input.text)
        if code in self.stocks
            self.stocks.remove(code)
            self._save_stocks()
            self.refresh_list_label()

    def apply_interval(self, _)
        try
            v = max(3, int(self.interval_input.text))
        except ValueError
            return
        self._schedule(v)

    def toggle_all_day(self, cb, active)
        self.all_day = active
        if not active
            self._maybe_hide()

    def toggle_name(self, cb, active)
        self.show_name = active

    def refresh_list_label(self)
        self.list_label.text = '当前股票：' + '、'.join(self.stocks)

    # ----- 调度 -----
    def _schedule(self, seconds)
        self.interval = seconds
        if self._event
            self._event.cancel()
        self._event = Clock.schedule_interval(lambda dt self.tick(), seconds)
        self.tick()

    def tick(self)
        if not (self.all_day or in_trade_time())
            self._maybe_hide()
            return
        if not self.stocks
            return
        threading.Thread(target=self._fetch_and_show, daemon=True).start()

    def _maybe_hide(self)
        try
            plyer_notify.cancel(NOTIFY_ID)
        except Exception
            pass
        if self.status_label
            self.status_label.text = '非交易时间，已隐藏'

    def _fetch_and_show(self)
        ok = True
        quotes = []
        try
            quotes = fetch_quotes(self.stocks)
            if not quotes
                ok = False
        except Exception
            ok = False
        Clock.schedule_once(lambda dt self._update_ui(quotes, ok))

    def _update_ui(self, quotes, ok)
        title, text = build_text(quotes, ok, show_name=self.show_name)
        plyer_notify.notify(title=title, message=text, timeout=1)
        if quotes
            self.status_label.text = '正常 ' + datetime.now().strftime('%H%M%S')
        else
            self.status_label.text = '获取数据失败'


if __name__ == '__main__'
    StockApp().run()