from datetime import datetime, timedelta

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework import status
from .serializers import RoomOrderSerializer
from rest_framework.permissions import IsAuthenticated

from .models import RoomOrder

# - order a room
#     + post method
#     + both admin and staff can order
#     + must order before use 30mins
#     + can't order if there is an order in that room at that time
#     + after order, the StaffListOrder automatically add the orderer to db
#     + can't order if time is in the past
# - edit an order
#     + put method
#     + only admin and the ordered can edit
#     + must edit before use 30mins
#     + can't edit if there is an order in that room at that time
#     + can't edit if the order is the order is done
# - delete an order
#     + delete method
#     + only admin and the ordered can delete
#     + can't edit if the order is the order is done
# - get orders(expand...)
# - StaffListOrder will be developed later

# Create your views here.
class OrderTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # use 'for' loop if number of rooms is large
        room_101_list = list(RoomOrder.objects.all().filter(room_name='101').filter(start_time__lte=datetime.now()).filter(end_time__gte=datetime.now()))
        room_201_list = list(RoomOrder.objects.all().filter(room_name='201').filter(start_time__lte=datetime.now()).filter(end_time__gte=datetime.now()))
        room_301_list = list(RoomOrder.objects.all().filter(room_name='301').filter(start_time__lte=datetime.now()).filter(end_time__gte=datetime.now()))

        room_condition = []
        room_condition.append(len(room_101_list))
        room_condition.append(len(room_201_list))
        room_condition.append(len(room_301_list))

        return JsonResponse({
            'room_condition': room_condition
        }, status = status.HTTP_200_OK)

    def post(self,request):
        mutable_data = {}
        mutable_data['room_name'] = request.data['room_name']
        mutable_data['start_time'] = request.data['start_time']
        mutable_data['end_time'] = request.data['end_time']
        mutable_data['user'] = request.user.id
        
        serializer = RoomOrderSerializer(data=mutable_data)
        if serializer.is_valid():
            now = datetime.now()
            start = datetime.strptime(mutable_data['start_time'], "%Y-%m-%d %H:%M")
            end = datetime.strptime(mutable_data['end_time'], "%Y-%m-%d %H:%M")

            if end <= start:
                return JsonResponse({
                    'message': 'End time must be after start time'
                }, status = status.HTTP_400_BAD_REQUEST)

            delta = start - now
            if (delta.total_seconds() / 60) < 15:
                return JsonResponse({
                    'message': 'You must order the room before use 15 minutes'
                }, status = status.HTTP_400_BAD_REQUEST)

            list_of_RoomOrder = RoomOrder.objects.all().filter(room_name=mutable_data['room_name']).filter(start_time__gt=datetime.now())
            serializer_tocheck = RoomOrderSerializer(list_of_RoomOrder, many=True)
            #filter time here...
            duplicate_flag = 0

            for roomorder in serializer_tocheck.data:
                model_temp = dict(roomorder)   
                model_start_time = datetime.strptime(model_temp['start_time'][:16].replace('T', ' '), '%Y-%m-%d %H:%M')
                model_end_time = datetime.strptime(model_temp['end_time'][:16].replace('T', ' '), '%Y-%m-%d %H:%M')

                if (start >= model_start_time and start <= model_end_time) or (end >= model_start_time and end <= model_end_time) or (start <= model_start_time  and end >= model_end_time):
                    duplicate_flag = 1
                    break

            if duplicate_flag == 1:
                return JsonResponse({
                    'message': 'There is also an order at this time in this room!'
                }, status = status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()

                return JsonResponse({
                    'message': f"Ordered successfully for room {request.data['room_name']} from {request.data['start_time']} to {request.data['end_time']}",
                    'full_name': request.user.full_name
                }, status = status.HTTP_200_OK)
        else:
            return JsonResponse({
                'message': 'Something wrong!'
            }, status = status.HTTP_400_BAD_REQUEST)

class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        my_orders = RoomOrder.objects.all().select_related()
        my_orders_user = []
        for o in my_orders:
            my_orders_user.append(o.user.full_name)

        serializer = RoomOrderSerializer(my_orders, many=True)

        return JsonResponse({
           'order_list': serializer.data,
           'order_list_user': my_orders_user
        }, status = status.HTTP_200_OK)