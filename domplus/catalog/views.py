from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.db.models import Q, Min, Max

from .models import Apartment, Favorite, ViewingRequest
from .forms import ApartmentFilterForm, ViewingRequestForm


# ============ СЕССИЯ (для избранного без логина) ============
def _ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# ============ ФИЛЬТРАЦИЯ (общая логика) ============
def _filter_apartments(request):
    qs = Apartment.objects.filter(is_active=True)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    district = request.GET.get('district')
    area_min = request.GET.get('area_min')
    floor_min = request.GET.get('floor_min')
    floor_max = request.GET.get('floor_max')

    if price_min:
        qs = qs.filter(price__gte=price_min)
    if price_max:
        qs = qs.filter(price__lte=price_max)
    if district:
        qs = qs.filter(district=district)
    if area_min:
        qs = qs.filter(area__gte=area_min)
    if floor_min:
        qs = qs.filter(floor__gte=floor_min)
    if floor_max:
        qs = qs.filter(floor__lte=floor_max)

    return qs


def _favorites_ids(request):
    session_key = request.session.session_key
    if not session_key:
        return []
    return list(
        Favorite.objects.filter(session_key=session_key)
        .values_list('apartment_id', flat=True)
    )


# ============ КАТАЛОГ ============
def catalog(request):
    session_key = _ensure_session(request)
    qs = _filter_apartments(request)

    paginator = Paginator(qs, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'apartments': page_obj.object_list,
        'filter_form': ApartmentFilterForm(request.GET or None),
        'favorites': _favorites_ids(request),
        'favorites_count': Favorite.objects.filter(session_key=session_key).count(),
        'total_count': qs.count(),
        'is_htmx': request.headers.get('HX-Request') == 'true',
    }

    # HTMX-запрос — возвращаем ТОЛЬКО список карточек
    if context['is_htmx']:
        return render(request, 'catalog/_apartment_list.html', context)

    return render(request, 'catalog/catalog.html', context)


# ============ КАРТОЧКА КВАРТИРЫ ============
def apartment_detail(request, pk):
    session_key = _ensure_session(request)
    apartment = get_object_or_404(Apartment, pk=pk, is_active=True)

    context = {
        'apartment': apartment,
        'form': ViewingRequestForm(),
        'is_favorite': Favorite.objects.filter(
            session_key=session_key, apartment=apartment
        ).exists(),
        'favorites_count': Favorite.objects.filter(session_key=session_key).count(),
    }
    return render(request, 'catalog/apartment_detail.html', context)


# ============ ИЗБРАННОЕ (HTMX) ============
@require_POST
def toggle_favorite(request, pk):
    session_key = _ensure_session(request)
    apartment = get_object_or_404(Apartment, pk=pk)

    fav, created = Favorite.objects.get_or_create(
        session_key=session_key, apartment=apartment
    )
    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    count = Favorite.objects.filter(session_key=session_key).count()

    return render(request, 'catalog/_favorite_button.html', {
        'apartment': apartment,
        'is_favorite': is_favorite,
        'favorites_count': count,
    })

# ============ СПИСОК ИЗБРАННОГО ============
def favorites_list(request):
    session_key = _ensure_session(request)
    favorites = Favorite.objects.filter(session_key=session_key).select_related('apartment')
    apartments = [f.apartment for f in favorites]

    context = {
        'apartments': apartments,
        'favorites': [a.pk for a in apartments],
        'favorites_count': len(apartments),
    }
    return render(request, 'catalog/favorites.html', context)


# ============ ЗАЯВКА НА ПРОСМОТР (HTMX) ============
@require_POST
def submit_request(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    form = ViewingRequestForm(request.POST)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.apartment = apartment
        obj.save()
        return render(request, 'catalog/_request_success.html', {'apartment': apartment})

    return render(request, 'catalog/_request_form.html', {
        'form': form, 'apartment': apartment
    })