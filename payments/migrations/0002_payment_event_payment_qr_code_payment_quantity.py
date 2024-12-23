# Generated by Django 5.1.1 on 2024-11-02 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_event_user'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='events.event'),
        ),
        migrations.AddField(
            model_name='payment',
            name='qr_code',
            field=models.ImageField(blank=True, upload_to='qr_codes/'),
        ),
        migrations.AddField(
            model_name='payment',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
