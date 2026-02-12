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

  // Notifications Tab State
  const [notificationsData, setNotificationsData] = useState({
    email_appointment_reminders: true,
    email_appointment_confirmations: true,
    email_new_leads: true,
    email_daily_summary: false,
    email_weekly_summary: true,
    sms_appointment_reminders: false,
    sms_appointment_confirmations: false,
    push_enabled: true,
  });

  // Integrations Tab State
  const [integrationsData, setIntegrationsData] = useState({
    api_key: '',
    webhook_url: '',
    google_calendar_connected: false,
    outlook_calendar_connected: false,
    stripe_connected: false,
    paypal_connected: false,
    zoom_connected: false,
  });

  const handleAccountChange = (e) => {
    const { name, value } = e.target;
    setAccountData(prev => ({ ...prev, [name]: value }));
  };

  const handleBusinessChange = (e) => {
    const { name, value } = e.target;
    setBusinessData(prev => ({ ...prev, [name]: value }));
  };

  const handleNotificationsChange = (e) => {
    const { name, checked } = e.target;
    setNotificationsData(prev => ({ ...prev, [name]: checked }));
  };

  const handleIntegrationsChange = (e) => {
    const { name, value } = e.target;
    setIntegrationsData(prev => ({ ...prev, [name]: value }));
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

  const handleNotificationsSave = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      // TODO: Implement actual API call
      // await settingsAPI.updateNotifications(notificationsData);
      showMessage('Preferencias de notificaciones guardadas', 'success');
    } catch (error) {
      console.error('Error updating notifications:', error);
      showMessage('Error al guardar preferencias', 'error');
    } finally {
      setSaving(false);
    }
  };

  const renderNotificationsTab = () => (
    <form onSubmit={handleNotificationsSave} className="settings-form">
      <div className="form-section">
        <h3>📧 Notificaciones por Email</h3>
        <p className="section-description">
          Configura qué notificaciones deseas recibir por correo electrónico
        </p>

        <div className="toggle-list">
          <div className="toggle-item">
            <input
              type="checkbox"
              id="email_appointment_reminders"
              name="email_appointment_reminders"
              checked={notificationsData.email_appointment_reminders}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="email_appointment_reminders" className="toggle-label">
              <span className="toggle-text">Recordatorios de citas</span>
              <span className="toggle-description">
                Recibe un email 24 horas antes de cada cita
              </span>
            </label>
          </div>

          <div className="toggle-item">
            <input
              type="checkbox"
              id="email_appointment_confirmations"
              name="email_appointment_confirmations"
              checked={notificationsData.email_appointment_confirmations}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="email_appointment_confirmations" className="toggle-label">
              <span className="toggle-text">Confirmaciones de citas</span>
              <span className="toggle-description">
                Confirmación inmediata cuando se agenda una cita
              </span>
            </label>
          </div>

          <div className="toggle-item">
            <input
              type="checkbox"
              id="email_new_leads"
              name="email_new_leads"
              checked={notificationsData.email_new_leads}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="email_new_leads" className="toggle-label">
              <span className="toggle-text">Nuevos leads</span>
              <span className="toggle-description">
                Notificación cuando llega un nuevo lead
              </span>
            </label>
          </div>

          <div className="toggle-item">
            <input
              type="checkbox"
              id="email_daily_summary"
              name="email_daily_summary"
              checked={notificationsData.email_daily_summary}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="email_daily_summary" className="toggle-label">
              <span className="toggle-text">Resumen diario</span>
              <span className="toggle-description">
                Resumen de citas y leads cada mañana
              </span>
            </label>
          </div>

          <div className="toggle-item">
            <input
              type="checkbox"
              id="email_weekly_summary"
              name="email_weekly_summary"
              checked={notificationsData.email_weekly_summary}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="email_weekly_summary" className="toggle-label">
              <span className="toggle-text">Resumen semanal</span>
              <span className="toggle-description">
                Estadísticas y resumen cada lunes
              </span>
            </label>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>📱 Notificaciones SMS</h3>
        <p className="section-description">
          Notificaciones por mensaje de texto (requiere créditos SMS)
        </p>

        <div className="toggle-list">
          <div className="toggle-item">
            <input
              type="checkbox"
              id="sms_appointment_reminders"
              name="sms_appointment_reminders"
              checked={notificationsData.sms_appointment_reminders}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="sms_appointment_reminders" className="toggle-label">
              <span className="toggle-text">Recordatorios de citas por SMS</span>
              <span className="toggle-description">
                SMS 24 horas antes de cada cita
              </span>
            </label>
          </div>

          <div className="toggle-item">
            <input
              type="checkbox"
              id="sms_appointment_confirmations"
              name="sms_appointment_confirmations"
              checked={notificationsData.sms_appointment_confirmations}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="sms_appointment_confirmations" className="toggle-label">
              <span className="toggle-text">Confirmaciones por SMS</span>
              <span className="toggle-description">
                SMS de confirmación al agendar
              </span>
            </label>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>🔔 Notificaciones Push</h3>
        <p className="section-description">
          Alertas en tiempo real en tu navegador
        </p>

        <div className="toggle-list">
          <div className="toggle-item">
            <input
              type="checkbox"
              id="push_enabled"
              name="push_enabled"
              checked={notificationsData.push_enabled}
              onChange={handleNotificationsChange}
              className="toggle-checkbox"
            />
            <label htmlFor="push_enabled" className="toggle-label">
              <span className="toggle-text">Habilitar notificaciones push</span>
              <span className="toggle-description">
                Alertas instantáneas de nuevos leads y citas
              </span>
            </label>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <Button type="submit" variant="primary" loading={saving}>
          Guardar Preferencias
        </Button>
      </div>
    </form>
  );

  const handleGenerateApiKey = () => {
    const newKey = 'sk_live_' + Math.random().toString(36).substring(2, 18);
    setIntegrationsData(prev => ({ ...prev, api_key: newKey }));
    showMessage('API Key generada exitosamente', 'success');
  };

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText(integrationsData.api_key);
    showMessage('API Key copiada al portapapeles', 'success');
  };

  const handleConnectIntegration = (integration) => {
    // Simular conexión a servicio externo
    showMessage(`Conectando con ${integration}... (próximamente)`, 'success');
    // TODO: Implement OAuth flow for each integration
  };

  const handleIntegrationsSave = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      // TODO: Implement actual API call
      // await settingsAPI.updateIntegrations(integrationsData);
      showMessage('Configuración de integraciones guardada', 'success');
    } catch (error) {
      console.error('Error updating integrations:', error);
      showMessage('Error al guardar configuración', 'error');
    } finally {
      setSaving(false);
    }
  };

  const renderIntegrationsTab = () => (
    <form onSubmit={handleIntegrationsSave} className="settings-form">
      <div className="form-section">
        <h3>🔑 API Keys</h3>
        <p className="section-description">
          Usa la API de ClientFlow Pro para integraciones personalizadas
        </p>

        <div className="api-key-section">
          {integrationsData.api_key ? (
            <>
              <div className="api-key-display">
                <code>{integrationsData.api_key}</code>
                <Button
                  type="button"
                  variant="ghost"
                  size="small"
                  onClick={handleCopyApiKey}
                >
                  Copiar
                </Button>
              </div>
              <Button
                type="button"
                variant="danger"
                size="small"
                onClick={() => setIntegrationsData(prev => ({ ...prev, api_key: '' }))}
              >
                Revocar Key
              </Button>
            </>
          ) : (
            <Button
              type="button"
              variant="primary"
              onClick={handleGenerateApiKey}
            >
              Generar API Key
            </Button>
          )}
        </div>

        <FormField
          label="Webhook URL"
          type="text"
          name="webhook_url"
          value={integrationsData.webhook_url}
          onChange={handleIntegrationsChange}
          placeholder="https://tu-servidor.com/webhook"
          helperText="URL para recibir notificaciones de eventos (nuevas citas, leads, etc.)"
        />
      </div>

      <div className="form-section">
        <h3>📅 Calendarios</h3>
        <p className="section-description">
          Sincroniza tus citas con Google Calendar u Outlook
        </p>

        <div className="integration-list">
          <div className="integration-item">
            <div className="integration-info">
              <span className="integration-icon">📅</span>
              <div>
                <h4>Google Calendar</h4>
                <p>Sincronización bidireccional de citas</p>
              </div>
            </div>
            <Button
              type="button"
              variant={integrationsData.google_calendar_connected ? "success" : "secondary"}
              size="small"
              onClick={() => handleConnectIntegration('Google Calendar')}
            >
              {integrationsData.google_calendar_connected ? 'Conectado' : 'Conectar'}
            </Button>
          </div>

          <div className="integration-item">
            <div className="integration-info">
              <span className="integration-icon">📆</span>
              <div>
                <h4>Outlook Calendar</h4>
                <p>Sincroniza con Microsoft Outlook</p>
              </div>
            </div>
            <Button
              type="button"
              variant={integrationsData.outlook_calendar_connected ? "success" : "secondary"}
              size="small"
              onClick={() => handleConnectIntegration('Outlook Calendar')}
            >
              {integrationsData.outlook_calendar_connected ? 'Conectado' : 'Conectar'}
            </Button>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>💳 Pagos</h3>
        <p className="section-description">
          Conecta tu cuenta de pagos para cobrar citas online
        </p>

        <div className="integration-list">
          <div className="integration-item">
            <div className="integration-info">
              <span className="integration-icon">💳</span>
              <div>
                <h4>Stripe</h4>
                <p>Acepta tarjetas de crédito y débito</p>
              </div>
            </div>
            <Button
              type="button"
              variant={integrationsData.stripe_connected ? "success" : "secondary"}
              size="small"
              onClick={() => handleConnectIntegration('Stripe')}
            >
              {integrationsData.stripe_connected ? 'Conectado' : 'Conectar'}
            </Button>
          </div>

          <div className="integration-item">
            <div className="integration-info">
              <span className="integration-icon">💰</span>
              <div>
                <h4>PayPal</h4>
                <p>Acepta pagos con PayPal</p>
              </div>
            </div>
            <Button
              type="button"
              variant={integrationsData.paypal_connected ? "success" : "secondary"}
              size="small"
              onClick={() => handleConnectIntegration('PayPal')}
            >
              {integrationsData.paypal_connected ? 'Conectado' : 'Conectar'}
            </Button>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>🎥 Videollamadas</h3>
        <p className="section-description">
          Enlaces automáticos de videollamada en confirmaciones
        </p>

        <div className="integration-list">
          <div className="integration-item">
            <div className="integration-info">
              <span className="integration-icon">📹</span>
              <div>
                <h4>Zoom</h4>
                <p>Crea reuniones de Zoom automáticamente</p>
              </div>
            </div>
            <Button
              type="button"
              variant={integrationsData.zoom_connected ? "success" : "secondary"}
              size="small"
              onClick={() => handleConnectIntegration('Zoom')}
            >
              {integrationsData.zoom_connected ? 'Conectado' : 'Conectar'}
            </Button>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <Button type="submit" variant="primary" loading={saving}>
          Guardar Configuración
        </Button>
      </div>
    </form>
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
          </button>
          <button
            className={`settings-tab ${activeTab === 'integrations' ? 'active' : ''}`}
            onClick={() => setActiveTab('integrations')}
          >
            <span className="tab-icon">🔌</span>
            <span>Integraciones</span>
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
