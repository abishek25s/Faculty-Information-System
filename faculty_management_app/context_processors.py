def staff_profile(request):
    staff_instance = None
    if request.user.is_authenticated and hasattr(request.user, 'staffs'):
        staff_instance = request.user.staffs
    return {'staff': staff_instance}