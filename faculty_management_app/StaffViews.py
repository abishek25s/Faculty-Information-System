from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
# from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count, Q, FileField, ImageField
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import datetime as dt
from datetime import date,datetime
from django.http import FileResponse, HttpResponseNotFound, Http404
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os,base64
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from faculty_management_app.models import CustomUser, Staffs, Journal,Conference,Qualification,Book, BookChapter, Copyright, Patent, Experience, CurrentExperience, OrganizedAC, AttendedAC, Certification,Consultancy_Project,Product_Development,Project_Proposal,Achievement

def contact_us(request):
    return render(request, "staff_template/contact_us.html")

def staff_home(request):
    staff = Staffs.objects.get(admin=request.user.id)

    journal_count = Journal.objects.filter(staff_id=request.user.staffs.id).count()
    conference_count = Conference.objects.filter(staff_id=request.user.staffs.id).count()
    book_count = Book.objects.filter(staff_id=request.user.staffs.id).count()
    book_chapter_count = BookChapter.objects.filter(staff_id=request.user.staffs.id).count()
    copyright_count = Copyright.objects.filter(staff_id=request.user.staffs.id).count()
    patent_count= Patent.objects.filter(staff_id=request.user.staffs.id).count()
    experiences = Experience.objects.filter(staff=staff)
    current_experience = CurrentExperience.objects.filter(staff=staff).first()
    total_count = journal_count+conference_count+book_count + book_chapter_count+copyright_count + patent_count
    consultancy_project_count=Consultancy_Project.objects.filter(staff_id=request.user.staffs.id).count()
    product_developed_count=Product_Development.objects.filter(staff_id=request.user.staffs.id).count()
    project_proposal_count=Product_Development.objects.filter(staff_id=request.user.staffs.id).count()

    academic_years, publication_counts = get_publication_counts_by_year(staff)
    
    total_experience_days = 0
    
    if current_experience:
        duration = timezone.now().date() - current_experience.from_date
        total_experience_days += duration.days
    
    # Convert days to years, months, and days
    years, remainder = divmod(total_experience_days, 365)
    months, days = divmod(remainder, 30)  # Simplified approximation

    context={
        "academic_years": academic_years,
        "publication_counts": publication_counts,
        "staff":staff,
        "journal_count" : journal_count,
        "conference_count" : conference_count,
        "book_count" : book_count,
        'book_chapter_count' : book_chapter_count,
        "experience_years": years,
        "experience_months": months,
        "experience_days": days,
        'copyright_count' : copyright_count,
        "patent_count" : patent_count,
        "total_count" : total_count,
        'consultancy_project_count' : consultancy_project_count,
        'product_developed_count':product_developed_count,
        'project_proposal_count':project_proposal_count
    }
    return render(request, "staff_template/staff_home_template.html", context)


def get_publication_counts_by_year(staff):
    
    # Define the start and end months for an academic year
    academic_year_start_month = 7  # June
    academic_year_end_month = 6    # May

    # Get the current date
    current_date = date.today()

    # Determine the current academic year based on the current date
    if current_date.month < academic_year_start_month:
        current_academic_year = f"{current_date.year - 1}-{current_date.year}"
    else:
        current_academic_year = f"{current_date.year}-{current_date.year + 1}"

    # Generate academic years from 5 years ago to the current academic year
    academic_years = [f"{year}-{year + 1}" for year in range(current_date.year - 5, current_date.year)]
    # If the current date is after the start of the new academic year, add it to the list
    if current_date.month >= academic_year_start_month:
        academic_years.append(current_academic_year)
    publication_count=[]
    for year in academic_years:
        count=Book.objects.filter(academic_year=year,staff_id=staff.id).count()+BookChapter.objects.filter(academic_year=year,staff_id=staff.id).count()+Copyright.objects.filter(academic_year=year,staff_id=staff.id).count()+Patent.objects.filter(academic_year=year,staff_id=staff.id).count()+Journal.objects.filter(academic_year=year,staff_id=staff.id).count()+Conference.objects.filter(academic_year=year,staff_id=staff.id).count()
        publication_count.append(count)
    return academic_years,publication_count

def generate_resume_pdf(request):
    # Retrieve user's profile information from the database (similar to staff_profile view)
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)
    journal_count = Journal.objects.filter(staff_id=request.user.staffs.id).count()
    conference_count = Conference.objects.filter(staff_id=request.user.staffs.id).count()
    book_count = Book.objects.filter(staff_id=request.user.staffs.id).count()
    book_chapter_count = BookChapter.objects.filter(staff_id=request.user.staffs.id).count()
    copyright_count = Copyright.objects.filter(staff_id=request.user.staffs.id).count()
    patent_count= Patent.objects.filter(staff_id=request.user.staffs.id).count()

    # Encode profile picture as Base64
    profile_picture_base64 = None
    if staff.profile_picture:
        with open(staff.profile_picture.path, "rb") as image_file:
            profile_picture_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Render resume template with user's profile information including the profile picture
    context = {
        'user': user,
        'staff': staff,
        'journal_count': journal_count,
        'conference_count': conference_count,
        'book_count': book_count,
        'book_chapter_count': book_chapter_count,
        'copyright_count': copyright_count,
        'patent_count': patent_count,
        'profile_picture_base64': profile_picture_base64,
        
        }
    html_string = render_to_string('staff_template/resume_template.html', context)

    # Create a PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    # Generate PDF from HTML using xhtml2pdf
    pisa_status = pisa.CreatePDF(
        html_string, dest=response, encoding='utf-8'
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response

def staff_aboutus(request):
    return render(request, "staff_template/aboutus.html")
       
def staff_add_publication(request):
    return render(request, 'staff_template/staff_add_publication_template.html')

def staff_add_projects(request):
    return render(request, 'staff_template/staff_add_projects.html')

def staff_add_consultancy_projects(request):
    return render(request, 'staff_template/staff_add_consultancy_projects.html')

def staff_add_product_development(request):
    return render(request, 'staff_template/staff_add_product_development.html')

def staff_add_project_proposal(request):
    return render(request, 'staff_template/staff_add_project_proposal.html')

def staff_add_achievement(request):
    return render(request, 'staff_template/staff_add_achievements.html')

def staff_add_consultancy_projects_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_consultancy_projects')
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        title = request.POST.get('title')
        
        # Get duration_numeric and duration_unit separately
        duration_numeric = request.POST.get('duration_numeric')
        duration_unit = request.POST.get('duration_unit')
        duration = f"{duration_numeric} {duration_unit}"
        amount = request.POST.get('amount')
        academic_year = request.POST.get('academic_year')
        funding_agency = request.POST.get('funding_agency')        
        status = request.POST.get('status')
        
        try:
            cp = Consultancy_Project(
                amount=amount,
                staff_id=staff_obj,
                title=title,
                duration=duration,  # Combine numeric and unit into one field
                academic_year=academic_year,
                funding_agency=funding_agency,
                status=status
            )
            cp.save()
            messages.success(request, "Consultancy Project details saved successfully.")
            return redirect('staff_add_consultancy_projects')
        except Exception as e:
            messages.error(request, f"Failed to save Consultancy Project details: {str(e)}")
            return redirect('staff_add_consultancy_projects')
    
def staff_add_product_development_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_product_development')
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        product_name = request.POST.get('product_name')
        academic_year = request.POST.get('academic_year')
        student_name = request.POST.get('student_name')
        
        try:
            pd = Product_Development(
                staff_id=staff_obj,
                product_name=product_name,
                academic_year=academic_year,
                student_name=student_name,
            )
            pd.save()
            messages.success(request, "Product Development details saved successfully.")
            return redirect('staff_add_product_development')
        except Exception as e:
            messages.error(request, f"Failed to save Product Development details: {str(e)}")
            return redirect('staff_add_product_development')
    
def staff_add_project_proposal_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_project_proposal')
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        title = request.POST.get('title')
        
        duration_numeric = request.POST.get('duration_numeric')
        duration_unit = request.POST.get('duration_unit')
        duration = f"{duration_numeric} {duration_unit}"
        amount = request.POST.get('amount')
        academic_year = request.POST.get('academic_year')
        funding_agency = request.POST.get('funding_agency')        
        status = request.POST.get('status')
        
        try:
            pp = Project_Proposal(
                amount=amount,
                staff_id=staff_obj,
                title=title,
                duration=duration, 
                academic_year=academic_year,
                funding_agency=funding_agency,
                status=status
            )
            pp.save()
            messages.success(request, "Project Proposal details saved successfully.")
            return redirect('staff_add_project_proposal')
        except Exception as e:
            messages.error(request, f"Failed to save Project Proposal details: {str(e)}")
            return redirect('staff_add_project_proposal')

def staff_add_achievement_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_achievement')
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        cert_pdf = request.FILES.get('cert_pdf')  # Assuming 'journal_pdf' field is where the PDF is uploaded
        title = request.POST.get('title')
        description = request.POST.get('description')
        month_and_year = request.POST.get('month_and_year')

    
        try:
            achievement = Achievement(
                staff_id=staff_obj,
                title=title,
                description=description,
                cert_pdf=cert_pdf,
                month_and_year=month_and_year,
            )
            achievement.save()
            messages.success(request, "Achievement details saved successfully.")
            return redirect('staff_add_achievement')
        except Exception as e:
            messages.error(request, f"Failed to save achievement details: {str(e)}")
            return redirect('staff_add_achievement')
        
def staff_view_project(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_consultancy_project.html', {})
    staffs=Staffs.objects.all()
    consultancy_project_count=Consultancy_Project.objects.filter(staff_id=request.user.staffs.id).count()
    product_development_count=Product_Development.objects.filter(staff_id=request.user.staffs.id).count()
    project_proposals_count=Project_Proposal.objects.filter(staff_id=request.user.staffs.id).count()
    context={
        'staffs':staffs,
        'consultancy_project_count':consultancy_project_count,
        'product_development_count':product_development_count,
        'project_proposals_count' : project_proposals_count,
    }
    return render(request,'staff_template/staff_view_project.html',context)

def staff_view_consultancy_project(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_consultancy_project.html', {})
    consultancy_project = Consultancy_Project.objects.filter(staff_id=staff_obj)
    academic_years = consultancy_project.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        consultancy_project = consultancy_project.filter(academic_year=selected_academic_year)
    
    context = {
        'consultancy_project': consultancy_project,
        'academic_years': academic_years,
    }
    return render(request, "staff_template/staff_view_consultancy_project.html", context)

def staff_view_product_development(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_product_development.html', {})
    product_development = Product_Development.objects.filter(staff_id=staff_obj)
    academic_years = product_development.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        product_development = product_development.filter(academic_year=selected_academic_year)
    
    context = {
        'product_development': product_development,
        'academic_years': academic_years,
    }
    return render(request, "staff_template/staff_view_product_development.html", context)

def staff_view_project_proposal(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_project_proposal.html', {})
    project_proposal = Project_Proposal.objects.filter(staff_id=staff_obj)
    academic_years = project_proposal.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        consultancy_project = consultancy_project.filter(academic_year=selected_academic_year)
    
    context = {
        'project_proposal': project_proposal,
        'academic_years': academic_years,
    }
    return render(request, "staff_template/staff_view_project_proposal.html", context)

def staff_view_achievements(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_achievements.html', {})
    
    achievements = Achievement.objects.filter(staff_id=staff_obj)    
    academic_years = achievements.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    selected_academic_year = request.GET.get('academic_year', '')
    
    if selected_academic_year:
        achievements = achievements.filter(academic_year=selected_academic_year)
        
    
    context = {
        'achievements': achievements,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }
    return render(request, "staff_template/staff_view_achievements.html", context)

def view_publications(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_publications.html', {})
    
    journal_count = Journal.objects.filter(staff_id=request.user.staffs.id).count()
    conference_count = Conference.objects.filter(staff_id=request.user.staffs.id).count()
    book_count = Book.objects.filter(staff_id=request.user.staffs.id).count()
    book_chapter_count = BookChapter.objects.filter(staff_id=request.user.staffs.id).count()
    copyright_count = Copyright.objects.filter(staff_id=request.user.staffs.id).count()
    patent_count= Patent.objects.filter(staff_id=request.user.staffs.id).count()
    total_count = journal_count+conference_count+book_count + book_chapter_count+copyright_count + patent_count

    context = {
        "journal_count" : journal_count,
        "conference_count" : conference_count,
        "book_count" : book_count,
        'book_chapter_count' : book_chapter_count,
        'copyright_count' : copyright_count,
        "patent_count" : patent_count,
        "total_count" : total_count
    }
    return render(request, 'staff_template/staff_view_publications.html', context)

def staff_view_journal(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_journal.html', {})
    
    publications = Journal.objects.filter(staff_id=staff_obj)
    academic_years = publications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        publications = publications.filter(academic_year=selected_academic_year)
    
    context = {
        'publications': publications,
        'academic_years': academic_years,
    }
    return render(request, "staff_template/staff_view_journal.html", context)

def staff_view_conference(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_conference.html', {})
    
    publications = Conference.objects.filter(staff_id=staff_obj)

    academic_years = publications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        publications = publications.filter(academic_year=selected_academic_year)
    
    context = {
        'publications': publications,
        'academic_years': academic_years,
        # Renamed 'staff' to 'staff_queryset' for clarity
    }
    return render(request, "staff_template/staff_view_conference.html", context)

def staff_view_books(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_conference.html', {})
    
    books = Book.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = books.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        books = books.filter(academic_year=selected_academic_year)
    context = {
        'books': books,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_books.html", context)

def staff_view_certifications(request):
    try:
        # Retrieve the staff object associated with the currently logged-in user
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        # If the staff object does not exist, render a template indicating an error or empty data
        return render(request, 'staff_template/staff_view_certifications.html', {})
    
    # Retrieve certifications associated with the staff member
    certifications = Certification.objects.filter(staff_id=staff_obj)
    
    # Get distinct academic years for filter options
    academic_years = certifications.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    # Apply filtering if academic year is selected
    if selected_academic_year:
        certifications = certifications.filter(academic_year=selected_academic_year)
    
    context = {
        'certifications': certifications,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_certifications.html", context)

def staff_view_academic_contribution(request):
    attended_AC_count = AttendedAC.objects.filter(staff_id=request.user.staffs.id).count()
    organized_AC_count = OrganizedAC.objects.filter(staff_id=request.user.staffs.id).count()
    context={
        'attended_AC_count':attended_AC_count,
        'organized_AC_count':organized_AC_count
    }
    return render(request, 'staff_template/staff_view_academic_contribution.html',context)

def staff_view_attended_AC(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_attended_AC.html', {})
    attendedAC = AttendedAC.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = attendedAC.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        attendedAC = attendedAC.filter(academic_year=selected_academic_year)
    context = {
        'attendedAC': attendedAC,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_attended_AC.html", context)

def staff_view_organized_AC(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_organized_AC.html', {})
    organizedAC = OrganizedAC.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = organizedAC.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        organizedAC = organizedAC.filter(academic_year=selected_academic_year)
    context = {
        'organizedAC': organizedAC,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_organized_AC.html", context)

def staff_view_patent(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_patent.html', {})
    patents = Patent.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = patents.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        patents = patents.filter(academic_year=selected_academic_year)
    context = {
        'patents': patents,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_patent.html", context)

def staff_view_book_chapters(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_conference.html', {})
    book_chapters = BookChapter.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = book_chapters.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        book_chapters = book_chapters.filter(academic_year=selected_academic_year)
    context = {
        'book_chapters': book_chapters,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_book_chapters.html", context)

def staff_view_copyrights(request):
    try:
        staff_obj = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        return render(request, 'staff_template/staff_view_copyrights.html', {})
    copyrights = Copyright.objects.filter(staff_id=staff_obj)
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = copyrights.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        copyrights = copyrights.filter(academic_year=selected_academic_year)
    context = {
        'copyrights': copyrights,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, "staff_template/staff_view_copyrights.html", context)

def view_journal(request):
    publications = Journal.objects.all()
    
    academic_years = publications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        publications = publications.filter(academic_year=selected_academic_year)
    
    context = {
        'publications': publications,
        'academic_years': academic_years,
        # Renamed 'staff' to 'staff_queryset' for clarity
    }
    return render(request, "hod_template/view_journal.html", context)

def delete_journal(request, staff_id):
    journal = Journal.objects.get(id=staff_id)
    if journal.journal_pdf:
        journal.journal_pdf.delete()
    try:
        journal.delete()
        messages.success(request, "Journal Deleted Successfully.")
        return redirect('staff_view_journal')
    except:
        messages.error(request, "Failed to Delete Journal.")
        return redirect('staff_view_journal')
    
def delete_conference(request, staff_id):
    conference = Conference.objects.get(id=staff_id)
    if conference.journal_pdf:
        conference.journal_pdf.delete()
    try:
        conference.delete()
        messages.success(request, "Conference Deleted Successfully.")
        return redirect('staff_view_conference')
    except:
        messages.error(request, "Failed to Delete Conference.")
        return redirect('staff_view_conference')
    
def delete_book(request, staff_id):
    book = Book.objects.get(id=staff_id)
    try:
        book.delete()
        messages.success(request, "Book Deleted Successfully.")
        return redirect('staff_view_books')
    except:
        messages.error(request, "Failed to Delete Book.")
        return redirect('staff_view_books')
    
def delete_book_chapter(request, staff_id):
    book_chapter = get_object_or_404(BookChapter, id=staff_id)
    try:
        book_chapter.delete()
        messages.success(request, "Book Chapter Deleted Successfully.")
    except:
        messages.error(request, "Failed to Delete Book Chapter.")
    return redirect('staff_view_book_chapters')
    
def delete_patent(request, staff_id):
    patent = Patent.objects.get(id=staff_id)
    if patent.proof_file:
        patent.proof_file.delete()
    try:
        patent.delete()
        messages.success(request, "Patent Deleted Successfully.")
        return redirect('staff_view_patent')
    except:
        messages.error(request, "Failed to Delete Patent.")
        return redirect('staff_view_patent')
    

def delete_copyright(request, staff_id):
    copyright = Copyright.objects.get(id=staff_id)
    try:
        copyright.delete()
        messages.success(request, "Copyright Deleted Successfully.")
        return redirect('staff_view_copyrights')
    except:
        messages.error(request, "Failed to Delete Copyright.")
        return redirect('staff_view_copyrights')
    
def delete_attended_AC(request, staff_id):
    attended_ac = AttendedAC.objects.get(id=staff_id)
    if attended_ac.report_proof:
        attended_ac.report_proof.delete()
    try:
        attended_ac.delete()
        messages.success(request, "Attended AC Deleted Successfully.")
        return redirect('staff_view_attended_AC')
    except:
        messages.error(request, "Failed to Delete Attended AC.")
        return redirect('staff_view_attended_AC')
    
def delete_organized_AC(request, staff_id):
    organized_AC = OrganizedAC.objects.get(id=staff_id)
    if organized_AC.report_proof:
        organized_AC.report_proof.delete()
    try:
        organized_AC.delete()
        messages.success(request, "Organized AC Deleted Successfully.")
        return redirect('staff_view_organized_AC')
    except:
        messages.error(request, "Failed to Delete Organized AC.")
        return redirect('staff_view_organized_AC')
    
def delete_certification(request, staff_id):
    certification = Certification.objects.get(id=staff_id)
    if certification.certificate:
        certification.certificate.delete()
    try:
        certification.delete()
        messages.success(request, "Certification Deleted Successfully.")
        return redirect('staff_view_certifications')
    except:
        messages.error(request, "Failed to Delete Certification.")
        return redirect('staff_view_certifications')
    
def delete_consultancy_project(request, staff_id):
    consultancy_project = Consultancy_Project.objects.get(id=staff_id)
    try:
        consultancy_project.delete()
        messages.success(request, "Consultancy_Project Deleted Successfully.")
        return redirect('staff_view_consultancy_project')
    except:
        messages.error(request, "Failed to Delete Consultancy_Project.")
        return redirect('staff_view_consultancy_project')
    
def delete_product_development(request, staff_id):
    product_development = Product_Development.objects.get(id=staff_id)
    try:
        product_development.delete()
        messages.success(request, "Product Development Deleted Successfully.")
        return redirect('staff_view_product_development')
    except:
        messages.error(request, "Failed to Delete Product Development.")
        return redirect('staff_view_product_development')

def delete_project_proposal(request, staff_id):
    project_proposal = Project_Proposal.objects.get(id=staff_id)
    try:
        project_proposal.delete()
        messages.success(request, "Project Proposal Deleted Successfully.")
        return redirect('staff_view_project_proposal')
    except:
        messages.error(request, "Failed to Delete Project Proposal.")
        return redirect('staff_view_project_proposal')
    
def delete_achievement(request, staff_id):
    achievement = Achievement.objects.get(id=staff_id)
    if achievement.cert_pdf:
        achievement.cert_pdf.delete()
    try:
        achievement.delete()
        messages.success(request, "Achievement Deleted Successfully.")
        return redirect('staff_view_achievements')
    except:
        messages.error(request, "Failed to Delete Achievement.")
        return redirect('staff_view_achievements')

def staff_add_journal_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_journal')
    else:
        # Get the currently logged-in staff member
        staff_obj = Staffs.objects.get(admin=request.user)

        # Retrieve form data
        title = request.POST.get('title')
        author = request.POST.get('author')
        department = request.POST.get('department')
        affiliating_institute = request.POST.get('affiliating_institute')
        journal_name = request.POST.get('journal_name')        
        year_of_publication = request.POST.get('year_of_publication')
        isbn_issn_number = request.POST.get('isbn_issn_number')
        doi_number = request.POST.get('doi_number')
        scopus_id = request.POST.get('scopus_id')
        journal_website = request.POST.get('journal_website')
        selected_indexes = request.POST.getlist('journal_index[]')
        journal_pdf = request.FILES.get('journal_pdf', None)

        # Check if 'Others' is selected
        if 'Others' in selected_indexes:
            # Get the value from 'other_journal_index' field
            other_journal_index = request.POST.get('other_journal_index', '')
            # Remove 'Others' from the selected indexes list
            selected_indexes.remove('Others')
            # Concatenate 'other_journal_index' with other selected checkboxes
            journal_index = ",".join(selected_indexes + [other_journal_index])
        else:
            # Create a comma-separated string of selected checkboxes
            journal_index = ",".join(selected_indexes)
            # Set 'other_journal_index' to None
            other_journal_index = None

        if not journal_pdf or not journal_pdf.name.endswith('.pdf'):
                messages.error(request, "Please upload a valid PDF file.")
                return redirect('staff_add_journal')

            # Check if the uploaded file is an instance of UploadedFile
        if not isinstance(journal_pdf, UploadedFile):
            messages.error(request, "Invalid file format.")
            return redirect('staff_add_')
        
        try:
            # Create a new Publication object with staff_id set to the currently logged-in staff member
            journal = Journal(
                staff_id=staff_obj,
                title=title,
                author=author,
                department=department,
                affiliating_institute=affiliating_institute,
                journal_name=journal_name,
                journal_index=journal_index,
                year_of_publication=year_of_publication,
                isbn_issn_number=isbn_issn_number,
                doi_number=doi_number,
                scopus_id=scopus_id,
                journal_website=journal_website,
                journal_pdf=journal_pdf
            )
            journal.save()
            messages.success(request, "Journal details saved successfully.")
            return redirect('staff_add_journal')
        except Exception as e:
            messages.error(request, f"Failed to save journal details: {str(e)}")
            return redirect('staff_add_journal')

def staff_add_conference_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_conference')
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        title = request.POST.get('title')
        author = request.POST.get('author')
        department = request.POST.get('department')
        affiliating_institute = request.POST.get('affiliating_institute')
        journal_name = request.POST.get('journal_name')        
        year_of_publication = request.POST.get('year_of_publication')
        isbn_issn_number = request.POST.get('isbn_issn_number')
        doi_number = request.POST.get('doi_number')
        scopus_id = request.POST.get('scopus_id')
        journal_website = request.POST.get('journal_website')
        selected_indexes = request.POST.getlist('journal_index[]')
        journal_pdf = request.FILES.get('journal_pdf', None)
        if 'Others' in selected_indexes:
            other_journal_index = request.POST.get('other_journal_index', '')
            selected_indexes.remove('Others')
            journal_index = ",".join(selected_indexes + [other_journal_index])
        else:
            journal_index = ",".join(selected_indexes)
            other_journal_index = None

        if not journal_pdf or not journal_pdf.name.endswith('.pdf'):
                messages.error(request, "Please upload a valid PDF file.")
                return redirect('staff_add_conference')

            # Check if the uploaded file is an instance of UploadedFile
        if not isinstance(journal_pdf, UploadedFile):
            messages.error(request, "Invalid file format.")
            return redirect('staff_add_conference')

        try:
            journal = Conference(
                staff_id=staff_obj,
                title=title,
                author=author,
                department=department,
                affiliating_institute=affiliating_institute,
                journal_name=journal_name,
                journal_index=journal_index,
                year_of_publication=year_of_publication,
                isbn_issn_number=isbn_issn_number,
                doi_number=doi_number,
                scopus_id=scopus_id,
                journal_website=journal_website,
                journal_pdf=journal_pdf
            )
            journal.save()
            messages.success(request, "Conference details saved successfully.")
            return redirect('staff_add_conference')
        except Exception as e:
            messages.error(request, f"Failed to save journal details: {str(e)}")
            return redirect('staff_add_conference')

def staff_add_book_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_add_book')
    else:
        # Retrieve the currently logged-in staff member
        staff_obj = Staffs.objects.get(admin=request.user)

        # Retrieve form data
        book_title = request.POST.get('book_title')
        author_name = request.POST.get('author_name')
        publisher_name = request.POST.get('publisher_name')
        isbn_no = request.POST.get('isbn_no')
        publication_date = request.POST.get('publication_date')
        affiliation_same = request.POST.get('affiliation_same') == 'True'

        try:
            # Create a new Book object with staff_id set to the currently logged-in staff member
            book = Book(
                staff_id=staff_obj,
                book_title=book_title,
                author_name=author_name,
                publisher_name=publisher_name,
                isbn_no=isbn_no,
                publication_date=publication_date,
                affiliation_same=affiliation_same
            )
            book.save()
            messages.success(request, "Book details saved successfully.")
            return redirect('staff_add_book')  # Make sure 'staff_add_book' is the correct URL name for the book addition page
        except Exception as e:
            messages.error(request, f"Failed to save book details: {str(e)}")
            return redirect('staff_add_book')

def staff_add_certifications(request):
    return render(request, 'staff_template/staff_add_certifications.html')
        
def staff_add_certifications_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_add_certifications')
    else:
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            staff_obj = Staffs.objects.get(admin=request.user)
            staff_name = request.POST.get('staff_name')
            certification_name = request.POST.get('certification_name')
            course_name = request.POST.get('course_name')
            duration_numeric = request.POST.get('duration_numeric')
            duration_unit = request.POST.get('duration_unit')
            duration = f"{duration_numeric} {duration_unit}"           
            certificate = request.FILES.get('certificate')

            # Check if a file is provided and if it's a PDF
            if not certificate or not certificate.name.endswith('.pdf'):
                messages.error(request, "Please upload a valid PDF file.")
                return redirect('staff_add_certifications')

            # Check if the uploaded file is an instance of UploadedFile
            if not isinstance(certificate, UploadedFile):
                messages.error(request, "Invalid file format.")
                return redirect('staff_add_certifications')

            certification = Certification(
                staff_id=staff_obj,
                staff_name=staff_name,
                certification_name=certification_name,
                course_name=course_name,
                duration=duration,
                end_date=end_date,
                start_date=start_date,
                certificate=certificate
            )
            certification.save()
            messages.success(request, "Certification details saved successfully.")
        except Exception as e:
            messages.error(request, f"Failed to save certification details: {str(e)}")
    return redirect('staff_add_certifications')



def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)
    try:
        current_experience = CurrentExperience.objects.get(id=staff.id)
    except CurrentExperience.DoesNotExist:
        current_experience = None
    context={
        "user": user,
        "staff": staff,
        "current_experience": current_experience
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        staffid = request.POST.get('staffid')
        address = request.POST.get('address')
        scopus_website = request.POST.get('scopus_website')
        google_website = request.POST.get('google_website')
        area_of_specialization = request.POST.get('area_of_specialization')
        salutation = request.POST.get('salutation') 
        designation = request.POST.get('designation')
        aadhar_no = request.POST.get('aadhar_no')
        pan_no = request.POST.get('pan_no')
        phone = request.POST.get('phone')
        profile_picture = request.FILES.get('profile_picture')



        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            customuser.staffid = staffid
            if password:
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            if profile_picture==None:
                pass
            elif staff.profile_picture:
                    staff.profile_picture.delete()
                    staff.profile_picture = profile_picture
            else:
                staff.profile_picture = profile_picture

            if len(aadhar_no) != 12 or not aadhar_no.isdigit():
                messages.error(request, "Invalid Aadhar Number")
                return redirect('staff_profile')
            staff.aadhar_no = aadhar_no

            if len(pan_no) != 10:
                messages.error(request, "Invalid PAN Number. PAN should be 10 characters long.")
                return redirect('staff_profile')
            
            staff.pan_no = pan_no
            staff.address = address
            staff.salutation = salutation
            staff.designation = designation
            staff.phone = phone
            staff.scopus_website = scopus_website 
            staff.google_website = google_website 
            
            if area_of_specialization:
                staff.area_of_specialization = None
                staff.area_of_specialization=area_of_specialization
            
            staff.save()

            degrees = request.POST.getlist('degree_type')
            streams = request.POST.getlist('qualifications[]')
            years = request.POST.getlist('year_gra')
            certificates = request.FILES.getlist('certificate')  # Handle multiple certificates

            for degree, stream, year, certificate in zip(degrees, streams, years, certificates):
                if degree and stream and year and certificate: 
                    qualification = Qualification.objects.create(
                        staff=staff,
                        degree=degree,
                        stream=stream,
                        year_of_graduation=year,
                        certificate=certificate
                    )
                
            organizations = request.POST.getlist('company[]')
            designations = request.POST.getlist('designation[]')
            from_dates = request.POST.getlist('from_date[]')
            to_dates = request.POST.getlist('to_date[]')
            work_place = request.POST.getlist('workplace[]')


            for organization, designation, from_date, to_date, workplace in zip(organizations, designations, from_dates, to_dates, work_place):
                if organization and designation and from_date and to_date and workplace: 
                    experience = Experience(
                        staff=staff,
                        organization=organization,
                        workplace=workplace,
                        designation=designation,
                        from_date=from_date,
                        to_date=to_date
                    )
                    experience.save()

            current_organization = "Panimalar Engineering College"
            current_from_date = request.POST.get('current_from_date')
            
            if current_organization and current_from_date:
                current_experience = CurrentExperience(
                    staff=staff,
                    organization=current_organization,
                    from_date=current_from_date
                )
                current_experience.save()
            else:
                messages.warning(request, "Current experience fields not provided. No changes were made.")

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except Exception as e:
            messages.error(request, f"Failed to Update Profile: {e}")
            return redirect('staff_profile')
        
        
def staff_add_AC(request):
    return render(request,"staff_template/staff_add_AC.html")

def staff_add_organized_AC(request):
    return render(request,"staff_template/staff_add_organized_AC.html")

def staff_add_organized_AC_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_organized_AC')  # Adjust the URL if needed
    else:
        # Get the currently logged-in staff member
        staff_obj = Staffs.objects.get(admin=request.user)

        # Retrieve form data
        event = request.POST.get('event')
        event_mode = request.POST.get('event_mode')
        title = request.POST.get('title')
        resource_person = request.POST.get('resource_person')
        club_name = request.POST.get('club_name')
        target_audience = request.POST.get('target_audience')
        count = request.POST.get('count')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        report_proof = request.FILES.get('report_proof', None)

        if not report_proof or not report_proof.name.endswith('.pdf'):
                messages.error(request, "Please upload a valid PDF file.")
                return redirect('staff_add_organized_AC')

            # Check if the uploaded file is an instance of UploadedFile
        if not isinstance(report_proof, UploadedFile):
            messages.error(request, "Invalid file format.")
            return redirect('staff_add_organized_AC')

        try:
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Create a new OrganizedAC object
            organized_ac = OrganizedAC(
                staff_id=staff_obj,
                event=event,
                event_mode=event_mode,
                title=title,
                resource_person=resource_person,
                club_name=club_name,
                target_audience=target_audience,
                count=count,
                start_date=start_date,
                end_date=end_date,
                report_proof=report_proof
            )
            organized_ac.save()
            messages.success(request, "Organized academic activity details saved successfully.")
            return redirect('staff_add_organized_AC')  # Adjust the URL if needed
        except Exception as e:
            messages.error(request, f"Failed to save organized academic activity details: {str(e)}")
            return redirect('staff_add_organized_AC')

def staff_add_attended_AC(request):
    return render(request,"staff_template/staff_add_attended_AC.html")

def staff_add_attended_AC_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_attended_AC')  # Adjust the URL if needed
    else:
        staff_obj = Staffs.objects.get(admin=request.user)
        event = request.POST.get('event')
        title = request.POST.get('title')
        college_name = request.POST.get('college_name')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        report_proof = request.FILES.get('report_proof', None)
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            organized_ac = AttendedAC(
                staff_id=staff_obj,
                event=event,
                title=title,
                college_name = college_name,
                start_date=start_date,
                end_date=end_date,
                report_proof=report_proof
            )
            organized_ac.save()
            messages.success(request, "Academic academic activity details saved successfully.")
            return redirect('staff_add_attended_AC')  # Adjust the URL if needed
        except Exception as e:
            messages.error(request, f"Failed to save organized Academic activity details: {str(e)}")
            return redirect('staff_add_attended_AC')
        
def download_staff_pdf(request, file_path):
    # Construct the full path to the PDF file
    # Construct the full file path
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    # Check if the file exists
    if os.path.exists(full_path):
        with open(full_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={os.path.basename(full_path)}'
            return response
    else:
        raise Http404("File not found")

@login_required
def qualifications_view(request,staff_id):
    try:
        staff = Staffs.objects.get(admin=request.user)
        qualifications = Qualification.objects.filter(staff=staff)
        experience=Experience.objects.filter(staff=staff)
        current_experience = CurrentExperience.objects.filter(staff=staff).first()
    except Staffs.DoesNotExist:
        staff = None
        current_experience=None
        qualifications = []
        experience=[]

    context = {
        'staff': staff,
        'qualifications': qualifications,
        'experience' : experience,
        'current_experience': current_experience
    }
    return render(request, 'staff_template/qualifications.html', context)

def staff_add_book_chapter(request):
    return render(request, 'staff_template/staff_add_book_chapter.html')


def staff_add_book_chapter_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_book_chapter')  # Adjust the URL if needed

    # Retrieve the currently logged-in staff member
    staff_obj = Staffs.objects.get(admin=request.user)

    # Retrieve form data
    author_name = request.POST.get('author_name')
    book_chapter_title = request.POST.get('book_chapter_title')
    publisher_name = request.POST.get('publisher_name')
    isbn_no = request.POST.get('isbn_no')
    month_year_publication = request.POST.get('month_year_publication')
    doi_if = request.POST.get('doi_if')
    is_scopus_indexed = request.POST.get('is_scopus_indexed') == 'True'
    paper_link = request.POST.get('paper_link')
    affil_institution_same = request.POST.get('affiliating_institution_same') == 'True'
    scopus_link = request.POST.get('scopus_link')
    

    try:
        # Create a new BookChapter object with staff_id set to the currently logged-in staff member
        book_chapter = BookChapter(
            staff_id=staff_obj,
            author_name=author_name,
            book_chapter_title=book_chapter_title,
            publisher_name=publisher_name,
            isbn_no=isbn_no,
            month_year_publication=month_year_publication,
            doi_if=doi_if,
            is_scopus_indexed=is_scopus_indexed,
            paper_link=paper_link,
            affiliating_institution_same=affil_institution_same,
            scopus_link=scopus_link
        )
        book_chapter.save()
        messages.success(request, "Book Chapter details saved successfully.")
        return redirect('staff_add_book_chapter')  # Adjust the URL if needed
    except Exception as e:
        messages.error(request, f"Failed to save Book Chapter details: {str(e)}")
        return redirect('staff_add_book_chapter') 

def staff_add_book(request):
    return render(request, 'staff_template/staff_add_book.html')

def staff_add_journal(request):
    return render(request, 'staff_template/staff_add_journal.html')

def staff_add_conference(request):
    return render(request, 'staff_template/staff_add_conference.html')

def staff_add_patent(request):
    return render(request, 'staff_template/staff_add_patent.html')


def staff_add_patent_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_patent')  # Adjust the URL if needed
    else:
        # Get the currently logged-in staff member
        staff_obj = Staffs.objects.get(admin=request.user)

        # Retrieve form data
        staff_name = request.POST.get('staff_name')
        co_authors = request.POST.get('co_authors')
        patent_name = request.POST.get('patent_name')
        country = request.POST.get('country')
        patent_number = request.POST.get('patent_number')
        month_and_year = request.POST.get('month_and_year')
        patent_link = request.POST.get('patent_link')
        proof_file = request.FILES.get('proof_file', None)

        if not proof_file or not proof_file.name.endswith('.pdf'):
                messages.error(request, "Please upload a valid PDF file.")
                return redirect('staff_add_patent')

            # Check if the uploaded file is an instance of UploadedFile
        if not isinstance(proof_file, UploadedFile):
            messages.error(request, "Invalid file format.")
            return redirect('staff_add_patent')

        try:
            # Create a new Patent object with staff_id set to the currently logged-in staff member
            patent = Patent(
                staff_id=staff_obj,
                staff_name=staff_name,
                co_authors=co_authors,
                patent_name=patent_name,
                country=country,
                patent_number=patent_number,
                month_and_year=month_and_year,
                patent_link=patent_link,
                proof_file=proof_file
            )
            patent.save()
            messages.success(request, "Patent details saved successfully.")
            return redirect('staff_add_patent')  # Adjust the URL if needed
        except Exception as e:
            messages.error(request, f"Failed to save patent details: {str(e)}")
            return redirect('staff_add_patent')

def staff_add_copyright(request):
    return render(request, 'staff_template/staff_add_copyright.html')
    
def staff_add_copyright_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_copyright')
    else:
        # Get the currently logged-in staff member
        staff_obj = Staffs.objects.get(admin=request.user)

        # Retrieve form data
        authors = request.POST.get('authors')
        work_title = request.POST.get('work_title')
        category = request.POST.get('category')
        filed_applied_date = request.POST.get('filed_applied_date')
        registered_published_date = request.POST.get('registered_published_date')
        status = request.POST.get('status')
        registration_no = request.POST.get('registration_no')
        dairy_no = request.POST.get('dairy_no')

        try:
            # Parse date strings to Python date objects
            filed_applied_date = dt.datetime.strptime(filed_applied_date, '%Y-%m-%d').date()
            registered_published_date = dt.datetime.strptime(registered_published_date, '%Y-%m-%d').date()

            # Create a new Copyright object with staff_id set to the currently logged-in staff member
            copyright = Copyright(
                staff_id=staff_obj,
                authors=authors,
                work_title=work_title,
                category=category,
                filed_applied_date=filed_applied_date,
                registered_published_date=registered_published_date,
                status=status,
                registration_no=registration_no,
                dairy_no=dairy_no
            )
            copyright.save()
            messages.success(request, "Copyright details saved successfully.")
            return redirect('staff_add_copyright')
        except Exception as e:
            messages.error(request, f"Failed to save copyright details: {str(e)}")
            return redirect('staff_add_copyright')
        
@login_required
def staff_contact_save(request):
    if request.method == 'POST':
        staff_name = request.POST.get('staff_name')
        email = request.user.email  # Fetch the email address of the logged-in staff member
        message = request.POST.get('message')

        try:
            send_mail(
                'Contact Us Form Submission from ',
                message,
                email,  # Use the email address of the logged-in staff member as the sender
                ['abisheks2505@gmail.com', 'arumugam.ak311@gmail.com', 'iantonygnanamuthu@gmail.com', 'abishekgopi20@gmail.com'],
                fail_silently=False
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('success_message')  # Redirect to success message page
        except Exception as e:
            messages.error(request, f"There was an error sending your message: {e}")

    return redirect('contact_us')

def success_message(request):
    return render(request, 'staff_template/success_message.html')