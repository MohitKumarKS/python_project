from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.http import JsonResponse

from .models import Location, Supplies, DisasterReport, SupplyRequest
from .mongodb_utils import get_collection

def home_view(request):
    # Add a timestamp to force template refresh
    current_time = timezone.now()
    return render(request, 'home.html', {'current_time': current_time})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            
            # Redirect based on user type
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            # Check if user exists but password is wrong
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.error(request, "Username not found. Please check your username or register.")
            
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validate inputs
        if not all([username, password, confirm_password, email]):
            messages.error(request, "All fields are required.")
            return render(request, 'register.html')
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(
                request, 'register.html', {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name}
            )
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')
    
    return render(request, 'register.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """View for admin dashboard"""
    # Get collections
    locations_coll = get_collection('locations')
    supplies_coll = get_collection('supplies')
    requests_coll = get_collection('supply_requests')
    
    # Get all locations
    locations = list(locations_coll.find())
    
    # Get all supplies
    supplies = list(supplies_coll.find())
    
    # Get pending requests
    pending_requests = list(requests_coll.find({'status': 'pending'}))
    
    # Calculate totals
    total_locations = len(locations)
    total_pending_requests = len(pending_requests)
    
    total_food = 0
    total_water = 0
    total_medical = 0
    
    # Process supplies data for display
    supplies_data = []

    for supply in supplies:
        # Find location for this supply
        location = next((loc for loc in locations if loc['_id'] == supply['location']), None)
        if location:
            # Convert ObjectId to string for template rendering
            supply['id'] = str(supply['_id'])

            # Add location info to supply
            supply['location_name'] = location['name']
            supply['location_address'] = location['address']

            # Add to totals
            total_food += supply.get('food_packs', 0)
            total_water += supply.get('water_supply', 0)
            total_medical += supply.get('medical_supply', 0)

            # Format date for display
            if 'last_updated' in supply:
                supply['last_updated_formatted'] = supply['last_updated'].strftime('%Y-%m-%d %H:%M')
            else:
                supply['last_updated_formatted'] = 'N/A'

            supplies_data.append(supply)
    
    context = {
        'total_locations': total_locations,
        'total_pending_requests': total_pending_requests,
        'total_food': total_food,
        'total_water': total_water,
        'total_medical': total_medical,
        'supplies': supplies_data,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    """View for user dashboard"""
    # Get all locations
    locations_coll = get_collection('locations')
    locations = list(locations_coll.find())

    # Convert ObjectId to string for template rendering for locations
    for location in locations:
        location['id'] = str(location['_id'])

    # Get supplies for each location
    supplies_coll = get_collection('supplies')
    supplies = []

    for location in locations:
        supply = supplies_coll.find_one({'location': location['_id']})
        if supply:
            # Convert ObjectId to string for template rendering
            supply['_id'] = str(supply['_id'])
            supply['location'] = location
            supplies.append(supply)

    # Print debug info
    print(f"Found {len(locations)} locations and {len(supplies)} supplies")

    return render(request, 'user_dashboard.html', {
        'supplies': supplies,
        'locations': locations
    })

def public_view(request):
    search_query = request.GET.get('search', '')
    
    # Get all locations
    locations_coll = get_collection('locations')
    
    # Apply search filter if provided
    if search_query:
        locations = list(locations_coll.find({
            '$or': [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'address': {'$regex': search_query, '$options': 'i'}}
            ]
        }))
    else:
        locations = list(locations_coll.find())
    
    # Get supplies for each location
    supplies_coll = get_collection('supplies')
    supplies = []
    for location in locations:
        supply = supplies_coll.find_one({'location': location['_id']})
        if supply:
            supply['location'] = location
            supplies.append(supply)
    
    return render(request, 'public_view.html', {
        'supplies': supplies,
        'locations': locations,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_requests(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        if request_id and action in ['approve', 'deliver', 'reject']:
            requests_coll = get_collection('supply_requests')
            supply_request = requests_coll.find_one({'_id': ObjectId(request_id)})
            
            if supply_request:
                status = {
                    'approve': 'approved',
                    'deliver': 'delivered',
                    'reject': 'rejected'
                }[action]
                
                # Update request status
                requests_coll.update_one(
                    {'_id': supply_request['_id']},
                    {'$set': {'status': status}}
                )
                
                if status == 'delivered':
                    # Update the supplies at the location
                    supplies_coll = get_collection('supplies')
                    supplies = supplies_coll.find_one({'location': supply_request['location']})
                    
                    if supplies:
                        supplies_coll.update_one(
                            {'_id': supplies['_id']},
                            {
                                '$inc': {
                                    'food_packs': supply_request['food_packs'],
                                    'water_supply': supply_request['water_supply'],
                                    'medical_supply': supply_request['medical_supply']
                                }
                            }
                        )
                
                messages.success(request, f"Request marked as {status}.")
            else:
                messages.error(request, "Error: Request not found.")
        else:
            messages.error(request, "Invalid request ID or action.")
    
    # Get all locations for reference
    locations_coll = get_collection('locations')
    locations = {str(loc['_id']): loc for loc in locations_coll.find()}
    
    # Get all users for reference
    from django.contrib.auth.models import User
    users = {user.id: user for user in User.objects.all()}
    
    # Get pending, approved, and completed requests
    requests_coll = get_collection('supply_requests')
    pending_requests = list(requests_coll.find({'status': 'pending'}).sort('request_date', -1))
    approved_requests = list(requests_coll.find({'status': 'approved'}).sort('request_date', -1))
    completed_requests = list(requests_coll.find({'status': {'$in': ['delivered', 'rejected']}}).sort('request_date', -1).limit(10))
    
    # Add location and user info to each request
    for requests_list in [pending_requests, approved_requests, completed_requests]:
        for req in requests_list:
            # Convert ObjectId to string for template rendering
            req['id'] = str(req['_id'])

            # Add location info
            location_id = req['location']
            if isinstance(location_id, ObjectId):
                location_id = str(location_id)

            if location_id in locations:
                req['location'] = locations[location_id]

            # Add user info
            user_id = req['requested_by']
            if user_id in users:
                req['requested_by'] = users[user_id]
    
    return render(request, 'manage_requests.html', {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'completed_requests': completed_requests
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def disaster_reports(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        action = request.POST.get('action')
        
        try:
            reports_coll = get_collection('disaster_reports')
            report = reports_coll.find_one({'_id': ObjectId(report_id)})
            
            if report:
                if action == 'resolve':
                    reports_coll.update_one(
                        {'_id': report['_id']},
                        {'$set': {'is_active': False}}
                    )
                    messages.success(request, "Disaster report marked as resolved.")
                
                elif action == 'reactivate':
                    reports_coll.update_one(
                        {'_id': report['_id']},
                        {'$set': {'is_active': True}}
                    )
                    messages.success(request, "Disaster report reactivated.")
            else:
                messages.error(request, "Error: Report not found.")
                
        except Exception as e:
            messages.error(request, f"Error processing report: {str(e)}")
    
    # Get all locations for reference
    locations_coll = get_collection('locations')
    locations = {str(loc['_id']): loc for loc in locations_coll.find()}
    
    # Get all users for reference
    from django.contrib.auth.models import User
    users = {user.id: user for user in User.objects.all()}
    
    # Get active and resolved reports
    reports_coll = get_collection('disaster_reports')
    active_reports = list(reports_coll.find({'is_active': True}).sort('reported_date', -1))
    resolved_reports = list(reports_coll.find({'is_active': False}).sort('reported_date', -1).limit(10))
    
    # Add location and user info to each report
    for reports_list in [active_reports, resolved_reports]:
        for report in reports_list:
            # Convert ObjectId to string for template rendering
            report['id'] = str(report['_id'])

            # Add location info
            location_id = report['location']
            if isinstance(location_id, ObjectId):
                location_id = str(location_id)

            if location_id in locations:
                report['location'] = locations[location_id]

            # Add user info
            user_id = report['reported_by']
            if user_id in users:
                report['reported_by'] = users[user_id]
    
    return render(request, 'disaster_reports.html', {
        'active_reports': active_reports,
        'resolved_reports': resolved_reports
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_supply(request, supply_id):
    """View for editing supplies"""
    supplies_coll = get_collection('supplies')
    locations_coll = get_collection('locations')
    
    try:
        supply = supplies_coll.find_one({'_id': ObjectId(supply_id)})
        if not supply:
            messages.error(request, "Supply not found")
            return redirect('admin_dashboard')
        
        location = locations_coll.find_one({'_id': supply['location']})
        
        if request.method == 'POST':
            # Update supply with form data
            food_packs = int(request.POST.get('food_packs', 0))
            water_supply = int(request.POST.get('water_supply', 0))
            medical_supply = int(request.POST.get('medical_supply', 0))
            
            supplies_coll.update_one(
                {'_id': ObjectId(supply_id)},
                {'$set': {
                    'food_packs': food_packs,
                    'water_supply': water_supply,
                    'medical_supply': medical_supply,
                    'last_updated': datetime.now()
                }}
            )
            
            messages.success(request, f"Supplies for {location['name']} updated successfully")
            return redirect('admin_dashboard')
        
        context = {
            'supply': supply,
            'location': location
        }
        return render(request, 'edit_supply.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('admin_dashboard')

def get_csrf_token(request):
    # This view can be used to get a fresh CSRF token
    return JsonResponse({'csrfToken': get_token(request)})
