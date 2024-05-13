from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.conf import settings
from django.apps import apps
from django.db.models import Count, Q, FileField, ImageField
from django.utils import timezone
import os
import datetime
from datetime import date

from faculty_management_app.models import CustomUser, Staffs, Journal,Conference, Book, BookChapter,Experience, Copyright, Patent, AttendedAC, OrganizedAC, Certification, Qualification, CurrentExperience,Consultancy_Project,Project_Proposal,Product_Development,Achievement


def staff_detail(request, id):
    # staff = get_object_or_404(Staffs, admin__id=id)
    staff = Staffs.objects.get(admin__id=id)
    journal_count = Journal.objects.filter(staff_id=staff.id).count()
    conference_count = Conference.objects.filter(staff_id=staff.id).count()
    book_count = Book.objects.filter(staff_id=staff.id).count()
    book_chapter_count = BookChapter.objects.filter(staff_id=staff.id).count()
    copyright_count = Copyright.objects.filter(staff_id=staff.id).count()
    patent_count= Patent.objects.filter(staff_id=staff.id).count()
    consultancy_project_count= Consultancy_Project.objects.filter(staff_id=staff.id).count()
    product_developed_count= Product_Development.objects.filter(staff_id=staff.id).count()
    project_proposal_count= Project_Proposal.objects.filter(staff_id=staff.id).count()

    experience=Experience.objects.filter(staff=staff)
    qualifications = Qualification.objects.filter(staff_id=staff.id)
    current_experience = CurrentExperience.objects.filter(staff_id=staff.id).first()
    total_experience_days = 0
    
    if current_experience:
        duration = timezone.now().date() - current_experience.from_date
        total_experience_days += duration.days
    
    # Convert days to years, months, and days
    years, remainder = divmod(total_experience_days, 365)
    months, days = divmod(remainder, 30)  # Simplified approximation
    context = {
        "staff":staff,
        "journal_count" : journal_count,
        "conference_count" : conference_count,
        "book_count" : book_count,
        'book_chapter_count' : book_chapter_count,
        'copyright_count' : copyright_count,
        "patent_count" : patent_count,
        "qualifications":qualifications,
        "experience": experience,
        "experience_years": years,
        "experience_months": months,
        "current_experience": current_experience,
        "consultancy_project_count":consultancy_project_count,
        "project_proposal_count": project_proposal_count,
        "product_developed_count": product_developed_count,
    }
    return render(request, 'hod_template/staff_detail_template.html', context)

def get_project_counts_by_year():
    # Define the start and end months for an academic year
    academic_year_start_month = 7  
    academic_year_end_month = 6    

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
    project_count=[]
    for year in academic_years:
        count=Project_Proposal.objects.filter(academic_year=year).count() + Product_Development.objects.filter(academic_year=year).count() + Consultancy_Project.objects.filter(academic_year=year).count()
        project_count.append(count)
    return academic_years,project_count

def get_publication_counts_by_year():
    # Define the start and end months for an academic year
    academic_year_start_month = 7  
    academic_year_end_month = 6    

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
        count=Book.objects.filter(academic_year=year).count()+BookChapter.objects.filter(academic_year=year).count()+Copyright.objects.filter(academic_year=year).count()+Patent.objects.filter(academic_year=year).count()+Journal.objects.filter(academic_year=year).count()+Conference.objects.filter(academic_year=year).count()
        publication_count.append(count)
    return academic_years,publication_count

def filter_faculty_by_experience(request):
    if request.method == 'GET':
        years = int(request.GET.get('years', 0))
        operator = request.GET.get('operator', '=')
        
        # Filter staff based on years and operator
        staff_filtered = Staffs.objects.all()

        if operator == '<':
            staff_filtered = [staff for staff in staff_filtered if get_total_experience(staff) < years]
        elif operator == '=':
            staff_filtered = [staff for staff in staff_filtered if get_total_experience(staff) == years]
        elif operator == '>':
            staff_filtered = [staff for staff in staff_filtered if get_total_experience(staff) > years]

        # Prepare data to be sent as JSON response
        experience_data = []
        pie_chart_data = []  # Initialize pie_chart_data list
        for staff in staff_filtered:
            staff_data = {
                'staffName': staff.admin.username,
                'designation': staff.designation,
                'experiences': get_total_experience(staff),
            }
            experience_data.append(staff_data)
            
            # Add staff data to pie_chart_data
            pie_chart_data.append({
                'staffName': staff.admin.username,
                'experiences': get_total_experience(staff),
            })

        data = {
            'years' : years,
            'operator' : operator,
            'experiences': experience_data,
            'pie_chart_data': pie_chart_data,  # Add pie_chart_data to response
        }    

        return JsonResponse(data)


def get_total_experience(staff):
    experiences = Experience.objects.filter(staff=staff)
    current_experience = CurrentExperience.objects.filter(staff=staff).first()

    total_experience_days = 0
    for experience in experiences:
        duration = experience.to_date - experience.from_date
        total_experience_days += duration.days

    if current_experience:
        duration = timezone.now().date() - current_experience.from_date
        total_experience_days += duration.days

    years, remainder = divmod(total_experience_days, 365)

    return years

def relieve_staff(request, id):  # Assuming `id` is the staff's admin ID passed from the URL.
    try:
        staff = Staffs.objects.get(admin__id=id)
        current_experience = CurrentExperience.objects.filter(staff=staff).first()
        if current_experience:
            if not current_experience.is_relieved:
                current_experience.to_date = datetime.datetime.now()
                current_experience.is_relieved = True
                current_experience.save()
                messages.success(request, "Faculty Relieved Successfully.")
            else:
                messages.success(request, "Faculty already Relieved.")
        else:
            messages.error(request, "No current experience found for the faculty.")
    except Staffs.DoesNotExist:
        messages.error(request, "Staff with provided ID does not exist.")
    except Exception as e:
        messages.error(request, f"Failed to relieve faculty: {str(e)}")
    
    return redirect('staff_detail', id=id) 

def view_patents(request):
    patents = Patent.objects.all()
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = patents.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        patents = patents.filter(academic_year=selected_academic_year)

    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        patents = patents.filter(staff_id=selected_staff_id)   

    context = {
        'patents': patents,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        'staffs':staffs,
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }

    return render(request, "hod_template/view_patents.html", context)




def download_proof(request, file_path):
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
    
def download_pdf(request, pdf_file):
    # Define the directory where the PDF files are stored
    pdf_directory = os.path.join(settings.MEDIA_ROOT, 'pdf')  # Assuming PDF files are stored in the 'pdf' directory of your media root

    # Construct the absolute path to the requested PDF file
    pdf_path = os.path.join(pdf_directory, pdf_file)

    # Check if the requested PDF file exists
    if os.path.exists(pdf_path):
        # Open the file in binary mode for reading
        with open(pdf_path, 'rb') as pdf:
            # Read the contents of the file
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            # Set the content-disposition header to force download
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(pdf_path))
            return response
    else:
        # Return a 404 error if the file does not exist
        return HttpResponse('File not found', status=404)

def get_publication_counts_by_staff(academic_year=None):
    staff_data = []
    for staff in Staffs.objects.all():
        # Initialize publication counts
        journal_count = conference_count = book_count = book_chapter_count = patent_count = copyright_count = 0
        
        # Filter based on the academic year if provided
        filter_args = {'academic_year': academic_year} if academic_year else {}

        # Assuming there is a direct relation from publications to staffs (adjust as necessary)
        journal_count = Journal.objects.filter(author=staff, **filter_args).count()
        conference_count = Conference.objects.filter(author=staff, **filter_args).count()
        book_count = Book.objects.filter(author=staff, **filter_args).count()
        book_chapter_count = BookChapter.objects.filter(author=staff, **filter_args).count()
        patent_count = Patent.objects.filter(author=staff, **filter_args).count()
        copyright_count = Copyright.objects.filter(author=staff, **filter_args).count()

        # Combine counts
        total_publications = journal_count + conference_count + book_count + book_chapter_count + patent_count + copyright_count
        
        staff_data.append({
            'staffName': staff.admin.username,
            'designation': staff.designation,
            'publications': {
                'Journals': journal_count,
                'Conferences': conference_count,
                'Books': book_count,
                'Book Chapters': book_chapter_count,
                'Patents': patent_count,
                'Copyrights': copyright_count,
                'Total': total_publications
            }
        })

    return staff_data

def aboutus(request):
    return render(request, "hod_template/aboutus.html")

def get_academic_years():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    if current_month >= 7:  # If current month is June or later
        next_year = current_year + 1
    else:
        next_year = current_year
    return [f"{year}-{year + 1}" for year in range(2019, next_year)]

def statistical_table(request):
    staff_members = Staffs.objects.all()

    academic_years = get_academic_years()
    selected_academic_year = request.GET.get('academic_year')

    statistics = []
    if selected_academic_year and selected_academic_year != "All":
        # If specific year is selected, count only for that year
        for staff_member in staff_members:
            journal_count = Journal.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            conference_count = Conference.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            book_count = Book.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            book_chapter_count = BookChapter.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            copyright_count = Copyright.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            patent_count = Patent.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            certification_count = Certification.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            attended_ac_count = AttendedAC.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            organized_ac_count = OrganizedAC.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            consultancy_project_count = Consultancy_Project.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            project_proposal_count = Project_Proposal.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            product_development_count = Product_Development.objects.filter(staff_id=staff_member, academic_year=selected_academic_year).count()
            

            statistics.append({
                'staff_member': staff_member,
                'journal_count': journal_count,
                'conference_count': conference_count,
                'book_count': book_count,
                'book_chapter_count': book_chapter_count,
                'copyright_count': copyright_count,
                'patent_count': patent_count,
                'certification_count': certification_count,
                'attended_ac_count': attended_ac_count,
                'organized_ac_count': organized_ac_count,
                'consultancy_project_count' : consultancy_project_count,
                'project_proposal_count' : project_proposal_count,
                'product_development_count' : product_development_count
            })
    else:
        # If "All" is selected or no year is selected, count for all years
        for staff_member in staff_members:
            journal_count = Journal.objects.filter(staff_id=staff_member).count()
            conference_count = Conference.objects.filter(staff_id=staff_member).count()
            book_count = Book.objects.filter(staff_id=staff_member).count()
            book_chapter_count = BookChapter.objects.filter(staff_id=staff_member).count()
            copyright_count = Copyright.objects.filter(staff_id=staff_member).count()
            patent_count = Patent.objects.filter(staff_id=staff_member).count()
            certification_count = Certification.objects.filter(staff_id=staff_member).count()
            attended_ac_count = AttendedAC.objects.filter(staff_id=staff_member).count()
            organized_ac_count = OrganizedAC.objects.filter(staff_id=staff_member).count()
            consultancy_project_count = Consultancy_Project.objects.filter(staff_id=staff_member).count()
            product_development_count = Product_Development.objects.filter(staff_id=staff_member).count()
            project_proposal_count = Project_Proposal.objects.filter(staff_id=staff_member).count()


            statistics.append({
                'staff_member': staff_member,
                'journal_count': journal_count,
                'conference_count': conference_count,
                'book_count': book_count,
                'book_chapter_count': book_chapter_count,
                'copyright_count': copyright_count,
                'patent_count': patent_count,
                'certification_count': certification_count,
                'attended_ac_count': attended_ac_count,
                'organized_ac_count': organized_ac_count,
                'consultancy_project_count' : consultancy_project_count,
                'project_proposal_count':project_proposal_count,
                'product_development_count':product_development_count

            })

    context = {
        'statistics': statistics,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
    }

    return render(request, 'hod_template/statistical_table.html', context)


def fetch_publications(request):
    if request.method == 'GET':
        academic_year = request.GET.get('year', 'All')
        if academic_year != 'All':
            year_filter = {'academic_year': academic_year}
        else:
            year_filter = {}
        
        publications_data = []
        for staff in Staffs.objects.all(): 
            staff_data = {
                'staffName': staff.admin.username,
                'designation': staff.designation,
                'publications': {
                    'Journals': Journal.objects.filter(staff_id=staff.id, **year_filter).count(),
                    'Conferences': Conference.objects.filter(staff_id=staff.id, **year_filter).count(),
                    'Books': Book.objects.filter(staff_id=staff.id, **year_filter).count(),
                    'Book Chapters': BookChapter.objects.filter(staff_id=staff.id, **year_filter).count(),
                    'Patents': Patent.objects.filter(staff_id=staff.id, **year_filter).count(),
                    'Copyrights': Copyright.objects.filter(staff_id=staff.id, **year_filter).count(),
                }
            }
            publications_data.append(staff_data)
        
        pie_chart_data = {
            'Journals': sum(item['publications']['Journals'] for item in publications_data),
            'Conferences': sum(item['publications']['Conferences'] for item in publications_data),
            'Books': sum(item['publications']['Books'] for item in publications_data),
            'Book Chapters': sum(item['publications']['Book Chapters'] for item in publications_data),
            'Patents': sum(item['publications']['Patents'] for item in publications_data),
            'Copyrights': sum(item['publications']['Copyrights'] for item in publications_data),
        }
        
        data = {
            'academic_year': academic_year,
            'publications': publications_data,
            'pie_chart_data': pie_chart_data,
        }
        
        return JsonResponse(data)


def admin_home(request):
    staff_count = Staffs.objects.all().count()
    journal_count = Journal.objects.all().count()
    conference_count = Conference.objects.all().count()
    book_count = Book.objects.all().count()
    book_chapter_count = BookChapter.objects.all().count()
    copyright_count = Copyright.objects.all().count()
    patent_count= Patent.objects.all().count()
    total_count = journal_count+conference_count+book_count + book_chapter_count+copyright_count+patent_count
    attended_count = AttendedAC.objects.all().count()
    organized_count = OrganizedAC.objects.all().count()
    total_ac_count = attended_count + organized_count
    consultancy_project_count=Consultancy_Project.objects.all().count()
    product_development_count=Product_Development.objects.all().count()
    project_proposals_count=Project_Proposal.objects.all().count()
    total_project_count=consultancy_project_count+product_development_count+project_proposals_count
    total_certification_count = Certification.objects.all().count()
    product_developed_count = Product_Development.objects.all().count()


    staff_name_list = []

    staffs = Staffs.objects.all()
    for staff in staffs:
        staff_name_list.append(staff.admin.first_name)
    
    staffs = Staffs.objects.all()
    
    # Get data for the bar chart
    academic_years,publication_count = get_publication_counts_by_year()
    scopus_count = get_scopus_counts_by_year()
    fdp_count = get_fdp_by_year()

    context = {
        "staff_count": staff_count,
        "staff_name_list": staff_name_list,
        "Staffs": staffs,
        "academic_years": academic_years,
        "total_count": total_count,
        'publication_count': publication_count,
        "journal_count": journal_count,
        "conference_count": conference_count,
        'book_count' : book_count,
        'book_chapter_count' : book_chapter_count,
        "patent_count": patent_count,
        'copyright_count' : copyright_count,
        'attended_count' : attended_count,
        'organized_count' :organized_count,
        'total_count' : total_count,
        'total_ac_count' : total_ac_count,
        'total_certification_count':total_certification_count,
        'consultancy_project_count':consultancy_project_count,
        'product_development_count':product_development_count,
        'project_proposals_count':project_proposals_count,
        'total_project_count':total_project_count,
        'product_developed_count' : product_developed_count,
        'scopus_count' : scopus_count,
        'fdp_count' : fdp_count,
    }
    return render(request, "hod_template/home_content.html", context)

def get_fdp_by_year():
    academic_year_start_month = 7  
    academic_year_end_month = 6    
    current_date = date.today()
    if current_date.month < academic_year_start_month:
        current_academic_year = f"{current_date.year - 1}-{current_date.year}"
    else:
        current_academic_year = f"{current_date.year}-{current_date.year + 1}"
		
    academic_years = [f"{year}-{year + 1}" for year in range(current_date.year - 5, current_date.year)]
    if current_date.month >= academic_year_start_month:
        academic_years.append(current_academic_year)
    fdp_count=[]
    for year in academic_years:
        count=AttendedAC.objects.filter(academic_year=year, event='FDP').count()
        fdp_count.append(count)
    return fdp_count

def get_scopus_counts_by_year():
    academic_year_start_month = 7  
    academic_year_end_month = 6    

    current_date = date.today()

    if current_date.month < academic_year_start_month:
        current_academic_year = f"{current_date.year - 1}-{current_date.year}"
    else:
        current_academic_year = f"{current_date.year}-{current_date.year + 1}"

    academic_years = [f"{year}-{year + 1}" for year in range(current_date.year - 5, current_date.year)]
    # If the current date is after the start of the new academic year, add it to the list
    if current_date.month >= academic_year_start_month:
        academic_years.append(current_academic_year)
    
    scopus_counts = []
    for year in academic_years:
        try:
            # Count publications where 'Scopus' is one of the values in the 'journal_index' field
            journal_count = Journal.objects.filter(academic_year=year, journal_index__contains='Scopus').count()
            conference_count = Conference.objects.filter(academic_year=year, journal_index__contains='Scopus').count()
            scopus_counts.append(journal_count + conference_count)
        except Exception as e:
            # Handle exceptions such as database errors
            print(f"Error processing year {year}: {e}")
            scopus_counts.append(0)  # Append 0 count if there's an error

    return scopus_counts

def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        salutation = request.POST.get('salutation')
        password = request.POST.get('password')
        address = request.POST.get('address')
        staffid = request.POST.get('staffid')

        try:
            user = CustomUser.objects.create_user(username=username, staffid=staffid, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.staffs.salutation = salutation
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except ValidationError as e:
            print(f"Validation Error: {e}")
            messages.error(request, f"Validation Error: {e}")
            return redirect('add_staff')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f"Failed to Add Staff: {e}")
            return redirect('add_staff')


def calculate_experience(from_date, to_date=None):
    """Calculate experience in years, months, and days."""
    if not to_date:
        to_date = timezone.now().date()  # Use current date if to_date is None
    total_days = (to_date - from_date).days
    years, remainder = divmod(total_days, 365)
    months, days = divmod(remainder, 30)  # Simplified approximation
    return years, months, days

def manage_staff(request):
    staffs = Staffs.objects.select_related('current_experience').prefetch_related('experiences', 'qualifications').all()

    for staff in staffs:
        total_years = total_months = total_days = 0

        # Calculate experience from past experiences
        for experience in staff.experiences.all():
            years, months, days = calculate_experience(experience.from_date, experience.to_date)
            total_years += years
            total_months += months
            total_days += days

        # Normalize months and days into years and months
        extra_months, total_days = divmod(total_days, 30)
        total_months += extra_months
        extra_years, total_months = divmod(total_months, 12)
        total_years += extra_years

        # Store total past experience (before adding current experience)
        staff.past_experience_years = total_years
        staff.past_experience_months = total_months
        staff.past_experience_days = total_days

        # Calculate current experience
        if hasattr(staff, 'current_experience'):
            current_experience = staff.current_experience
            current_years, current_months, current_days = calculate_experience(current_experience.from_date, current_experience.to_date)
            
            # Add current experience to total
            total_years += current_years
            total_months += current_months
            total_days += current_days

            # Normalize again after adding current experience
            extra_months, total_days = divmod(total_days, 30)
            total_months += extra_months
            extra_years, total_months = divmod(total_months, 12)
            total_years += extra_years

            # Attach the calculated current experience to the staff object
            staff.current_experience_years = current_years
            staff.current_experience_months = current_months
            staff.current_experience_days = current_days

        else:  # If there's no current experience, set them to zero
            staff.current_experience_years = 0
            staff.current_experience_months = 0
            staff.current_experience_days = 0

        # Attach the calculated total experience to the staff object
        staff.total_experience_years = total_years
        staff.total_experience_months = total_months
        staff.total_experience_days = total_days

    context = {
        "staffs": staffs,
    }
    return render(request, "hod_template/manage_staff_template.html", context)



def view_publications(request):
    Staff=Staffs.objects.all()

    journal_count = Journal.objects.all().count()
    conference_count = Conference.objects.all().count()
    book_count = Book.objects.all().count()
    book_chapter_count = BookChapter.objects.all().count()
    copyright_count = Copyright.objects.all().count()
    patent_count = Patent.objects.all().count()
    total_count = journal_count +conference_count +book_count + book_chapter_count+patent_count+copyright_count
        
    academic_years,publication_count = get_publication_counts_by_year()


    context = {
        'Staff':Staff,
        'journal_count': journal_count,
        'conference_count': conference_count,
        'book_count': book_count,
        'book_chapter_count': book_chapter_count,
        "patent_count":patent_count,
        'copyright_count': copyright_count,
        'total_count': total_count,
        'academic_years' : academic_years,
        'publication_count' : publication_count,
    }

    return render(request, "hod_template/view_publications_template.html", context)

def view_books(request):
    books = Book.objects.all()
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = books.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        books = books.filter(academic_year=selected_academic_year)

    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        books = books.filter(staff_id=selected_staff_id) 

    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('book')
    )
    publications_count_per_year = books.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        'books': books,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        "staff_queryset" : staff_queryset,
        "publications_count_per_year" : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }

    return render(request, "hod_template/view_books.html", context)

def view_certifications(request):
    certifications = Certification.objects.all()
    staff = Staffs.objects.all()
    academic_years = certifications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    selected_academic_year = request.GET.get('academic_year', '')
    if selected_academic_year:
        certifications = certifications.filter(academic_year=selected_academic_year)
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        certifications = certifications.filter(staff_id=selected_staff_id)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('certification')
    )
    publications_count_per_year = certifications.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        'certifications': certifications,
        'staff': staff,
        'academic_years': academic_years,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'selected_academic_year': selected_academic_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request, "hod_template/view_certifications.html", context)

def view_achievements(request):    
    achievements = Achievement.objects.all()
    academic_years = achievements.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    selected_academic_year = request.GET.get('academic_year', '')
    
    if selected_academic_year:
        achievements = achievements.filter(academic_year=selected_academic_year)
        
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        achievements = achievements.filter(staff_id=selected_staff_id) 

    context = {
        'achievements': achievements,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        'staffs': staffs,  

    }
    return render(request, "hod_template/view_achievements.html", context)

def view_patents(request):
    patents = Patent.objects.all()
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = patents.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        patents = patents.filter(academic_year=selected_academic_year)
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        patents = patents.filter(staff_id=selected_staff_id)

    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('patent')
    )
    publications_count_per_year = patents.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        'patents': patents,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }

    return render(request, "hod_template/view_patents.html", context)

def view_book_chapters(request):
    book_chapters = BookChapter.objects.all()
    staff = Staffs.objects.all()
    
    academic_years = book_chapters.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        book_chapters = book_chapters.filter(academic_year=selected_academic_year)

    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        book_chapters = book_chapters.filter(staff_id=selected_staff_id)  

    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('bookchapter')
    )
    publications_count_per_year = book_chapters.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        'book_chapters': book_chapters,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }

    return render(request, "hod_template/view_bookChapters_template.html", context)

def view_copyrights(request):
    copyrights = Copyright.objects.all()
    staff = Staffs.objects.all()
    
    # Get distinct academic years for filter options
    academic_years = copyrights.order_by('academic_year').values_list('academic_year', flat=True).distinct()

    selected_academic_year = request.GET.get('academic_year', '')

    if selected_academic_year:
        copyrights = copyrights.filter(academic_year=selected_academic_year)

    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        copyrights = copyrights.filter(staff_id=selected_staff_id)  

    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('copyright')
    )
    publications_count_per_year = copyrights.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        'copyrights': copyrights,
        'staff': staff,
        'academic_years': academic_years,
        'selected_academic_year': selected_academic_year,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }

    return render(request, "hod_template/view_copyrights.html", context)

def view_journal(request):
    publications = Journal.objects.all()

    academic_years = publications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        publications = publications.filter(academic_year=selected_academic_year)
    
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        publications = publications.filter(staff_id=selected_staff_id)  
    
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('journal')
    )
    publications_count_per_year = publications.values('academic_year').annotate(publication_count=Count('id'))

    context = {
        'publications': publications,
        'academic_years': academic_years,
        'staff_queryset': staff_queryset,
        'publications_count_per_year': publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request, "hod_template/view_journal.html", context)


def view_conference(request):
    publications = Conference.objects.all()

    academic_years = publications.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        publications = publications.filter(academic_year=selected_academic_year)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('conference')
    )
    publications_count_per_year = publications.values('academic_year').annotate(publication_count=Count('id'))
    
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        publications = publications.filter(staff_id=selected_staff_id)  

    context = {
        'publications': publications,
        'academic_years': academic_years,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request, "hod_template/view_conference.html",context)

def view_academic_contribution(request):
    attended_count = AttendedAC.objects.all().count()
    organized_count = OrganizedAC.objects.all().count()

    academic_years,attended_ac_count = get_attended_ac_counts_by_year()
    organized_ac_count = get_organized_ac_counts_by_year()

    context = {
        "attended_count": attended_count,
        "organized_count" : organized_count,
        "academic_years" : academic_years,
        "attended_ac_count" : attended_ac_count,
        "organized_ac_count" : organized_ac_count,
    }
    return render(request, "hod_template/view_academic_contribution.html",context)

def get_attended_ac_counts_by_year():
    academic_year_start_month = 7  
    academic_year_end_month = 6    
    current_date = date.today()
    if current_date.month < academic_year_start_month:
        current_academic_year = f"{current_date.year - 1}-{current_date.year}"
    else:
        current_academic_year = f"{current_date.year}-{current_date.year + 1}"
		
    academic_years = [f"{year}-{year + 1}" for year in range(current_date.year - 5, current_date.year)]
    if current_date.month >= academic_year_start_month:
        academic_years.append(current_academic_year)
    attended_ac_count=[]
    for year in academic_years:
        count=AttendedAC.objects.filter(academic_year=year).count()
        attended_ac_count.append(count)
    return academic_years,attended_ac_count

def get_organized_ac_counts_by_year():
    academic_year_start_month = 7  
    academic_year_end_month = 6    
    current_date = date.today()
    if current_date.month < academic_year_start_month:
        current_academic_year = f"{current_date.year - 1}-{current_date.year}"
    else:
        current_academic_year = f"{current_date.year}-{current_date.year + 1}"
		
    academic_years = [f"{year}-{year + 1}" for year in range(current_date.year - 5, current_date.year)]
    if current_date.month >= academic_year_start_month:
        academic_years.append(current_academic_year)
    organized_ac_count=[]
    for year in academic_years:
        count=OrganizedAC.objects.filter(academic_year=year).count()
        organized_ac_count.append(count)
        
    return organized_ac_count

def view_attended_AC(request):
    attended_ac = AttendedAC.objects.all()
    academic_years = attended_ac.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    
    if selected_academic_year:
        attended_ac = attended_ac.filter(academic_year=selected_academic_year)

    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        attended_ac = attended_ac.filter(staff_id=selected_staff_id)

    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('attendedac')
    )
    publications_count_per_year = attended_ac.values('academic_year').annotate(publication_count=Count('id'))
    context = {
        "attended_ac": attended_ac,
        'academic_years': academic_years,
        "staff_queryset" : staff_queryset,
        "publications_count_per_year" : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request, "hod_template/view_attended_AC.html",context)

def view_organized_AC(request):
    organized_ac = OrganizedAC.objects.all()
    academic_years = organized_ac.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        organized_ac = organized_ac.filter(staff_id=selected_staff_id)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('organizedac')
    )
    publications_count_per_year = organized_ac.values('academic_year').annotate(publication_count=Count('id'))
    if selected_academic_year:
        organized_ac = organized_ac.filter(academic_year=selected_academic_year)
    context={
        "organized_ac" : organized_ac,
        'academic_years': academic_years,
        "staff_queryset" : staff_queryset,
        "publications_count_per_year" : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request,"hod_template/view_organized_AC.html",context)

def view_projects(request):
    consultancy_project_count=Consultancy_Project.objects.all().count()
    product_development_count=Product_Development.objects.all().count()
    project_proposals_count=Project_Proposal.objects.all().count()
    academic_years, project_count = get_project_counts_by_year()

    context={
        'consultancy_project_count':consultancy_project_count,
        'product_development_count':product_development_count,
        'project_proposals_count' : project_proposals_count,
        'academic_years' : academic_years,
        'project_count' : project_count,
    }
    return render(request,"hod_template/view_projects.html",context)

def view_consultancy_project(request):
    consultancy_project=Consultancy_Project.objects.all()
    academic_years = consultancy_project.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        consultancy_project = consultancy_project.filter(staff_id=selected_staff_id)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('consultancy_project')
    )
    publications_count_per_year = consultancy_project.values('academic_year').annotate(publication_count=Count('id'))
    if selected_academic_year:
        consultancy_project = consultancy_project.filter(academic_year=selected_academic_year)
    context={
        'consultancy_project':consultancy_project,
        'academic_years' : academic_years,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request,'hod_template/view_consultancy_project.html',context)

def view_product_development(request):
    product_development=Product_Development.objects.all()
    academic_years = product_development.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        product_development = product_development.filter(staff_id=selected_staff_id)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('product_development')
    )
    publications_count_per_year = product_development.values('academic_year').annotate(publication_count=Count('id'))
    if selected_academic_year:
        product_development = product_development.filter(academic_year=selected_academic_year)
    context={
        'product_development':product_development,
        'academic_years' : academic_years,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request,'hod_template/view_product_development.html',context)

def view_project_proposal(request):
    project_proposal=Project_Proposal.objects.all()
    academic_years = project_proposal.order_by('academic_year').values_list('academic_year', flat=True).distinct()
    
    selected_academic_year = request.GET.get('academic_year')
    staffs = Staffs.objects.all()
    
    selected_staff_id = request.GET.get('staff_name')
    
    if selected_staff_id:
        project_proposal = project_proposal.filter(staff_id=selected_staff_id)
    staff_queryset = Staffs.objects.annotate(
        publication_count=Count('project_proposal')
    )
    publications_count_per_year = project_proposal.values('academic_year').annotate(publication_count=Count('id'))
    if selected_academic_year:
        project_proposal = project_proposal.filter(academic_year=selected_academic_year)
    context={
        'project_proposal':project_proposal,
        'academic_years' : academic_years,
        'staff_queryset' : staff_queryset,
        'publications_count_per_year' : publications_count_per_year,
        'staffs': staffs,  
        'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 
    }
    return render(request,'hod_template/view_project_proposal.html',context)

def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        staffid= request.POST.get('staffid')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.staffid = staffid
            user.email = email
            user.username = username
            user.phone = phone
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)


def delete_staff(request, staff_id):
    staff = CustomUser.objects.get(id=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    # You can access first_name and last_name like this
    first_name = user.first_name
    last_name = user.last_name

    context = {
        "user": user,
        "first_name": first_name,
        "last_name": last_name,
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.phone = phone
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')    

def staff_profile(request):
    pass

