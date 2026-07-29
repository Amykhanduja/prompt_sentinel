export interface ScanResult {
  version: string;
  timestamp: string;
  prompt: string;
  detections: any[];
  risk_score: number;
  severity: string;
  risk_summary: string;
  technique_count: number;
  evidence_groups: any[];
  risk_breakdown: any[];
  action: string;
}

export interface FileScanResponse {
  file: string;
  results: ScanResult[];
  // If it's a single result, it might just return ScanResult directly. 
  // We'll normalize this in the service.
}

export interface NormalizedScanResult {
  file: string;
  size: number;
  type: string;
  results: ScanResult[];
  metadata: {
    filename: string;
    extension: string;
    sizeBytes: number;
    uploadTime: string;
    mimeType: string;
  }
}

export const scanFile = async (file: File): Promise<NormalizedScanResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/v1/scan-file', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Scan failed: ${response.status} ${response.statusText} - ${errorText}`);
  }

  const data = await response.json();
  
  // Normalize the response whether it's a single result or a list of results
  let results: ScanResult[] = [];
  if (data.results && Array.isArray(data.results)) {
    results = data.results;
  } else if (data.prompt || data.detections) {
    // Single result directly returned
    results = [data as ScanResult];
  }

  return {
    file: file.name,
    size: file.size,
    type: file.type,
    results,
    metadata: {
      filename: file.name,
      extension: file.name.split('.').pop() || '',
      sizeBytes: file.size,
      uploadTime: new Date().toISOString(),
      mimeType: file.type,
    }
  };
};
