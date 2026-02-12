import React, { useState, useEffect } from 'react';
import Table from '../components/Table';
import Button from '../components/Button';
import ClientDetailModal from '../components/ClientDetailModal';
import './ClientsPage.css';

// TODO: Add to apiService.js when backend implements /api/users/clients endpoint
const mockClientsAPI = {
  getAll: async ({ status, search }) => {
    // Mock data - replace with actual API call when backend is ready
    return {
      data: [
        {
          id: 1,
          full_name: 'Juan Pérez García',
          email: 'juan.perez@email.com',
          phone: '555-0123',
          total_appointments: 12,
          last_appointment_date: '2026-02-10',
          status: 'active',
          no_show_rate: 0,
          created_at: '2025-11-15',
        },
        {
          id: 2,
          full_name: 'María López Sánchez',
          email: 'maria.lopez@email.com',
          phone: '555-0456',
          total_appointments: 8,
          last_appointment_date: '2026-02-08',
          status: 'active',
          no_show_rate: 12.5,
          created_at: '2025-12-01',
        },
        {
          id: 3,
          full_name: 'Carlos Ruiz Medina',
          email: 'carlos.ruiz@email.com',
          phone: '555-0789',
          total_appointments: 5,
          last_appointment_date: '2026-01-20',
          status: 'active',
          no_show_rate: 0,
          created_at: '2026-01-05',
        },
      ],
    };
  },
  getStats: async (clientId) => {
    // Mock stats - replace with actual API call
    return {
      data: {
        total_appointments: 12,
        completed: 10,
        cancelled: 1,
        no_show: 1,
        no_show_rate: 8.3,
        average_rating: 4.8,
      },
    };
  },
};

const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showClientDetail, setShowClientDetail] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
  });

  useEffect(() => {
    fetchClients();
  }, [filters]);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await mockClientsAPI.getAll(filters);
      setClients(response.data);
    } catch (error) {
      console.error('Error fetching clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClientClick = (client) => {
    setSelectedClient(client);
    setShowClientDetail(true);
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value,
    }));
  };

  const handleSearch = (searchTerm) => {
    setFilters(prev => ({
      ...prev,
      search: searchTerm,
    }));
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      active: { label: 'Activo', className: 'status-active' },
      inactive: { label: 'Inactivo', className: 'status-inactive' },
      vip: { label: 'VIP', className: 'status-vip' },
    };
    const statusInfo = statusMap[status] || { label: status, className: '' };
    return <span className={`client-status-badge ${statusInfo.className}`}>{statusInfo.label}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const columns = [
    {
      key: 'full_name',
      label: 'Nombre',
      sortable: true,
      render: (client) => (
        <div className="client-name-cell">
          <div className="client-avatar">
            {client.full_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="client-name">{client.full_name}</div>
            <div className="client-email">{client.email}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'phone',
      label: 'Teléfono',
      sortable: false,
    },
    {
      key: 'total_appointments',
      label: 'Total Citas',
      sortable: true,
      render: (client) => (
        <span className="appointments-count">{client.total_appointments}</span>
      ),
    },
    {
      key: 'last_appointment_date',
      label: 'Última Cita',
      sortable: true,
      render: (client) => formatDate(client.last_appointment_date),
    },
    {
      key: 'no_show_rate',
      label: 'No-Show',
      sortable: true,
      render: (client) => (
        <span className={`no-show-rate ${client.no_show_rate > 20 ? 'high' : ''}`}>
          {client.no_show_rate}%
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Estado',
      sortable: true,
      render: (client) => getStatusBadge(client.status),
    },
  ];

  return (
    <div className="clients-page">
      <div className="clients-header">
        <div>
          <h1>Clientes (CRM)</h1>
          <p className="clients-subtitle">
            Gestiona tu base de clientes y su historial
          </p>
        </div>
        <Button variant="primary" onClick={() => alert('Crear nuevo cliente - Funcionalidad próximamente')}>
          Nuevo Cliente
        </Button>
      </div>

      <div className="backend-notice">
        <span className="notice-icon">ℹ️</span>
        <div className="notice-content">
          <strong>Nota de Desarrollo:</strong> Esta página muestra datos de ejemplo.
          El endpoint <code>GET /api/users/clients</code> debe implementarse en el backend para conectar datos reales.
        </div>
      </div>

      <div className="clients-filters">
        <div className="filter-group">
          <label>Estado:</label>
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="filter-select"
          >
            <option value="">Todos</option>
            <option value="active">Activo</option>
            <option value="inactive">Inactivo</option>
            <option value="vip">VIP</option>
          </select>
        </div>
      </div>

      <div className="clients-table-container">
        <Table
          columns={columns}
          data={clients}
          onRowClick={handleClientClick}
          loading={loading}
          emptyMessage="No se encontraron clientes"
          searchable
          onSearch={handleSearch}
        />
      </div>

      {selectedClient && showClientDetail && (
        <ClientDetailModal
          isOpen={showClientDetail}
          onClose={() => {
            setShowClientDetail(false);
            setSelectedClient(null);
          }}
          client={selectedClient}
          onRefresh={fetchClients}
        />
      )}
    </div>
  );
};

export default ClientsPage;
