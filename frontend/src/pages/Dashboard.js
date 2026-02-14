import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import StatCard from '../components/StatCard';
import AppointmentDetailModal from '../components/AppointmentDetailModal';
import LeadDetailModal from '../components/LeadDetailModal';
import { dashboardAPI } from '../services/apiService';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [upcoming, setUpcoming] = useState([]);
  const [recentLeads, setRecentLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [showAppointmentDetail, setShowAppointmentDetail] = useState(false);
  const [showLeadDetail, setShowLeadDetail] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      const [statsRes, upcomingRes, leadsRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getUpcoming(5),
        dashboardAPI.getRecentLeads(5),
      ]);
      
      setStats(statsRes.data);
      setUpcoming(upcomingRes.data || []);
      setRecentLeads(leadsRes.data || []);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching dashboard:', error);
      }
      setError('Error cargando datos');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;
  if (error) return <div className="loading" style={{color: 'red'}}>Error: {error}</div>;

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { class: 'status-pending', label: 'Pendiente' },
      'confirmed': { class: 'status-confirmed', label: 'Confirmada' },
      'completed': { class: 'status-completed', label: 'Completada' },
      'cancelled': { class: 'status-cancelled', label: 'Cancelada' },
      'no_show': { class: 'status-noshow', label: 'No asistió' },
    };
    const statusInfo = statusMap[status] || { class: '', label: status };
    return <span className={`status-badge ${statusInfo.class}`}>{statusInfo.label}</span>;
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      {/* Stats Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Leads"
          value={stats?.total_leads || 0}
          change="+12%"
          changeType="positive"
          icon="🎯"
        />
        <StatCard
          title="Citas este mes"
          value={stats?.total_appointments || 0}
          change="+5%"
          changeType="positive"
          icon="📅"
        />
        <StatCard
          title="Tasa de conversión"
          value={`${stats?.conversion_rate || 0}%`}
          change="+2%"
          changeType="positive"
          icon="📈"
        />
        <StatCard
          title="Ingresos"
          value={`$${stats?.revenue_this_month || 0}`}
          change={stats?.revenue_this_month > stats?.revenue_last_month ? '+8%' : '-3%'}
          changeType={stats?.revenue_this_month > stats?.revenue_last_month ? 'positive' : 'negative'}
          icon="💰"
        />
      </div>

      {/* Two Column Layout */}
      <div className="dashboard-grid">
        {/* Upcoming Appointments */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Próximas citas</h2>
            <Link to="/calendar" className="view-all">Ver todas</Link>
          </div>
          
          {upcoming.length === 0 ? (
            <p className="empty-state">No hay citas próximas</p>
          ) : (
            <div className="appointments-list">
              {upcoming.map((appt) => (
                <div
                  key={appt.id}
                  className="appointment-item clickable"
                  onClick={() => {
                    setSelectedAppointment(appt);
                    setShowAppointmentDetail(true);
                  }}
                >
                  <div className="appointment-info">
                    <h4>{appt.client_name}</h4>
                    <p>{appt.service_type || 'Consulta general'}</p>
                    <span className="appointment-date">
                      {appt.appointment_date} • {appt.start_time}
                    </span>
                  </div>
                  {getStatusBadge(appt.status)}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Leads */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Leads recientes</h2>
            <Link to="/leads" className="view-all">Ver todos</Link>
          </div>
          
          {recentLeads.length === 0 ? (
            <p className="empty-state">No hay leads recientes</p>
          ) : (
            <div className="leads-list">
              {recentLeads.map((lead) => (
                <div
                  key={lead.id}
                  className="lead-item clickable"
                  onClick={() => {
                    setSelectedLead(lead);
                    setShowLeadDetail(true);
                  }}
                >
                  <div className="lead-info">
                    <h4>{lead.name}</h4>
                    <p>{lead.email}</p>
                  </div>
                  <span className={`lead-status status-${lead.status}`}>
                    {lead.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {selectedAppointment && (
        <AppointmentDetailModal
          isOpen={showAppointmentDetail}
          onClose={() => setShowAppointmentDetail(false)}
          appointment={selectedAppointment}
          onEdit={() => {}}
          onDelete={() => {}}
          onRefresh={fetchDashboardData}
        />
      )}

      {selectedLead && (
        <LeadDetailModal
          isOpen={showLeadDetail}
          onClose={() => setShowLeadDetail(false)}
          lead={selectedLead}
          onEdit={() => {}}
          onDelete={() => {}}
          onRefresh={fetchDashboardData}
        />
      )}
    </div>
  );
};

export default Dashboard;
