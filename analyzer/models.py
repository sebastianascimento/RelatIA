from django.db import models
from django.utils import timezone


class UploadedFile(models.Model):
    """Model to store uploaded files and their analysis results."""
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    content_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField()  
    
    def __str__(self):
        return self.filename


class AnalysisResult(models.Model):
    """Model to store the analysis results from each agent."""
    AGENT_CHOICES = (
        ('structure', 'Structure Analyzer'),
        ('security', 'Security Analyzer'),
        ('quality', 'Quality Analyzer'),
    )
    
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='analyses')
    agent = models.CharField(max_length=20, choices=AGENT_CHOICES)
    result = models.TextField()
    completed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.agent} analysis for {self.file.filename}"


class AnalysisReport(models.Model):
    """Model to store the combined analysis report."""
    file = models.OneToOneField(UploadedFile, on_delete=models.CASCADE, related_name='report')
    summary = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 
    status = models.CharField(max_length=20, default='pending', 
                             choices=(('pending', 'Pending'), 
                                      ('processing', 'Processing'),
                                      ('completed', 'Completed'),
                                      ('failed', 'Failed')))
    
    def __str__(self):
        return f"Report for {self.file.filename}"