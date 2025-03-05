from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer


class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("audio_stream", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("audio_stream", self.channel_name)

    async def send_audio(self, event):
        chunk = event["chunk"]

        await self.send(bytes_data=chunk)  


class AudioReceive(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # When bytes_data is received, send it to the audio_stream group
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                "audio_stream",  # Group name
                {
                    "type": "send_audio",
                    "chunk": bytes_data
                }
            )
