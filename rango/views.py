from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

"""client side cookie tracking """
# def index(request):
#     context_dict = {}
#     # query the database for a list of All categories
#     # order categorys by likes
#     # retrieve top 5, or al if less then 5 exist
#     # place the list in the context dictionary
#     # and which will be passed to the template
#     category_list = Category.objects.order_by('-likes')[:5]
#     context_dict['categories'] = category_list
#     page_list = Page.objects.order_by('-views')[:5]
#     context_dict['pages'] = page_list

#     # get the number of visits to the site, use COOKIES.get
#     # function to obtain the visits cookie, if the cookie exists, the value 
#     # returned is casted into an integer. if not we default to zero
#     visits = int(request.COOKIES.get('visits', '1'))

#     reset_last_visit_time = False

#     # Return a rendered response to send to the client.
#     # We make use of the shortcut function to make our lives easier.
#     # Note that the first parameter is the template we wish to use.
#     response = render(request, 'rango/index.html', context_dict)

#     # does the last_visit cookie exist ?
#     if 'last_visit' in request.COOKIES:
#         # yes, get the cookies's value
#         last_visit = request.COOKIES['last_visit']
#         # cast the value to a python date/time object
#         last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
#         # If it's been more than a day since the last visit...
#         # if (datetime.now() - last_visit_time).days > 0:
#         if (datetime.now() - last_visit_time).seconds > 5:
#             visits = visits + 1
#             # flag that the cookie last visit needs to be updated
#             reset_last_visit_time = True
#     else:
#         # Cookie last_visit doesn't exist, so flag that it should be set.
#         reset_last_visit_time = True

#         context_dict['visits'] = visits
#         # Obtain our Response object early so we can add cookie information.
#         response = render(request, 'rango/index.html', context_dict)

#     if reset_last_visit_time:
#         response.set_cookie('last_visit', datetime.now())
#         response.set_cookie('visits', visits)

#     # Return response back to the user, updating any cookies that need changed.
#     return response
def index(request):
    """server side cookie tracking"""
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')

    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7],  "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response

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

        # save categor view count in category model table
        category.views = category.views + 1
        category.save()

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

    visits = request.session.get('visits')

    if visits:
        experiment_dict['visits'] = visits
    else:
        experiment_dict['visits'] = 0   

    return render(request, 'rango/about.html', experiment_dict)


# def register(request):
#     # A boolean value for telling the template
#     # whether the registration was successful.
#     # Set to False initially. Code changes value to True
#     # when registration succeeds.
#     registered = False

#     # If it's a HTTP POST, we're interested in processing form data.
#     if request.method == 'POST':
#         # Attempt to grab data form the raw form information
#         # NOTE: we both user UserForm and UserProfileForm forms
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)

#         # check if fields are valid
#         if user_form.is_valid() and profile_form.is_valid():
#             # first let's talke the user_form data
#             # go ahead and save user form data into db
#             user = user_form.save()

#             # hash password wit set_password method
#             # once hashed update the user object
#             user.set_password(user.password)
#             user.save()

#             # now tackle the UserProfileForm instance data
#             # deley commiting the save into db because
#             # data still has to be added
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # check if user provided picture
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']

#             # save UserProfile info
#             profile.save()

#             # update registered variable
#             registered = True
#             # return HttpResponse("Temporary success!")

#         # print out errors if form contain missing values or errors
#         else:
#             print user_form.errors, profile_form.errors

#     # Not a POST request? ernder form using two ModelForm instances
#     # These forms will be blank, ready ofr user imput
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()

#     #Render the template depending on the context
#     return render(request,
#                 'rango/register.html',
#                 {'user_form': user_form,
#                 'profile_form': profile_form,
#                 'registered': registered})


# def user_login(request):
#     # If the request is a HTTP POST,
#     # try to pull out the relevant information.
#     if request.method == 'POST':
#         # Gather the username and password provided by the user.
#         # This information is obtained from the login form.
#             # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
#             # because request.POST.get('<variable>') returns None, if the value does not exist,
#             # while request.POST['<variable>'] will raise key error exception
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # Use Django's machinery to attempt to see if the username/password
#         # combination is valid - a User object is returned if it is.

#         user = authenticate(username=username, password=password)

#         # If we have a User object, the details are correct.
#         # If None (Python's way of representing the absence of a value)
#         # no user with matching credentials was found.

#         if user:
#             # is account active
#             if user.is_active:
#                 # If the account is valid and active, we can log the user in.
#                 # We'll send the user back to the homepage.
#                 login(request, user)
#                 return HttpResponseRedirect('/rango/')
#             else:
#                 # An inactive account was used - no logging in!
#                 return HttpResponse("your Rango account is disabled.")
#         else:
#             # Bad login details were provided. So we can't log the user in.
#             # print "Invalid login details: {0}, {1}.".format(username, password)
#             return HttpResponse("Invalid login details: {0}, {1}.".format(username, password))

#     # The reques is not a HTTP POST, so display the login form.
#     # this scenario would most likely be a HTTP Get
#     else:
#         # No context variables to pass to the template system, hence the
#         # blank dictionary object...
#         return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    context_dict = {'content': "Since you're logged in , you can see this text!"}
    return render(request, 'rango/restricted.html', context_dict)


# @login_required
# def user_logout(request):
#     # Since we know the user is logged in, we can now just log them out.
#     logout(request)

#     # Take the user back to the homepage.
#     return HttpResponseRedirect('/rango/')
def search(request, urlquery=None):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    else:
        if urlquery:
            rawquery = urlquery.strip()
            query = rawquery.replace("+"," ")
            if query:
                result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page = Page.objects.get(id=page_id)

            # update pageviews
            page.views = page.views + 1
            page.save()

            # redirect to page url
            return HttpResponseRedirect(page.url)
        else:
            return HttpResponse("Url not found")
    else:
        return HttpResponseNotFound()
