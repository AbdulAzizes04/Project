import { useRef, useState } from 'react';
import { Upload, Film, Image, X, CheckCircle } from 'lucide-react';

export default function UploadZone({
  label,
  accept,
  icon: Icon = Upload,
  onFile,
  file,
}) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (f) => {
    if (f) onFile?.(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);
  const onChange = (e) => handleFile(e.target.files[0]);

  const ext = accept?.replace(/\./g, '').toUpperCase().split(',').join(' / ');

  return (
    <div
      className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      style={{ position: 'relative', minHeight: 140 }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={onChange}
      />

      {file ? (
        <div className="flex flex-col items-center gap-2">
          <CheckCircle size={32} color="#00ff88" />
          <div style={{ fontSize: 13, fontWeight: 600, color: '#00ff88' }}>
            {file.name}
          </div>
          <div style={{ fontSize: 11, color: '#4a5568' }}>
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onFile?.(null); }}
            style={{
              background: '#ff444422', border: '1px solid #ff444444',
              color: '#ff4444', borderRadius: 6, padding: '3px 10px',
              fontSize: 11, cursor: 'pointer', marginTop: 4,
            }}
          >
            Remove
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          <div
            className="flex items-center justify-center rounded-xl"
            style={{
              width: 52, height: 52,
              background: '#00d4ff12',
              border: '1px solid #00d4ff33',
            }}
          >
            <Icon size={22} color="#00d4ff" />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginBottom: 4 }}>
              {label}
            </div>
            <div style={{ fontSize: 11, color: '#4a5568' }}>
              Drag & drop or <span style={{ color: '#00d4ff' }}>browse</span>
            </div>
            <div style={{ fontSize: 10, color: '#1a2a4a', marginTop: 6, letterSpacing: '0.05em' }}>
              {ext}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
