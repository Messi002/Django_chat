import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message


# ChatConsumer is an asynchronous WebSocket consumer that handles real-time
# chat communication between clients.
class ChatConsumer(AsyncWebsocketConsumer):

    # This function is called when the WebSocket connection is established.
    async def connect(self):
        # Generate a unique room name based on the room_name passed in the URL
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"

        # Add the current WebSocket connection to the group corresponding to the room.
        # `channel_layer` allows communication between multiple consumers (clients).
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        # Accept the WebSocket connection and establish the communication.
        await self.accept()

    # This function is called when the WebSocket connection is closed or disconnected.
    async def disconnect(self, code):
        # Remove the current WebSocket connection from the group of the room.
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        # Close the WebSocket connection with the provided code.
        self.close(code)

    # This function is called when the WebSocket receives a message from the client.
    async def receive(self, text_data):
        # Convert the received JSON-encoded data to a Python dictionary.
        data_json = json.loads(text_data)

        # Create an event with the message data to be sent to the group.
        # The "type" key specifies the name of the handler for the event.
        event = {"type": "send_message", "message": data_json}

        # Send the event to the group associated with the room name.
        # This ensures that the message will be sent to all clients in the room.
        await self.channel_layer.group_send(self.room_name, event)

    # This function handles sending the message to all WebSocket clients in the room.
    # It is triggered by the group_send method when an event with "type": "send_message" is received.
    async def send_message(self, event):
        # Extract the message data from the event.
        data = event["message"]

        # Store the message in the database by calling the create_message method.
        await self.create_message(data=data)

        # Create a response dictionary containing the sender and the message content.
        response = {"sender": data["sender"], "message": data["message"]}

        # Send the response as JSON-encoded data back to the client that sent the message.
        await self.send(text_data=json.dumps({"message": response}))

    # This method runs in a separate database thread to avoid blocking the async event loop.
    # It stores the message in the database.
    @database_sync_to_async
    def create_message(self, data):
        # Fetch the Room object where the message is being sent, using the room_name from the data.
        get_room = Room.objects.get(room_name=data["room_name"])

        # Check if the exact message from the sender already exists to avoid duplication.
        if not Message.objects.filter(
            message=data["message"], sender=data["sender"]
        ).exists():
            # If the message doesn't exist, create a new Message object and store it in the database.
            new_message = Message.objects.create(
                room=get_room, message=data["message"], sender=data["sender"]
            )
