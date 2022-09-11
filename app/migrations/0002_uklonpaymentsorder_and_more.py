# Generated by Django 4.0.5 on 2022-08-17 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UklonPaymentsOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal', models.CharField(max_length=8)),
                ('licence_plate', models.CharField(max_length=8)),
                ('total_rides', models.PositiveIntegerField()),
                ('total_distance', models.PositiveIntegerField()),
                ('total_amount_cach', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount_cach_less', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount_without_comission', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bonuses', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='ajustment_payment',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='cancel_payment',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='cash',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='fare',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='fare2',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='out_of_city',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='paid_to_you',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='service_tax',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='tax',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='tips',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='transfered_to_bank',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='trip_uuid',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='wait_time',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='paymentsorder',
            name='your_earnings',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]