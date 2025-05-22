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

    # Adicionar suporte para arquivos de código
    if extension in [
        ".txt",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".html",
        ".css",
    ]:
        try:
            return file_content.decode("utf-8")
        except UnicodeDecodeError:
            for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return file_content.decode("utf-8", errors="replace")

    elif extension == ".pdf" and PyPDF2:
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
    """
    print(f"DEBUG: Iniciando análise do arquivo {filename}")
    print(f"DEBUG: Tamanho do conteúdo: {len(file_content)} bytes")

    text_content = extract_text_from_file(file_content, filename)
    print(f"DEBUG: Texto extraído, primeiros 100 caracteres: {text_content[:100]}")

    if text_content.startswith("Unsupported file type"):
        print(f"ALERTA: Tipo de arquivo não suportado: {filename}")
        text_content = (
            f"// Conteúdo do arquivo {filename} (não foi possível extrair o texto)"
        )

    # Função para capturar output de um agente
    def run_agent_with_capture(agent, task_creator, agent_name):
        import io
        from contextlib import redirect_stdout

        output_capture = io.StringIO()
        result = None

        try:
            # Capturar a saída
            with redirect_stdout(output_capture):
                crew = Crew(
                    agents=[agent], tasks=[task_creator(agent, text_content)], verbose=2
                )
                result = crew.kickoff()[0]

            # Processar a saída capturada
            captured_text = output_capture.getvalue()
            print(f"DEBUG: Capturado {len(captured_text)} chars para {agent_name}")

            # Extrair a análise real dos logs
            # Procurar por padrões como "**Final Answer:**" seguido pelo conteúdo
            import re

            analysis_pattern = r"\*\*Final Answer:\*\*(.*?)(?=>|$)"
            matches = re.findall(analysis_pattern, captured_text, re.DOTALL)

            if matches and len(matches[-1].strip()) > 10:
                # Usar a última ocorrência de Final Answer, que deve ser o resultado final
                extracted_result = matches[-1].strip()
                print(
                    f"DEBUG: Extraído resultado de {len(extracted_result)} chars para {agent_name}"
                )
                return extracted_result

            # Se não encontrou pelo padrão, tente outro método
            if "Task output: **" in captured_text:
                parts = captured_text.split("Task output: **")
                if len(parts) > 1:
                    content = parts[1].split("\n\n")[0]
                    if len(content.strip()) > 10:
                        return content.strip()

            # Se tudo falhar, retorne o resultado original ou um fallback
            if result and len(result) > 10:
                return result
            return f"Não foi possível extrair análise de {agent_name}."

        except Exception as e:
            print(f"ERRO ao executar {agent_name}: {str(e)}")
            return f"Erro ao analisar {agent_name}: {str(e)}"

    # Executar análises individualmente
    analysis_results = {}

    try:
        # Configuração de agentes
        agent_factory = AgentFactory()
        task_factory = TaskFactory()

        # Estrutura
        structure_agent = agent_factory.create_structure_analyzer()
        structure_result = run_agent_with_capture(
            structure_agent, task_factory.create_structure_analysis_task, "estrutura"
        )
        analysis_results["structure"] = structure_result

        # Segurança
        security_agent = agent_factory.create_security_analyzer()
        security_result = run_agent_with_capture(
            security_agent, task_factory.create_security_analysis_task, "segurança"
        )
        analysis_results["security"] = security_result

        # Qualidade
        quality_agent = agent_factory.create_quality_analyzer()
        quality_result = run_agent_with_capture(
            quality_agent, task_factory.create_quality_analysis_task, "qualidade"
        )
        analysis_results["quality"] = quality_result

    except Exception as e:
        print(f"ERRO na análise global: {str(e)}")
        # Fornecer resultados padrão em caso de erro
        if "structure" not in analysis_results:
            analysis_results["structure"] = f"Erro ao analisar estrutura: {str(e)}"
        if "security" not in analysis_results:
            analysis_results["security"] = f"Erro ao analisar segurança: {str(e)}"
        if "quality" not in analysis_results:
            analysis_results["quality"] = f"Erro ao analisar qualidade: {str(e)}"

    # Log detalhado dos resultados antes de retornar
    for agent, content in analysis_results.items():
        print(f"DEBUG CREW OUTPUT {agent}: {len(content or '')} chars")
        print(f"DEBUG CREW PREVIEW {agent}: {(content or '')[:100]}")

        # Se for muito curto, algo deu errado
        if content is None or len(content) < 10:
            print(f"ALERTA: Resultado muito curto para {agent}")
            analysis_results[
                agent
            ] = f"Análise para {agent} não foi completada adequadamente. Possível erro de processamento."

    return analysis_results
