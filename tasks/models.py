from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def overdue_tasks_count(self):
        """Return the count of overdue tasks for this user"""
        return Task.objects.filter(
            user=self.user,
            status__in=['pending', 'in_progress'],
            deadline__lt=timezone.now()
        ).count()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Check if the task is overdue"""
        if self.deadline and self.status in ['pending', 'in_progress']:
            return timezone.now() > self.deadline
        return False
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.finished:
            self.finished = timezone.now()
        super().save(*args, **kwargs)