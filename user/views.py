import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import LoginRegister, UserRegistration
from .helper import send_forget_password_mail
from .models import (
    AddToCart,
    AdminNumber,
    Category,
    ChangePassword,
    Customer,
    MainBanner,
    Product,
    SubBanners1,
    SubBanners2,
    SubCategory,
    Wishlist,
)

# from django.http.response import JsonResponse

# Create your views here.


def logout_view(request):
    logout(request)
    return redirect("user:login")


@csrf_exempt
def login_views(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        password = request.POST.get("pass")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_customer:
                return redirect("/")
        else:
            messages.info(request, "Invalid Credentials")
    return render(request, "web/login.html")


@csrf_exempt
def user_register(request):
    login_form = LoginRegister()
    user_form = UserRegistration()

    if request.method == "POST":
        login_form = LoginRegister(request.POST)

        user_form = UserRegistration(request.POST)

        if login_form.is_valid() and user_form.is_valid():
            user = login_form.save(commit=False)
            user.is_customer = True
            user.save()

            c = user_form.save(commit=False)
            c.user = user
            c.save()

            messages.info(request, "User Registration Successfull")
            return redirect("user:login")
    return render(request, "web/sign-up.html", {"login_form": login_form, "user_form": user_form})


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user_obj = Customer.objects.get(email=email)

        token = str(uuid.uuid4())
        ChangePassword.objects.create(user=user_obj, forgot_password_token=token)
        send_forget_password_mail(user_obj.email, token)

        messages.warning(request, "An email is sent")
        return redirect("user:forgot password")
    context = {}
    return render(request, "web/forgot.html", context)


def change_password(request, token):
    change_password_obj = ChangePassword.objects.get(forgot_password_token=token)

    if change_password_obj.status == True:
        messages.error(request, "Link expired...")
        return redirect("web:forget password")

    if change_password_obj.user:
        customer = Customer.objects.all()
        for customer in customer:
            if change_password_obj.user == customer:
                if change_password_obj.user.email == customer.email:
                    user_id = Customer.objects.filter(email=change_password_obj.user.email).first()

                    if request.method == "POST":
                        new_password = request.POST.get("new_password")
                        confirm_password = request.POST.get("confirm_password")
                        user_id = request.POST.get("user_id")

                        if user_id is None:
                            messages.error(request, "User not found...")
                            return redirect(f"/change password/{token}/")

                        if new_password != confirm_password:
                            messages.error(request, "Your Password and confirm Password dosen't match")
                            return redirect(f"/change password/{token}/")

                        user_obj = Customer.objects.get(email=change_password_obj.user.email)
                        user_obj.set_password(new_password)
                        user_obj.save()
                        ChangePassword.objects.filter(forgot_password_token=token).update(status=True)
                        messages.success(request, "Your password is updated")
                        return redirect("/")
                context = {"manager_id": change_password_obj.user.id}
                return render(request, "web/change-password.html", context)


def index(request):
    mainbanner = MainBanner.objects.last()
    subbanners1 = SubBanners1.objects.last()
    subbanners2 = SubBanners2.objects.last()
    subcategory = SubCategory.objects.all()
    topsave = Product.objects.filter(is_top_save_today=True)
    bestseller = Product.objects.filter(is_best_seller=True).count()
    bestseller1 = Product.objects.filter(is_best_seller=True)[::-1]
    bestseller2 = Product.objects.filter(is_best_seller=True)[::1]
    context = {
        "mainbanner": mainbanner,
        "subbanner1": subbanners1,
        "subbanner2": subbanners2,
        "topsave": topsave,
        "bestseller1": bestseller1,
        "bestseller2": bestseller2,
        "subcategory": subcategory,
    }
    return render(request, "web/index.html", context)


def product(request, id):
    products = Product.objects.get(id=id)
    topsave = Product.objects.all()

    sub = products.subcategory
    print(products.old_price)
    if products.old_price is None:
        pass
    else:
        percentage = ((products.old_price - products.new_price) / products.old_price) * 100
        context = {"products": products, "subcategory": sub, "percentage": percentage, "topsave": topsave}
        return render(request, "web/product-slider.html", context)
    context = {"products": products, "subcategory": sub, "topsave": topsave}
    return render(request, "web/product-slider.html", context)


def shop(request, id):
    category = Category.objects.get(id=id)
    print(category.category)
    products = Product.objects.filter(category=category.id)
    print(category.id)
    print(products)
    context = {"category": category, "products": products}
    return render(request, "web/shop-left-sidebar.html", context)


# @csrf_protect
# @login_required(login_url='login')


def addtowishlist(request, id):
    if request.user.is_authenticated:
        if Customer.objects.get(user=request.user):
            print(request.user)
            product = Product.objects.get(id=id)
            if product:
                cust = Customer.objects.get(user=request.user)
                if Wishlist.objects.filter(user=cust, product=product):
                    return redirect("/")
                else:
                    user = Customer.objects.get(user=request.user)
                    Wishlist.objects.create(user=user, product=product)

                    return redirect("/")
                # return JsonResponse({'status':"Product added successfully"})
            else:
                messages.error(request, "No such product found...")

        else:
            messages.error(request, "Login to continue")
            return redirect("user:login")
    else:
        messages.error(request, "Login to continue")
        return redirect("user:login")


def viewwishlist(request):
    if request.user.is_authenticated:
        if Customer.objects.get(user=request.user):
            my_p = Customer.objects.get(user=request.user)
            wished_item = Wishlist.objects.filter(user=my_p)

            context = {"wished_items": wished_item}
            return render(request, "web/wishlist.html", context)
        else:
            messages.error(request, "pls login to continue")
            return redirect("user:login")
    else:
        print("hello")
        messages.error(request, "pls login to continue")
        return redirect("user:login")


def deletefromwishlist(request, id):
    user = Customer.objects.get(user=request.user)
    product = Wishlist.objects.get(user=user, id=id)

    product.delete()

    return redirect("/")

    # return JsonResponse({'status':"Product added successfully"})


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

    # try:
    #     cart = Cart.objects.get(cart_id=_cart_id(request))
    # except Cart.DoesNotExist:
    #     cart = Cart.objects.create(cart_id=_cart_id(request))
    # cart.save()


@csrf_exempt
def addtocart(request):
    id = request.POST["id"]
    count = request.POST["count"]
    # if request.user.is_authenticated:
    # print(request.user)
    # if Customer.objects.get(user = request.user):
    product = Product.objects.get(id=id)
    new_price = product.new_price
    if product:
        # my_p = Customer.objects.get(user=request.user)
        if AddToCart.objects.filter(Cart_id=_cart_id(request), product=product):
            # messages.warning(request,"product is already in cart")
            data = {"cartcount": count}
            return JsonResponse(data)
        else:
            # my_p = Customer.objects.get(user=request.user)
            AddToCart.objects.create(Cart_id=_cart_id(request), product=product, total=new_price)
            # messages.warning(request,"Product added successfully")
            new_count = int(count) + 1
            data = {"cartcount": new_count}
            return JsonResponse(data)
    else:
        # messages.error(request,"product is not available")
        data = {"cartcount": count}
        return JsonResponse(data)

    # else:
    #     messages.warning(request,"Login to Continue")
    #     return redirect('user:login')
    # else:
    #         messages.warning(request,"Login to Continue")
    #         return redirect('user:login')


def addQuantity(request):
    quantity = request.GET["quantity"]
    print(quantity, "%" * 20)
    # my_p = Customer.objects.get(user=request.user)
    id = request.GET["id"]
    print(id)
    cart_obj = AddToCart.objects.get(id=id, Cart_id=request.session.session_key)

    print("########")

    new_quantity = int(quantity) + 1
    product_total = float(new_quantity) * float(cart_obj.product.new_price)
    print(cart_obj.product.new_price)

    print("*****")

    cart_obj.total = product_total
    print(cart_obj.total)

    cart_obj.save()
    AddToCart.objects.filter(id=id).update(quantity=new_quantity, total=product_total)
    gtotal = AddToCart.objects.filter(Cart_id=request.session.session_key).aggregate(Sum("total"))
    print(gtotal, "#" * 10)
    data = {"total": cart_obj.total, "gtotal": gtotal["total__sum"]}
    return JsonResponse(data)


def lessQuantity(request):
    quantity = request.GET["quantity"]

    # my_p = Customer.objects.get(user=request.user)

    id = request.GET["id"]
    cart_obj = AddToCart.objects.get(id=id, Cart_id=request.session.session_key)
    new_quantity = int(quantity) - 1
    product_total = float(new_quantity) * float(cart_obj.product.new_price)
    cart_obj.total = product_total
    cart_obj.save()
    AddToCart.objects.filter(id=id).update(quantity=new_quantity, total=product_total)
    gtotal = AddToCart.objects.filter(Cart_id=request.session.session_key).aggregate(Sum("total"))
    print(gtotal, "#" * 10)
    data = {"total": cart_obj.total, "gtotal": gtotal["total__sum"]}
    return JsonResponse(data)


def viewcart(request):
    # if request.user.is_authenticated:
    # if request.user:

    # my_p = Customer.objects.get(user=request.user)
    sub_total = AddToCart.objects.filter(Cart_id=request.session.session_key).aggregate(Sum("total"))
    carted_item = AddToCart.objects.filter(Cart_id=request.session.session_key)

    context = {"carted_item": carted_item, "sub_total": sub_total}
    return render(request, "web/cart.html", context)
    #     else:
    #         messages.warning(request,"Login to Continue")
    #         return redirect('user:login')
    # else:
    #         messages.warning(request,"Login to Continue")
    #         return redirect('user:login')


@csrf_exempt
def whatsappFun(request):
    messagestring = ""
    grandtotal = 0

    cart_obj = AddToCart.objects.filter(Cart_id=request.session.session_key)
    grandtotal = AddToCart.objects.filter(Cart_id=request.session.session_key).aggregate(Sum("total"))
    gtotal = grandtotal["total__sum"]
    data = []

    if request.user is not None:
        print(request.user, "#" * 10)
        number_obj = AdminNumber.objects.all().last()
        number = number_obj.phone_number
    else:
        number = 0

    try:
        messagestring = "https://wa.me/+91" + number + "?text=Table Name :" + "Items" + "%0a------Order Details------"
        print(messagestring)

        for i in cart_obj:
            data1 = {
                "name": i.product.product,
                "quantity": i.quantity,
                "price": i.product.old_price,
                "sub_total": i.total,
            }
            data.append(data1)

        for i in data:
            messagestring += (
                "%0aProduct-Name:"
                + str(i["name"])
                + "%0aQuantity:"
                + str(i["quantity"])
                + "%0aUnit-Price:"
                + str(i["price"])
                + "%0aTotal :"
                + str(i["sub_total"])
                + "%0a-----------------------------"
            )

        messagestring += (
            "%0a-----------------------------%0a\
            Grand Total :"
            + str(gtotal)

        )

    except Exception as e:
        pass

    data = {"link": messagestring}

    return JsonResponse(data)


# @csrf_exempt
# def whatsappFun(request):
#     message_string = ""
#     grand_total = 0

#     cart_obj = AddToCart.objects.filter(Cart_id=request.session.session_key)
#     grand_total = AddToCart.objects.filter(Cart_id=request.session.session_key).aggregate(Sum("total"))
#     gtotal = grand_total["total__sum"]
#     data = []

#     if request.user is not None:
#         print(request.user, "#" * 10)
#         number_obj = AdminNumber.objects.all().last()
#         number = number_obj.phone_number
#     else:
#         number = 0

#     try:
#         message_string = (
#             "https://wa.me/+91"
#             + number
#             + "?text=Table Name :"
#             + "Items"
#             + "%0a------Order Details------"
#         )
#         print(message_string)

#         for i in cart_obj:
#             data1 = {
#                 "name": i.product.product,
#                 "quantity": i.quantity,
#                 "price": i.product.old_price,
#                 "sub_total": i.total,
#             }
#             data.append(data1)

#         for i in data:
#             message_string += (
#                 f"\nProduct-Name: {i['name']}"
#                 f"\nQuantity: {i['quantity']}"
#                 f"\nUnit-Price: {i['price']}"
#                 f"\nTotal: {i['sub_total']}"
#                 "\n-----------------------------"
#             )

#         message_string += (
#             "\n-----------------------------\n"
#             f"Grand Total: {gtotal}"
#             "\n-----------------------------"
#         )

#     except Exception as e:
#         pass

#     data = {
#         "link": message_string,
#     }

#     return JsonResponse(data)


def deletefromcart(request, id):
    cart_obj = AddToCart.objects.filter(Cart_id=request.session.session_key)
    product = AddToCart.objects.get(Cart_id=request.session.session_key, id=id)
    product.delete()

    return redirect("/cart")


def checkout(request):
    return render(request, "web/checkout.html")
    # if request.user.is_authenticated:
    #     if Customer.objects.get(user = request.user):

    #         my_p = Customer.objects.get(user=request.user)
    #         carted_item = AddToCart.objects.filter(user=my_p)

    #         context= {
    #             'carted_item':carted_item
    #         }
    #         return render(request,'web/cart.html',context)
    #     else:
    #         messages.warning(request,"Login to Continue")
    #         return redirect('user:login')
    # else:
    #         messages.warning(request,"Login to Continue")
    #         return redirect('user:login')


def about_us(request):
    context = {}
    return render(request, "web/about.html", context)


def blog_detail(request):
    context = {}
    return render(request, "web/blog-detail.html", context)


def blog_grid(request):
    context = {}
    return render(request, "web/blog-grid.html", context)


def blog_list(request):
    context = {}
    return render(request, "web/blog-list.html", context)


def coming_soon(request):
    context = {}
    return render(request, "web/coming-soon.html", context)


def compare(request):
    context = {}
    return render(request, "web/compare.html", context)


def contact_us(request):
    context = {}
    return render(request, "web/contact-us.html", context)


def faq(request):
    context = {}
    return render(request, "web/faq.html", context)


# def forgot(request):
#     context = {}
#     return render(request, "web/forgot.html", context)


def index_2(request):
    context = {}
    return render(request, "web/index-2.html", context)


def index_3(request):
    context = {}
    return render(request, "web/index-3.html", context)


def index_4(request):
    context = {}
    return render(request, "web/index-4.html", context)


def index_5(request):
    context = {}
    return render(request, "web/index-5.html", context)


def index_6(request):
    context = {}
    return render(request, "web/index-6.html", context)


def index_7(request):
    context = {}
    return render(request, "web/index-7.html", context)


def index_8(request):
    context = {}
    return render(request, "web/index-8.html", context)


def index_9(request):
    context = {}
    return render(request, "web/index-9.html", context)


def order_success(request):
    context = {}
    return render(request, "web/order-success.html", context)


def order_tracking(request):
    context = {}
    return render(request, "web/order-tracking.html", context)


def otp(request):
    context = {}
    return render(request, "web/otp.html", context)


def product_4_image(request):
    context = {}
    return render(request, "web/product-4-image.html", context)


def product_bottom_thumbnail(request):
    context = {}
    return render(request, "web/product-bottom-thumbnail.html", context)


def product_bundle(request):
    context = {}
    return render(request, "web/product-bundle.html", context)


def product_left_thumbnail(request):
    context = {}
    return render(request, "web/product-left-thumbnail.html", context)


def product_right_thumbnail(request):
    context = {}
    return render(request, "web/product-right-thumbnail.html", context)


def product_sticky(request):
    context = {}
    return render(request, "web/product-sticky.html", context)


def search(request):
    # query = request.GET.get('search')
    # print(search)
    # allprod = []
    # catsubcats = SubCategory.objects.values('subcategory',id)
    # cats = {item['subcategory'] for item in catsubcats}
    # for cat in cats:
    #     prodtemp=Product.objects.filter(subcategory=cat)
    kw = request.GET.get("search")
    print(kw)
    if kw:
        if Product.objects.filter(Q(product__icontains=kw) or Q(description__icontains=kw)):
            results = Product.objects.filter(Q(product__icontains=kw) | Q(description__icontains=kw))
            print(kw)
            print(results)
            context = {"results": results, "status": 1}
            return render(request, "web/search.html", context)
        else:
            messages.error(request, "No matching products found...")
            context = {"status": 0}
            return render(request, "web/search.html", context)
    else:
        return render(request, "web/search.html")


def seller_become(request):
    context = {}
    return render(request, "web/seller-become.html", context)


def seller_dashboard(request):
    context = {}
    return render(request, "web/seller-dashboard.html", context)


def seller_detail_2(request):
    context = {}
    return render(request, "web/seller-detail-2.html", context)


def seller_detail(request):
    context = {}
    return render(request, "web/seller-detail.html", context)


def seller_grid_2(request):
    context = {}
    return render(request, "web/seller-grid-2.html", context)


def seller_grid(request):
    context = {}
    return render(request, "web/seller-grid.html", context)


def shop_banner(request):
    context = {}
    return render(request, "web/shop-banner.html", context)


def shop_category_slider(request):
    context = {}
    return render(request, "web/shop-category-slider.html", context)


def shop_category(request, id):
    subcategory = SubCategory.objects.filter(id=id)
    context = {"subcategory": subcategory}
    return render(request, "web/shop-category.html", context)


def shop_list(request):
    context = {}
    return render(request, "web/shop-list.html", context)


def shop_right_sidebar(request):
    context = {}
    return render(request, "web/shop-right-sidebar.html", context)


def shop_top_filter(request):
    context = {}
    return render(request, "web/shop-top-filter.html", context)


def sign_up(request):
    context = {}
    return render(request, "web/sign-up.html", context)


def user_dashboard(request):
    context = {}
    return render(request, "web/user-dashboard.html", context)


def error_404(request):
    context = {}
    return render(request, "web/404.html", context)


# def couponApplied(reqest):
#     code = reqest.GET['couponcode']
#     code_obj = Coupon.objects.get(code)
#     if code_obj.is_expired:
#         messages.warning('coupon expired')
