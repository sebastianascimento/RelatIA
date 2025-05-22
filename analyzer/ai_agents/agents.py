from crewai import Agent
from langchain_community.llms import Ollama


class AgentFactory:
    def __init__(self):
        self.llm = Ollama(model="gemma:2b", base_url="http://ollama:11434")

    def create_structure_analyzer(self):
        """Creates an agent that analyzes the structure of code files."""
        return Agent(
            role="Code Structure Analyzer",
            goal="Analyze the structure and organization of the code",
            backstory="You are an expert in code architecture and design patterns. "
            "Your job is to analyze the structure of code files and provide "
            "insights on how well organized they are.",
            verbose=True,
            llm=self.llm,
            tools=[],
        )

    def create_security_analyzer(self):
        """Creates an agent that analyzes the security aspects of code files."""
        return Agent(
            role="Security Analyzer",
            goal="Identify potential security vulnerabilities in the code",
            backstory="You are a cybersecurity expert specialized in code security. "
            "Your job is to analyze code files for security vulnerabilities "
            "like SQL injections, XSS, insecure dependencies, and more.",
            verbose=True,
            llm=self.llm,
            tools=[],
        )

    def create_quality_analyzer(self):
        """Creates an agent that analyzes the code quality."""
        return Agent(
            role="Code Quality Analyzer",
            goal="Assess the quality and maintainability of the code",
            backstory="You are a coding standards expert with deep knowledge of clean code principles. "
            "Your job is to analyze code files for readability, maintainability, "
            "complexity, and adherence to best practices.",
            verbose=True,
            llm=self.llm,
            tools=[],
        )
