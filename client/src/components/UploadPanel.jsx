import React, { useState, useRef } from "react";
import { UploadCloud, FileJson, ArrowRight, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "./ui/Card";
import { Button } from "./ui/Button";

function UploadPanel({ onAnalyze }) {
  const [oldFile, setOldFile] = useState(null);
  const [newFile, setNewFile] = useState(null);
  const [isDragging, setIsDragging] = useState(null); // 'old' or 'new'
  const [loading, setLoading] = useState(false);

  const handleDragOver = (e, type) => {
    e.preventDefault();
    setIsDragging(type);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(null);
  };

  const handleDrop = (e, type) => {
    e.preventDefault();
    setIsDragging(null);
    const file = e.dataTransfer.files[0];
    if (file) {
      type === 'old' ? setOldFile(file) : setNewFile(file);
    }
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      type === 'old' ? setOldFile(file) : setNewFile(file);
    }
  };

  const handleSubmit = async () => {
    if (!oldFile || !newFile) return;
    setLoading(true);
    await onAnalyze(oldFile, newFile);
    setLoading(false);
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
        {/* Old Version Upload */}
        <UploadZone
          label="Original API Spec"
          description="Drag & drop old Swagger/OpenAPI file"
          file={oldFile}
          onFileSelect={(f) => setOldFile(f)}
          isDragging={isDragging === 'old'}
          onDragOver={(e) => handleDragOver(e, 'old')}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, 'old')}
          id="old-file"
        />

        {/* Divider / Arrow */}
        <div className="hidden md:flex absolute inset-0 items-center justify-center pointer-events-none">
          <div className="bg-slate-900 p-2 rounded-full border border-slate-700 z-10">
            <ArrowRight className="text-slate-500" />
          </div>
        </div>

        {/* New Version Upload */}
        <UploadZone
          label="New API Spec"
          description="Drag & drop new Swagger/OpenAPI file"
          file={newFile}
          onFileSelect={(f) => setNewFile(f)}
          isDragging={isDragging === 'new'}
          onDragOver={(e) => handleDragOver(e, 'new')}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, 'new')}
          id="new-file"
        />
      </div>

      <div className="mt-8 flex justify-center">
        <Button 
          size="lg" 
          onClick={handleSubmit} 
          disabled={!oldFile || !newFile}
          isLoading={loading}
          className="w-full md:w-auto min-w-[200px]"
        >
          Run Analysis
        </Button>
      </div>
    </Card>
  );
}

const UploadZone = ({ 
  label, 
  description, 
  file, 
  onFileSelect, 
  isDragging, 
  onDragOver, 
  onDragLeave, 
  onDrop,
  id 
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-slate-300 ml-1">
        {label}
      </label>
      
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`
          relative group cursor-pointer border-2 border-dashed rounded-xl p-6 h-48
          flex flex-col items-center justify-center text-center transition-all duration-300
          ${isDragging 
            ? "border-blue-500 bg-blue-500/10 scale-[1.02]" 
            : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/50 bg-slate-900/50"
          }
          ${file ? "border-solid border-slate-600" : ""}
        `}
      >
        <input
          type="file"
          id={id}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={(e) => onFileSelect(e.target.files[0])}
        />
        
        <AnimatePresence mode="wait">
          {file ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center w-full"
            >
              <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-3 text-emerald-400">
                <FileJson size={24} />
              </div>
              <p className="text-sm font-medium text-slate-200 truncate w-full px-4 text-center">
                {file.name}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {(file.size / 1024).toFixed(1)} KB
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  onFileSelect(null);
                }}
                className="mt-3 p-1 rounded-full hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors z-20 relative"
              >
                <X size={16} />
              </button>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center"
            >
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-3 transition-colors ${isDragging ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-slate-300"}`}>
                <UploadCloud size={24} />
              </div>
              <p className="text-sm text-slate-300 font-medium">
                Click to upload
              </p>
              <p className="text-xs text-slate-500 mt-1 max-w-[140px]">
                {description}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default UploadPanel;
