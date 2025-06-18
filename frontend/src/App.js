import React from 'react';
import FileUpload from './FileUpload';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🖨️ PrintQA</h1>
        <p>Análise de qualidade para arquivos de impressão 3D</p>
      </header>
      <main>
        <FileUpload />
      </main>
      <footer className="App-footer">
        <p>Desenvolvido por Print3D Labs</p>
      </footer>
    </div>
  );
}

export default App;