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
            logging.debug(u"Trigger disconnect callback")
            self.disconnect_callback()
            logging.debug(u"Trigger shutdown")
            self.shutdown()


    def _handle_event(self, event):
        from errbot.backends.base import Message

        type_ = event.get(u'type')
        if type_ in (u'message',):
            ##logging.debug(u"event: %s" % event)
            channel = event[u'channel']
            if channel == u'D03MABG2M':
                type_ = u'chat'
            else:
                type_ = u'groupchat'
            msg = Message(event[u'text'], type_=type_)
            msg.frm = event[u'channel']
            msg.to = self.jid
            self.callback_message(msg)


    def send_message(self, msg):
        super(SlackBackend, self).send_message(msg)
        self.conn.rtm_send_message(unicode(msg.to), msg.body)


    def connect(self):
        from slackclient import SlackClient

        if not self.conn:
            self.conn = SlackClient(self.token)
            self.conn.rtm_connect()
        return self.conn


    def build_message(self, text):
        from errbot.backends.base import Message, build_text_html_message_pair

        text, html = build_text_html_message_pair(text)
        return Message(text, html=html)


    def join_room(self, room, username=None, password=None):
        pass


    @property
    def mode(self):
        return u'null'

