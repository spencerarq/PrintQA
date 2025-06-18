import React, { useState } from 'react';

// Componente para renderizar o resultado da análise de forma legível
const AnalysisReport = ({ data }) => {
  // Converte snake_case para Title Case e substitui _ por espaço
  const formatKey = (key) => {
    return key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  };

  return (
    <div className="analysis-report">
      <h3>📋 Relatório de Análise</h3>
      <ul>
        {Object.entries(data).map(([key, value]) => (
          <li key={key}>
            <strong>{formatKey(key)}:</strong> 
            <span>
              {typeof value === 'boolean' ? (value ? '✅ Sim' : '❌ Não') : value}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};


function FileUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.stl') || file.name.endsWith('.obj'))) {
        setSelectedFile(file);
        setAnalysisResult(null);
        setError(null);
    } else {
        setSelectedFile(null);
        setError('Por favor, selecione um arquivo .stl ou .obj');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Nenhum arquivo selecionado.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/analyze_mesh/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Tenta ler uma mensagem de erro mais detalhada do corpo da resposta
        const errJson = await response.json().catch(() => null);
        const detail = errJson?.detail || response.statusText;
        throw new Error(detail);
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (e) {
      console.error("Erro no upload:", e);
      // Extrai uma mensagem mais limpa para o usuário
      const detail = e.message.includes("Failed to fetch") ? "Failed to fetch" : e.message;
      setError(`Falha ao analisar o arquivo. Verifique se o backend está rodando e acessível. Detalhe: ${detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <p className="instructions">
        Faça o upload de um modelo 3D (<code>.stl</code>, <code>.obj</code>) para receber um relatório de problemas comuns de impressão.
      </p>
      
      <div className="upload-controls">
        <input type="file" id="file-upload" accept=".stl,.obj" onChange={handleFileChange} />
        {/* ATRIBUTO ATUALIZADO AQUI */}
        <label htmlFor="file-upload" className="file-label" data-testid="button-choose-file">
          {selectedFile ? selectedFile.name : 'Escolher arquivo'}
        </label>
        {/* ATRIBUTO ATUALIZADO AQUI */}
        <button onClick={handleUpload} disabled={isLoading || !selectedFile} data-testid="button-analyze-file">
          {isLoading ? 'Analisando...' : 'Analisar Arquivo'}
        </button>
      </div>

      {error && <div className="error-message" data-testid="error-message">{error}</div>}
      
      {isLoading && <div className="loader" data-testid="loader"></div>}

      {analysisResult && <AnalysisReport data={analysisResult} />}
    </div>
  );
}

export default FileUpload;