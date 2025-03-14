from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
import requests
from .models import Task, Profile, Category
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TaskForm, CategoryForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a default category
            Category.objects.create(
                name='General',
                description='Default category for tasks',
                user=user
            )
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            
            # Xử lý avatar từ URL
            avatar_url = request.POST.get('avatar_url')
            if avatar_url:
                try:
                    response = requests.get(avatar_url)
                    if response.status_code == 200:
                        # Tạo tên file từ URL
                        file_name = f"avatar_{request.user.username}.png"
                        # Lưu avatar vào profile
                        request.user.profile.avatar.save(
                            file_name,
                            ContentFile(response.content),
                            save=True
                        )
                except Exception as e:
                    messages.error(request, f'Error downloading avatar: {str(e)}')
            else:
                p_form.save()
            
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    tasks = Task.objects.filter(user=request.user)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'overdue_tasks_count': request.user.profile.overdue_tasks_count(),
        'total_tasks_count': tasks.count(),
        'pending_tasks_count': tasks.filter(status='pending').count(),
        'in_progress_tasks_count': tasks.filter(status='in_progress').count(),
        'completed_tasks_count': tasks.filter(status='completed').count()
    }
    return render(request, 'tasks/profile.html', context)

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created')
    overdue_tasks = [task for task in tasks if task.is_overdue()]
    
    context = {
        'tasks': tasks,
        'overdue_tasks': overdue_tasks,
        'overdue_tasks_count': request.user.profile.overdue_tasks_count(),
        'pending_tasks_count': tasks.filter(status='pending').count(),
        'in_progress_tasks_count': tasks.filter(status='in_progress').count(),
        'completed_tasks_count': tasks.filter(status='completed').count()
    }
    return render(request, 'tasks/dashboard.html', context)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        return context

class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        # Only show categories that belong to this user
        context['form'].fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return context

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        # Only show categories that belong to this user
        context['form'].fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return context

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task-list')
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.user

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'tasks/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'tasks/category_form.html'
    success_url = reverse_lazy('category-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overdue_tasks_count'] = self.request.user.profile.overdue_tasks_count()
        return context

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('login')
    return render(request, 'tasks/logout.html')