import sys
import threading  # Adicionando a importação que faltava


# Detectar se estamos rodando em modo de teste
def is_test_environment():
    return "test" in sys.argv
