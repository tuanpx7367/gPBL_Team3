from django.db import models
from authen.models import User

# Create your models here.
class RoomOrder(models.Model):
    room_name = models.CharField(max_length=255)
    # orderer_email = models.EmailField(max_length=255)
    # orderer_full_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class StaffOrder(models.Model):
    roomOrder_id = models.ForeignKey(RoomOrder, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.BooleanField(default=False)