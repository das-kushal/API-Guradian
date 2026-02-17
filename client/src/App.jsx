import React, { useState } from "react";
import axios from "axios";
import UploadPanel from "./components/UploadPanel";
import DiffView from "./components/DiffView";
import RiskPanel from "./components/RiskPanel";
import AISummary from "./components/AISummary";
import Layout from "./components/Layout";

function App() {
  const [result, setResult] = useState(null);

  const handleAnalyze = async (oldFile, newFile) => {
    const formData = new FormData();
    formData.append("old", oldFile);
    formData.append("new", newFile);

    const res = await axios.post("http://localhost:5000/analyze", formData);
    setResult(res.data);
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4 py-8">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Secure Your API Changes
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Upload your API specifications to detect breaking changes and analyze security risks instantly using AI.
          </p>
        </div>

        <UploadPanel onAnalyze={handleAnalyze} />

        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <RiskPanel score={result.risk_score} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <DiffView diff={result.diff} />
              <AISummary ai={result.ai_analysis} />
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default App;
