import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CollaborationSession, ChatMessage, SharedNote, Poll, PollResponse


class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'collaboration_{self.session_id}'
        
        # Join session group
        await self.channel_layer.group_add(self.session_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(self.session_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'note_update':
            await self.handle_note_update(data)
        elif message_type == 'poll_create':
            await self.handle_poll_create(data)
        elif message_type == 'poll_vote':
            await self.handle_poll_vote(data)
    
    async def handle_chat_message(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        message = await self.save_chat_message(data['message'])
        
        # Send to group
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'chat_message_broadcast',
                'message': message,
                'user_email': user.email,
                'timestamp': message['created_at']
            }
        )
    
    async def handle_note_update(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        note = await self.save_or_update_note(data['content'])
        
        # Send to group
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'note_update_broadcast',
                'note': note,
                'user_email': user.email,
                'timestamp': note['updated_at']
            }
        )
    
    async def handle_poll_create(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        poll = await self.create_poll(data['question'], data['options'])
        
        # Send to group
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'poll_create_broadcast',
                'poll': poll,
                'user_email': user.email
            }
        )
    
    async def handle_poll_vote(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        response = await self.save_poll_vote(data['poll_id'], data['selected_option'])
        
        # Get updated results
        results = await self.get_poll_results(data['poll_id'])
        
        # Send to group
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'poll_vote_broadcast',
                'poll_id': data['poll_id'],
                'results': results
            }
        )
    
    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_email': event['user_email'],
            'timestamp': event['timestamp']
        }))
    
    async def note_update_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'note_update',
            'note': event['note'],
            'user_email': event['user_email'],
            'timestamp': event['timestamp']
        }))
    
    async def poll_create_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'poll_create',
            'poll': event['poll'],
            'user_email': event['user_email']
        }))
    
    async def poll_vote_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'poll_results',
            'poll_id': event['poll_id'],
            'results': event['results']
        }))
    
    @database_sync_to_async
    def save_chat_message(self, message):
        from django.utils import timezone
        chat = ChatMessage.objects.create(
            session_id=self.session_id,
            author=self.scope['user'],
            message=message
        )
        return {
            'id': chat.id,
            'message': chat.message,
            'created_at': chat.created_at.isoformat()
        }
    
    @database_sync_to_async
    def save_or_update_note(self, content):
        from django.utils import timezone
        note, created = SharedNote.objects.update_or_create(
            session_id=self.session_id,
            author=self.scope['user'],
            defaults={'content': content}
        )
        return {
            'id': note.id,
            'content': note.content,
            'updated_at': note.updated_at.isoformat()
        }
    
    @database_sync_to_async
    def create_poll(self, question, options):
        from django.utils import timezone
        poll = Poll.objects.create(
            session_id=self.session_id,
            question=question,
            options=options
        )
        return {
            'id': poll.id,
            'question': poll.question,
            'options': poll.options,
            'created_at': poll.created_at.isoformat()
        }
    
    @database_sync_to_async
    def save_poll_vote(self, poll_id, selected_option):
        response, created = PollResponse.objects.get_or_create(
            poll_id=poll_id,
            user=self.scope['user'],
            defaults={'selected_option': selected_option}
        )
        if not created:
            response.selected_option = selected_option
            response.save()
        return {'selected_option': response.selected_option}
    
    @database_sync_to_async
    def get_poll_results(self, poll_id):
        poll = Poll.objects.get(id=poll_id)
        responses = poll.responses.all()
        
        option_counts = {option: 0 for option in poll.options}
        for response in responses:
            if 0 <= response.selected_option < len(poll.options):
                option_name = poll.options[response.selected_option]
                option_counts[option_name] = option_counts.get(option_name, 0) + 1
        
        return {
            'question': poll.question,
            'options': poll.options,
            'results': option_counts,
            'total_votes': responses.count()
        }
