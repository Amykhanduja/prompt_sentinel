import React from 'react';
import { NormalizedScanResult } from '../../services/scannerApi';
import { File, Calendar, HardDrive, Hash, AlignLeft, Layers } from 'lucide-react';

interface FileMetadataProps {
  data: NormalizedScanResult;
}

export const FileMetadata: React.FC<FileMetadataProps> = ({ data }) => {
  const meta = data.metadata;

  return (
    <div className="glass-panel p-5">
      <h3 className="text-lg font-bold flex items-center gap-2 text-white mb-4">
        <File className="w-5 h-5 text-primary" />
        File Information
      </h3>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><AlignLeft className="w-4 h-4"/> Filename</span>
          <span className="text-sm font-medium text-gray-200 truncate max-w-[200px]" title={meta.filename}>{meta.filename}</span>
        </div>
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><File className="w-4 h-4"/> Extension</span>
          <span className="text-sm font-medium text-gray-200 uppercase">{meta.extension || 'Unknown'}</span>
        </div>
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><HardDrive className="w-4 h-4"/> Size</span>
          <span className="text-sm font-medium text-gray-200">{(meta.sizeBytes / 1024).toFixed(1)} KB</span>
        </div>
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><Calendar className="w-4 h-4"/> Upload Time</span>
          <span className="text-sm font-medium text-gray-200">{new Date(meta.uploadTime).toLocaleString()}</span>
        </div>
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><Hash className="w-4 h-4"/> MIME Type</span>
          <span className="text-sm font-medium text-gray-200">{meta.mimeType || 'application/octet-stream'}</span>
        </div>
        
        <div className="flex justify-between items-center pb-2">
          <span className="text-sm text-gray-400 flex items-center gap-2"><Layers className="w-4 h-4"/> Extracted Parts</span>
          <span className="text-sm font-medium text-gray-200">{data.results.length}</span>
        </div>
      </div>
    </div>
  );
};

