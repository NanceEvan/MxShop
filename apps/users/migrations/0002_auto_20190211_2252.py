# Generated by Django 2.1.5 on 2019-02-11 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verifycode',
            options={'verbose_name': '短信验证码', 'verbose_name_plural': '短信验证码'},
        ),
    ]
