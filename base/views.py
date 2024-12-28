from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topics, Message, User
from .forms import Roomform, UserForm, MyUserCreationForm

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# rooms = [
#     {'id' : 1, 'name': 'salma'},
#     {'id' : 2, 'name': 'shafna'},
#     {'id' : 3, 'name': 'samad'},
# ]


def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user doesnt exit')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'user doesnt exit not')

    context = {'page': page}
    return render(request, 'base/loginreg.html', context)

def logoutuser(request):
    logout(request)
    return redirect('home')

def registeruser(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'error occured during registrattion')
    return render(request, 'base/loginreg.html', {'form': form})

def home(request):
    q = request.GET.get('q') if  request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topics__name__icontains=q)| Q(name__icontains=q)| Q(description__icontains=q))
    
    topics = Topics.objects.all()[0:5]
    room_count = rooms.count()
    room_messeges = Message.objects.filter(Q(room__topics__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messeges}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = Roomform()
    topics = Topics.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topics', '').strip()
        if not topic_name:
            messages.error(request, 'Topic name cannot be empty.')
            return render(request, 'base/roomform.html', {'form': form, 'topics': topics})

        topics, created = Topics.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topics=topics,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/roomform.html', context)

# @login_required(login_url='login')
# def createRoom(request):
#     form = Roomform()
#     topics = Topics.objects.all()
#     if request.method == 'POST':
#         topic_name = request.POST.get('topics')
#         topics, created = Topics.objects.get_or_create(name = topic_name)
#         Room.objects.create(host=request.user, topics=topics, name = request.POST.get('name'), description=request.POST.get('description'))
        
#         return redirect('home')
#     context = {'form': form, 'topics': topics}
#     return render(request, 'base/roomform.html', context)

@login_required(login_url='login')
def updateroom(request, pk):
    room = Room.objects.get(id=pk)
    form = Roomform(instance=room)
    topics = Topics.objects.all()

    if request.user != room.host:
        return HttpResponse('ur are not allowed here')

    if request.method =='POST':
        topic_name = request.POST.get('topics', '').strip()
        if not topic_name:
            messages.error(request, 'Topic name cannot be empty.')
            return render(request, 'base/roomform.html', {'form': form, 'topics': topics})

        topics, created = Topics.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topics = request.POST.get('Topics')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form':form, 'topics': topics, 'room': room}
    return render(request, 'base/roomform.html', context)

@login_required(login_url='login')
def deleteroom(request, pk):
    room = Room.objects.get(id=pk)
    form = Roomform(instance=room)
    if request.method =='POST':
        room.delete()
        return redirect('home')


    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deletemessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('your not allowed here!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')


    return render(request, 'base/delete.html', {'obj': message})


def userprofile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topics.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def edituser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'base/edit-user.html', {'form': form})

def topicspage(request):
    q = request.GET.get('q') if  request.GET.get('q') != None else ''
    topics = Topics.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activitypage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})

# from django.contrib.auth.models import User

# Replace 'samad' with the username you're testing




