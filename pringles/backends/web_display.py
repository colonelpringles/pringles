import tornado.web
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import os
from pathlib import Path
import threading
import asyncio

from pringles.models import Model


class ServerThread(threading.Thread):

    _join_called = False

    def run(self):
        new_io_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_io_loop)
        WebApplication.initialize()

        ioloop = tornado.ioloop.IOLoop.current()

        def healthcheck():
            if ServerThread._join_called:
                ioloop.stop()

        # Add a healthcheck every 1 second
        PeriodicCallback(healthcheck, 1000).start()

        ioloop.start()
        ioloop.close()

    # Overriding join method to mark the ioloop to be disposed
    def join(self):
        ServerThread._join_called = True
        super().join()


web_model_display_thread = ServerThread()


class WebApplication(tornado.web.Application):

    initialized = False
    url_prefix = ''
    target_url = ''
    # Hacky way to force the ipython render method to wait for the tornado server to start
    started_latch = threading.Semaphore(0)

    # Display model as html request handler
    class DisplayModel(tornado.web.RequestHandler):
        def get(self):
            self.write("Not implemented yet")

    class TestGetWithBodyHandler(tornado.web.RequestHandler):
        def get(self):
            written_response = "tutuc"
            self.write(written_response)

    def __init__(self, url_prefix: str = ''):
        super().__init__([
            (url_prefix + r'/heartbeat', self.TestGetWithBodyHandler),
            (url_prefix + r'/_static/(.*)',
                tornado.web.StaticFileHandler, {'path': _get_static_files_path()})
        ])

    @classmethod
    def initialize(cls, url_prefix: str = '', port: int = None, address: str = None):
        if cls.initialized:
            return

        app = cls(url_prefix=url_prefix)
        cls.url_prefix = url_prefix

        try:
            if port is None:
                port = cls._get_random_free_port()
            cls.target_url = 'http://localhost:' + str(port)

            app.listen(port)
            cls.initialized = True
        finally:
            cls.started_latch.release()

    @staticmethod
    def _get_random_free_port() -> int:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port


def _get_static_files_path() -> str:
    return os.path.join(
        os.path.dirname(__file__), 'statics')


def ipython_inline_display(model: Model) -> bytes:
    import tornado.template
    from pringles.serializers import JsonSerializer

    if not web_model_display_thread.is_alive():
        web_model_display_thread.start()
        WebApplication.started_latch.acquire()

    single_model_template = Path(_get_static_files_path(), 'basic.html').read_bytes()
    single_template = tornado.template.Template(single_model_template)
    return single_template.generate(
        model_source=JsonSerializer.serialize(model),
        url_prefix=WebApplication.target_url
    )
