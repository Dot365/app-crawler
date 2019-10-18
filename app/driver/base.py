import time
import logging
import uiautomator2 as u2

FORMAT = "[%(process)d-%(filename)s:%(lineno)s - %(funcName)20s %(levelname)s] %(message)s"


class BaseDriver:
    def __init__(self):
        self.device = u2.connect()
        self.session = None
        self.pkg_name = None
        self.activity = None
        self.size = self.device.window_size()
        self.width, self.height = self.size

        self.popup_list = []

        # set logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format=FORMAT)
        self.logger.setLevel(logging.DEBUG)

    def app_start(self):
        self.device.app_start(self.pkg_name, self.activity)
        self.session = self.device.session(self.pkg_name, attach=True)

    def open_schema(self, url_schema):
        self.device.shell(f'am start -W -a android.intent.action.VIEW -d {url_schema} {self.pkg_name}')

    def size(self):
        self.device.window_size()
        self.device.push_url()

    def get_source(self):
        return self.device.dump_hierarchy()

    def get_current_package(self):
        pkg_name = self.device.info.get('currentPackageName')
        return pkg_name

    def do_forever(self, action, *args, **kwargs):
        num = 0
        """TODO 更改为装饰器
        """
        while True:
            num += 1
            if num > 5000:
                num = 0
                self.logger.info('自动重启app')
                self.close_app()
                time.sleep(10)
                self.app_start()
                self.logger.info('重启app成功')

            action_name = action.__name__
            self.logger.info(f'{action_name} action to do...; num: {num}')
            if self.is_app_alive():
                # print(self.get_source())
                self.close_popup()
                action(*args, **kwargs)
            else:
                self.close_app()
                self.click_if_exist(text="确认")
                time.sleep(2)
                self.app_start()
            self.logger.info(f'{action_name} action done!')

    def swipe(self, *args):
        self.device.swipe(*args)

    def swipe_right(self, t=0.1, delay=1):
        self.device.swipe(0.1, 0.5, 0.9, 0.5, t)
        time.sleep(delay)

    def swipe_left(self, t=0.1, delay=1):
        self.device.swipe(0.9, 0.5, 0.1, 0.5, t)
        time.sleep(delay)

    def swipe_up(self, t=0.02, delay=0.5):
        self.device.swipe(self.width * 0.5, self.height * 0.8, self.width * 0.5, self.height * 0.3, t)
        time.sleep(delay)

    def swipe_down(self, t=0.02, delay=0.5):
        self.device.swipe(self.width * 0.5, self.height * 0.1, self.width * 0.5, self.height * 0.8, t)
        time.sleep(delay)

    def scroll(self):
        self.device(scrollable=True).scroll(steps=10)

    def fling(self):
        self.device(scrollable=True).fling()
        # self.device.wait_activity()

    def exists(self, **kwargs):
        return self.device(**kwargs).exists

    def click_if_exist(self, **kwargs):
        d = self.device(**kwargs)
        if d.exists:
            try:
                d.click(timeout=2)
            except Exception as e:
                self.logger.info(e)

    def close_popup(self):
        for text in self.popup_list:
            try:
                self.click_if_exist(text=text)
            except Exception:
                self.logger.info(f'close_popup: {text}')

    def is_app_alive(self):
        if self.get_current_package() != self.pkg_name:
            self.logger.info('应用已经退出')
            return False
        else:
            return True

    def close_app(self):
        if self.session:
            self.session.close()
        else:
            self.logger.info('Please open_app first')
