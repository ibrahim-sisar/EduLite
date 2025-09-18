import json
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your models here.

# --- Notes model ---
User = get_user_model()
# get_user_model() is needed so if we decide to not use the default user model in the future it does'nt cause any problems in this model
class Notes(models.Model):
    """Stored Notes in the database"""
    # Subject and course choices keep being added as subject and courses add on the site
    # Subject, Courseand level choices make filtering and searching for notes much easier and faster
    SUBJECT_CHOICES = [
    ("math", "Mathematics"),
    ("physics", "Physics"),
    ("chemistry", "Chemistry"),
    ("biology", "Biology"),
    ("cs", "Computer Science"),
    ("it", "Information Technology"),
    ("engineering", "Engineering"),
    ("datasci", "Data Science"),
    ("ai", "Artificial Intelligence"),
    ("envsci", "Environmental Science"),
    ("astronomy", "Astronomy"),
    ("stats", "Statistics"),
    ("robotics", "Robotics"),
    ("electronics", "Electronics"),
    ("psych", "Psychology"),
    ("sociology", "Sociology"),
    ("polisci", "Political Science"),
    ("economics", "Economics"),
    ("anthropology", "Anthropology"),
    ("intlrel", "International Relations"),
    ("criminology", "Criminology"),
    ("history", "History"),
    ("philosophy", "Philosophy"),
    ("literature", "Literature"),
    ("linguistics", "Linguistics"),
    ("religion", "Religious Studies"),
    ("cultural", "Cultural Studies"),
    ("classics", "Classics"),
    ("visualart", "Visual Arts"),
    ("music", "Music"),
    ("performing", "Performing Arts"),
    ("architecture", "Architecture"),
    ("design", "Graphic Design"),
    ("film", "Film & Media Studies"),
    ("photo", "Photography"),
    ("fashion", "Fashion Design"),
    ("business", "Business Administration"),
    ("accounting", "Accounting"),
    ("finance", "Finance"),
    ("marketing", "Marketing"),
    ("hrm", "Human Resource Management"),
    ("entrepreneurship", "Entrepreneurship"),
    ("project", "Project Management"),
    ("supplychain", "Supply Chain Management"),
    ("education", "Education"),
    ("earlyedu", "Early Childhood Education"),
    ("specialedu", "Special Education"),
    ("english", "English Language"),
    ("foreignlang", "Foreign Languages"),
    ("translation", "Translation Studies"),
    ("tesol", "TESOL / ESL"),
    ("law", "Law"),
    ("legal", "Legal Studies"),
    ("constitutional", "Constitutional Law"),
    ("publicpolicy", "Public Policy"),
    ("politicaltheory", "Political Theory"),
    ("medicine", "Medicine"),
    ("nursing", "Nursing"),
    ("pharmacy", "Pharmacy"),
    ("publichealth", "Public Health"),
    ("nutrition", "Nutrition"),
    ("veterinary", "Veterinary Science"),
    ("dentistry", "Dentistry"),
    ("biomed", "Biomedical Science"),
    ("physicaltherapy", "Physical Therapy")
]
    NOTES_COURSE_CHOICES = [
        ("algebra", "Algebra"),
        ("calculus", "Calculus"),
        ("programming", "Programming 101"),
        ("databases", "Databases"),
        ("ai", "Artificial Intelligence"),
        ("microeconomics", "Microeconomics"),
        ("macroeconomics", "Macroeconomics"),
    ]
    # Levels are to be uodated depending on the different levels of courses we have
    LEVEL_CHOICES = [
        ("elementary", "Elementary School"),
        ("high_school", "High School"),
        ("university", "University"),
        ("masters", "Masters"),
    ]
    # Model fields
    uploader = models.ForeignKey(
        User, 
        on_delete=models.DO_NOTHING, 
        related_name="notes_uploader"
        ) 
    title = models.CharField(max_length=60)
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES
        )
    # Course field is not required because users can upload notes that are not nessesarily about an EduLite course, users can upload, search and find notes for their school classes
    notes_course = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        choices=NOTES_COURSE_CHOICES
    )
    
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.level} - {self.subject})"

# Function to define upload path dynamically
def note_file_path(instance, filename):
    level = instance.note.level
    subject = instance.note.subject
    return f"NoteFiles/{level}/{subject}/{filename}"

class NotesFiles(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="files")
    files = models.FileField(upload_to=note_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.note.title}: {self.file.name}"

    