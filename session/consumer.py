
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

from django.utils.timezone import now

from session.models import Chat, Message

from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)
logging.basicConfig(filename='positalk.log', level=logging.INFO)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f'chat_{self.chat_id}'
        logger.info(self.scope['user'])

        if not await self.chat_exists_db():
            logger.info(f"CHAT {self.chat_id} DOESN'T EXIST")
            await self.close()
            return
        self.user = self.scope['user']

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @sync_to_async(thread_sensitive=True)
    def chat_exists_db(self):
        chat =  Chat.objects.filter(id=self.chat_id)
        if chat.exists():
            chat = chat.first()
            if chat.client == self.scope['user'] or chat.psychologist == self.scope['user']:
                return True
        return False

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['text']
        sender = self.scope['nickname']
        created_at = now()
        await self.create_message(message)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'text': message,
                'sender': sender,
                'created_at': created_at
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'text': event['text'],
            'sender': event['sender'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def create_message(self, content):
        logger.critical(f"sent message, creating {content}")
        message = Message.objects.create(chat_id=self.chat_id, sender=self.user, text=content)
        return message