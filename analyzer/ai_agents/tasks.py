from crewai import Task


class TaskFactory:
    def create_structure_analysis_task(self, agent, file_content):
        """Create a task for analyzing code structure."""
        return Task(
            description=f"""
            Analyze the structure and organization of the provided code. Consider:
            1. Modularity of the code
            2. Function and class organization
            3. File structure if multiple files are involved
            4. Use of design patterns
            5. Separation of concerns
            6. Dependency management

            The code is:
            ```
            {file_content}
            ```

            Provide a detailed analysis with specific examples from the code.
            """,
            agent=agent,
            expected_output="A comprehensive analysis of the code structure with strengths and suggestions for improvement.",
        )

    def create_security_analysis_task(self, agent, file_content):
        """Create a task for analyzing security aspects."""
        return Task(
            description=f"""
            Analyze the provided code for security vulnerabilities. Look for:
            1. Injection vulnerabilities (SQL, Command, etc.)
            2. Authentication issues
            3. Sensitive data exposure
            4. Insecure dependencies
            5. Missing access controls
            6. Security misconfiguration

            The code is:
            ```
            {file_content}
            ```

            Provide a detailed security analysis with specific vulnerabilities found (if any) and recommendations.
            """,
            agent=agent,
            expected_output="A detailed security analysis highlighting potential vulnerabilities and remediation steps.",
        )

    def create_quality_analysis_task(self, agent, file_content):
        """Create a task for analyzing code quality."""
        return Task(
            description=f"""
            Analyze the quality and maintainability of the provided code. Consider:
            1. Code readability and documentation
            2. Complexity (cyclomatic complexity, nesting levels)
            3. Code duplication
            4. Naming conventions
            5. Error handling
            6. Adherence to SOLID principles and best practices

            The code is:
            ```
            {file_content}
            ```

            Provide a detailed quality analysis with examples and suggestions for improvement.
            """,
            agent=agent,
            expected_output="A comprehensive code quality assessment with specific examples and recommendations.",
        )
