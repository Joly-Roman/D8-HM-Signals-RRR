from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from tasks.models import TodoItem, Category


# Использую pk_set, в котором сохраняются pk изменившихся моделей
@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model,pk_set, **kwargs):
    if action == "post_add":
        print('post_add')
        print(pk_set)
        for category in instance.category.all():
            if category.pk in pk_set:
                category.todos_count += 1
                category.save()


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model,pk_set, **kwargs):
    if action == 'post_remove':
        print('post_remove')
        print(pk_set)
        for category in Category.objects.all():
            if category.pk in pk_set:
                if category.todos_count > 0:
                    category.todos_count -= 1
                if category.priority_count > 0:
                    category.priority_count -= 1
                category.save()



