from django.shortcuts import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Topic, Post

###############
# TOPIC VIEWS #
###############


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'forum/index.html'
    context_object_name = 'topics'


class TopicDetailView(DetailView):
    model = Topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(topic=self.kwargs.get('pk'))
        return context


class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    fields = ['title', 'description']

    def form_valid(self, form):
        return super().form_valid(form)

##############
# POST VIEWS #
##############


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['body']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.topic = Topic.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'forum:topic-detail', kwargs={'pk': self.object.topic.id})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'forum/post_update.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_success_url(self):
        return reverse(
            'forum:topic-detail', kwargs={'pk': self.object.topic.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_success_url(self):
        return reverse(
            'forum:topic-detail', kwargs={'pk': self.object.topic.id})
