from django.conf import settings
from django.db import models
from django.urls import reverse


class Apartment(models.Model):
    """Квартира в каталоге."""

    class District(models.TextChoices):
        KHAMOVNIKI = 'khamovniki', 'Хамовники'
        ARBAT = 'arbat', 'Арбат'
        PRESNYA = 'presnya', 'Пресня'
        SOKOL = 'sokol', 'Сокол'
        TVERSKOY = 'tverskoy', 'Тверской'
        SOKOLINAYA = 'sokolinaya', 'Соколиная гора'
        OTHER = 'other', 'Другой'

    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание', blank=True)
    address = models.CharField('Адрес', max_length=300)
    district = models.CharField(
        'Район', max_length=30,
        choices=District.choices,
        default=District.OTHER,
    )
    price = models.DecimalField('Цена, ₽', max_digits=12, decimal_places=0)
    area = models.DecimalField('Площадь, м²', max_digits=6, decimal_places=1)
    rooms = models.PositiveSmallIntegerField('Комнат')
    floor = models.PositiveSmallIntegerField('Этаж')
    floors_total = models.PositiveSmallIntegerField('Этажей в доме')
    year_built = models.PositiveSmallIntegerField('Год постройки', null=True, blank=True)
    image = models.ImageField('Фото', upload_to='apartments/', blank=True, null=True)
    agent_name = models.CharField('Агент', max_length=100, default='Анна Петрова')
    agent_phone = models.CharField('Телефон агента', max_length=20, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Квартира'
        verbose_name_plural = 'Квартиры'
        indexes = [
            models.Index(fields=['district', 'price']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.title} — {self.price:,.0f} ₽'.replace(',', ' ')

    def get_absolute_url(self):
        return reverse('apartment_detail', args=[self.pk])


class Favorite(models.Model):
    """Избранное пользователя (по session_key, без обязательной авторизации)."""
    session_key = models.CharField('Ключ сессии', max_length=40, db_index=True)
    apartment = models.ForeignKey(
        Apartment, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Квартира',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_key', 'apartment')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.session_key[:8]}... → {self.apartment}'


class ViewingRequest(models.Model):
    """Заявка на просмотр квартиры."""
    apartment = models.ForeignKey(
        Apartment, on_delete=models.CASCADE,
        related_name='requests', verbose_name='Квартира',
    )
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    preferred_date = models.DateTimeField('Желаемая дата', null=True, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField('Обработана', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка на просмотр'
        verbose_name_plural = 'Заявки на просмотр'

    def __str__(self):
        return f'{self.name} — {self.apartment.title}'