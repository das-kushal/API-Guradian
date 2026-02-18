import React, { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import DiffView from "./components/DiffView";
import RiskPanel from "./components/RiskPanel";
import AISummary from "./components/AISummary";
import Layout from "./components/Layout";

function App() {
  const [diff, setDiff] = useState(null);
  const [riskScore, setRiskScore] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiStreaming, setAiStreaming] = useState(false);
  const [aiRawText, setAiRawText] = useState("");
  const [error, setError] = useState(null);

  const handleAnalyze = async (oldFile, newFile) => {
    // Reset state
    setDiff(null);
    setRiskScore(null);
    setAiAnalysis(null);
    setAiRawText("");
    setAiStreaming(false);
    setError(null);

    const formData = new FormData();
    formData.append("old", oldFile);
    formData.append("new", newFile);

    try {
      const response = await fetch("http://localhost:5000/analyze/stream", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "diff") {
              // Phase 1: instant diff + preliminary risk score
              setDiff(event.diff);
              setRiskScore(event.risk_score);
              setAiStreaming(true);
            } else if (event.type === "ai_token") {
              // Phase 2: stream AI tokens
              setAiRawText((prev) => prev + event.token);
            } else if (event.type === "ai_done") {
              // Phase 3: final structured result
              setAiAnalysis(event.ai_analysis);
              setRiskScore(event.risk_score);
              setAiStreaming(false);
            } else if (event.type === "error") {
              setError(event.message);
            }
          } catch (e) {
            // skip malformed event
          }
        }
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const hasResults = diff !== null;

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

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
            ⚠️ {error}
          </div>
        )}

        {hasResults && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <RiskPanel score={riskScore} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <DiffView diff={diff} />
              <AISummary
                ai={aiAnalysis}
                isStreaming={aiStreaming}
                rawText={aiRawText}
              />
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default App;
