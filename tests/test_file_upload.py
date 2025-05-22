from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from analyzer.models import UploadedFile, AnalysisReport


class FileUploadTest(TestCase):
    def test_file_upload_view_get(self):
        """Test file upload view GET request."""
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analyzer/upload.html")

    def test_file_upload_view_post(self):
        """Test file upload view POST request with valid file."""
        content = "def hello_world():\n    print('Hello, World!')\n"
        file = SimpleUploadedFile(
            "test_file.py", content.encode("utf-8"), content_type="text/plain"
        )

        response = self.client.post(reverse("upload"), {"file": file})

        self.assertEqual(UploadedFile.objects.count(), 1)

        self.assertEqual(AnalysisReport.objects.count(), 1)

        report = AnalysisReport.objects.first()
        self.assertRedirects(response, reverse("report", args=[report.id]))


class ReportViewTest(TestCase):
    def setUp(self):
        """Set up test data."""
        content = "def test_func():\n    return True\n"
        file = SimpleUploadedFile(
            "file.py", content.encode("utf-8"), content_type="text/plain"
        )

        uploaded_file = UploadedFile.objects.create(
            file=file,
            filename="file.py",
            content_type="text/plain",
            file_size=len(content),
        )

        self.report = AnalysisReport.objects.create(
            file=uploaded_file, summary="Test summary", status="completed"
        )

    def test_report_view(self):
        """Test report view."""
        response = self.client.get(reverse("report", args=[self.report.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analyzer/report.html")
        self.assertContains(response, "Test summary")
        self.assertContains(response, "file.py")
