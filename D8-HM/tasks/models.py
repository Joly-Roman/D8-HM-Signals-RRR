from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import *
from collections import Counter


class Category(models.Model):
    slug = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    todos_count = models.PositiveIntegerField(default=0)
    priority_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class TodoItem(models.Model):
    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "Высокий приоритет"),
        (PRIORITY_MEDIUM, "Средний приоритет"),
        (PRIORITY_LOW, "Низкий приоритет"),
    ]

    description = models.TextField("описание")
    is_completed = models.BooleanField("выполнено", default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tasks"
    )
    priority = models.IntegerField(
        "Приоритет", choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    category = models.ManyToManyField(Category, blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задача'

    def __str__(self):
        return self.description.lower()

    def get_absolute_url(self):
        return reverse("tasks:details", args=[self.pk])

# Сигнал сохраняет предыдущее значение поля Приоритет
@receiver(pre_save, sender=TodoItem)
def pre_update_model(sender, **kwargs):
    # check if the updated fields exist and if you're not creating a new object
    if not kwargs['update_fields'] and kwargs['instance'].pk:
        # Save it so it can be used in post_save
        kwargs['instance'].old = TodoItem.objects.get(pk=kwargs['instance'].pk)

# Сигнал,проверяющий изменение поля Приоритет
@receiver(post_save, sender=TodoItem)
def update_model(sender, **kwargs):
    instance = kwargs['instance']

    # Add updated_fields, from old instance, so the method logic remains unchanged
    if not kwargs['update_fields'] and hasattr(instance, 'old'):
        kwargs['update_fields'] = []
        if (instance.priority !=
                instance.old.priority):
            kwargs['update_fields'].append('priority')

    try:
        if 'priority' in kwargs['update_fields']:
            print(kwargs['update_fields'], ' is changed')
            category = instance.category.get()
            category.priority_count += 1
            category.save()
    except TypeError:
        pass


# Сигнал при удалении задачи
@receiver(pre_delete, sender=TodoItem)
def reduce_if_item_is_deleted(instance, **kwargs):
    category = instance.category.get()
    if category.todos_count > 0:
        category.todos_count -= 1
    if category.priority_count > 0:
        category.priority_count -= 1
    category.save()



