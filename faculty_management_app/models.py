from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    staffid = models.CharField(max_length=20, unique=True, blank=True, null=True)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    SALUTATION_CHOICES = [
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Dr', 'Dr'),
        ('Ms', 'Ms'),
    ]
    DESIGNATION_CHOICES = [
        ('Assistant Professor', 'Assistant Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Professor', 'Professor'),
    ]
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    aadhar_no = models.CharField(max_length=12, blank=True, null=True)
    pan_no = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=16, blank= True, null = True)
    scopus_website = models.URLField() 
    google_website = models.URLField()
    designation = models.CharField(max_length=30, choices=DESIGNATION_CHOICES, null=True, blank=True)
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    area_of_specialization = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/',null=True, blank=True)
    objects = models.Manager()

class Book(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=100)
    book_title = models.CharField(max_length=200)
    publisher_name = models.CharField(max_length=100)
    isbn_no = models.CharField(max_length=20)
    publication_date = models.CharField(max_length = 255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    affiliation_same = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'year_of_publication'
        if self.publication_date:
            year, month = map(int, self.publication_date.split('-'))

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)
    objects = models.Manager()

class Certification(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=100)
    certification_name = models.CharField(max_length=200)
    course_name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()    
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    certificate = models.FileField(upload_to='certificates/')
    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'start_date'
        if self.start_date:
            year = self.end_date.year
            month = self.end_date.month
            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"
        super().save(*args, **kwargs)
    objects = models.Manager()

    def _str_(self):
        return self.certification_name

class Experience(models.Model):
    staff = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name="experiences")
    organization = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    objects = models.Manager()
    
class CurrentExperience(models.Model):
    staff = models.OneToOneField(Staffs, on_delete=models.CASCADE, related_name="current_experience")
    organization = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True) 
    is_relieved = models.BooleanField(default=False) 
    objects = models.Manager()

class Patent(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    staff_name = models.CharField(max_length=255)
    co_authors = models.CharField(max_length=255)
    patent_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    patent_number = models.CharField(max_length=255)
    month_and_year = models.CharField(max_length=7)  # Assuming format YYYY-MM
    patent_link = models.URLField()
    proof_file = models.FileField(upload_to='patent_proof_files/', null=True, blank=True)
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'month_and_year'
        if self.month_and_year:
            year, month = map(int, self.month_and_year.split('-'))

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.patent_name

class BookChapter(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    book_chapter_title = models.CharField(max_length=200)
    publisher_name = models.CharField(max_length=100)
    isbn_no = models.CharField(max_length=20)
    month_year_publication = models.CharField(max_length=7)  # Assuming format like 'YYYY-MM'
    doi_if = models.CharField(max_length=20)
    is_scopus_indexed = models.BooleanField(default=False)
    paper_link = models.URLField(max_length=255)
    affiliating_institution_same = models.BooleanField(default=False)
    scopus_link = models.URLField(max_length=255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'month_year_publication'
        if self.month_year_publication:
            year, month = map(int, self.month_year_publication.split('-'))

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book_chapter_title} by {self.author_name}"
    
class Copyright(models.Model):
    staff_id = models.ForeignKey('Staffs', on_delete=models.CASCADE)
    authors = models.TextField()
    work_title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    filed_applied_date = models.DateField()
    registered_published_date = models.DateField()
    status = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=255)
    dairy_no = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'registered_published_date'
        if self.registered_published_date:
            year, month = self.registered_published_date.year, self.registered_published_date.month

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.work_title} by {self.authors}"
    
class Consultancy_Project(models.Model):
    staff_id = models.ForeignKey('Staffs', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    funding_agency = models.CharField(max_length=255)
    amount = models.CharField(max_length=20)
    status = models.CharField(max_length=255)

class Product_Development(models.Model):
    staff_id = models.ForeignKey('Staffs', on_delete=models.CASCADE)
    student_name = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    product_name = models.CharField(max_length=255)

class Project_Proposal(models.Model):
    staff_id = models.ForeignKey('Staffs', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    funding_agency = models.CharField(max_length=255)
    amount = models.CharField(max_length=20)
    status = models.CharField(max_length=255)

class Achievement(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    month_and_year = models.CharField(max_length=7)  
    cert_pdf = models.FileField(upload_to='achievement/pdfs/', null=True, blank=True)
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.month_and_year:
            year, month = map(int, self.month_and_year.split('-'))

            if month < 7: 
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)
    objects = models.Manager()
    
    def _str_(self):
        return self.title


    objects = models.Manager()
    
class Qualification(models.Model):
    staff = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name="qualifications")
    degree = models.CharField(max_length=100)
    stream = models.CharField(max_length=100)
    year_of_graduation = models.CharField(max_length=4) 
    certificate = models.FileField(upload_to='Qualification_Certificates/', null=True, blank=True)
    objects = models.Manager()

class Journal(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    affiliating_institute = models.CharField(max_length=255)
    journal_name = models.CharField(max_length=255)
    journal_index = models.CharField(max_length=255)
    other_journal_index = models.CharField(max_length=255, null=True, blank=True)
    year_of_publication = models.CharField(max_length = 255)
    isbn_issn_number = models.IntegerField()
    doi_number = models.CharField(max_length=255)
    scopus_id = models.CharField(max_length=255)
    journal_website = models.URLField()
    journal_pdf = models.FileField(upload_to='journal/pdfs/', null=True, blank=True) 

    
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'year_of_publication'
        if self.year_of_publication:
            year, month = map(int, self.year_of_publication.split('-'))

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)

    objects = models.Manager()

class Conference(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    affiliating_institute = models.CharField(max_length=255)
    journal_name = models.CharField(max_length=255)
    journal_index = models.CharField(max_length=255)
    other_journal_index = models.CharField(max_length=255, null=True, blank=True)
    year_of_publication = models.CharField(max_length = 255)
    isbn_issn_number = models.IntegerField()
    doi_number = models.CharField(max_length=255)
    scopus_id = models.CharField(max_length=255)
    journal_website = models.URLField()
    journal_pdf = models.FileField(upload_to='conference/pdfs/', null=True, blank=True) 

    
    academic_year = models.CharField(max_length=9, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'year_of_publication'
        if self.year_of_publication:
            year, month = map(int, self.year_of_publication.split('-'))

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)

    objects = models.Manager()
    
    def __str__(self):
        return f"{self.title} ({self.author})"
    
class OrganizedAC(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    event = models.CharField(max_length=255)
    event_mode = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    resource_person = models.CharField(max_length=255)
    club_name = models.CharField(max_length=255)
    target_audience = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    report_proof = models.FileField(upload_to='organized_ac_reports/', null=True, blank=True)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    no_of_days = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'start_date'
        if self.start_date:
            year = self.start_date.year
            month = self.start_date.month

            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"

        # Calculate the number of days between start_date and end_date
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.no_of_days = delta.days + 1  # Including both start and end dates

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class AttendedAC(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    event = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    college_name = models.CharField(max_length=255)
    report_proof = models.FileField(upload_to='attended_ac_reports/', null=True, blank=True)
    academic_year = models.CharField(max_length=9, null=True, blank=True)
    no_of_days = models.IntegerField(null=True, blank=True)
    def save(self, *args, **kwargs):
        # Set 'academic_year' based on 'start_date'
        if self.start_date:
            year = self.start_date.year
            month = self.start_date.month
            if month < 7:  # Before June
                self.academic_year = f"{year - 1}-{year}"
            else:
                self.academic_year = f"{year}-{year + 1}"
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.no_of_days = delta.days + 1  # Including both start and end dates
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
