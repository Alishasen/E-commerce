from django.urls import path

from . import views


app_name = "pages"


urlpatterns = [

    path(
        "about/",
        views.about,
        name="about",
    ),

    path(
        "contact/",
        views.contact,
        name="contact",
    ),

    path(
        "contact/success/",
        views.contact_success,
        name="contact_success",
    ),

    path(
        "support/",
        views.support,
        name="support",
    ),

    path(
        "faqs/",
        views.faqs,
        name="faqs",
    ),

]