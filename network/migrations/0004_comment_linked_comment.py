# Generated by Django 3.2 on 2021-06-14 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_alter_like_liked_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='linked_comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='network.comment'),
        ),
    ]