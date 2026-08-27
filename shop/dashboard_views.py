from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator

from .models import Category, Product, ProductTag
from .dashboard_forms import CategoryForm, ProductForm, ProductImageFormSet, ProductTagForm
from .decorators import staff_required


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get("next") or "dashboard:home"
            return redirect(next_url)

        messages.error(request, "Invalid credentials or insufficient permissions.")

    return render(request, "dashboard/login.html")


def dashboard_logout(request):
    logout(request)
    return redirect("dashboard:login")


@staff_required
def dashboard_home(request):
    context = {
        "total_products": Product.objects.count(),
        "total_categories": Category.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
        "featured_products": Product.objects.filter(is_featured=True).count(),
        "out_of_stock": Product.objects.filter(unlimited_stock=False, stock=0).count(),
        "recent_products": Product.objects.order_by("-created_at")[:6],
    }
    return render(request, "dashboard/home.html", context)


# ===== Categories =====

@staff_required
def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count("products")
    ).order_by("sort_order", "name")

    return render(request, "dashboard/category_list.html", {"categories": categories})


@staff_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm()

    return render(request, "dashboard/category_form.html", {"form": form, "is_edit": False})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "dashboard/category_form.html",
        {"form": form, "is_edit": True, "category": category},
    )


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("dashboard:category_list")

    return render(request, "dashboard/category_confirm_delete.html", {"category": category})


# ===== Products =====

@staff_required
def product_list(request):
    products = Product.objects.select_related("category").order_by("-created_at")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query) | Q(brand__icontains=query)
        )

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_id,
    }
    return render(request, "dashboard/product_list.html", context)


@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
            messages.success(request, "Product created successfully.")
            return redirect("dashboard:product_list")
        formset = ProductImageFormSet(request.POST, request.FILES)
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(
        request,
        "dashboard/product_form.html",
        {"form": form, "formset": formset, "is_edit": False},
    )


@staff_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Product updated successfully.")
            return redirect("dashboard:product_list")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(
        request,
        "dashboard/product_form.html",
        {"form": form, "formset": formset, "is_edit": True, "product": product},
    )


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("dashboard:product_list")

    return render(request, "dashboard/product_confirm_delete.html", {"product": product})


# ===== Product Tags =====

@staff_required
def tag_list(request):
    tags = ProductTag.objects.annotate(product_count=Count("products")).order_by("name")
    return render(request, "dashboard/tag_list.html", {"tags": tags})


@staff_required
def tag_create(request):
    if request.method == "POST":
        form = ProductTagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created successfully.")
            return redirect("dashboard:tag_list")
    else:
        form = ProductTagForm()

    return render(request, "dashboard/tag_form.html", {"form": form, "is_edit": False})


@staff_required
def tag_delete(request, pk):
    tag = get_object_or_404(ProductTag, pk=pk)

    if request.method == "POST":
        tag.delete()
        messages.success(request, "Tag deleted.")
        return redirect("dashboard:tag_list")

    return render(request, "dashboard/tag_confirm_delete.html", {"tag": tag})
