# Generated by Django 4.0.4 on 2022-08-15 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_businesstype_subcategories_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='GroupFiles/')),
                ('description', models.TextField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.group')),
            ],
        ),
        migrations.DeleteModel(
            name='FreeFile',
        ),
    ]