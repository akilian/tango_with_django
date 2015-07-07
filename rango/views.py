from django.shortcuts import render, redirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm


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

        # pass the category name slug
        context_dict['category_name_slug'] = category.slug

    except Category.DoesNotExist:
        # handle exception when there is no match of the category slug
        pass

    # Render response and return to the client
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # is form contend valid ?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            return index(request)
        else:
            # if data in form no valid return errors
            print form.errors
    else:
        # if request was not a POST, display form to enter details
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
            cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
                # return redirect(category, category_name_slug)
        else:
            print form.errors
    else:
            form = PageForm()

    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


def about(request):
    experiment_dict = {'twany': "this is the dict content"}

    return render(request, 'rango/about.html', experiment_dict)
