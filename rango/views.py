from django.shortcuts import render
from rango.models import Category


def index(request):
    # query the database for a list of All categories
    # order categorys by likes
    # retrieve top 5, or al if less then 5 exist
    # place the list in the context dictionary
    # and which will be passed to the template
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.

    return render(request, 'rango/index.html', context_dict)


def about(request):
    experiment_dict = {'twany': "this is the dict content"}

    return render(request, 'rango/about.html', experiment_dict)
