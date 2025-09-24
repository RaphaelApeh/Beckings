import factory

from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL  # "auth.User"
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: "user%s" % n)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    is_staff = factory.Iterator((True, False))


class ProductFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = "products.Product"

    user = factory.SubFactory(UserFactory)
    product_name = factory.Faker("name")
    product_description = factory.Faker("text")
    price = factory.Faker("pyint")
