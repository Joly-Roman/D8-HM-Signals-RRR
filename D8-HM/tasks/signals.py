from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from tasks.models import TodoItem, Category
from collections import Counter


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):


    for cat in instance.category.all():
        slug = cat.slug

        count = cat.todos_count
        for task in TodoItem.objects.all():
            count += task.category.filter(slug=slug).count()

        Category.objects.filter(slug=slug).update(todos_count=count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):


    cat_counter = Counter()
    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.slug] += 1

    for slug, new_count in cat_counter.items():
        Category.objects.filter(slug=slug).update(todos_count=new_count)