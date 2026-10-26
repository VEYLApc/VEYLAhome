from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Menu, Dish, Order, OrderItem

STATUS_STEPS = [
    Order.Status.PENDING,
    Order.Status.PREPARING,
    Order.Status.READY,
    Order.Status.DELIVERED,
]


def menu_list(request):
    menus = Menu.objects.prefetch_related("dishes").all()
    return render(request, "vlhomeapp/menu.html", {"menus": menus})


def dish_list(request):
    menus = Menu.objects.all()
    dishes = Dish.objects.filter(is_available=True).select_related("menu")

    selected = request.GET.get("menu")
    selected_id = int(selected) if selected and selected.isdigit() else None
    if selected_id:
        dishes = dishes.filter(menu_id=selected_id)

    return render(request, "vlhomeapp/dishes.html", {
        "menus": menus,
        "dishes": dishes,
        "selected_id": selected_id,
    })


def order_create(request):
    dishes = (
        Dish.objects.filter(is_available=True)
        .select_related("menu")
        .order_by("menu__name", "name")
    )

    if request.method == "POST":
        name = request.POST.get("customer_name", "").strip()
        table = request.POST.get("table_number", "").strip()

        items = []
        for dish in dishes:
            try:
                qty = int(request.POST.get(f"qty_{dish.id}", "0"))
            except ValueError:
                qty = 0
            if qty > 0:
                items.append((dish, min(qty, 50)))

        if not name:
            messages.error(request, "Iltimos, ismingizni kiriting.")
        elif not items:
            messages.error(request, "Kamida bitta taom tanlang.")
        else:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=request.user if request.user.is_authenticated else None,
                    customer_name=name,
                    table_number=int(table) if table.isdigit() else None,
                )
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, dish=d, quantity=q, price=d.price)
                    for d, q in items
                ])
            return redirect("order_detail", pk=order.pk)

    return render(request, "vlhomeapp/order_create.html", {"dishes": dishes})


def order_lookup(request):
    number = request.GET.get("number", "").strip().lstrip("#")
    if number:
        if number.isdigit() and Order.objects.filter(pk=int(number)).exists():
            return redirect("order_detail", pk=int(number))
        messages.error(request, "Bunday raqamli buyurtma topilmadi.")
    return render(request, "vlhomeapp/order_lookup.html")


def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__dish"), pk=pk
    )

    steps = []
    if order.status != Order.Status.CANCELLED:
        current = STATUS_STEPS.index(order.status)
        for i, step in enumerate(STATUS_STEPS):
            state = "done" if i < current else "current" if i == current else "todo"
            steps.append({"label": step.label, "state": state})

    return render(request, "vlhomeapp/order_detail.html", {
        "order": order,
        "steps": steps,
    })


# test: git tekshiruvi