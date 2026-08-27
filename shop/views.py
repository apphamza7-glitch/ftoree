from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Category, Product
from .cart import Cart


def home(request):
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True,
    )[:8]
    new_products = Product.objects.filter(
        is_active=True,
    ).order_by("-created_at")[:8]

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "new_products": new_products,
    }

    return render(request, "shop/home.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True)

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query)
            | Q(brand__icontains=query)
        )

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    sort = request.GET.get("sort")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    else:
        products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.filter(is_active=True),
        "query": query,
        "selected_category": category_slug,
        "sort": sort,
    }

    return render(request, "shop/product_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True,
    ).order_by("-created_at")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "page_obj": page_obj,
        "categories": Category.objects.filter(is_active=True),
    }

    return render(request, "shop/category_detail.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    Product.objects.filter(pk=product.pk).update(views=product.views + 1)

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
    ).exclude(pk=product.pk)[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "shop/product_detail.html", context)


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart.add(product=product, quantity=quantity)
    messages.success(request, f'"{product.name}" was added to your cart.')

    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        cart.remove(product)
        messages.success(request, f'"{product.name}" was removed from your cart.')
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, "Cart updated.")

    return redirect("shop:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'"{product.name}" was removed from your cart.')

    return redirect("shop:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "shop/cart_detail.html", {"cart": cart})
