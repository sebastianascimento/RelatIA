from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from analyzer.models import UploadedFile, AnalysisReport, AnalysisResult
from django.core.files.uploadedfile import SimpleUploadedFile

class MockAgentTests(TestCase):
    
    @patch('analyzer.views.analyze_file')
    def test_file_analysis_with_mock(self, mock_analyze):
        """Test file analysis with mocked AI analysis"""
        mock_analyze.return_value = {
            'structure': 'Mock estrutura: O código está bem organizado.',
            'security': 'Mock segurança: Não há vulnerabilidades.',
            'quality': 'Mock qualidade: Código segue boas práticas.'
        }
        
        test_content = b"def test(): return 'Hello'"
        test_file = SimpleUploadedFile(
            name='test_mock.py',
            content=test_content,
            content_type='text/plain'
        )
        
        response = self.client.post(reverse('upload'), {
            'file': test_file,
            'filename': 'test_mock.py'
        })
        
        self.assertEqual(response.status_code, 302)  
        
        self.assertEqual(UploadedFile.objects.count(), 1)
        
        self.assertEqual(AnalysisReport.objects.count(), 1)
        
        mock_analyze.assert_called_once()
        
        report = AnalysisReport.objects.first()
        self.assertEqual(report.status, 'completed')
        
        results = AnalysisResult.objects.filter(file=report.file)
        self.assertEqual(results.count(), 3)