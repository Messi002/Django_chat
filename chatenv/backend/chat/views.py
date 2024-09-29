from django.shortcuts import render, redirect
from .models import Room, Message

# Create your views here.
def HomeView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        room = request.POST.get("room")
        
        try:
            existing_room = Room.objects.get(room_name__icontains=room)
        except Room.DoesNotExist:
            r = Room.objects.create(room_name=room)
            return redirect("room", room_name=room, username=username)
        
        return redirect("room", room_name=room, username=username) 
    else:
        # Handle GET request
        return render(request, 'index.html')

def RoomView(request, room_name, username):
    existing_room = Room.objects.get(room_name__icontains=room_name)
    print(vars(existing_room))
    get_messages = Message.objects.filter(room = existing_room)
    context = {"messages": get_messages, "user": username, "room_name": existing_room.room_name}
    return render(request, 'room.html', context)
    # return render(request, 'room.html', {'room_name': room_name})