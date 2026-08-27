from .cart import Cart


def cart_context(request):
    return {
        "cart_item_count": len(Cart(request)),
    }
