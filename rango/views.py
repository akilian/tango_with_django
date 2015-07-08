from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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


@login_required
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


@login_required
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


def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to True
    # when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab data form the raw form information
        # NOTE: we both user UserForm and UserProfileForm forms
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # check if fields are valid
        if user_form.is_valid() and profile_form.is_valid():
            # first let's talke the user_form data
            # go ahead and save user form data into db
            user = user_form.save()

            # hash password wit set_password method
            # once hashed update the user object
            user.set_password(user.password)
            user.save()

            # now tackle the UserProfileForm instance data
            # deley commiting the save into db because
            # data still has to be added
            profile = profile_form.save(commit=False)
            profile.user = user

            # check if user provided picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save UserProfile info
            profile.save()

            # update registered variable
            registered = True
            # return HttpResponse("Temporary success!")

        # print out errors if form contain missing values or errors
        else:
            print user_form.errors, profile_form.errors

    # Not a POST request? ernder form using two ModelForm instances
    # These forms will be blank, ready ofr user imput
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    #Render the template depending on the context
    return render(request,
                'rango/register.html',
                {'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered})


def user_login(request):
    # If the request is a HTTP POST,
    # try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
            # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
            # because request.POST.get('<variable>') returns None, if the value does not exist,
            # while request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.

        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value)
        # no user with matching credentials was found.

        if user:
            # is account active
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            # print "Invalid login details: {0}, {1}.".format(username, password)
            return HttpResponse("Invalid login details: {0}, {1}.".format(username, password))

    # The reques is not a HTTP POST, so display the login form.
    # this scenario would most likely be a HTTP Get
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    context_dict = {'content': "Since you're logged in , you can see this text!"}
    return render(request, 'rango/restricted.html', context_dict)


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
