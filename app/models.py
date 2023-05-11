import csv
import datetime
import glob
import os
import shutil
import string
import sys
import random
from django.contrib.auth.hashers import make_password, check_password
from django.db import models, IntegrityError
from django.db.models import Sum, QuerySet
from django.db.models.base import ModelBase
from django.utils.safestring import mark_safe
from django.utils import timezone
from polymorphic.models import PolymorphicModel
from selenium.common import TimeoutException, WebDriverException

from auto import settings


class PaymentsOrder(models.Model):
    class Meta:
        verbose_name = 'Payments order'
        verbose_name_plural = 'Payments order'

    transaction_uuid = models.UUIDField()
    driver_uuid = models.UUIDField()
    driver_name = models.CharField(max_length=30)
    driver_second_name = models.CharField(max_length=30)
    trip_uuid = models.CharField(max_length=255)
    trip_description = models.CharField(max_length=50)
    organization_name = models.CharField(max_length=50)
    organization_nickname = models.CharField(max_length=50)
    transaction_time = models.DateTimeField()
    paid_to_you = models.DecimalField(decimal_places=2, max_digits=10)
    your_earnings = models.DecimalField(decimal_places=2, max_digits=10)
    cash = models.DecimalField(decimal_places=2, max_digits=10)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    fare2 = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    wait_time = models.DecimalField(decimal_places=2, max_digits=10)
    out_of_city = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    ajustment_payment = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)


class GenericPaymentsOrder(ModelBase):
    _registry = {}

    def __new__(cls, name, bases, attrs):

        if attrs.get('vendor_name') is None:
            raise NotImplementedError(f'vendor_name must be implemented in {name}')
        try:
            if not callable(getattr(attrs.get('Scopes'), 'filter_by_driver_external_id')):
                raise NotImplementedError(f'{name}.Scopes.filter_by_driver_external_id() must be callable')
        except AttributeError:
            raise NotImplementedError(f'{name}.Scopes.filter_by_driver_external_id() must be implemented')

        scopes_bases = filter(None, [attrs.get('Scopes')] +
                              [getattr(b, 'Scopes', None) for b in bases])

        attrs['Scopes'] = type('ScopesFor' + name, tuple(scopes_bases), {})

        ScopedQuerySet = type('ScopedQuerySetFor' + name, (QuerySet, attrs['Scopes']), {})
        ScopedManager = type('ScopedManagerFor' + name, (models.Manager, attrs['Scopes']), {
            'use_for_related_fields': True,
            'get_query_set': lambda self: ScopedQuerySet(self.model, using=self._db)
        })

        attrs['objects'] = ScopedManager()

        vendor_name_ = attrs.get('vendor_name')
        if vendor_name_ in cls._registry:
            raise ValueError(f'{vendor_name_} is already registered for {name}')

        new_cls = ModelBase.__new__(cls, name, bases, attrs)
        cls._registry[vendor_name_] = new_cls

        return new_cls

    @classmethod
    def filter_by_driver(cls, vendor, driver_external_id):
        if vendor in cls._registry:
            return cls._registry[vendor].objects.filter_by_driver_external_id(driver_external_id)
        else:
            raise NotImplementedError(f'{vendor} is not registered in {cls}')


class UklonPaymentsOrder(models.Model, metaclass=GenericPaymentsOrder):
    class Meta:
        verbose_name = 'Payments order: Uklon'
        verbose_name_plural = 'Payments order: Uklon'

    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    signal = models.CharField(max_length=8)
    licence_plate = models.CharField(max_length=8)
    total_rides = models.PositiveIntegerField()
    total_distance = models.PositiveIntegerField()
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach_less = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_without_comission = models.DecimalField(decimal_places=2, max_digits=10)
    bonuses = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor_name = 'Uklon'

    class Scopes:
        def filter_by_driver_external_id(self, driver_external_id):
            return self.filter(signal=driver_external_id)

    class Meta:
        unique_together = (('report_from', 'report_to', 'licence_plate', 'signal'))

    def driver_id(self):
        return self.signal

    def report_text(self, name=None, rate=0.35):
        return f'Uklon {name} {self.signal}: Касса({"%.2f" % self.kassa()}) * {"%.0f" % (rate * 100)}% = {"%.2f" % (self.kassa() * rate)} - Наличные(-{"%.2f" % float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate=0.35):
        return -(self.kassa()) * rate

    def vendor(self):
        return 'uklon'

    def total_owner_amount(self, rate=0.35):
        return -self.total_drivers_amount(rate)

    def kassa(self):
        return float(self.total_amount) * 0.81


class NewUklonPaymentsOrder(models.Model, metaclass=GenericPaymentsOrder):
    class Meta:
        verbose_name = 'Payments order: NewUklon'
        verbose_name_plural = 'Payments order: NewUklon'

    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)  # "Водій"
    signal = models.CharField(max_length=8)  # "Позивний"
    total_rides = models.PositiveIntegerField()  # "Кількість поїздок"
    total_distance = models.DecimalField(decimal_places=2, max_digits=10)  # "Пробіг під замовленнями, км"
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)  # "Готівкою, грн"
    total_amount_cach_less = models.DecimalField(decimal_places=2, max_digits=10)  # "На гаманець, грн"
    total_amount_on_card = models.DecimalField(decimal_places=2, max_digits=10)  # "На картку, грн"
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)  # "Всього, грн"
    tips = models.DecimalField(decimal_places=2, max_digits=10)  # "Чайові, грн"
    bonuses = models.DecimalField(decimal_places=2, max_digits=10)  # "Бонуси, грн"
    fares = models.DecimalField(decimal_places=2, max_digits=10)  # "Штрафи, грн"
    comission = models.DecimalField(decimal_places=2, max_digits=10)  # "Комісія Уклон, грн"
    total_amount_without_comission = models.DecimalField(decimal_places=2, max_digits=10)  # " Разом, грн"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor_name = 'NewUklon'

    class Scopes:
        def filter_by_driver_external_id(self, driver_external_id):
            return self.filter(signal=driver_external_id)

    class Meta:
        unique_together = (('report_from', 'report_to', 'full_name', 'signal'))

    def driver_id(self):
        return self.signal

    def report_text(self, name=None, rate=0.35):
        return f'Uklon: Каса {"%.2f" % self.kassa()}  * {"%.0f" % (rate * 100)}% = {"%.2f" % (self.kassa() * rate)} - Готівка(-{"%.2f" % float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate=0.35):
        return -(self.kassa()) * rate

    def vendor(self):
        return 'new_uklon'

    def total_drivers_amount(self, rate=0.35):
        return self.kassa() * (1 - rate) - float(self.total_amount_cach)

    def total_owner_amount(self, rate=0.35):
        return -self.total_drivers_amount(rate)

    def kassa(self, fleet_rate=0.81):
        return float(self.total_amount) * fleet_rate + float(self.tips) + float(self.bonuses)


class BoltPaymentsOrder(models.Model, metaclass=GenericPaymentsOrder):
    class Meta:
        verbose_name = 'Payments order: Bolt'
        verbose_name_plural = 'Payments order: Bolt'

    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_full_name = models.CharField(max_length=24)
    mobile_number = models.CharField(max_length=24)
    range_string = models.CharField(max_length=50)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    cancels_amount = models.DecimalField(decimal_places=2, max_digits=10)
    autorization_payment = models.DecimalField(decimal_places=2, max_digits=10)
    autorization_deduction = models.DecimalField(decimal_places=2, max_digits=10)
    additional_fee = models.DecimalField(decimal_places=2, max_digits=10)
    fee = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    discount_cash_trips = models.DecimalField(decimal_places=2, max_digits=10)
    driver_bonus = models.DecimalField(decimal_places=2, max_digits=10)
    compensation = models.DecimalField(decimal_places=2, max_digits=10)
    refunds = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    weekly_balance = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor_name = 'Bolt'

    class Scopes:
        def filter_by_driver_external_id(self, driver_external_id):
            return self.filter(mobile_number=driver_external_id)

    class Meta:
        unique_together = (('report_from', 'report_to', 'driver_full_name', 'mobile_number'))

    def driver_id(self):
        return self.mobile_number

    def report_text(self, name=None, rate=0.65):
        return f'Bolt: Каса {"%.2f" % self.kassa()} * {"%.0f" % (rate * 100)}% = {"%.2f" % (self.kassa() * rate)} - Готівка({"%.2f" % float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate=0.65):
        res = self.total_cach_less_drivers_amount() * rate + float(self.total_amount_cach)
        return res

    def total_cach_less_drivers_amount(self):
        return float(self.total_amount) + float(self.fee) + float(self.cancels_amount) + float(
            self.driver_bonus) + float(self.autorization_payment) + float(self.tips)

    def vendor(self):
        return 'bolt'

    def kassa(self):
        return (self.total_cach_less_drivers_amount())

    def total_owner_amount(self, rate=0.65):
        return self.total_cach_less_drivers_amount() * (1 - rate) - self.total_drivers_amount(rate)


class UberPaymentsOrder(models.Model, metaclass=GenericPaymentsOrder):
    class Meta:
        verbose_name = 'Payments order: Uber'
        verbose_name_plural = 'Payments order: Uber'

    report_from = models.DateTimeField()
    report_to = models.DateTimeField()
    report_file_name = models.CharField(max_length=255)
    driver_uuid = models.UUIDField()
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    total_clean_amout = models.DecimalField(decimal_places=2, max_digits=10)
    total_amount_cach = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    returns = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor_name = 'Uber'

    class Scopes:
        def filter_by_driver_external_id(self, driver_external_id):
            return self.filter(driver_uuid=driver_external_id)

    class Meta:
        unique_together = (('report_from', 'report_to', 'driver_uuid'))

    def driver_id(self):
        return str(self.driver_uuid)

    def report_text(self, name=None, rate=0.65):
        return f'Uber: Каса {"%.2f" % self.kassa()}  * {"%.0f" % (rate * 100)}% = {"%.2f" % (self.kassa() * rate)} - Готівка({float(self.total_amount_cach)}) = {"%.2f" % self.total_drivers_amount(rate)}'

    def total_drivers_amount(self, rate=0.65):
        return float(self.total_amount) * rate + float(self.total_amount_cach)

    def vendor(self):
        return 'uber'

    def total_owner_amount(self, rate=0.65):
        return float(self.total_amount) * (1 - rate) - self.total_drivers_amount(rate)

    def kassa(self):
        return float(self.total_amount)


class FileNameProcessed(models.Model):
    filename_weekly = models.CharField(max_length=150, unique=True)

    @staticmethod
    def save_filename_to_db(processed_files: list):
        for name in processed_files:
            order = FileNameProcessed(
                filename_weekly=name)

            order.save()


class User(models.Model):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        PARTNER = 'PARTNER', 'Partner'
        DRIVER = 'DRIVER', 'Driver'
        DRIVER_MANAGER = 'DRIVER_MANAGER', 'Driver manager'
        SERVICE_STATION_MANAGER = 'SERVICE_STATION_MANAGER', 'Service station manager'
        SUPPORT_MANAGER = 'SUPPORT_MANAGER', 'Support manager'
        OWNER = 'OWNER', 'Owner'

    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ім'я")
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Прізвище')
    email = models.EmailField(blank=True, max_length=254, verbose_name='Електрона пошта')
    phone_number = models.CharField(blank=True, max_length=13, verbose_name='Номер телефона')
    chat_id = models.CharField(blank=True, max_length=10, verbose_name='Індетифікатор чата')
    created_at = models.DateTimeField(editable=False, auto_now=datetime.datetime.now(), verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Видалено')

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self) -> str:
        return self.full_name()

    def full_name(self):
        return f'{self.name} {self.second_name}'

    @staticmethod
    def get_by_chat_id(chat_id):
        """
        Returns user by chat_id
        :param chat_id: chat_id by which we need to find the user
        :type chat_id: str
        :return: user object or None if a user with such ID does not exist
        """
        try:
            user = User.objects.get(chat_id=chat_id)
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def fill_deleted_at_by_number(number):
        """
        :param number: a number of a user to fill deleted_at
        :type number: str
        """
        user = User.objects.filter(phone_number=number).first()
        user.deleted_at = datetime.datetime.now()
        user.save()
        return user

    @staticmethod
    def name_and_second_name_validator(name) -> str:
        """This func validator for name and second name"""
        if len(name) <= 255:
            return name.title()
        else:
            return None

    @staticmethod
    def email_validator(email) -> str:
        pattern = r"^([a-zA-Z0-9]+\.?[a-zA-Z0-9]+)+@([a-zA-Z0-9]+\.)+[a-zA-Z0-9]{2,4}$"
        if re.match(pattern, email) is not None:
            return email
        else:
            return None

    @staticmethod
    def phone_number_validator(phone_number) -> str:

        pattern = r"^(\+380|380|80|0)+\d{9}$"
        if re.match(pattern, phone_number) is not None:
            if len(phone_number) == 13:
                return phone_number
            elif len(phone_number) == 10:
                valid_phone_number = f'+38{phone_number}'
                return valid_phone_number
            elif len(phone_number) == 12:
                valid_phone_number = f'+{phone_number}'
                return valid_phone_number
            elif len(phone_number) == 11:
                valid_phone_number = f'+3{phone_number}'
                return valid_phone_number
        else:
            return None


class Driver(User):
    ACTIVE = 'Готовий прийняти заказ'
    WITH_CLIENT = 'В дорозі'
    WAIT_FOR_CLIENT = 'Очікую клієнта'
    OFFLINE = 'Не працюю'
    RENT = 'Орендую авто'

    fleet = models.OneToOneField('Fleet', blank=True, null=True, on_delete=models.SET_NULL)
    # partner = models.ManyToManyField('Partner', blank=True)
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.DRIVER)
    driver_status = models.CharField(max_length=35, null=False, default='Offline', verbose_name='Статус водія')

    class Meta:
        verbose_name = 'Водій'
        verbose_name_plural = 'Водії'

    def get_driver_external_id(self, vendor: str) -> str:
        try:
            return Fleets_drivers_vehicles_rate.objects.get(fleet__name=vendor, driver=self,
                                                            deleted_at=None).driver_external_id
        except Fleets_drivers_vehicles_rate.DoesNotExist:
            return ''

    def get_rate(self, vendor: str) -> float:
        try:
            return float(Fleets_drivers_vehicles_rate.objects.get(fleet__name=vendor.capitalize(), driver=self,
                                                                  deleted_at=None).rate)
        except Fleets_drivers_vehicles_rate.DoesNotExist:
            return 0

    def get_kassa(self, vendor: str, week_number: [str, None] = None) -> float:
        driver_external_id = self.get_driver_external_id(vendor)
        st = SeleniumTools(session='', week_number=week_number)
        qset = GenericPaymentsOrder.filter_by_driver(vendor, driver_external_id) \
            .filter(report_from__lte=st.end_of_week(), report_to__gte=st.start_of_week())
        return sum(map(lambda x: x.kassa(), qset))

    def get_dynamic_rate(self, vendor: str, week_number: [str, None] = None, kassa: float = None) -> float:
        if kassa is None:
            kassa = self.get_kassa(vendor, week_number)
        dct = DriverRateLevels.objects.filter(fleet__name=vendor, threshold_value__gte=kassa,
                                              deleted_at=None).aggregate(Sum('rate_delta'))
        rate = self.get_rate(vendor) + float(dct['rate_delta__sum'] if dct['rate_delta__sum'] is not None else 0)
        return max(rate, 0)

    def get_salary(self, vendor: str, week_number: [str, None] = None) -> float:
        try:
            min_fee = float(Fleet.objects.get(name=vendor).min_fee)
        except Fleet.DoesNotExist:
            min_fee = 0
        kassa = self.get_kassa(vendor, week_number)
        rate = self.get_dynamic_rate(vendor, week_number, kassa)
        salary = kassa * rate
        print(kassa, rate, salary, min(salary, max(kassa - min_fee, 0)))
        return min(salary, max(kassa - min_fee, 0))

    def __str__(self) -> str:
        return f'{self.name} {self.second_name}'

    @staticmethod
    def save_driver_status(status):
        driver = Driver.objects.create(driver_status=status)
        driver.save()

    @staticmethod
    def get_by_chat_id(chat_id):
        """
        Returns user by chat_id
        :param chat_id: chat_id by which we need to find the driver
        :type chat_id: str
        :return: driver object or None if a driver with such ID does not exist
        """
        try:
            driver = Driver.objects.get(chat_id=chat_id)
            return driver
        except Driver.DoesNotExist:
            return None


class ParkStatus(models.Model):
    status = models.CharField(max_length=35, null=False, default='Offline', verbose_name='Статус водія в ParkFleet')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status

    class Meta:
        ordering = ['-created_at']


class StatusChange(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Назва статусу')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class RentInformation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    driver_name = models.CharField(max_length=50, blank=True)
    rent_time = models.DurationField(null=True, blank=True, verbose_name='Час оренди')
    rent_distance = models.DecimalField(null=True, blank=True, max_digits=6,
                                        decimal_places=2, verbose_name='Орендована дистанція')
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Інформація по оренді'


class Fleet(PolymorphicModel):
    name = models.CharField(max_length=255)
    fees = models.DecimalField(decimal_places=2, max_digits=3, default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    min_fee = models.DecimalField(decimal_places=2, max_digits=15, default=0)

    class Meta:
        verbose_name = 'Автопарк'
        verbose_name_plural = 'Автопарки'

    def __str__(self) -> str:
        return f'{self.name}'


class Client(User):
    # support_manager_id: ManyToManyField already exists in SupportManager
    # we have to delete this
    support_manager_id = models.ManyToManyField('SupportManager', blank=True)
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.CLIENT)

    class Meta:
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            client = Client.objects.get(chat_id=chat_id)
            return client
        except Client.DoesNotExist:
            return None


# class Partner(User):
#     fleet = models.OneToOneField(Fleet,  blank=True, null=True, on_delete=models.SET_NULL)
#     driver = models.ManyToManyField(Driver,  blank=True)
#     role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.PARTNER)


class DriverManager(User):
    driver_id = models.ManyToManyField(Driver, blank=True, verbose_name='Driver')
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.DRIVER_MANAGER)

    class Meta:
        verbose_name = 'Менеджер водія'
        verbose_name_plural = 'Менеджер водіїв'

    def __str__(self):
        return f'{self.name} {self.second_name}'

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            driver_manager = DriverManager.objects.get(chat_id=chat_id)
            return driver_manager
        except DriverManager.DoesNotExist:
            return None


class ServiceStationManager(User):
    car_id = models.ManyToManyField('Vehicle', blank=True)
    fleet_id = models.ManyToManyField(Fleet, blank=True)
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.SERVICE_STATION_MANAGER)
    service_station = models.OneToOneField('ServiceStation', on_delete=models.RESTRICT, verbose_name='Сервісний центр')

    class Meta:
        verbose_name = 'Менеджер сервісного центра'
        verbose_name_plural = 'Менеджери сервісних центрів'

    def __str__(self):
        return self.full_name()

    @staticmethod
    def save_name_of_service_station(name_of_service_station):
        service = ServiceStationManager.objects.create(name_of_service_station=name_of_service_station)
        service.save()

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            manager = ServiceStationManager.objects.get(chat_id=chat_id)
            return manager
        except ServiceStationManager.DoesNotExist:
            return None


class SupportManager(User):
    client_id = models.ManyToManyField(Client, blank=True)
    driver_id = models.ManyToManyField(Driver, blank=True)
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.SUPPORT_MANAGER)

    class Meta:
        verbose_name = 'Менеджер служби підтримки'
        verbose_name_plural = 'Менеджери служби підтримки'

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            support_manager = SupportManager.objects.get(chat_id=chat_id)
            return support_manager
        except SupportManager.DoesNotExist:
            return None


class Owner(User):
    role = models.CharField(max_length=50, choices=User.Role.choices, default=User.Role.OWNER)

    class Meta:
        verbose_name = 'Власник'
        verbose_name_plural = 'Власники'

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            owner = Owner.objects.get(chat_id=chat_id)
            return owner
        except Owner.DoesNotExist:
            return None


class BoltFleet(Fleet):
    def download_weekly_report(self, week_number=None, driver=True, sleep=5, headless=True):
        return Bolt.download_weekly_report(week_number=week_number, driver=driver, sleep=sleep, headless=headless)

    def download_daily_report(self, day=None, driver=True, sleep=5, headless=True):
        """the same method as weekly report. it gets daily report if day is non None"""
        if day == pendulum.now().start_of('day'):
            return None  # do if you need to get today report
        period = pendulum.now() - day
        if period.in_days() > 30:
            return None  # do if you need to get report elder then 30 days

        return Bolt.download_daily_report(day=day, driver=driver, sleep=sleep, headless=headless)


class NewUklonFleet(Fleet):
    token = models.CharField(max_length=40, default=None, null=True, verbose_name="Код автопарку")

    def download_weekly_report(self, week_number=None, driver=True, sleep=5, headless=True):
        return NewUklon.download_weekly_report(week_number=week_number, driver=driver, sleep=sleep, headless=headless)

    def download_daily_report(self, day=None, driver=True, sleep=5, headless=True):
        return NewUklon.download_daily_report(day=day, driver=driver, sleep=sleep, headless=headless)


class UberFleet(Fleet):
    def download_weekly_report(self, week_number=None, driver=True, sleep=5, headless=True):
        return Uber.download_weekly_report(week_number=week_number, driver=driver, sleep=sleep, headless=headless)

    def download_daily_report(self, day=None, driver=True, sleep=5, headless=True):
        return Uber.download_daily_report(day=day, driver=driver, sleep=sleep, headless=headless)


class UklonFleet(Fleet):
    def download_weekly_report(self, week_number=None, driver=True, sleep=5, headless=True):
        return Uklon.download_weekly_report(week_number=week_number, driver=driver, sleep=sleep, headless=headless)

    def download_daily_report(self, day=None, driver=True, sleep=5, headless=True):
        """the same method as weekly report. it gets daily report if day is non None"""
        return Uklon.download_daily_report(day=day, driver=driver, sleep=sleep, headless=headless)


class Vehicle(models.Model):
    ELECTRO = 'Електро'

    name = models.CharField(max_length=255, verbose_name='Назва')
    model = models.CharField(max_length=50, verbose_name='Модель')
    type = models.CharField(max_length=20, default=ELECTRO, verbose_name='Тип')
    licence_plate = models.CharField(max_length=24, unique=True, verbose_name='Номерний знак')
    vin_code = models.CharField(max_length=17)
    gps_imei = models.CharField(max_length=100, default='')
    car_status = models.CharField(max_length=18, null=False, default="Serviceable", verbose_name='Статус автомобіля')
    driver = models.ForeignKey(Driver, null=True, on_delete=models.RESTRICT, verbose_name='Водій')
    created_at = models.DateTimeField(editable=False, auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Видалено')

    class Meta:
        verbose_name = 'Автомобіль'
        verbose_name_plural = 'Автомобілі'

    def __str__(self) -> str:
        return f'{self.licence_plate}'

    @staticmethod
    def get_by_numberplate(licence_plate):
        try:
            vehicle = Vehicle.objects.get(licence_plate=licence_plate)
            return vehicle
        except Vehicle.DoesNotExist:
            return None

    @staticmethod
    def name_validator(name):
        if len(name) <= 255:
            return name.title()
        else:
            return None

    @staticmethod
    def model_validator(model):
        if len(model) <= 50:
            return model.title()
        else:
            return None

    @staticmethod
    def licence_plate_validator(licence_plate):
        if len(licence_plate) <= 24:
            return licence_plate.upper()
        else:
            return None

    @staticmethod
    def vin_code_validator(vin_code):
        if len(vin_code) <= 17:
            return vin_code.upper()
        else:
            return None

    @staticmethod
    def gps_imei_validator(gps_imei):
        if len(gps_imei) <= 100:
            return gps_imei.upper()
        else:
            return None


class Fleets_drivers_vehicles_rate(models.Model):
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver_external_id = models.CharField(max_length=255)
    rate = models.DecimalField(decimal_places=2, max_digits=3, default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    pay_cash = models.BooleanField(default=False)
    withdraw_money = models.BooleanField(default=False)

    def __str__(self) -> str:
        return ''


class DriverRateLevels(models.Model):
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, verbose_name='Автопарк')
    threshold_value = models.DecimalField(decimal_places=2, max_digits=15, default=0)
    rate_delta = models.DecimalField(decimal_places=2, max_digits=3, default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Рівень рейтингу водія'
        verbose_name_plural = 'Рівень рейтингу водіїв'


class RawGPS(models.Model):
    imei = models.CharField(max_length=100)
    client_ip = models.CharField(max_length=100)
    client_port = models.IntegerField()
    data = models.CharField(max_length=1024)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        verbose_name = 'GPS Raw'
        verbose_name_plural = 'GPS Raw'

    def __str__(self):
        return f'{self.data}'


class GPS(PolymorphicModel):
    date_time = models.DateTimeField(null=False)
    lat = models.DecimalField(decimal_places=6, max_digits=10, default=0)
    lat_zone = models.CharField(max_length=1)
    lon = models.DecimalField(decimal_places=6, max_digits=10, default=0)
    lon_zone = models.CharField(max_length=1)
    speed = models.IntegerField(default=0)
    course = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    def __str__(self):
        return f'{self.lat}{self.lat_zone}:{self.lon}{self.lon_zone}'


class VehicleGPS(GPS):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    raw_data = models.OneToOneField(RawGPS, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'GPS Vehicle'
        verbose_name_plural = 'GPS Vehicle'


class WeeklyReportFile(models.Model):
    organization_name = models.CharField(max_length=20)
    report_file_name = models.CharField(max_length=255, unique=True)
    report_from = models.CharField(max_length=10)
    report_to = models.CharField(max_length=10)
    file = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def transfer_reports_to_db(self, company_name, report_name, from_date, until_date, header, rows):
        self.organization_name = company_name
        self.report_file_name = report_name
        self.report_from = from_date
        self.report_to = until_date
        self.file = (header + rows)
        self.save()

    # Calculates the number of days in the report
    def check_full_data(self, start, end, file_name):
        start = datetime.strptime(start, '%Y-%m-%d').date()
        end = datetime.strptime(end, '%Y-%m-%d').date()
        difference = end - start
        if difference.days == 7:
            return True
        else:
            print(f"{file_name} include {difference.days} days of the week")
            return False

    # Help separate the date from file name
    def convert_file_name(self, split_symbol, name_list):
        converted_list = []
        for string in name_list:
            string = string.split(split_symbol)
            for part in string:
                converted_list.append(part)
        return converted_list

    def save_weekly_reports_to_db(self):

        for file in csv_list:
            rows = []
            try:
                with open(file, 'r') as report:
                    report_name = report.name
                    csvreader = csv.reader(report)
                    header = next(csvreader)
                    for row in csvreader:
                        rows.append(row)

                    # Checks Uber, Uklon and Bolt name in report and report dates; checks the number of days in
                    # the report. If days are less than seven, code issues a warning message and does not
                    # add file to the database.

                    if "payments_driver" in report.name:
                        company_name = "uber"
                        from_date = report.name[0:4] + '-' + report.name[4:6] + '-' + report.name[6:8]
                        until_date = report.name[9:13] + '-' + report.name[13:15] + '-' + report.name[15:17]
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)

                    elif "Income" in report.name:
                        company_name = "uklon"
                        refactor_file_name = report.name.split(" ")
                        refactor_file_name = [refactor_file_name[2], refactor_file_name[4]]
                        refactor_file_name = self.convert_file_name('-', refactor_file_name)
                        refactor_file_name.pop(1)
                        refactor_file_name = self.convert_file_name('_', refactor_file_name)
                        refactor_file_name.pop(0)

                        # Adds a zero to a single digit
                        for date in refactor_file_name:
                            if len(date) == 1:
                                refactor_file_name[refactor_file_name.index(date)] = "0" + date

                        from_date = str(
                            refactor_file_name[2] + '-' + refactor_file_name[0] + '-' + refactor_file_name[1])
                        until_date = str(
                            refactor_file_name[-1] + '-' + refactor_file_name[-3] + '-' + refactor_file_name[-2])
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)

                    elif "Bolt" in report.name:
                        company_name = "bolt"
                        bolt_date_report = rows[1][2]
                        from_date = bolt_date_report[8:18]
                        until_date = bolt_date_report[-10:]
                        if self.check_full_data(start=from_date, end=until_date, file_name=report_name):
                            pass
                        else:
                            continue
                        WeeklyReportFile.transfer_reports_to_db(self=WeeklyReportFile(), company_name=company_name,
                                                                report_name=report_name, from_date=from_date,
                                                                until_date=until_date, header=header, rows=rows)
                    else:
                        continue

            # Catches an error if the filename is already exist in DB
            except django.db.utils.IntegrityError as error:
                print(f"{report_name} already exists in Database")


class UberTransactions(models.Model):
    transaction_uuid = models.UUIDField(unique=True)
    driver_uuid = models.UUIDField()
    driver_name = models.CharField(max_length=50)
    driver_second_name = models.CharField(max_length=50)
    trip_uuid = models.UUIDField()
    trip_description = models.CharField(max_length=50)
    organization_name = models.CharField(max_length=50)
    organization_nickname = models.CharField(max_length=50)
    transaction_time = models.CharField(max_length=50)
    paid_to_you = models.DecimalField(decimal_places=2, max_digits=10)
    your_earnings = models.DecimalField(decimal_places=2, max_digits=10)
    cash = models.DecimalField(decimal_places=2, max_digits=10)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    fare2 = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    wait_time = models.DecimalField(decimal_places=2, max_digits=10)
    transfered_to_bank = models.DecimalField(decimal_places=2, max_digits=10)
    peak_rate = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)

    @staticmethod
    def save_transactions_to_db(file_name):
        with open(file_name, 'r', encoding='utf-8') as fl:
            reader = csv.reader(fl)
            next(reader)
            for row in reader:
                try:
                    transaction = UberTransactions(transaction_uuid=row[0],
                                                   driver_uuid=row[1],
                                                   driver_name=row[2],
                                                   driver_second_name=row[3],
                                                   trip_uuid=row[4],
                                                   trip_description=row[5],
                                                   organization_name=row[6],
                                                   organization_nickname=row[7],
                                                   transaction_time=row[8],
                                                   paid_to_you=row[9],
                                                   your_earnings=row[10],
                                                   cash=row[11],
                                                   fare=row[12],
                                                   tax=row[13],
                                                   fare2=row[14],
                                                   service_tax=row[15],
                                                   wait_time=row[16],
                                                   transfered_to_bank=row[17],
                                                   peak_rate=row[18],
                                                   tips=row[19],
                                                   cancel_payment=row[20])
                    transaction.save()
                except IntegrityError:
                    print(f"{row[0]} transaction is already in DB")


class BoltTransactions(models.Model):
    driver_name = models.CharField(max_length=50)
    driver_number = models.CharField(max_length=13)
    trip_date = models.CharField(max_length=50)
    payment_confirmed = models.CharField(max_length=50)
    boarding = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=30)
    requsted_time = models.CharField(max_length=5)
    fare = models.DecimalField(decimal_places=2, max_digits=10)
    payment_authorization = models.DecimalField(decimal_places=2, max_digits=10)
    service_tax = models.DecimalField(decimal_places=2, max_digits=10)
    cancel_payment = models.DecimalField(decimal_places=2, max_digits=10)
    tips = models.DecimalField(decimal_places=2, max_digits=10)
    order_status = models.CharField(max_length=50)
    car = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=30)

    class Meta:
        unique_together = (('driver_name', 'driver_number', 'trip_date', 'payment_confirmed', 'boarding'))

    @staticmethod
    def save_transactions_to_db(file_name):
        with open(file_name, 'r', encoding='utf-8') as fl:
            reader = csv.reader(fl)
            for row in reader:
                if row[17] == "" and row[0] != "" and row[0] != "Ім'я водія":
                    try:
                        transaction = BoltTransactions(driver_name=row[0],
                                                       driver_number=row[1],
                                                       trip_date=row[2],
                                                       payment_confirmed=row[3],
                                                       boarding=row[4],
                                                       payment_method=row[5],
                                                       requsted_time=row[6],
                                                       fare=row[7],
                                                       payment_authorization=row[8],
                                                       service_tax=row[9],
                                                       cancel_payment=row[10],
                                                       tips=row[11],
                                                       order_status=row[12],
                                                       car=row[13],
                                                       license_plate=row[14])
                        transaction.save()
                    except IntegrityError:
                        print(f"Transaction is already in DB")


class RepairReport(models.Model):
    repair = models.CharField(max_length=255, verbose_name='Фото звіту про ремонт')
    numberplate = models.CharField(max_length=12, unique=True, verbose_name='Номер автомобіля')
    start_of_repair = models.DateTimeField(blank=True, null=False, verbose_name='Початок ремонту')
    end_of_repair = models.DateTimeField(blank=True, null=False, verbose_name='Закінчення ремонту')
    status_of_payment_repair = models.BooleanField(default=False, verbose_name='Статус оплати')  # Paid, Unpaid
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Водій')

    class Meta:
        verbose_name = 'Звіт про ремонт'
        verbose_name_plural = 'Звіти про ремонти'

    def __str__(self):
        return f'{self.numberplate}'


class ServiceStation(models.Model):
    name = models.CharField(max_length=120, verbose_name='Назва')
    owner = models.CharField(max_length=150, verbose_name='Власник')
    lat = models.DecimalField(decimal_places=4, max_digits=10, default=0, verbose_name='Широта')
    lat_zone = models.CharField(max_length=1, verbose_name='Пояс-Широти')
    lon = models.DecimalField(decimal_places=4, max_digits=10, default=0, verbose_name='Довгота')
    lon_zone = models.CharField(max_length=1, verbose_name='Пояс-Довготи')
    description = models.CharField(max_length=255, verbose_name='Опис')

    class Meta:
        verbose_name = "Сервісний Центр"
        verbose_name_plural = 'Сервісні центри'

    def __str__(self):
        return f'{self.name}'


class Comment(models.Model):
    comment = models.TextField(verbose_name='Відгук')
    chat_id = models.CharField(blank=True, max_length=10, verbose_name='ID в чаті')
    processed = models.BooleanField(default=False, verbose_name='Опрацьовано')

    created_at = models.DateTimeField(editable=False, auto_now=datetime.datetime.now(), verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Видалено')

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']


class Order(models.Model):
    WAITING = 'Очікується'
    IN_PROGRESS = 'Виконується'
    COMPLETED = 'Виконаний'
    CANCELED = 'Скасовано клієнтом'
    ON_TIME = 'На певний час'

    from_address = models.CharField(max_length=255)
    latitude = models.CharField(max_length=10)
    longitude = models.CharField(max_length=10)
    to_the_address = models.CharField(max_length=255)
    to_latitude = models.CharField(max_length=10, null=True)
    to_longitude = models.CharField(max_length=10, null=True)
    phone_number = models.CharField(max_length=13)
    chat_id_client = models.CharField(max_length=10)
    message_chat_id = models.CharField(max_length=10, null=True)
    car_delivery_price = models.CharField(max_length=30, null=True, blank=True)
    sum = models.CharField(max_length=30)
    order_time = models.DateTimeField(null=True, blank=True, verbose_name='Час подачі')
    payment_method = models.CharField(max_length=70)
    status_order = models.CharField(max_length=70)
    distance_gps = models.CharField(max_length=10)
    distance_google = models.CharField(max_length=10)
    driver = models.ForeignKey(Driver, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    comment = models.OneToOneField(Comment, null=True, on_delete=models.SET_NULL)

    @staticmethod
    def get_order(chat_id_client, phone, status_order):
        try:
            order = Order.objects.get(chat_id_client=chat_id_client, phone_number=phone, status_order=status_order)
            return order
        except Order.DoesNotExist:
            return None


class Report_of_driver_debt(models.Model):
    driver = models.CharField(max_length=255, verbose_name='Водій')
    image = models.ImageField(upload_to='.', verbose_name='Фото')

    created_at = models.DateTimeField(editable=False, auto_now=datetime.datetime.now(), verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Видалено')

    class Meta:
        verbose_name = 'Звіт заборгованості водія'
        verbose_name_plural = 'Звіти заборгованості водіїв'
        ordering = ['driver']


class Event(models.Model):
    full_name_driver = models.CharField(max_length=255, verbose_name='Водій')
    event = models.CharField(max_length=20, verbose_name='Подія')
    chat_id = models.CharField(blank=True, max_length=10, verbose_name='Індетифікатор чата')
    status_event = models.BooleanField(default=False, verbose_name='Працює')

    created_at = models.DateTimeField(editable=False, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Подія'
        verbose_name_plural = 'Події'


class SubscribeUsers(models.Model):
    email = models.EmailField(max_length=254, verbose_name='Електрона пошта')
    created_at = models.DateTimeField(editable=False, auto_now=True, verbose_name='Створено')

    class Meta:
        verbose_name = 'Підписник'
        verbose_name_plural = 'Підписники'

    @staticmethod
    def get_by_email(email):
        """
        Returns subscriber by email
        :param email: email by which we need to find the subscriber
        :type email: str
        :return: subscriber object or None if a subscriber with such email does not exist
        """
        try:
            subscriber = SubscribeUsers.objects.get(email=email)
            return subscriber
        except SubscribeUsers.DoesNotExist:
            return None


class JobApplication(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=255, verbose_name='Прізвище')
    email = models.EmailField(max_length=255, verbose_name='Електронна пошта')
    password = models.CharField(max_length=12, verbose_name='Пароль Uklon')
    phone_number = models.CharField(max_length=20, verbose_name='Телефон')
    license_expired = models.DateField(blank=True, verbose_name='Термін дії посвідчення')
    driver_license_front = models.ImageField(blank=True, upload_to='job/licenses/front',
                                             verbose_name='Лицьова сторона посвідчення')
    driver_license_back = models.ImageField(blank=True, upload_to='job/licenses/back',
                                            verbose_name='Тильна сторона посвідчення')
    photo = models.ImageField(blank=True, upload_to='job/photo', verbose_name='Фото водія')
    car_documents = models.ImageField(blank=True, upload_to='job/car', default="docs/default_car.jpg",
                                      verbose_name='Фото техпаспорту')
    insurance = models.ImageField(blank=True, upload_to='job/insurance', default="docs/default_insurance.png",
                                  verbose_name='Автоцивілка')
    insurance_expired = models.DateField(default=datetime.date(2023, 12, 15), verbose_name='Термін дії автоцивілки')
    role = models.CharField(max_length=255, verbose_name='Роль')
    status_bolt = models.DateField(null=True, verbose_name='Опрацьована BOLT')
    status_uklon = models.DateField(null=True, verbose_name='Опрацьована Uklon')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачі заявки')

    @staticmethod
    def validate_date(date_str):
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.datetime.today()
            future_date = datetime.datetime(2077, 12, 31)
            if date < today:
                return False
            elif date > future_date:
                return False
            else:
                return True
        except ValueError:
            return False

    def save(self, *args, **kwargs):
        if not self.id:
            self.password = self.generate_password()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_lowercase + string.digits
        password = ''.join(random.choice(chars) for _ in range(length - 2))
        password += random.choice(string.ascii_uppercase)
        password += random.choice(string.digits)
        return ''.join(random.sample(password, len(password)))

    def admin_photo(self):
        return admin_image_preview(self.photo)

    def admin_front(self):
        return admin_image_preview(self.driver_license_front)

    def admin_back(self):
        return admin_image_preview(self.driver_license_back)

    def admin_insurance(self):
        return admin_image_preview(self.insurance)

    def admin_car_document(self):
        return admin_image_preview(self.car_documents)

    admin_back.short_description = 'License back'
    admin_photo.short_description = 'Photo'
    admin_front.short_description = 'License front'
    admin_insurance.short_description = 'Insurance'
    admin_car_document.short_description = 'Car document'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def admin_image_preview(image, default_image=None):
    if image:
        url = image.url
        return mark_safe(f'<a href="{url}"><img src="{url}" width="200" height="150"></a>')
    return None


class UseOfCars(models.Model):
    user_vehicle = models.CharField(max_length=255, verbose_name='Користувач автомобіля')
    chat_id = models.CharField(blank=True, max_length=10, verbose_name='Індетифікатор чата')
    licence_plate = models.CharField(max_length=24, verbose_name='Номерний знак')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата використання авто')
    end_at = models.DateTimeField(null=True, blank=True, verbose_name='Кінець використання авто')

    class Meta:
        verbose_name = 'Користувачі автомобіля'
        verbose_name_plural = 'Користувачі автомобілів'

    def __str__(self):
        return f"{self.user_vehicle}: {self.licence_plate}"


class ParkSettings(models.Model):
    key = models.CharField(max_length=255, verbose_name='Ключ')
    value = models.CharField(max_length=255, verbose_name='Значення')
    description = models.CharField(max_length=255, null=True, verbose_name='Опиc')

    class Meta:
        verbose_name = 'Налаштування автопарка'
        verbose_name_plural = 'Налаштування автопарків'

    def __str__(self):
        return f'{self.value}'

    @staticmethod
    def get_value(key, default=None):
        try:
            setting = ParkSettings.objects.get(key=key)
            return setting.value
        except ParkSettings.DoesNotExist:
            return default


class Service(PolymorphicModel):
    key = models.CharField(max_length=255, verbose_name='Ключ')
    value = models.CharField(max_length=255, verbose_name='Значення')
    description = models.CharField(max_length=255, null=True, verbose_name='Опиc')

    class Meta:
        verbose_name = 'Сервіс'
        verbose_name_plural = 'Сервіси'

    @staticmethod
    def get_value(key, default=None):
        try:
            setting = Service.objects.get(key=key)
            return setting.value
        except Service.DoesNotExist:
            return default


class BoltService(Service):
    @staticmethod
    def get_value(key, default=None):
        try:
            setting = BoltService.objects.get(key=key)
            return setting.value
        except BoltService.DoesNotExist:
            return default


class NewUklonService(Service):
    @staticmethod
    def get_value(key, default=None):
        try:
            setting = NewUklonService.objects.get(key=key)
            return setting.value
        except NewUklonService.DoesNotExist:
            return default


class UaGpsService(Service):
    @staticmethod
    def get_value(key, default=None):
        try:
            setting = UaGpsService.objects.get(key=key)
            return setting.value
        except UaGpsService.DoesNotExist:
            return default


class UberService(Service):
    @staticmethod
    def get_value(key, default=None):
        try:
            setting = UberService.objects.get(key=key)
            return setting.value
        except UberService.DoesNotExist:
            return default
