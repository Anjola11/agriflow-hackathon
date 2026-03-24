import { useState } from 'react';
import Modal from './Modal';
import api from '../utils/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

export default function KYCModal({ isOpen, onClose, role }) {
  const [bvn, setBvn] = useState('');
  const [loading, setLoading] = useState(false);
  const [scoreData, setScoreData] = useState(null); // { trust_score, trust_tier }
  const [view, setView] = useState('input'); // 'input' | 'score'
  const { addToast } = useToast();
  const { fetchProfile } = useAuth();

  const handleBvnVerify = async (e) => {
    e.preventDefault();
    if (bvn.length !== 11 || !/^\d+$/.test(bvn)) {
      addToast("BVN must be exactly 11 digits", "error");
      return;
    }
    setLoading(true);
    try {
      const endpoint = role === 'farmer' ? '/farmers/verify-bvn' : '/investors/verify-bvn';
      const { data } = await api.post(endpoint, { bvn });
      
      // Update local state to trigger rerender immediately on dashboards
      await fetchProfile(); 
      
      const payload = data.data || data; // handle response layout wrappers
      
      if (role === 'farmer') {
        setScoreData({
          trust_score: payload.trust_score || 65,
          trust_tier: payload.trust_tier || 'Emerging Farmer'
        });
        setView('score');
      } else {
        addToast("BVN Verified ✅", "success");
        onClose(); // Advanced to Bank details directly in next steps
      }
    } catch (err) {
      addToast(err.response?.data?.detail || err.response?.data?.message || "Verification failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    if (!tier) return '#D97706';
    const t = tier.toLowerCase();
    if (t.includes('emerging')) return '#D97706'; // Amber
    if (t.includes('verified')) return '#10B981'; // Green
    return '#6B7280';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={view === 'input' ? "Verify identity via BVN" : "BVN Verified ✅"} width={480}>
      {view === 'input' ? (
        <form onSubmit={handleBvnVerify} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
              11-Digit BVN
            </label>
            <input 
              type="text" 
              value={bvn} 
              onChange={e => setBvn(e.target.value.replace(/\D/g, '').slice(0, 11))} 
              placeholder="Enter 11 digit numbers..."
              style={{
                width: '100%',
                padding: '12px 14px',
                borderRadius: '8px',
                border: '1px solid var(--color-border)',
                background: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                fontSize: '15px'
              }}
              required
            />
            <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              We use your BVN to verify your legal identity and build your trust profile.
            </p>
          </div>
          <button 
            type="submit" 
            className="btn btn-solid" 
            disabled={loading || bvn.length !== 11}
            style={{ width: '100%', background: 'var(--color-primary)' }}
          >
            {loading ? "Verifying..." : "Verify BVN"}
          </button>
        </form>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            background: 'linear-gradient(135deg, rgba(217, 119, 6, 0.05) 0%, rgba(217, 119, 6, 0.01) 100%)', 
            border: '1px solid rgba(217, 119, 6, 0.2)', 
            borderRadius: '16px', 
            padding: '24px', 
            marginBottom: '24px' 
          }}>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '8px' }}>Your Trust Score</p>
            <div style={{ fontSize: '42px', fontWeight: 800, color: 'var(--color-text-primary)', marginBottom: '8px' }}>
              {scoreData?.trust_score} <span style={{ fontSize: '20px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>/ 100</span>
            </div>
            
            <div style={{ 
              background: `${getTierColor(scoreData?.trust_tier)}1A`, 
              color: getTierColor(scoreData?.trust_tier), 
              padding: '6px 14px', 
              borderRadius: '20px', 
              display: 'inline-block', 
              fontSize: '13px', 
              fontWeight: 600,
              marginBottom: '16px'
            }}>
              ⭐ {scoreData?.trust_tier}
            </div>
            
            <div style={{ marginTop: '4px', fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
              Add your bank account next to boost your score and unlock full access to listed setups.
            </div>
          </div>
          
          <button 
            className="btn btn-solid" 
            style={{ width: '100%', background: 'var(--color-primary)' }}
            onClick={onClose}
          >
            Continue
          </button>
        </div>
      )}
    </Modal>
  );
}
