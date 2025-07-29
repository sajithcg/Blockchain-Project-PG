from django.db import models
from django.utils import timezone
import hashlib
import json
from datetime import datetime


class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    
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

    
class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(default="")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    blockchain_id = models.CharField(max_length=256, blank=True, null=True)  

    def save(self, *args, **kwargs):
        blockchain = Blockchain()
        last_block = blockchain.get_last_block()
        previous_hash = last_block['hash'] if last_block else '0'

        blockchain.create_block(self.sender.username, self.receiver.username, self.message, previous_hash)
        self.blockchain_id = blockchain.get_last_block()['hash']
        super().save(*args, **kwargs)

