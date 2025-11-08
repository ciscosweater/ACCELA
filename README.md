# ACCELA - Steam Depot Downloader GUI

Interface gráfica para download de depots Steam com recursos avançados de gerenciamento.

## 🚀 Instalação Rápida

### Linux
```bash
# Execute o script de instalação
chmod +x install_and_setup.sh
./install_and_setup.sh
```

### Manual (Todas as plataformas)
```bash
# 1. Crie ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute o aplicativo
python main.py
```

## 📋 Requisitos

- Python 3.8+
- PyQt6
- Conexão com internet
- Conta Steam (para downloads autenticados)

## 🎮 Como Usar

1. **Execute o ACCELA** através do instalador ou manualmente
2. **Configure suas credenciais Steam** (opcional, para downloads privados)
3. **Selecione o jogo** desejado na lista
4. **Escolha os depots/manifestos** para download
5. **Configure o diretório** de destino
6. **Inicie o download** e acompanhe o progresso

## 🔧 Funcionalidades

- ✅ Interface intuitiva baseada em PyQt6
- ✅ Download de múltiplos depots simultâneos
- ✅ Suporte a arquivos ZIP para processamento
- ✅ Monitoramento de velocidade de download
- ✅ Gerenciamento de jogos instalados
- ✅ Tema escuro moderno
- ✅ Suporte a SLSSteam para variantes especiais

## 📁 Estrutura de Arquivos

```
ACCELA Python/
├── main.py              # Ponto de entrada principal
├── requirements.txt     # Dependências Python
├── install_and_setup.sh # Script de instalação Linux
├── core/               # Lógica principal da aplicação
├── ui/                 # Componentes da interface
├── utils/              # Utilitários e helpers
├── config/             # Arquivos de configuração
├── external/           # Ferramentas externas
├── Steamless/          # Ferramenta Steamless
└── SLSsteam-Any/       # SLSSteam para variantes
```

## ⚠️ Aviso Importante

Este software é destinado para uso educacional e pessoal. Os usuários são responsáveis por:
- Respeitar os Termos de Serviço da Steam
- Apenas baixar conteúdo que possuem legalmente
- Não distribuir conteúdo protegido por direitos autorais

## 🔐 Segurança

- Credenciais Steam são armazenadas localmente
- Nenhuma informação é enviada para servidores externos
- Use sempre a versão mais recente do aplicativo

## 🐛 Problemas Comuns

**Aplicativo não inicia**: Verifique se Python 3.8+ está instalado
**Erro de dependências**: Execute `pip install -r requirements.txt`
**Falha no download**: Verifique conexão e credenciais Steam

## 📞 Suporte

Para problemas e sugestões, verifique a documentação ou contate o desenvolvedor.

---

**Versão**: 1.0  
**Desenvolvido com**: Python, PyQt6, Steam API  
**Plataformas**: Linux, Windows, macOS