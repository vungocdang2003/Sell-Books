def count_gio_hang(cart):
    total_amount = 0
    total_quantity = 0
    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity']*c['price']
    return {
        "total_amount": total_amount,
        "total_quantity": total_quantity
    }