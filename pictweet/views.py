from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DeleteView
from django.views.generic.edit import UpdateView, FormMixin, CreateView
from django.views.generic.detail import DetailView
from .models import Tweet, Comment
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegisterForm, CommentForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


# def tweet_list(request):
#     tweets = Tweet.objects.all().order_by('-created_at')  # 投稿を作成日時の降順で取得
#     return render(request, 'tweet_list.html', {'tweets': tweets})


class TweetListView(ListView):
    model = Tweet  # 使用するモデルを指定
    template_name = 'tweet_list.html'  # 使用するテンプレートを指定
    context_object_name = 'tweets'  # テンプレート内でリストにアクセスする際の変数名
    ordering = ['-created_at']  # 投稿を作成日時の降順で並び替え

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')  # URLから検索クエリを取得
        if query:
            queryset = queryset.filter(text__icontains=query)  # 'content'フィールドでフィルタリング
        return queryset


class TweetCreateView(CreateView):
    model = Tweet
    template_name = 'tweet_create.html'
    fields = ['text', 'image']
    # template_name属性を省略すると、デフォルトで"tweet_form.html"を探します。
    success_url = reverse_lazy('tweet_list')  # ''はホームページのURLパターン名

    def form_valid(self, form):
        form.instance.author = self.request.user  # 現在ログインしているユーザーを作者として設定
        return super().form_valid(form)


class TweetDeleteView(DeleteView):
    model = Tweet
    success_url = reverse_lazy('tweet_list')  # 削除成功後のリダイレクト先

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # 現在表示しているオブジェクトを取得
        self.object.delete()  # オブジェクトを削除

        # ここでリダイレクト先を指定します。例えばホームページにリダイレクトする場合：
        return HttpResponseRedirect(self.get_success_url())


class TweetUpdateView(UpdateView):
    model = Tweet
    fields = ['text', 'image']
    template_name = 'tweet_edit.html'  # 編集ページのテンプレート
    success_url = reverse_lazy('tweet_list')  # 更新成功後のリダイレクト先


class TweetDetailView(FormMixin, DetailView):
    model = Tweet
    template_name = 'tweet_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('tweet_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()  # コメントフォームをコンテキストに追加
        # 現在のツイートに対するコメントを取得
        comments = Comment.objects.filter(tweet=self.object).order_by('-created_at')
        context['comments'] = comments
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # 現在表示しているTweetオブジェクトを取得
        form = self.get_form()  # form_classに基づいたフォームのインスタンスを取得
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # フォームのデータが妥当であれば、ここで処理を行う
        # 例: コメントオブジェクトを保存する
        comment = form.save(commit=False)
        comment.tweet = self.object  # コメントにTweetを関連付ける
        comment.author = self.request.user  # コメントの作者を現在のユーザーに設定
        comment.save()

        return HttpResponseRedirect(self.get_success_url())  # 成功URLへリダイレクト

    def form_invalid(self, form):
        # フォームのデータが無効な場合、フォームのエラーを表示する
        return render(self.request, self.template_name, {'form': form, 'object': self.object})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('tweet_list')  # ユーザーダッシュボードやホームページへリダイレクト
    else:
        form = UserRegisterForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tweet_list')  # ログイン後のリダイレクト先
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('tweet_list')  # ログアウト後にリダイレクトするURL名


def user_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    tweets = Tweet.objects.filter(author=profile_user).order_by('-created_at')
    return render(request, 'profile_user.html', {'profile_user': profile_user, 'tweets': tweets})


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        # コメントが紐付くTweetの取得
        form.instance.tweet = Tweet.objects.get(pk=self.kwargs['tweet_id'])
        form.instance.author = self.request.user
        return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tweet_detail', kwargs={'pk': self.object.tweet.pk})
