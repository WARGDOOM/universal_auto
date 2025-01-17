# Generated by Django 4.1 on 2023-07-20 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_carefficiency_partner_ubertrips_partner_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UberSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=255, verbose_name='Ідентифікатор сесії')),
                ('cook_session', models.CharField(max_length=255, verbose_name='Ідентифікатор cookie')),
                ('uber_uuid', models.UUIDField(verbose_name='Код автопарку Uber')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.partner', verbose_name='Партнер')),
            ],
        ),
    ]
