from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from django.views import View
from .models import *
from .forms import *
from django.views.generic.edit import UpdateView,DeleteView

# Create your views here.
class PostListView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        # logged_in_user = request.user
        # posts = Post.objects.filter(
        #     author__profile__followers__in=[logged_in_user]
        # ).order_by('-created_on')
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm()

        context = {
            'post_list':posts,
            'form':form,
        }
        return render(request,'social/post_list.html',context)

    def post(self,request,*args,**kwargs):
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST,request.FILES)
        files=request.FILES.getlist('image')

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

            for f in files:
                img = Image(image=f)
                img.save()
                new_post.image.add(img)
            
            new_post.save()

        context = {
            'post_list':posts,
            'form':form,
        }
        return render(request,'social/post_list.html',context)
    
class PostDetailView(LoginRequiredMixin, View):
    def get(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post':post,
            'form':form,
            'comments':comments,
        }
        return render(request,'social/post_detail.html',context)

    def post(self,request,pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
        
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post':post,
            'form':form,
            'comments':comments,
        }
        return render(request,'social/post_detail.html',context)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail',kwargs = {'pk':pk})
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'            

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail',kwargs = {'pk':pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class ProfileView(View):
    def get(self,request,pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')

        friends = profile.friends.all()

        if len(friends) ==0:
            is_adding=False

        for friend in friends:
            if friend == request.user:
                is_adding = True
                break
            else:
                is_adding = False

        number_of_friends = len(friends)

        context = {
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_friends': number_of_friends,
            'is_adding':is_adding,
        }

        return render(request,'social/profile.html',context)

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name','bio','birth_date','location','picture']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile',kwargs = {'pk':pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFriend(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.friends.add(request.user)

        return redirect('profile',pk=profile.pk)

class RemoveFriend(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.friends.remove(request.user)

        return redirect('profile',pk=profile.pk)

class AddLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        
        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
        
        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)

class Dislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        
        if is_like:
            post.likes.remove(request.user)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)
        
        if is_dislike:
            post.dislikes.remove(request.user)
        
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)

class UserSearch(View):
    def get(self,request,*args,**kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )

        context = {
            'profile_list':profile_list,
        }

        return render(request,'social/search.html',context)

class ListFriends(View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        friends = profile.friends.all()

        context = {
            'profile':profile,
            'friends':friends
        }

        return render(request,'social/friends_list.html',context)

class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }

        return render(request, 'social/inbox.html', context)

class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form
        }

        return render(request, 'social/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')
        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)
        except:
            messages.error(request,'Invalid username')
            return redirect('create-thread')

class ThreadView(View):
    def get(self,request,pk,*args,**kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread':thread,
            'form':form,
            'message_list':message_list
        }

        return render(request,'social/thread.html',context)

class CreateMessage(View):
    def post(self,request,pk,*args,**kwargs):
        form = MessageForm(request.POST,request.FILES)
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user=request.user
            message.receiver_user = receiver
            message.save()

        # message = MessageModel(
        #     thread = thread,
        #     sender_user = request.user,
        #     receiver_user = receiver,
        #     body = request.POST.get('message')
        # )

        #message.save()
        return redirect('thread',pk=pk)

        


