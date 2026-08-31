from django.shortcuts import redirect, render

from .forms import ContactForm


def about(request):

    return render(
        request,
        "pages/about.html",
    )


def contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "pages:contact_success"
            )

    else:

        form = ContactForm()

    return render(
        request,
        "pages/contact.html",
        {
            "form": form,
        },
    )


def contact_success(request):

    return render(
        request,
        "pages/contact_success.html",
    )


def support(request):

    return render(
        request,
        "pages/support.html",
    )


def faqs(request):

    return render(
        request,
        "pages/faqs.html",
    )