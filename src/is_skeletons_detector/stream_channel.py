from is_wire.core import Channel
from is_wire.core.wire.conversion import WireV1


class StreamChannel(Channel):
    def consume(self, return_dropped=False):
        def clean_and_consume(timeout=None):
            self.amqp_message = None
            while self.amqp_message is None:
                self.connection.drain_events(timeout=timeout)
            return self.amqp_message

        _amqp_message = clean_and_consume()
        dropped = 0
        while True:
            try:
                # will raise an exceptin when no message remained
                _amqp_message = clean_and_consume(timeout=0.0)
                dropped += 1
            except:
                # returns last message
                msg = WireV1.from_amqp_message(_amqp_message)
                return (msg, dropped) if return_dropped else msg
