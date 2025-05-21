import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UploadedFile, AnalysisResult, AnalysisReport
from .forms import FileUploadForm
from .ai_agents.crew_config import analyze_file
import threading

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
                
                report = AnalysisReport.objects.create(
                    file=uploaded_file,
                    summary="Analysis in progress...",
                    status="processing"
                )
                
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
            uploaded_file.file.seek(0)  
            file_content = uploaded_file.file.read()
            
            report = AnalysisReport.objects.get(file=uploaded_file)
            report.status = "processing"
            report.save()
            
            analysis_results = analyze_file(file_content, uploaded_file.filename)
            
            for agent_type, result in analysis_results.items():
                # Log detalhado antes do salvamento
                print(f"DEBUG: Salvando resultado para {agent_type}, tamanho: {len(result or '')}")
                
                # Garantir que result seja uma string e não None
                safe_result = str(result) if result is not None else "No result generated"
                
                # Criar o objeto e verificar se foi salvo corretamente
                analysis = AnalysisResult.objects.create(
                    file=uploaded_file,
                    agent=agent_type,
                    result=safe_result
                )
                print(f"DEBUG: Resultado salvo, ID={analysis.id}, tamanho={len(analysis.result)}")
            
            summary = f"Analysis completed for {uploaded_file.filename}.\n\n"
            summary += "Key findings:\n"
            for agent_type, result in analysis_results.items():
                brief = result.split('\n')[0][:100] if result else "No results"
                summary += f"\n• {agent_type.title()}: {brief}..."
            
            report.summary = summary
            report.status = "completed"
            report.save()
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            report = AnalysisReport.objects.get(file=uploaded_file)
            report.status = "failed"
            report.summary = f"Error during analysis: {str(e)}"
            report.save()


class ReportView(View):
    """View for displaying analysis reports."""
    def get(self, request, report_id):
        report = get_object_or_404(AnalysisReport, id=report_id)
        
        analyses = AnalysisResult.objects.filter(file=report.file)
        
        logger.info(f"Report {report_id} for file {report.file.filename}:")
        logger.info(f"Status: {report.status}")
        logger.info(f"Summary length: {len(report.summary)} chars")
        logger.info(f"Found {analyses.count()} analyses")
        
        # Modificação principal aqui - processar TODOS os resultados
        processed_analyses = []
        for analysis in analyses:
            logger.info(f"Analysis {analysis.id}: agent={analysis.agent}, result length={len(analysis.result)}")
            
            # Normalizar quebras de linha, mas não filtrar resultados vazios
            result = analysis.result.replace('\r\n', '\n') if analysis.result else "No result available"
            analysis.result = result
            processed_analyses.append(analysis)
            
            # Log mais detalhado para diagnóstico
            logger.info(f"Processed result for {analysis.agent}, length: {len(result)}")
            logger.info(f"First 30 chars: '{result[:30]}'")
        
        context = {
            'report': report,
            'analyses': processed_analyses,  
            'file': report.file,
            'debug': {
                'has_analyses': len(processed_analyses) > 0,
                'analyses_count': len(processed_analyses),
                'raw_analyses': [
                    {
                        'agent': a.agent,
                        'length': len(a.result),
                        'preview': a.result[:50]
                    } for a in processed_analyses
                ]
            }
        }
        
        return render(request, 'analyzer/report.html', context)
    

class RawReportView(View):
    """View for displaying raw analysis data."""
    def get(self, request, report_id):
        report = get_object_or_404(AnalysisReport, id=report_id)
        
        analyses = AnalysisResult.objects.filter(file=report.file)
        
        context = {
            'report': report,
            'analyses': analyses,
            'file': report.file,
            'debug': {
                'has_analyses': analyses.exists(),
                'analyses_count': analyses.count(),
            }
        }
        
        return render(request, 'analyzer/raw_report.html', context)


class ReportListView(View):
    """View for listing all reports."""
    def get(self, request):
        reports = AnalysisReport.objects.all().order_by('-created_at')
        return render(request, 'analyzer/report_list.html', {'reports': reports})
    

class ReportDeleteView(View):
    """View for deleting reports."""
    def get(self, request, report_id):
        report = get_object_or_404(AnalysisReport, id=report_id)
        return render(request, 'analyzer/confirm_delete.html', {'report': report})
    
    def post(self, request, report_id):
        report = get_object_or_404(AnalysisReport, id=report_id)
        filename = report.file.filename
        
        # Exclui o arquivo associado também
        uploaded_file = report.file
        
        # Primeiro exclui o relatório
        report.delete()
        
        # Depois exclui o arquivo (para evitar problemas de integridade referencial)
        uploaded_file.delete()
        
        messages.success(request, f'Relatório "{filename}" excluído com sucesso.')
        return redirect('report_list')