import pytest


from products.models import Product


@pytest.mark.django_db
class TestProductModel:

    def test_model_indexes(self) -> None:

        indexes = Product._meta.indexes
        index_names = [index.name for index in indexes]

        assert isinstance(index_names, (list, tuple))
        assert "product_name_index" in index_names
