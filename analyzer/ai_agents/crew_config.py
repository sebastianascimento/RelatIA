from crewai import Crew
from .agents import AgentFactory
from .tasks import TaskFactory
import os
import logging
from io import BytesIO

try:
    import PyPDF2
except ImportError:
    logging.warning("PyPDF2 not installed. PDF analysis may not work correctly.")
    PyPDF2 = None

logger = logging.getLogger(__name__)

def extract_text_from_file(file_content, filename):
    """
    Extract text from a file based on its extension.
    
    Args:
        file_content: The binary content of the file
        filename: The name of the file with extension
    
    Returns:
        str: The extracted text content
    """
    extension = os.path.splitext(filename)[1].lower()
    
    if extension == '.txt':
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return file_content.decode('utf-8', errors='replace')
            
    elif extension == '.pdf' and PyPDF2:
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"Error extracting text from PDF: {e}"
    else:
        return f"Unsupported file type: {extension}"

def analyze_file(file_content, filename):
    """
    Analyze a file using three specialized AI agents.
    
    Args:
        file_content: The binary content of the file
        filename: The name of the file with extension
        
    Returns:
        dict: A dictionary containing the analysis results from each agent
    """
    text_content = extract_text_from_file(file_content, filename)
    
    agent_factory = AgentFactory()
    structure_agent = agent_factory.create_structure_analyzer()
    security_agent = agent_factory.create_security_analyzer()
    quality_agent = agent_factory.create_quality_analyzer()
    
    task_factory = TaskFactory()
    structure_task = task_factory.create_structure_analysis_task(structure_agent, text_content)
    security_task = task_factory.create_security_analysis_task(security_agent, text_content)
    quality_task = task_factory.create_quality_analysis_task(quality_agent, text_content)
    
    crew = Crew(
        agents=[structure_agent, security_agent, quality_agent],
        tasks=[structure_task, security_task, quality_task],
        verbose=2
    )
    
    result = crew.kickoff()
    
    analysis_results = {
        'structure': result[0], 
        'security': result[1],  
        'quality': result[2],    
    }
    
    return analysis_results