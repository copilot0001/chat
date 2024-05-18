import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import CustomUser, Message
from django.conf import settings
import jwt

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        self.user = None
        self.accept()

    def receive(self, text_data):
        if not self.user:
            # Extract the access token from the first message
            access_token = text_data.strip()
            try:
                # Decode and verify the access token
                decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_token.get('user_id')  # Assuming 'user_id' is stored in the token
                if user_id is None:
                    raise jwt.InvalidTokenError("User ID not found in token")
                
                self.user = CustomUser.objects.get(pk=user_id)
            except jwt.ExpiredSignatureError:
                # Token has expired
                self.send_error_message("Token has expired")
                return
            except (jwt.InvalidTokenError, CustomUser.DoesNotExist) as e:
                # Invalid token or user not found
                self.send_error_message("Invalid token or user not found")
                return

            # If the user is authenticated, proceed with connecting to the group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            return

        text_data_json = json.loads(text_data)
        print(text_data)
        message_text = text_data_json.get('message')
        sender_email = text_data_json.get('sender')
        receiver_email = text_data_json.get('receiver')

        if not all([message_text, sender_email, receiver_email]):
            self.send_error_message("Missing required fields")
            return

        # Fetch the sender user instance using their email
        sender = CustomUser.objects.filter(email=sender_email).first()
        if sender is None:
            # If sender user not found, close the connection
            self.send_error_message("Sender not found")
            return

        # Fetch the receiver user instance using their email
        receiver = CustomUser.objects.filter(email=receiver_email).first()
        if receiver is None:
            self.send_error_message("Receiver not found")
            return

        message = Message.objects.create(sender=sender, receiver=receiver, content=message_text)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_email': sender_email,
                'timestamp': message.timestamp.isoformat()
            }
        )

    def send_error_message(self, error_message):
        self.send(text_data=json.dumps({
            'type': 'error',
            'error_message': error_message
        }))

    def chat_message(self, event):
        message = event['message']
        sender_email = event['sender_email']
        timestamp = event['timestamp']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'sender_email': sender_email,
            'timestamp': timestamp
        }))




# import json
# from channels.generic.websocket import WebsocketConsumer
# from asgiref.sync import async_to_sync
# from .models import CustomUser, Message

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_group_name = 'test'

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message_text = text_data_json['message']
#         sender_email = text_data_json['sender']  # assuming sender's email is sent from the frontend

#         sender = CustomUser.objects.get(email=sender_email)
#         print(sender)
#         receiver = self.scope['user']  # Assuming receiver is the authenticated user

#         message = Message.objects.create(sender=sender, receiver=receiver, content=message_text)

#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message_text,
#                 'sender_email': sender_email,
#                 'timestamp': message.timestamp.isoformat()  # assuming you want to send timestamp back to frontend
#             }
#         )

#     def chat_message(self, event):
#         message = event['message']
#         sender_email = event['sender_email']
#         timestamp = event['timestamp']

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'type': 'chat',
#             'message': message,
#             'sender_email': sender_email,
#             'timestamp': timestamp
#         }))



# import json
# from channels.generic.websocket import WebsocketConsumer
# from asgiref.sync import async_to_sync

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_group_name = 'test'

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()
   

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type':'chat_message',
#                 'message':message
#             }
#         )

#     def chat_message(self, event):
#         message = event['message']

#         self.send(text_data=json.dumps({
#             'type':'chat',
#             'message':message
#         }))