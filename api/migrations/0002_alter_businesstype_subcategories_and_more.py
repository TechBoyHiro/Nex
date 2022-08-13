# Generated by Django 4.0.4 on 2022-08-13 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesstype',
            name='subcategories',
            field=models.ManyToManyField(blank=True, null=True, to='api.subcategory'),
        ),
        migrations.AlterField(
            model_name='group',
            name='followers',
            field=models.ManyToManyField(blank=True, null=True, to='api.shop'),
        ),
        migrations.AlterField(
            model_name='group',
            name='subcategories',
            field=models.ManyToManyField(blank=True, null=True, to='api.subcategory'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='gigs',
            field=models.ManyToManyField(blank=True, null=True, to='api.gig'),
        ),
    ]
