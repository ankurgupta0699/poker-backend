from rest_framework import serializers

from accounts import (
    models as accounts_models,
    serializers as account_serializers
)
from pokerboards import (
    constant as pokerboard_constants,
    models as pokerboard_models
)


class PokerboardSerializer(serializers.ModelSerializer):
    manager = account_serializers.UserReadSerializer(read_only=True)

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = ['id', 'name', 'manager', 'estimate_type',
                  'deck', 'duration', 'is_deleted']
        extra_kwargs = {
            'manager': {'read_only': True},
            'is_deleted': {'write_only': True}
        }

    def create(self, validated_data):
        pokerboard = super().create(validated_data)
        pokerboard_models.UserPokerboard.objects.create(
            pokerboard=pokerboard, user=validated_data['manager'], role=[pokerboard_constants.PLAYER])
        return pokerboard


class UserPokerboardSerializer(serializers.ModelSerializer):
    user = account_serializers.UserReadSerializer(read_only=True)
    pokerboard = PokerboardSerializer(read_only=True)

    class Meta:
        model = pokerboard_models.UserPokerboard
        fields = ['id', 'user', 'role', 'pokerboard', 'is_deleted']
        extra_kwargs = {
            'is_deleted': {'write_only': True}
        }


class PokerInvitationsSerializer(serializers.ModelSerializer):
    pokerboard = PokerboardSerializer(read_only=True)
    verification = account_serializers.VerificationSerializer(read_only=True)
    user = account_serializers.UserReadSerializer(read_only=True)

    class Meta:
        model = pokerboard_models.PokerboardInvitation
        fields = ['id', 'user', 'status', 'role', 'pokerboard', 'verification']


class UserJiraTokenSerializer(serializers.ModelSerializer):
    user = account_serializers.UserReadSerializer(read_only=True)

    def create(self, validated_data):
        instance = accounts_models.UserJiraToken.objects.create(user=self.context["request"].user, jira_token=validated_data.get('jira_token'))
        return instance
    
    class Meta:
        model = accounts_models.UserJiraToken
        fields = ['id', 'user', 'jira_token']


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = pokerboard_models.Ticket
        fields = ['id', 'ticket_id', 'pokerboard', 'order', 'final_estimate', 'status']


class TicketListSerializer(serializers.ListSerializer):
    child = TicketSerializer()
    
    def create(self, validated_data):
        tickets = [pokerboard_models.Ticket(**item) for item in validated_data]
        return pokerboard_models.Ticket.objects.bulk_create(tickets)
