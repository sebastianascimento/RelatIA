from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UploadedFile, AnalysisResult, AnalysisReport
from .forms import FileUploadForm
from .ai_agents.crew_config import analyze_file
import threading
import logging

logger = logging.getLogger(__name__)

class HomeView(View):
    """Home page view."""
    def get(self, request):
        return render(request, 'analyzer/home.html')


class FileUploadView(View):
    """View for handling file upload."""
    def get(self, request):
        form = FileUploadForm()
        return render(request, 'analyzer/upload.html', {'form': form})
    
    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = form.save()
                
                # Create report entry with pending status
                report = AnalysisReport.objects.create(
                    file=uploaded_file,
                    summary="Analysis in progress...",
                    status="processing"
                )
                
                # Start analysis in background thread
                threading.Thread(
                    target=self._process_file_analysis,
                    args=(uploaded_file,)
                ).start()
                
                messages.success(request, 'File uploaded successfully! Analysis in progress...')
                return HttpResponseRedirect(reverse('report', args=[report.id]))
            except Exception as e:
                logger.error(f"Error in file upload: {str(e)}")
                messages.error(request, f"Error uploading file: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return render(request, 'analyzer/upload.html', {'form': form})
    
    def _process_file_analysis(self, uploaded_file):
        """Process file analysis in background."""
        try:
            # Read file content as binary (don't decode yet)
            uploaded_file.file.seek(0)  # Make sure we're at the beginning of the file
            file_content = uploaded_file.file.read()
            
            # Update report status
            report = AnalysisReport.objects.get(file=uploaded_file)
            report.status = "processing"
            report.save()
            
            # Run AI analysis with filename parameter
            analysis_results = analyze_file(file_content, uploaded_file.filename)
            
            # Store results
            for agent_type, result in analysis_results.items():
                AnalysisResult.objects.create(
                    file=uploaded_file,
                    agent=agent_type,
                    result=result
                )
            
            # Generate summary from all analyses
            summary = f"Analysis completed for {uploaded_file.filename}.\n\n"
            summary += "Key findings:\n"
            for agent_type, result in analysis_results.items():
                # Add a brief summary line for each analysis result
                brief = result.split('\n')[0][:100] if result else "No results"
                summary += f"\n• {agent_type.title()}: {brief}..."
            
            # Update report with results
            report.summary = summary
            report.status = "completed"
            report.save()
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            # Update report with error status
            report = AnalysisReport.objects.get(file=uploaded_file)
            report.status = "failed"
            report.summary = f"Error during analysis: {str(e)}"
            report.save()


class ReportView(View):
    """View for displaying analysis reports."""
    def get(self, request, report_id):
        report = get_object_or_404(AnalysisReport, id=report_id)
        analyses = report.file.analyses.all()
        
        # Prepare context with all information
        context = {
            'report': report,
            'analyses': analyses,
            'file': report.file,
        }
        
        return render(request, 'analyzer/report.html', context)


class ReportListView(View):
    """View for listing all reports."""
    def get(self, request):
        reports = AnalysisReport.objects.all().order_by('-created_at')
        return render(request, 'analyzer/report_list.html', {'reports': reports})