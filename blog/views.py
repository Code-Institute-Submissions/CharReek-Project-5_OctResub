from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import UpdateView, DeleteView
from .models import Post, Image
from .forms import CommentForm
from django.contrib.auth.decorators import login_required


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog/blog_post.html'
    paginate_by = 6


class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')

        return render(
            request,
            "blog/post_detail.html",

            {
                "post": post,
                "comments": comments,
                "commented": False,
                "comment_form": CommentForm,

            },
        )

    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "blog/post_detail.html",

            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": CommentForm,

            },
        )


class EditPostDetail(UserPassesTestMixin, UpdateView):
    """model to delete blog post"""
    model = Post
    fields = ['content', 'excerpt', 'title']
    template_name = 'blog/post_edit.html'

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('post_detail', kwargs={'slug': slug})

    def test_func(self):
        """check user is author or throw 403"""
        return self.request.user == self.get_object().author


class DeletePostDetail(UserPassesTestMixin, DeleteView):
    """model to delete blog post"""
    model = Post
    template_name = 'blog/post_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        """check user is author or throw 403"""
        return self.request.user == self.get_object().author
