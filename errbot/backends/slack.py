import logging
from errbot.errBot import ErrBot



class SlackBackend(ErrBot):

    def __init__(self, config):
        from errbot.backends.base import Identifier

        super(self.__class__, self).__init__(config)
        self.conn = None
        self.token = config.BOT_IDENTITY[u'token']
        self.jid = Identifier(u'errbot')


    def serve_forever(self):
        from time import sleep

        self.connect()  # be sure we are "connected" before the first command
        self.connect_callback()  # notify that the connection occured
        try:
            while True:
                events = self.conn.rtm_read()
                for i_event in events:
                    self._handle_event(i_event)
                sleep(1)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect_callback()
            self.shutdown()


    def _handle_event(self, event):
        from errbot.backends.base import Message

        type_ = event.get('type')
        text = event.get('text')
        subtype = event.get('subtype')
        if type_ in (u'message',) and subtype is None and text:
            channel = event[u'channel']
            if channel == u'D03MABG2M':
                type_ = u'chat'
            else:
                type_ = u'groupchat'
            msg = Message(text, type_=type_)
            msg.frm = event[u'channel']
            msg.to = self.jid
            self.callback_message(msg)


    def send_message(self, msg):
        super(SlackBackend, self).send_message(msg)
        logging.info(u"send_message {}".format(msg))
        self.conn.api_call(
            'chat.postMessage',
            token=self.token,
            channel=str(msg.to),
            text=msg.body,
            icon_url='https://raw.githubusercontent.com/gbin/err/master/docs/_static/err.png',
            username=msg.frm,
        )
        #self.conn.rtm_send_message(str(msg.to), msg.body)


    def connect(self):
        from slackclient import SlackClient

        if not self.conn:
            self.conn = SlackClient(self.token)
            r = self.conn.rtm_connect()
            if not r:
                raise RuntimeError("SLACK: Connection failed. Invalid token '%s'?" % self.token)
        return self.conn


    def build_message(self, text):
        from errbot.backends.base import Message, build_message
        return build_message(text, Message)


    def join_room(self, room, username=None, password=None):
        pass


    @property
    def mode(self):
        return u'null'

