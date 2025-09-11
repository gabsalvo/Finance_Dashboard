import subprocess

def deduci_importo_ai(xml_content: str, model: str = "tinyllama:latest") -> float:
    """
    Chiama Ollama (modello tinyllama:latest ) per dedurre l'importo totale da un file XML.
    Ritorna un float con l'importo (0.0 se non trovato o errore).
    Funziona su Windows, Linux e macOS.
    """
    prompt = f"""
Sei un assistente che legge fatture XML.
Ti fornisco il contenuto del file e devi restituire SOLO l'importo totale da pagare,
in formato numerico puro (senza simboli, lettere o testo extra).

Fattura XML:
{xml_content}
    """

    try:
        process = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # cross-platform (gestisce encoding automaticamente)
        )

        stdout, stderr = process.communicate(input=prompt)

        if stderr:
            print("⚠️ Errore Ollama:", stderr.strip())

        risposta = (stdout or "").strip()

        # Estrazione numero dalla risposta
        importo = None
        for token in risposta.replace("\n", " ").split():
            token = token.replace(",", ".").strip()
            try:
                importo = float(token)
                break
            except ValueError:
                continue

        return importo if importo is not None else 0.0

    except Exception as e:
        print("❌ Errore durante la chiamata a Ollama:", str(e))
        return 0.0
