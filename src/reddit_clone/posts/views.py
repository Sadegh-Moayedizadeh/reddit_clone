from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from .models import Post, Vote
from .serializers import PostSerializer, VoteSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post)

    def perform_create(self, serializer):
        if self.get_queryset():
            raise ValidationError('You can\'t vote for one post twice.')
        serializer.save(
            voter=self.request.user,
            post=Post.objects.get(pk=self.kwargs['pk'])
        )

    def delete(self, request, *args, **kwargs):
        if not self.get_queryset():
            raise ValidationError('There is no vote to delete.')
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
