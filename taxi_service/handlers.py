import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict

from taxi_service.forms import SubscriberForm, MainOrderForm, CommentForm
from taxi_service.utils import active_vehicles_gps, update_order_sum_or_status, order_confirm


class PostRequestHandler:
    def handle_order_form(self, request):
        order_form = MainOrderForm(request.POST)
        if order_form.is_valid():
            save_form = order_form.save(
                payment=request.POST.get('payment_method'),
                on_time=request.POST.get('order_time')
            )
            order_dict = model_to_dict(save_form)
            json_data = json.dumps(order_dict, cls=DjangoJSONEncoder)
            return JsonResponse({'data': json_data}, safe=False)
        else:
            return JsonResponse(order_form.errors, status=400)

    def handle_subscribe_form(self, request):
        sub_form = SubscriberForm(request.POST)
        if sub_form.is_valid():
            sub_form.save()
        else:
            return JsonResponse(sub_form.errors, status=400)

    def handle_comment_form(self, request):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse(
                {'success': False, 'errors': 'Щось пішло не так!'})

    def handle_update_order(self, request):
        id_order = request.POST.get('idOrder')
        sum_value = request.POST.get('sum')
        action = request.POST.get('action')

        update_order_sum_or_status(id_order, sum_value, action)

        return JsonResponse({}, status=200)

    def handle_unknown_action(self, request):
        return JsonResponse({}, status=400)


class GetRequestHandler:
    def handle_active_vehicles_locations(self, request):
        active_vehicle_locations = active_vehicles_gps()
        json_data = JsonResponse({'data': active_vehicle_locations}, safe=False)
        response = HttpResponse(json_data, content_type='application/json')
        return response

    def handle_order_confirm(self, request):
        id_order = request.GET.get('id_order')
        driver = order_confirm(id_order)
        json_data = JsonResponse({'data': driver}, safe=False)
        response = HttpResponse(json_data, content_type='application/json')
        return response

    def handle_unknown_action(self, request):
        return JsonResponse({}, status=400)