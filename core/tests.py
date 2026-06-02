from django.test import TestCase, Client
from django.urls import reverse
from .models import UserData, Category, Transaction
from datetime import datetime
# Create your tests here.


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserData.objects.create_user(
            username="testuser",
            password="correct_password"
        )

    def test_login_with_correct_credentials(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "testuser", "password": "correct_password"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_incorrect_credentials(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "testuser", "password": "incorrect_password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)


class RegistrarionTestCase(TestCase):
    def test_registration_with_correct_credentials(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "testCorrectuser",
                "password1": "correct_password",
                "password2": "correct_password"
                }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], reverse("index"))

    def test_registration_with_short_password(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "testuser",
                "password1": "pass!12",
                "password2": "pass!12"
                }
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_with_different_passwords(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "testuser",
                "password1": "correct_password",
                "password2": "correct_password23"
                }
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_with_void_username(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "",
                "password1": "correct_password",
                "password2": "correct_password"
                }
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_with_void_password(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "testuser",
                "password1": "",
                "password2": ""
                }
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_already_registered_user(self):
        response = self.client.post(
            reverse("register"),
            data={
                "username": "Registereduser",
                "password1": "correct_password",
                "password2": "correct_password"
                }
        )
        response = self.client.post(
            reverse("register"),
            data={
                "username": "Registereduser",
                "password1": "other_correct_password",
                "password2": "other_correct_password"
                }
        )
        self.assertEqual(response.status_code, 200)


class CategoryCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserData.objects.create_user(
            username="testuser",
            password="correct_password"
        )
        self.client.login(username="testuser", password="correct_password")

    def test_add_category_success(self):
        response = self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(user=self.user, category_name="Продукты").exists())

    # def test_add_category_with_void_field(self):
    #     self.client.post(
    #         reverse("add_category"),
    #         data={"category_name": ""}
    #     )
    #     self.assertFalse(Category.objects.filter(user=self.user, category_name="").exists())

    # def test_add_already_existed_category(self):
    #     response = self.client.post(
    #         reverse("add_category"),
    #         data={"category_name": "Продкты"}
    #     )
    #     self.assertEqual(response.status_code, 200)

    def test_change_category_success(self):
        response = self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        category = Category.objects.get(user=self.user, category_name="Продукты")
        response = self.client.post(
            reverse("change_category"),
            data={"id": category.category_id, "category_name": "Еда"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(user=self.user, category_name="Еда").exists())

    def test_change_category_with_void_field(self):
        self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        category = Category.objects.get(user=self.user, category_name="Продукты")
        self.client.post(
            reverse("change_category"),
            data={"id": category.category_id, "category_name": ""}
        )
        self.assertFalse(Category.objects.filter(user=self.user, category_name="").exists())

    def test_delete_category(self):
        self.client.post(
            reverse("add_category"),
            data={"category_name": "Интернет покупки"}
        )
        category = Category.objects.get(user=self.user, category_name="Интернет покупки")
        self.client.post(
            reverse("delete_category"),
            data={"id": category.category_id}
        )
        self.assertFalse(Category.objects.filter(user=self.user, category_name="Интернет покупки").exists())


class TransactionCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserData.objects.create_user(
            username="testuser",
            password="correct_password"
        )
        self.client.login(username="testuser", password="correct_password")

    def test_add_transaction_success(self):
        self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        category = Category.objects.get(user=self.user, category_name="Продукты")
        self.client.post(
            reverse("add_transaction"),
            data={"category": category.category_id,
                  "operation": "Consumption",
                  "amount": "300",
                  "date": datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                  "description": "test description"
                  }
            )
        self.assertTrue(Transaction.objects.filter(user=self.user,
                                                   transaction_sum="300",
                                                   date=str(datetime(2026, 4, 12).strftime("%Y-%m-%d")),
                                                   description="test description").exists()
                        )

    def test_delete_transaction_success(self):
        self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        category = Category.objects.get(user=self.user, category_name="Продукты")
        self.client.post(
            reverse("add_transaction"),
            data={"category": category.category_id,
                  "operation": "Consumption",
                  "amount": "300",
                  "date": datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                  "description": "test description"
                  }
            )
        transaction = Transaction.objects.get(user=self.user,
                                              transaction_sum="300",
                                              date=datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                                              description="test description")
        self.client.post(
            reverse("delete_transaction"),
            data={"id": transaction.id}
            )
        self.assertFalse(Transaction.objects.filter(user=self.user,
                                                    transaction_sum="300",
                                                    date=datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                                                    description="test description").exists())

    def test_change_transaction_success(self):
        self.client.post(
            reverse("add_category"),
            data={"category_name": "Продукты"}
        )
        category = Category.objects.get(user=self.user, category_name="Продукты")
        self.client.post(
            reverse("add_transaction"),
            data={"category": category.category_id,
                  "operation": "Consumption",
                  "amount": "300",
                  "date": datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                  "description": "test description"
                  }
            )
        transaction = Transaction.objects.get(user=self.user,
                                              transaction_sum="300",
                                              date=datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                                              description="test description")
        self.client.post(
            reverse("change_transaction", kwargs={"pk": transaction.id}),
            data={"category": category.category_id,
                  "operation": "Income",
                  "amount": "12300",
                  "date": datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                  "description": "test change description"}
            )
        self.assertFalse(Transaction.objects.filter(user=self.user,
                                                    transaction_sum="300",
                                                    date=datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                                                    description="test description").exists())
        self.assertTrue(Transaction.objects.filter(user=self.user,
                                                   transaction_sum="12300",
                                                   date=datetime(2026, 4, 12).strftime("%Y-%m-%d"),
                                                   description="test change description").exists())
