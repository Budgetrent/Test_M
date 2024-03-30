from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Bid, Property, Location, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings":Property.objects.filter(isActive=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def create_page(request):
    return render(request, "auctions/create_listing.html")

# here im getting all the data from the form in create_listing page and storing it in corresponding 
# objects. 
@login_required
def create(request):
    try:
        if request.method == 'POST':
            owner = request.user
            name = request.POST["listingName"]
            year = request.POST["listingYear"]
            description = request.POST["listingDescription"]
            category = request.POST["options"]
            listingCity = request.POST["listingCity"]
            listingStreet = request.POST["listingStreet"]
            listingProvince = request.POST["listingProvince"]
            square_meters = request.POST["listingSize"]
            price = request.POST["listingPrice"]
            photo = request.POST["listingPhoto"]
            # this function is checking if category exsists and if it doesnt it creates new one users can use 
            try:
                newCategory = Category.objects.get(category_type=category)
            except Category.DoesNotExist:
                newCategory = Category.objects.create(category_type=category)
            # this function checks if location exsists and if not creates new one
            try:
                newCity = Location.objects.get(city=listingCity)
            except Location.DoesNotExist:
                newCity = Location.objects.create(city=listingCity)
            try:
                newStreet = Location.objects.get(street=listingStreet)
            except Location.DoesNotExist:
                newStreet = Location.objects.create(street=listingStreet)
            try:
                newProvince = Location.objects.get(province=listingProvince)
            except Location.DoesNotExist:
                newProvince = Location.objects.create(province=listingProvince)
            # creates new location 
            newLocation = Location(
                    city = newCity,
                    street = newStreet,
                    province = newProvince
                )
            newLocation.save()
            # creates new bid
            bid = Bid.objects.create(bid=price)
            
            # here we create new property using all the data and save it in database 
            newProperty = Property(
                owner = owner,
                name = name,
                description = description,
                year = year,
                category = newCategory,
                price = bid,
                location = newLocation,
                square_meters = square_meters,
                photo = photo,
            )
            newProperty.save()
            return HttpResponseRedirect(reverse("index"))
                
    except ValueError:
        return render(request, "auctions/create_listing.html")
    
    # function first checks if the listing is active , and than renders the listing page
    # in case the listing is not active and the user with the last bid is viewing the page 
        # the page will display winner message.
    # else if the user that is not the winner try's to view the page, function will render 
        # error_page instead
def listing_page(request, id):
    try:
        listing = Property.objects.get(pk=id)
        currentUser = request.user
        winner = request.user
        comments = Comment.objects.filter(property_id=listing.id)
        if listing.isActive == True:
            return render(request, "auctions/listing_page.html",{
                "listing":listing,
                "comments":comments
            })
        elif currentUser == listing.price.user and listing.isActive == False:
            return render(request, "auctions/listing_page.html",{
                "listing":listing,
                "messageW":"Congratulations , you are the winner!!",
                "comments":comments
            })
        else:
            return render(request, "auctions/error_page.html")
    except ValueError:
        return render(request, "auctions/error_page.html")
        
    
# function gets the id of current listing, requests the current user and than
# stores that user in the Property.watchlist so we can use the ManyToMany relation
# and filter the Property by checking if user is in the watchlist 
@login_required
def add_watchlist(request, id):
    addListing = Property.objects.get(pk=id)
    addUser = request.user
    addListing.watchlist.add(addUser)
    
    return HttpResponseRedirect(reverse("listingPage", args=(id, )))

# gets all the Property's that have the current user stored in their wathlist
@login_required
def watchlist(request):
    userWatchlist = request.user
    checkbool = True
    watchlistListings = Property.objects.filter(watchlist=userWatchlist,isActive=checkbool)
    
    return render(request, "auctions/watchlist.html", {
        "listings":watchlistListings
    })
    
# removes the user from the wathlist of Property
@login_required
def remove_watchlist(request, id):
    removeListing = Property.objects.get(pk=id)
    removeUser = request.user
    removeListing.watchlist.remove(removeUser)
    
    return HttpResponseRedirect(reverse("listingPage", args=(id, )))

# removes te listing from the watchlist page, and stays on the watchlist page 
@login_required
def watchlist_remowe(request, id):
    removeListing = Property.objects.get(pk=id)
    removeUser = request.user
    removeListing.watchlist.remove(removeUser)
    
    checkbool = True
    watchlistListings = Property.objects.filter(watchlist=removeUser,isActive=checkbool)
    
    return render(request, "auctions/watchlist.html", {
        "listings":watchlistListings
    })
    
    
    

# function gets the current Property objects bid value, and checks if its greater or lesser than the 
# value user inputed, if it is than it updates the bid with the user input ammount and updates the user of the bid 
# tied to the property
@login_required
def add_bid(request, id):
    listingBid = Property.objects.get(pk=id)
    newBid = request.POST["user_Bid"]
    currentUser = request.user
    comments = Comment.objects.filter(property_id=id)
    try:
        if listingBid.price.bid < int(newBid):
            listingBid.price.bid = int(newBid)
            listingBid.price.user = currentUser
            listingBid.price.save()
            return render(request, "auctions/listing_page.html", {
                "listing":listingBid,
                "messageW":"Congratulations: You are the new high bidder!",
                "comments":comments       
            })       
        else:
            return render(request, "auctions/listing_page.html", {
                "listing":listingBid,
                "messageE":"Error: your bid is lower than the current bid!",
                "comments":comments           
            })
    except ValueError:
         return render(request, "auctions/listing_page.html", {
            "listing":listingBid,
            "messageA":"Alert: you didnt place the bid!",
            "comments":comments          
        })
        
        
@login_required       
def close_auction(request, id):
    closeListing = Property.objects.get(pk=id)
    closeListing.isActive = False 
    closeListing.save()
    return HttpResponseRedirect(reverse("listingPage", args=(id, )))
    
def category_page(request, category):
    getCategory = Category.objects.get(category_type=category)
    sameCategory = Property.objects.filter(category=getCategory)
    category = category
    return render(request, "auctions/category_page.html", {
        "listings":sameCategory,
        "category":category
    })

@login_required
def add_comment(request, id):
    comment = request.POST["userComment"]
    listingID = Property.objects.get(pk=id)
    user = request.user
    
    newComment = Comment(
        user = user,
        property_id = listingID,
        comment = comment
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listingPage", args=(id, )))

    
        
