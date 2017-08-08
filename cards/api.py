import datetime
import dateutil.parser
import rest_framework.exceptions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from cards.tasks import ApiException, search_card
from .models import TyreVendor, TsMark, TsModel, Request
from .serializers import TyreVendorReadSerializer, TsMarkReadSerializer, TsModelReadSerializer, RequestReadSerializer, \
    CardSearchSerializer


class TyreVendorReadView(ListAPIView):
    queryset = TyreVendor.objects.all()

    def list(self, request, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        if request.GET.get('q'):
            queryset = queryset.filter(name__istartswith=request.GET.get('q'))
        serializer = TyreVendorReadSerializer(queryset, many=True)
        return Response(serializer.data)


class TsMarkReadView(ListAPIView):
    queryset = TsMark.objects.all()

    def list(self, request, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        if request.GET.get('q'):
            queryset = queryset.filter(name__istartswith=request.GET.get('q'))
        serializer = TsMarkReadSerializer(queryset, many=True)
        return Response(serializer.data)


class TsModelReadView(ListAPIView):
    queryset = TsModel.objects.all()

    def list(self, request, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        if request.GET.get('q') and request.GET.get('mark'):
            queryset = queryset.filter(name__istartswith=request.GET.get('q'),
                                       mark__name__iexact=request.GET.get('mark'))
        else:
            queryset = queryset.none()
        serializer = TsModelReadSerializer(queryset, many=True)
        return Response(serializer.data)


class RequestReadView(RetrieveAPIView):
    serializer_class = RequestReadSerializer

    def get_queryset(self):
        return Request.objects.filter(author_id=self.request.user.pk)


class CardSearchView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, diagcard_num):
        try:
            task_kwargs = {'diagcard_num': diagcard_num, 'user_id': self.request.user.pk}
            task_result = search_card.apply(kwargs=task_kwargs)
            result = task_result.get()

            if not result:
                raise rest_framework.exceptions.NotFound(detail='Карта не найдена')

            if result.get('expire_date'):
                if isinstance(result.get('expire_date'), datetime.datetime) \
                        or isinstance(result.get('expire_date'), datetime.date):
                    result['expire_date'] = result.get('expire_date').strftime('%d.%m.%Y')
                else:
                    result['expire_date'] = dateutil.parser.parse(result.get('expire_date')).strftime('%d.%m.%Y')
            if result.get('date_done'):
                if isinstance(result.get('date_done'), datetime.datetime) \
                        or isinstance(result.get('date_done'), datetime.date):
                    result['date_done'] = result.get('date_done').strftime('%d.%m.%Y')
                else:
                    result['date_done'] = dateutil.parser.parse(result.get('date_done')).strftime('%d.%m.%Y')
            result['ts_mark_model'] = "{} {}".format(result.get('ts_mark'), result.get('ts_model'))

            return result

        except ApiException:
            rest_framework.exceptions.APIException(detail=str('Ошибка доступа к ЕАИСТО'))

    def post(self, request, format=None):

        serializer = CardSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        result = self.get_object(serializer.validated_data['diagcard_num'])
        return Response(result)

