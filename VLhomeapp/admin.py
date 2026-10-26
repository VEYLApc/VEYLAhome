from django.contrib import admin
from .models import Restaurant, Menu, Dish, Order, OrderItem

admin.site.site_header = "VL Gold boshqaruv paneli"
admin.site.site_title = "VL Gold"
admin.site.index_title = "Boshqaruv"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "address")


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "menu", "price", "is_available")
    list_filter = ("menu", "is_available")
    search_fields = ("name",)
    list_editable = ("price", "is_available")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("subtotal",)

    @admin.display(description="Summa")
    def subtotal(self, obj):
        return obj.subtotal if obj.pk else "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "customer_name", "table_number",
        "status", "total", "created_at",
    )
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("id", "customer_name")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [OrderItemInline]
    actions = ["mark_preparing", "mark_ready", "mark_delivered", "mark_cancelled"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("items")

    @admin.display(description="Jami (so'm)")
    def total(self, obj):
        return f"{obj.total_price:,.0f}".replace(",", " ")

    @admin.action(description="Tanlanganlarni: Tayyorlanmoqda")
    def mark_preparing(self, request, queryset):
        queryset.update(status=Order.Status.PREPARING)

    @admin.action(description="Tanlanganlarni: Tayyor")
    def mark_ready(self, request, queryset):
        queryset.update(status=Order.Status.READY)

    @admin.action(description="Tanlanganlarni: Yetkazildi")
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)

    @admin.action(description="Tanlanganlarni: Bekor qilish")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Order.Status.CANCELLED)