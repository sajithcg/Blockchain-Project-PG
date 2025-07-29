from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
import hashlib
import json
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(sender="Genesis", receiver="Genesis", message="Start of blockchain", previous_hash="0")

    def create_block(self, sender, receiver, message, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'previous_hash': previous_hash,
            'hash': self.calculate_hash(sender, receiver, message, previous_hash)
        }
        self.chain.append(block)
        return block

    def calculate_hash(self, sender, receiver, message, previous_hash):
        block_data = f"{sender}{receiver}{message}{previous_hash}{str(datetime.now())}"
        return hashlib.sha256(block_data.encode('utf-8')).hexdigest()

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            if current_block['hash'] != self.calculate_hash(current_block['sender'], current_block['receiver'], current_block['message'], current_block['previous_hash']):
                return False
        return True



def home(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        obj = User()
        if User.objects.filter(email=email).exists():
           msg="Email already exists"
        else:
            obj.username = username
            obj.email=email
            obj.password = password
            obj.save()
            msg="User Registered successfully"
        
        return render(request, 'register.html',{'message':msg})
        
    return render(request, 'register.html')


def login(request):
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
                  
        user = User.objects.get(email=email, password=password)
        
        
        if(user):
            request.session['username'] = user.username
            request.session['email'] = user.email
            return redirect('dashboard')
        else:
            return render(request,'login.html')
    
    return render(request,'login.html')

def dashboard(request):
    username = request.session.get('username', 'Guest')
    email = request.session.get('email')

    if email:
        data = User.objects.exclude(email=email)
    else:
        data = User.objects.all()  

    return render(request, 'dashboard.html', {'username': username, 'email': email, 'users': data})

def caesar_cipher_encrypt(message, shift):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            encrypted_message += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_message += char  
    return encrypted_message


def caesar_cipher_decrypt(encrypted_message, shift):
    decrypted_message = ""
    for char in encrypted_message:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            decrypted_message += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_message += char  
    return decrypted_message

blockchain = Blockchain() 

def chatarea(request, uid, email):
    username = request.session.get('username', 'Guest')
    receiver_id = uid
    sender_email = email

    receiver = User.objects.get(id=receiver_id)
    sender = User.objects.get(email=sender_email)

    request.session['receiver-name'] = receiver.username
    request.session['receiver-email'] = receiver.email

    messages = Messages.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).order_by('timestamp')

    shift = 3 

    decrypted_messages = []
    for msg in messages:
        decrypted_message = caesar_cipher_decrypt(msg.message, shift)
        decrypted_messages.append(decrypted_message)

    if request.method == "POST":
        message = request.POST['msg']

        encrypted_message = caesar_cipher_encrypt(message, shift)

        message_obj = Messages.objects.create(sender=sender, receiver=receiver, message=encrypted_message)
        message_obj.save()

        messages = Messages.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).order_by('timestamp')

        decrypted_messages = []  
        for msg in messages:
            decrypted_message = caesar_cipher_decrypt(msg.message, shift)
            decrypted_messages.append(decrypted_message)

    messages_and_decrypted = zip(messages, decrypted_messages)

    return render(request, "chatarea.html", {'name': receiver.username, 'messages_and_decrypted': messages_and_decrypted})




    
     