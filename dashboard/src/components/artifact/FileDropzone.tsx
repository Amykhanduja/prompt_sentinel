import React, { useCallback, useState } from 'react';
import { UploadCloud, File, AlertCircle, X, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface FileDropzoneProps {
  onScan: (file: File) => void;
  disabled: boolean;
}

const SUPPORTED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/html', 'message/rfc822', 'text/plain', 'application/zip', 'text/markdown', 'application/json', 'text/csv', 'application/xml', 'text/xml', 'image/png', 'image/jpeg', 'image/tiff'];
const SUPPORTED_EXTS = ['.pdf', '.docx', '.html', '.htm', '.eml', '.txt', '.zip', '.md', '.json', '.csv', '.xml', '.png', '.jpg', '.jpeg', '.tiff', '.tif'];
const MAX_SIZE_MB = 50;

export const FileDropzone: React.FC<FileDropzoneProps> = ({ onScan, disabled }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const validateFile = (file: File) => {
    setError(null);
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!SUPPORTED_EXTS.includes(ext) && !SUPPORTED_TYPES.includes(file.type)) {
      setError(`Unsupported file type. Supported: ${SUPPORTED_EXTS.join(', ')}`);
      return false;
    }
    
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File size exceeds ${MAX_SIZE_MB}MB limit.`);
      return false;
    }
    
    return true;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  }, [disabled]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (disabled) return;
    
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  return (
    <div className="glass-panel p-6 mb-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <UploadCloud className="text-primary w-6 h-6" />
        Upload Artifact
      </h3>
      
      {!selectedFile ? (
        <div 
          className={`relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-colors ${
            dragActive ? 'border-primary bg-primary/10' : 'border-white/20 hover:border-white/40 hover:bg-white/5'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            onChange={handleChange}
            disabled={disabled}
            accept={SUPPORTED_EXTS.join(',')}
          />
          <UploadCloud className={`w-12 h-12 mb-4 ${dragActive ? 'text-primary' : 'text-gray-400'}`} />
          <p className="text-lg font-medium text-white mb-2">
            Drag & drop a file here, or click to select
          </p>
          <p className="text-sm text-gray-400 text-center max-w-md">
            Supported formats: {SUPPORTED_EXTS.join(', ')}<br/>
            Max file size: {MAX_SIZE_MB}MB
          </p>
          
          {error && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 flex items-center gap-2 text-danger bg-danger/10 px-4 py-2 rounded-lg">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">{error}</span>
            </motion.div>
          )}
        </div>
      ) : (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="border border-white/20 bg-black/40 rounded-xl p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/20 rounded-lg">
                <File className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-white truncate max-w-xs sm:max-w-md">{selectedFile.name}</h4>
                <p className="text-sm text-gray-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.name.split('.').pop()?.toUpperCase()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button 
                onClick={clearFile}
                disabled={disabled}
                className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors disabled:opacity-50"
                title="Clear file"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div className="mt-6 flex justify-end gap-3">
            <button 
              onClick={clearFile}
              disabled={disabled}
              className="px-4 py-2 rounded-lg border border-white/20 text-gray-300 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button 
              onClick={() => onScan(selectedFile)}
              disabled={disabled}
              className="px-6 py-2 rounded-lg bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-2 transition-colors disabled:opacity-50 neon-accent"
            >
              {disabled ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Scanning...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Scan File
                </>
              )}
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};
