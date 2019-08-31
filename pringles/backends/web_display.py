import tornado.web
import tornado.ioloop
import sys
import os
from pathlib import Path
import signal
import threading
from contextlib import contextmanager
import asyncio

from pringles.models import Model


class ServerThread(threading.Thread):
    def run(self):
        new_io_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_io_loop)
        tornado.ioloop.IOLoop.current().start()


web_model_display_thread = ServerThread()


class WebApplication(tornado.web.Application):

    initialized = False
    started = False
    url_prefix = ''

    # Display model as html request handler
    class DisplayModel(tornado.web.RequestHandler):
        def get(self):
            self.write("Not implemented yet")

    class TestGetWithBodyHandler(tornado.web.RequestHandler):

        def get(self):
            written_response = "holis"
            self.write(written_response)

    def __init__(self, url_prefix: str = ''):
        super().__init__([
            (url_prefix + r'/test', self.TestGetWithBodyHandler),
        ])

    @classmethod
    def initialize(cls, url_prefix: str = '', port: int = None, address: str = None):
        if cls.initialized:
            return

        app = cls(url_prefix=url_prefix)
        cls.url_prefix = url_prefix

        if port is None:
            # NOTE: This is a random part for testing purposes
            port = 10982

        # Add logic to grab a random *available* port
        app.listen(port)
        cls.initialized = True

    @classmethod
    def start(cls):
        if cls.started:
            return

        ioloop = tornado.ioloop.IOLoop.current()

        def shutdown():
            ioloop.stop()
            print("Server is stopped")
            sys.stdout.flush()
            cls.started = False

        @contextmanager
        def chatch_sigint():
            old_handler = signal.signal(
                signal.SIGINT,
                lambda sig, frame: ioloop.add_callback_from_signal(shutdown))
            try:
                yield
            finally:
                signal.signal(signal.SIGINT, old_handler)

        cls.started = True
        print("Press CTRL-C to stop the display server")
        sys.stdout.flush()
        with chatch_sigint():
            ioloop.start()


def ipython_inline_display(model: Model) -> bytes:
    import tornado.template
    from pringles.serializers import JsonSerializer

    WebApplication.initialize()
    if not web_model_display_thread.is_alive():
        web_model_display_thread.start()

    single_model_template = Path(os.path.join(
        os.path.dirname(__file__), 'statics'), 'test.html').read_bytes()
    single_template = tornado.template.Template(single_model_template)
    return single_template.generate(
        model_source=JsonSerializer.serialize(model)
    )
