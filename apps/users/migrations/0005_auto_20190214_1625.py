# Generated by Django 2.1.5 on 2019-02-14 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190214_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifycode',
            name='email',
            field=models.EmailField(default='', max_length=100, verbose_name='邮箱'),
        ),
    ]
