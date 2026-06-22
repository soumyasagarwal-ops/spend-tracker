import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../../api/client';
import type { IngestLog } from '../../types';
import LoadingSpinner from '../shared/LoadingSpinner';

interface Props {
  onClose: () => void;
}

const ACCEPTED_FORMATS = [
  { ext: 'CSV', desc: 'Comma-separated values' },
  { ext: 'XLS', desc: 'Excel 97–2003 workbook' },
  { ext: 'XLSX', desc: 'Excel workbook' },
];

export default function FileUploadModal({ onClose }: Props) {
  const [result, setResult] = useState<IngestLog | null>(null);
  const [extError, setExtError] = useState(false);
  const qc = useQueryClient();

  const upload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      const res = await client.post<IngestLog>('/upload?mode=real', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: (data) => {
      setResult(data);
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  const ALLOWED_EXTS = ['.csv', '.xls', '.xlsx'];

  const onDrop = useCallback((files: File[]) => {
    const file = files[0];
    if (!file) return;
    setExtError(false);
    // Validate by extension — macOS reports inconsistent MIME types for .xls
    const ext = ('.' + (file.name.split('.').pop() ?? '')).toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      setExtError(true);
      return;
    }
    upload.mutate(file);
  }, [upload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    // Don't restrict by MIME type — macOS assigns inconsistent types to .xls files.
    // Extension validation is handled in onDrop instead.
    multiple: false,
    disabled: upload.isPending,
  });

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="font-semibold text-slate-800">Import Bank Statement</h2>
            <p className="text-xs text-slate-400 mt-0.5">Supports HDFC, ICICI, and most Indian bank formats</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors text-xl leading-none">&times;</button>
        </div>

        <div className="p-6 space-y-4">
          {!result ? (
            <>
              {/* Drop zone */}
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-indigo-400 bg-indigo-50'
                    : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50'
                } ${upload.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                {upload.isPending ? (
                  <div className="flex flex-col items-center gap-3">
                    <LoadingSpinner size="lg" />
                    <p className="text-sm text-slate-500">Processing your statement...</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-indigo-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">
                        {isDragActive ? 'Drop your file here' : 'Drag & drop your statement'}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">or <span className="text-indigo-500 font-medium">click to browse</span></p>
                    </div>
                  </div>
                )}
              </div>

              {/* Accepted formats */}
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">Accepted file formats</p>
                <div className="flex gap-2">
                  {ACCEPTED_FORMATS.map(({ ext, desc }) => (
                    <div key={ext} className="flex-1 bg-slate-50 rounded-lg px-3 py-2 text-center border border-slate-100">
                      <p className="text-xs font-bold text-slate-700">.{ext.toLowerCase()}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">{desc}</p>
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-amber-600 mt-2">
                  Note: PDF uploads are not supported. Please export your statement as CSV or Excel from your bank's net banking portal.
                </p>
              </div>

              {extError && (
                <div className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
                  <p className="text-amber-700 text-sm">Unsupported file type. Please upload a .csv, .xls or .xlsx file.</p>
                </div>
              )}
              {upload.isError && (
                <div className="bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                  <p className="text-red-600 text-sm">Upload failed. Please check the file format and try again.</p>
                </div>
              )}
            </>
          ) : (
            <div className="space-y-4">
              {/* Status banner */}
              <div className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium ${
                result.status === 'success'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                  : 'bg-red-50 text-red-700 border border-red-100'
              }`}>
                <span className="text-lg">{result.status === 'success' ? '✓' : '✗'}</span>
                {result.status === 'success' ? 'Import Successful' : 'Import Failed'}
              </div>

              {/* Stats */}
              <div className="bg-slate-50 rounded-xl p-4 space-y-2 text-sm border border-slate-100">
                <div className="flex justify-between">
                  <span className="text-slate-500">File</span>
                  <span className="font-medium text-slate-700 truncate ml-4 max-w-[180px]">{result.filename}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Format detected</span>
                  <span className="font-medium text-slate-700 uppercase">{result.parser_used}</span>
                </div>
                <div className="h-px bg-slate-200 my-1" />
                <div className="flex justify-between">
                  <span className="text-slate-500">New transactions</span>
                  <span className="font-bold text-emerald-600">{result.rows_inserted}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Skipped (already imported)</span>
                  <span className="font-medium text-slate-400">{result.rows_skipped}</span>
                </div>
              </div>

              {result.error_message && (
                <div className="bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                  <p className="text-red-600 text-xs">{result.error_message}</p>
                </div>
              )}

              <button
                onClick={onClose}
                className="w-full bg-indigo-600 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
