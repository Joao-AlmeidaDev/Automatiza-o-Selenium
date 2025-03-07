# Automation-Selenium

Este projeto automatiza o acesso e a manutenção de um sistema de uma clínica. Ele foi desenvolvido para realizar o login no painel de senhas e no totem, eliminando a necessidade de um funcionário operar os equipamentos manualmente todos os dias.

O projeto utiliza Selenium e PyAutoGUI para efetuar o login, selecionar unidades e manter o navegador aberto conforme o horário de funcionamento das clínicas.

## 📌 Funcionalidades
- Login automático.
- Seleção da unidade pelo dropdown.
- Manutenção do navegador aberto até o horário de fechamento da clínica.
- Configuração de horários e URLs via arquivo `config.txt`.

## 🛠 Tecnologias Utilizadas
- Python 3.x
- Selenium 4.23.1
- PyAutoGUI
- WebDriver (Edge)

## 📂 Estrutura do Projeto
```
📦 Automation-Selenium
 ┣ 📜 main.py              # Script principal de automação
 ┣ 📜 config.txt           # Arquivo de configuração (URLs, horários, unidade)
 ┣ 📜 requirements.txt     # Dependências do projeto
 ┣ 📜 README.md            # Documentação do projeto
```

## 🔧 Personalização
- Para modificar os horários ou URLs, edite diretamente o `config.txt`.
- Caso precise rodar em outro navegador, altere o WebDriver no `main.py`.

## 📝 Notas
- O navegador permanecerá aberto até o horário especificado no `config.txt`.
- Certifique-se de que o WebDriver está atualizado e compatível com o navegador.

## 📌 Autor
Projeto desenvolvido por **João**.

