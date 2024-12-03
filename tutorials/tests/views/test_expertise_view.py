from django.test import TestCase
from django.urls import reverse
from tutorials.models import Expertise


class ExpertiseListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("expertise_list")
        Expertise.objects.create(name="a")
        Expertise.objects.create(name="b")
        Expertise.objects.create(name="c")

    def test_expertise_list_url(self):
        self.assertEqual(self.url, "/expertise/")

    def test_get_expertise_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_list.html")
        expertise_list = response.context["expertise"]
        self.assertEqual(expertise_list.count(), 3)

    def test_search_expertise(self):
        response = self.client.get(self.url, {"search": "a"})
        self.assertEqual(response.status_code, 200)
        expertise_list = response.context["expertise"]
        self.assertEqual(expertise_list.count(), 1)
        self.assertEqual(expertise_list.first().name, "a")  # Updated to expect lowercase


class ExpertiseAddViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("expertise_add")

    def test_expertise_add_url(self):
        self.assertEqual(self.url, "/expertise/add/")

    def test_get_expertise_add(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_add.html")
        form = response.context["form"]
        self.assertTrue(form.is_bound is False)

    def test_post_expertise_add_valid_data(self):
        response = self.client.post(self.url, {"name": "c++"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("expertise_list"))
        self.assertTrue(Expertise.objects.filter(name="c++").exists())  # Updated to expect lowercase

    def test_post_expertise_add_invalid_data(self):
        response = self.client.post(self.url, {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_add.html")
        self.assertFalse(Expertise.objects.filter(name="").exists())


class ExpertiseEditViewTestCase(TestCase):
    def setUp(self):
        self.expertise = Expertise.objects.create(name="a")
        self.url = reverse("expertise_edit", kwargs={"expertise_id": self.expertise.id})

    def test_expertise_edit_url(self):
        self.assertEqual(self.url, f"/expertise/{self.expertise.id}/edit/")

    def test_get_expertise_edit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_edit.html")
        form = response.context["form"]
        self.assertTrue(form.is_bound is False)

    def test_post_expertise_edit_valid_data(self):
        response = self.client.post(self.url, {"name": "e"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("expertise_list"))
        self.expertise.refresh_from_db()
        self.assertEqual(self.expertise.name, "e")  # Updated to expect lowercase

    def test_post_expertise_edit_invalid_data(self):
        response = self.client.post(self.url, {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_edit.html")
        self.expertise.refresh_from_db()
        self.assertEqual(self.expertise.name, "a")  # Updated to expect lowercase


class ExpertiseDeleteViewTestCase(TestCase):
    def setUp(self):
        self.expertise = Expertise.objects.create(name="a")
        self.url = reverse("expertise_delete", kwargs={"expertise_id": self.expertise.id})

    def test_expertise_delete_url(self):
        self.assertEqual(self.url, f"/expertise/{self.expertise.id}/delete/")

    def test_get_expertise_delete(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expertise_delete.html")

    def test_post_expertise_delete(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("expertise_list"))
        self.assertFalse(Expertise.objects.filter(id=self.expertise.id).exists())
