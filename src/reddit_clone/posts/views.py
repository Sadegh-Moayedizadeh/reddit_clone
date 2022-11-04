from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Post, Vote
from .serializers import PostSerializer, VoteSerializer
from rest_framework.exceptions import ValidationError


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class VoteCreate(generics.CreateAPIView):
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
