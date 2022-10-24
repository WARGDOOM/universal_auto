# Generated by Django 4.0.5 on 2022-10-15 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileNameProcessed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename_weekly', models.CharField(max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fleet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('fees', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UberTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_uuid', models.UUIDField(unique=True)),
                ('driver_uuid', models.UUIDField()),
                ('driver_name', models.CharField(max_length=50)),
                ('driver_second_name', models.CharField(max_length=50)),
                ('trip_uuid', models.UUIDField()),
                ('trip_description', models.CharField(max_length=50)),
                ('organization_name', models.CharField(max_length=50)),
                ('organization_nickname', models.CharField(max_length=50)),
                ('transaction_time', models.CharField(max_length=50)),
                ('paid_to_you', models.DecimalField(decimal_places=2, max_digits=10)),
                ('your_earnings', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cash', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fare', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fare2', models.DecimalField(decimal_places=2, max_digits=10)),
                ('service_tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('wait_time', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transfered_to_bank', models.DecimalField(decimal_places=2, max_digits=10)),
                ('peak_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tips', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cancel_payment', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('licence_plate', models.CharField(max_length=24)),
                ('vin_code', models.CharField(max_length=17)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='boltpaymentsorder',
            name='mobile_number',
            field=models.CharField(max_length=24),
        ),
        migrations.CreateModel(
            name='Fleets_drivers_vehicles_rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_external_id', models.CharField(max_length=255)),
                ('rate', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.driver')),
                ('fleet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.fleet')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='BoltTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(max_length=50)),
                ('driver_number', models.CharField(max_length=13)),
                ('trip_date', models.CharField(max_length=50)),
                ('payment_confirmed', models.CharField(max_length=50)),
                ('boarding', models.CharField(max_length=255)),
                ('payment_method', models.CharField(max_length=30)),
                ('requsted_time', models.CharField(max_length=5)),
                ('fare', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_authorization', models.DecimalField(decimal_places=2, max_digits=10)),
                ('service_tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cancel_payment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tips', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_status', models.CharField(max_length=50)),
                ('car', models.CharField(max_length=50)),
                ('license_plate', models.CharField(max_length=30)),
            ],
            options={
                'unique_together': {('driver_name', 'driver_number', 'trip_date', 'payment_confirmed', 'boarding')},
            },
        ),
    ]