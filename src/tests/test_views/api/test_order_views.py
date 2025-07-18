from django.urls import reverse
from django.utils.lorem_ipsum import words

from products.models import Order, create_bulk_product


def test_order_list_view( 
            authenticated_client,
            user,
            products) -> None:
    product = products.create(
        product_name="Hello World",
    )
    Order.objects.create(user=user, product=product)

    response = authenticated_client.get(reverse("user_order"))

    assert response.status_code == 200
    assert all(x["user"]["username"] == user.username for x in response.data)


def test_user_order_create(
                        user,
                        authenticated_client,
                        products) -> None:
    
    data = {
        "manifest": "%s" % words(12),
        "number_of_items": 1
    }
    obj = products.create(product_name=f"{words(4)}")
    response = authenticated_client.post(reverse("product_retrieve",
                                        kwargs={
                                            "pk": obj.pk,
                                            "product_slug": obj.product_slug
                                        }), 
                                        data)

    obj.refresh_from_db()

    assert response.status_code == 201
    assert obj.quantity == 0
    assert response.data["message"] == "Added Item"
    assert Order.objects.count() >= 1


def test_user_order_retrieve(user, authenticated_client) -> None:
    
    create_bulk_product([
        {
            "product_name": "IPhone",
            "user": user,
        },
        {
            "product_name": "Television",
            "user": user,
        },
        {
            "product_name": "Gucci Bag",
            "user": user,
        },
    ])
    obj = Order.objects.create(product_id=1, user=user)

    response = authenticated_client.get(reverse("order_retrieve", args=(obj.order_id,)))

    assert response.status_code == 200

