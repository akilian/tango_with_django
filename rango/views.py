from django.shortcuts import render
from rango.models import Category, Page


def index(request):
    context_dict = {}
    # query the database for a list of All categories
    # order categorys by likes
    # retrieve top 5, or al if less then 5 exist
    # place the list in the context dictionary
    # and which will be passed to the template
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.

    return render(request, 'rango/index.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}

    try:
        # try to find a category name slug
        # get model instance or raise an exception if otherwise
        category = Category.objects.get(slug=category_name_slug)
        # populate the context dict wich category_name value pair
        context_dict['category_name'] = category.name

        # Retrieve all associated pages
        # what is the difference between filter and get ?
        # seems to be pretty much the same
        pages = Page.objects.filter(category=category)

        # append result to context dictionary
        context_dict['pages'] = pages

        # the category object has to be added to the context as well
        # when rendering the cat templat i will check if a category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # handle exception when there is no match of the category slug
        pass

    # Render response and return to the client
    return render(request, 'rango/category.html', context_dict)


def about(request):
    experiment_dict = {'twany': "this is the dict content"}

    return render(request, 'rango/about.html', experiment_dict)
