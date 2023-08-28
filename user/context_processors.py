from user.models import AddToCart, Category, HeaderFlash, Product, SubCategory


def main_context(request):
    headerflash = HeaderFlash.objects.last()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    products = Product.objects.all()

    if request.user.is_anonymous:
        return {
            "headerflash": headerflash,
            "categories": categories,
            "subcategories": subcategories,
            "products": products,
            "status": 0,
        }
    else:
        return {
            "headerflash": headerflash,
            "categories": categories,
            "subcategories": subcategories,
            "products": products,
            "status": 1,
        }


def cart_count(request):
    cart = AddToCart.objects.filter(Cart_id=request.session.session_key).count()
    print(cart, "@" * 10)
    return {"count": cart}
