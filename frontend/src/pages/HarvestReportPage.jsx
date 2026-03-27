import { useState } from 'react';
import { useAuth } from '../context/auth-context';
import { useToast } from '../context/ToastContext';
import { useDropzone } from 'react-dropzone';
import DashboardLayout from '../components/DashboardLayout';
import CurrencyInput from '../components/CurrencyInput';
import { mockFarmerFarms } from '../data/mockData';
import { useNavigate } from 'react-router-dom';
import Icon from '../components/Icon';

const PAYMENT_EVIDENCE_LIMIT_MB = 5;

const mbToBytes = (mb) => mb * 1024 * 1024;

const loadImageFromFile = (file) => new Promise((resolve, reject) => {
  const objectUrl = URL.createObjectURL(file);
  const img = new Image();

  img.onload = () => {
    URL.revokeObjectURL(objectUrl);
    resolve(img);
  };

  img.onerror = () => {
    URL.revokeObjectURL(objectUrl);
    reject(new Error('Unable to load image'));
  };

  img.src = objectUrl;
});

const canvasToBlob = (canvas, quality) => new Promise((resolve, reject) => {
  canvas.toBlob(
    (blob) => {
      if (!blob) {
        reject(new Error('Image compression failed'));
        return;
      }
      resolve(blob);
    },
    'image/jpeg',
    quality
  );
});

async function compressImageIfNeeded(file, maxSizeMB) {
  const maxSizeBytes = mbToBytes(maxSizeMB);
  if (!file?.type?.startsWith('image/') || file.size <= maxSizeBytes) {
    return file;
  }

  const image = await loadImageFromFile(file);
  let width = image.width;
  let height = image.height;
  const maxDimension = 1920;

  if (Math.max(width, height) > maxDimension) {
    const scale = maxDimension / Math.max(width, height);
    width = Math.round(width * scale);
    height = Math.round(height * scale);
  }

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return file;

  canvas.width = width;
  canvas.height = height;
  ctx.drawImage(image, 0, 0, width, height);

  let quality = 0.85;
  let blob = await canvasToBlob(canvas, quality);

  while (blob.size > maxSizeBytes && quality > 0.45) {
    quality -= 0.1;
    blob = await canvasToBlob(canvas, quality);
  }

  if (blob.size > maxSizeBytes) {
    canvas.width = Math.round(width * 0.85);
    canvas.height = Math.round(height * 0.85);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    blob = await canvasToBlob(canvas, Math.max(quality, 0.5));
  }

  if (blob.size > maxSizeBytes) {
    return file;
  }

  const originalName = file.name.replace(/\.[^.]+$/, '');
  return new File([blob], `${originalName}.jpg`, { type: 'image/jpeg' });
}

const navItems = [
  { key: 'farms', label: 'My Farms', icon: 'farms' },
  { key: 'add', label: 'Add Farm', icon: 'add' },
  { key: 'milestones', label: 'Milestones', icon: 'milestones' },
  { key: 'harvest', label: 'Harvest Reports', icon: 'harvest' },
  { key: 'explore', label: 'Explore Farms', icon: 'explore' },
  { key: 'settings', label: 'Settings', icon: 'settings' },
];

export default function HarvestReportPage() {
  const { user, logout } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [ay, setAy] = useState('');
  const [evidence, setEvidence] = useState(null);
  const [selectedFarm, setSelectedFarm] = useState('');
  
  const farms = user?.isNewUser ? [] : mockFarmerFarms;
  const expected = 4.2;
  const v = ay ? (((parseFloat(ay) - expected) / expected) * 100).toFixed(1) : null;
  const { getRootProps, getInputProps } = useDropzone({
    maxFiles: 1,
    accept: { 'image/*': [] },
    onDrop: async (files) => {
      const file = files?.[0];
      if (!file) return;

      try {
        const processed = await compressImageIfNeeded(file, PAYMENT_EVIDENCE_LIMIT_MB);
        if (processed.size > mbToBytes(PAYMENT_EVIDENCE_LIMIT_MB)) {
          addToast(`Evidence image must be ${PAYMENT_EVIDENCE_LIMIT_MB}MB or less`, 'error');
          return;
        }
        setEvidence(processed);
      } catch {
        addToast('Could not optimize image. Please try another file.', 'error');
      }
    },
    onDropRejected: () => {
      addToast('Please upload a valid image file only.', 'error');
    }
  });

  const handleTabChange = (k) => {
    navigate(`/farmer/dashboard?tab=${k}`);
  };

  const navFooter = (
    <>
      <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>{user?.name}</div>
      <button className="btn btn-ghost btn-sm btn-full" onClick={() => { logout(); navigate('/auth'); }}>Log Out</button>
    </>
  );

  return (
    <DashboardLayout navItems={navItems} activeTab="harvest" onTabChange={handleTabChange} footer={navFooter}>
      <div>
        <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '24px', fontFamily: 'var(--font-heading)' }}>Harvest Report</h1>
        <div className="card" style={{ padding: '28px', maxWidth: '560px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div className="form-group">
            <label className="form-label">Select Farm to Report On</label>
            <select className="form-input form-select" value={selectedFarm} onChange={e => setSelectedFarm(e.target.value)}>
              <option value="">Select a farm...</option>
              {farms.length === 0 ? (
                <option value="" disabled>No farms available</option>
              ) : (
                farms.map(f => <option key={f.id} value={f.id}>{f.name} - {f.crop}</option>)
              )}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">
                Actual Yield ({farms.find(f => f.id === selectedFarm)?.crop === 'Poultry' ? 'birds' : 'tons'})
              </label>
              <input className="form-input" type="number" value={ay} onChange={e => setAy(e.target.value)} placeholder="e.g. 3.8" disabled={!selectedFarm} />
            </div>
            <div className="form-group">
              <label className="form-label">Unit</label>
              <select className="form-input form-select" disabled={!selectedFarm}>
                <option>tons</option>
                <option>kg</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Total Sales (₦)</label>
            <CurrencyInput className="form-input text-mono" placeholder="e.g. 950,000" disabled={!selectedFarm} />
          </div>

          <div className="form-group">
            <label className="form-label">Harvest Date</label>
            <input className="form-input" type="date" disabled={!selectedFarm} />
          </div>

          <div className="form-group">
            <label className="form-label">Buyer (optional)</label>
            <input className="form-input" placeholder="e.g. Dangote Foods" disabled={!selectedFarm} />
          </div>
          
          <div className="form-group">
            <label className="form-label">Payment Evidence <span style={{ color: 'var(--color-danger)' }}>*</span></label>
            <div 
              {...getRootProps()} 
              style={{
                border: '2px dashed var(--color-border)', 
                padding: '20px', 
                borderRadius: '8px', 
                textAlign: 'center', 
                cursor: selectedFarm ? 'pointer' : 'not-allowed', 
                background: evidence ? 'var(--color-primary-light)' : 'transparent', 
                borderColor: evidence ? 'var(--color-primary)' : 'var(--color-border)',
                opacity: selectedFarm ? 1 : 0.6
              }}
            >
              <input {...getInputProps()} disabled={!selectedFarm} />
              {evidence ? (
                <span style={{ color: 'var(--color-primary)', fontWeight: 500, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <Icon name="milestones" size={18} /> {evidence.name} attached
                </span>
              ) : (
                <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <Icon name="add" size={20} /> Upload bank alert or receipt photo
                </span>
              )}
            </div>
            <p style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '6px' }}>Required to verify harvest proceeds before investor payout. Max size: {PAYMENT_EVIDENCE_LIMIT_MB}MB.</p>
          </div>

          {v !== null && selectedFarm && (
            <div style={{ padding: '12px 16px', background: 'var(--color-card-alt)', borderRadius: '8px', fontSize: '13px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <span>Expected: <strong>{expected} tons</strong></span>
              <span>Reported: <strong>{ay} tons</strong></span>
              <span>Variance: <strong style={{ color: parseFloat(v) > -10 ? 'var(--color-accent)' : 'var(--color-danger)' }}>{v > 0 ? '+' : ''}{v}%</strong></span>
            </div>
          )}

          <button className="btn btn-solid" disabled={!selectedFarm || !ay || !evidence} onClick={() => addToast('Harvest report submitted!', 'success', 'Option A Verification step initiated.')}>
            Submit Report & Evidence
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
