import React, { useState } from 'react';
import FormField from '../components/FormField';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';
import './SettingsPage.css';

const SettingsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  // Account Tab State
  const [accountData, setAccountData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Business Tab State
  const [businessData, setBusinessData] = useState({
    timezone: 'America/Mexico_City',
    currency: 'MXN',
    language: 'es',
    date_format: 'DD/MM/YYYY',
  });

  const handleAccountChange = (e) => {
    const { name, value } = e.target;
    setAccountData(prev => ({ ...prev, [name]: value }));
  };

  const handleBusinessChange = (e) => {
    const { name, value } = e.target;
    setBusinessData(prev => ({ ...prev, [name]: value }));
  };

  const handleAccountSave = async (e) => {
    e.preventDefault();

    // Validate password change
    if (accountData.new_password) {
      if (accountData.new_password !== accountData.confirm_password) {
        showMessage('Las contraseñas no coinciden', 'error');
        return;
      }
      if (!accountData.current_password) {
        showMessage('Ingresa tu contraseña actual', 'error');
        return;
      }
      if (accountData.new_password.length < 8) {
        showMessage('La nueva contraseña debe tener al menos 8 caracteres', 'error');
        return;
      }
    }

    try {
      setSaving(true);
      // TODO: Implement actual API call
      // await usersAPI.updateAccount(accountData);
      showMessage('Cuenta actualizada exitosamente', 'success');

      // Clear password fields
      setAccountData(prev => ({
        ...prev,
        current_password: '',
        new_password: '',
        confirm_password: '',
      }));
    } catch (error) {
      console.error('Error updating account:', error);
      showMessage('Error al actualizar la cuenta', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleBusinessSave = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      // TODO: Implement actual API call
      // await professionalsAPI.updateBusinessSettings(businessData);
      showMessage('Configuración guardada exitosamente', 'success');
    } catch (error) {
      console.error('Error updating business settings:', error);
      showMessage('Error al guardar configuración', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleExportData = async () => {
    if (window.confirm('¿Exportar todos tus datos en formato CSV?')) {
      try {
        // TODO: Implement actual API call
        // const response = await usersAPI.exportData();
        showMessage('Datos exportados exitosamente. Revisa tu email.', 'success');
      } catch (error) {
        console.error('Error exporting data:', error);
        showMessage('Error al exportar datos', 'error');
      }
    }
  };

  const handleDeleteAccount = async () => {
    const confirmation = window.prompt(
      'Esta acción es IRREVERSIBLE. Todos tus datos serán eliminados permanentemente.\\n\\n' +
      'Para confirmar, escribe "ELIMINAR CUENTA":'
    );

    if (confirmation === 'ELIMINAR CUENTA') {
      try {
        // TODO: Implement actual API call
        // await usersAPI.deleteAccount();
        showMessage('Cuenta eliminada. Redirigiendo...', 'success');
        // Logout and redirect
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } catch (error) {
        console.error('Error deleting account:', error);
        showMessage('Error al eliminar cuenta', 'error');
      }
    } else if (confirmation !== null) {
      showMessage('Texto incorrecto. Eliminación cancelada.', 'error');
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  };

  const renderAccountTab = () => (
    <form onSubmit={handleAccountSave} className="settings-form">
      <div className="form-section">
        <h3>Información Personal</h3>

        <FormField
          label="Nombre completo"
          name="full_name"
          value={accountData.full_name}
          onChange={handleAccountChange}
          required
        />

        <FormField
          label="Email"
          type="email"
          name="email"
          value={accountData.email}
          onChange={handleAccountChange}
          disabled
          helperText="Contacta soporte para cambiar tu email"
        />

        <FormField
          label="Teléfono"
          type="tel"
          name="phone"
          value={accountData.phone}
          onChange={handleAccountChange}
          placeholder="555-123-4567"
        />
      </div>

      <div className="form-section">
        <h3>Cambiar Contraseña</h3>

        <FormField
          label="Contraseña actual"
          type="password"
          name="current_password"
          value={accountData.current_password}
          onChange={handleAccountChange}
          placeholder="••••••••"
        />

        <FormField
          label="Nueva contraseña"
          type="password"
          name="new_password"
          value={accountData.new_password}
          onChange={handleAccountChange}
          placeholder="••••••••"
          helperText="Mínimo 8 caracteres"
        />

        <FormField
          label="Confirmar nueva contraseña"
          type="password"
          name="confirm_password"
          value={accountData.confirm_password}
          onChange={handleAccountChange}
          placeholder="••••••••"
        />
      </div>

      <div className="form-actions">
        <Button type="submit" variant="primary" loading={saving}>
          Guardar Cambios
        </Button>
      </div>
    </form>
  );

  const renderBusinessTab = () => (
    <form onSubmit={handleBusinessSave} className="settings-form">
      <div className="form-section">
        <h3>Preferencias de Negocio</h3>

        <FormField
          label="Zona horaria"
          type="select"
          name="timezone"
          value={businessData.timezone}
          onChange={handleBusinessChange}
          options={[
            { value: 'America/Mexico_City', label: 'Ciudad de México (GMT-6)' },
            { value: 'America/Monterrey', label: 'Monterrey (GMT-6)' },
            { value: 'America/Cancun', label: 'Cancún (GMT-5)' },
            { value: 'America/Tijuana', label: 'Tijuana (GMT-8)' },
            { value: 'America/New_York', label: 'Nueva York (GMT-5)' },
            { value: 'America/Los_Angeles', label: 'Los Ángeles (GMT-8)' },
          ]}
        />

        <FormField
          label="Moneda"
          type="select"
          name="currency"
          value={businessData.currency}
          onChange={handleBusinessChange}
          options={[
            { value: 'MXN', label: 'Peso Mexicano (MXN)' },
            { value: 'USD', label: 'Dólar Estadounidense (USD)' },
            { value: 'EUR', label: 'Euro (EUR)' },
          ]}
        />

        <FormField
          label="Idioma"
          type="select"
          name="language"
          value={businessData.language}
          onChange={handleBusinessChange}
          options={[
            { value: 'es', label: 'Español' },
            { value: 'en', label: 'English' },
          ]}
          helperText="Idioma de la interfaz y emails"
        />

        <FormField
          label="Formato de fecha"
          type="select"
          name="date_format"
          value={businessData.date_format}
          onChange={handleBusinessChange}
          options={[
            { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (31/12/2026)' },
            { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/31/2026)' },
            { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2026-12-31)' },
          ]}
        />
      </div>

      <div className="form-actions">
        <Button type="submit" variant="primary" loading={saving}>
          Guardar Configuración
        </Button>
      </div>
    </form>
  );

  const renderNotificationsTab = () => (
    <div className="placeholder-tab">
      <div className="placeholder-content">
        <h3>📧 Notificaciones</h3>
        <p>La configuración de notificaciones estará disponible en la Fase 3.</p>
        <ul>
          <li>Preferencias de email (recordatorios, confirmaciones)</li>
          <li>Notificaciones SMS</li>
          <li>Alertas push</li>
          <li>Resumen diario/semanal</li>
        </ul>
      </div>
    </div>
  );

  const renderIntegrationsTab = () => (
    <div className="placeholder-tab">
      <div className="placeholder-content">
        <h3>🔌 Integraciones</h3>
        <p>Las integraciones estarán disponibles en la Fase 3.</p>
        <ul>
          <li>API Keys</li>
          <li>Webhooks</li>
          <li>Calendario (Google, Outlook)</li>
          <li>Pagos (Stripe, PayPal)</li>
          <li>Zoom / Google Meet</li>
        </ul>
      </div>
    </div>
  );

  const renderDangerTab = () => (
    <div className="settings-form">
      <div className="danger-section">
        <h3>⚠️ Zona de Peligro</h3>
        <p className="danger-warning">
          Las acciones en esta sección son irreversibles. Procede con precaución.
        </p>

        <div className="danger-action">
          <div className="action-info">
            <h4>Exportar Datos</h4>
            <p>Descarga todos tus datos en formato CSV</p>
          </div>
          <Button variant="secondary" onClick={handleExportData}>
            Exportar Datos
          </Button>
        </div>

        <div className="danger-action">
          <div className="action-info">
            <h4>Eliminar Cuenta</h4>
            <p>Elimina permanentemente tu cuenta y todos tus datos</p>
          </div>
          <Button variant="danger" onClick={handleDeleteAccount}>
            Eliminar Cuenta
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Configuración</h1>
        <p className="settings-subtitle">
          Gestiona tu cuenta y preferencias
        </p>
      </div>

      {message && (
        <div className={`message-banner message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="settings-container">
        <div className="settings-sidebar">
          <button
            className={`settings-tab ${activeTab === 'account' ? 'active' : ''}`}
            onClick={() => setActiveTab('account')}
          >
            <span className="tab-icon">👤</span>
            <span>Cuenta</span>
          </button>
          <button
            className={`settings-tab ${activeTab === 'business' ? 'active' : ''}`}
            onClick={() => setActiveTab('business')}
          >
            <span className="tab-icon">💼</span>
            <span>Negocio</span>
          </button>
          <button
            className={`settings-tab ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            <span className="tab-icon">🔔</span>
            <span>Notificaciones</span>
            <span className="tab-badge">Fase 3</span>
          </button>
          <button
            className={`settings-tab ${activeTab === 'integrations' ? 'active' : ''}`}
            onClick={() => setActiveTab('integrations')}
          >
            <span className="tab-icon">🔌</span>
            <span>Integraciones</span>
            <span className="tab-badge">Fase 3</span>
          </button>
          <button
            className={`settings-tab ${activeTab === 'danger' ? 'active' : ''}`}
            onClick={() => setActiveTab('danger')}
          >
            <span className="tab-icon">⚠️</span>
            <span>Zona de Peligro</span>
          </button>
        </div>

        <div className="settings-content">
          {activeTab === 'account' && renderAccountTab()}
          {activeTab === 'business' && renderBusinessTab()}
          {activeTab === 'notifications' && renderNotificationsTab()}
          {activeTab === 'integrations' && renderIntegrationsTab()}
          {activeTab === 'danger' && renderDangerTab()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
