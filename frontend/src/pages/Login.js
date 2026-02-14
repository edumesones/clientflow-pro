import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Iniciar sesión</h1>
        <p className="auth-subtitle">Bienvenido de vuelta a ClientFlow Pro</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
        
        <p className="auth-footer">
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>
        
        {/* Debug info solo visible en desarrollo */}
        {process.env.NODE_ENV === 'development' && (
          <>
            <div className="auth-demo">
              <p>Credenciales demo:</p>
              <code>demo@clientflow.pro / demo123</code>
            </div>
            <div style={{
              marginTop: '20px', 
              padding: '10px', 
              background: '#f3f4f6', 
              borderRadius: '4px', 
              fontSize: '11px', 
              color: '#6b7280', 
              wordBreak: 'break-all'
            }}>
              <strong>Debug:</strong> API URL = {process.env.REACT_APP_API_URL || 'localhost:8000'}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Login;
