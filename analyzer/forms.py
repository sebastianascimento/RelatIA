from django import forms
from .models import UploadedFile
import os
import logging

logger = logging.getLogger(__name__)


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["file"]

    def clean_file(self):
        file = self.cleaned_data.get("file")

        logger.debug(f"File validation: {file}")

        if file and file.size > 5 * 1024 * 1024:
            logger.error(f"File too large: {file.size} bytes")
            raise forms.ValidationError("File size cannot exceed 5MB")

        allowed_extensions = [
            ".py",
            ".js",
            ".c",
            ".cpp",
            ".java",
            ".html",
            ".css",
            ".go",
            ".php",
            ".rb",
            ".ts",
            ".swift",
            ".kt",
            ".rs",
            ".sh",
        ]

        extension = os.path.splitext(file.name)[1].lower()
        if extension not in allowed_extensions:
            logger.error(f"Unsupported file type: {extension}")
            raise forms.ValidationError(
                f'Only code files ({", ".join(allowed_extensions)}) are supported.'
            )

        self.instance.filename = file.name
        self.instance.content_type = file.content_type
        self.instance.file_size = file.size

        return file

    def is_valid(self):
        result = super().is_valid()
        logger.debug(f"Form validation result: {result}")
        if not result:
            logger.debug(f"Form errors: {self.errors}")
        return result
