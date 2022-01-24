from django.db.models.query_utils import Q
from rest_framework import generics, status, viewsets
from rest_framework.response import Response

from accounts import models as accounts_models, serializers
from pokerboards import (
    constant as poker_constants,
    models as pokerboard_models,
    serializers as pokerboard_serializers
)


class PokerboardViewsets(viewsets.ModelViewSet):
    serializer_class = pokerboard_serializers.PokerboardSerializer

    def get_queryset(self):
        queryset = pokerboard_models.Pokerboard.objects.filter(manager=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        queryset = pokerboard_models.UserPokerboard.objects.filter(pokerboard__id=instance.id)
        for obj in queryset:
            obj.delete()
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPokerboardView(generics.ListAPIView, generics.DestroyAPIView): 
    serializer_class = pokerboard_serializers.UserPokerboardSerializer

    def get_queryset(self):
        pokerboard_id = self.request.query_params.get('pokerboard_id')
        if pokerboard_id:
            queryset = pokerboard_models.UserPokerboard.objects.filter(pokerboard__id=pokerboard_id)
            return queryset

        queryset = pokerboard_models.UserPokerboard.objects.filter(Q(user__id=self.request.user.id) & Q(pokerboard__is_deleted=False))
        return queryset


    def destroy(self, request, *args, **kwargs):
        user_pokerboard_obj = self.get_object()
        user_pokerboard_obj.delete()
        return Response({'message': poker_constants.USER_REMOVED})


class PokerInvitationsView(viewsets.ModelViewSet):
    serializer_class = pokerboard_serializers.PokerInvitationsSerializer

    def get_queryset(self):
        queryset = pokerboard_models.PokerboardInvitation.objects.filter(
            Q(pokerboard__manager=self.request.user) |
            Q(verification__email=self.request.user.email) |
            Q(user=self.request.user)
        )
        return queryset


class UserJiraTokenView(viewsets.ModelViewSet):
    serializer_class = pokerboard_serializers.UserJiraTokenSerializer

    def get_queryset(self):
        return accounts_models.UserJiraToken.objects.filter(user__id=self.request.user.id)


class JiraTicketViewsets(viewsets.ModelViewSet):

    def get_queryset(self):
        print('hey....',pokerboard_models.Ticket.objects.get(ticket_id=1003))
        pokerboard = self.request.query_params.get('pokerboard')
        return pokerboard_models.Ticket.objects.filter(Q(pokerboard__manager__id=self.request.user.id) & Q(pokerboard__id=pokerboard))

    def get_serializer_class(self):
        if self.action == 'create':
            return pokerboard_serializers.TicketListSerializer
        return pokerboard_serializers.TicketSerializer

    def destroy(self, request, *args, **kwargs):
        print('hey..........')
        jira_ticket_id = self.request.query_params.get('ticket')
        instance = pokerboard_models.Ticket.objects.get(ticket_id=jira_ticket_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
