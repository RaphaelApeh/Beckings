from django.test import TestCase
from django.urls import reverse


class HealthCheckTestCase(TestCase):

    def test_health_check_view(self) -> None:

        response = self.client.get(reverse("health-check"))
        
        self.assertContains(response, "Ok")

        self.assertEqual(response.status_code, 200)

