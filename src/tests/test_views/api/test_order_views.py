import pytest

from django.urls import reverse
from django.utils.lorem_ipsum import words

from products.models import Order


@pytest.mark.django_db
class TestOrderAPI:

    def test_order_list_view(self, 
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


    def test_user_order_create(self,
                               user,
                               authenticated_client,
                               products) -> None:
        
        data = {
            "manifest": "%s" % words(12)
        }
        obj = products.create(product_name=f"{words(4)}")
        response = authenticated_client.post(reverse("product_retrieve",
                                                     kwargs={
                                                         "pk": obj.pk,
                                                         "product_slug": obj.product_slug
                                                     }), 
                                                     data)

        assert response.status_code == 201

        assert response.data["message"] == "Added Item"
        assert Order.objects.count() >= 1

