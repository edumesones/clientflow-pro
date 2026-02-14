import React, { useState, useEffect, useCallback } from 'react';
import Table from '../components/Table';
import Button from '../components/Button';
import ClientDetailModal from '../components/ClientDetailModal';
import { usersAPI } from '../services/apiService';
import './ClientsPage.css';

const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showClientDetail, setShowClientDetail] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
  });

  const fetchClients = useCallback(async () => {
    try {
      setLoading(true);
      const response = await usersAPI.getClients(filters);
      // Manejar formato paginado o array directo
      const clientsData = response.data?.items || response.data || [];
      setClients(clientsData);
    } catch (error) {
      console.error('Error fetching clients:', error);
      alert('Error al cargar clientes. Por favor intenta de nuevo.');
      setClients([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

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
