from django.contrib import admin

from user.models import (
    AddToCart,
    AdminNumber,  # SubBanners1,; SubBanners2,
    Cart,
    Category,
    ChangePassword,
    Customer,
    HeaderFlash,
    Login,
    MainBanner,
    Product,
    SubCategory,
    Wishlist,
)

# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(SubCategory)


class ProductAdmin(admin.ModelAdmin):
    exclude = ("is_top_save_today", "is_best_seller", "sub_image1", "sub_image2", "sub_image3")


admin.site.register(Product, ProductAdmin)
admin.site.register(MainBanner)
# admin.site.register(SubBanners1)
# admin.site.register(SubBanners2)
admin.site.register(HeaderFlash)
admin.site.register(Login)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(AddToCart)
admin.site.register(ChangePassword)
# admin.site.register(Coupon)
# admin.site.register(CouponApplied)
admin.site.register(AdminNumber)
