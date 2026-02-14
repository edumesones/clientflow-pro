import React, { useState, useEffect, useCallback } from 'react';
import Table from '../components/Table';
import Modal from '../components/Modal';
import Button from '../components/Button';
import StatusBadge from '../components/StatusBadge';
import Pagination from '../components/Pagination';
import FormField from '../components/FormField';
import AppointmentForm from '../components/AppointmentForm';
import AppointmentDetailModal from '../components/AppointmentDetailModal';
import { appointmentsAPI } from '../services/apiService';
import './AppointmentsPage.css';

const AppointmentsPage = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState(null);

  // Filters
  const [filters, setFilters] = useState({
    status: '',
    start_date: '',
    end_date: '',
  });

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;

      const response = await appointmentsAPI.getAll(params);
      // Manejar formato paginado o array directo
      setAppointments(response.data?.items || response.data || []);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  };

  const handleQuickFilter = (type) => {
    const today = new Date();
    let start_date = '';
    let end_date = '';

    switch (type) {
      case 'today':
        start_date = today.toISOString().split('T')[0];
        end_date = start_date;
        break;
      case 'week':
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay());
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        start_date = weekStart.toISOString().split('T')[0];
        end_date = weekEnd.toISOString().split('T')[0];
        break;
      case 'month':
        start_date = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        end_date = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().split('T')[0];
        break;
      case 'all':
        start_date = '';
        end_date = '';
        break;
      default:
        break;
    }

    setFilters({ ...filters, start_date, end_date });
    setCurrentPage(1);
  };

  const handleRowClick = (appointment) => {
    setSelectedAppointment(appointment);
    setShowDetail(true);
  };

  const handleCreateAppointment = () => {
    setEditingAppointment(null);
    setShowForm(true);
  };

  const handleEditAppointment = (appointment) => {
    setEditingAppointment(appointment);
    setShowForm(true);
    setShowDetail(false);
  };

  const handleDeleteAppointment = async (appointmentId) => {
    if (window.confirm('¿Estás seguro de que deseas cancelar esta cita?')) {
      try {
        await appointmentsAPI.cancel(appointmentId);
        fetchAppointments();
        setShowDetail(false);
      } catch (error) {
        console.error('Error canceling appointment:', error);
        alert('Error al cancelar la cita');
      }
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingAppointment(null);
    fetchAppointments();
  };

  // Pagination
  const totalPages = Math.ceil(appointments.length / itemsPerPage);
  const paginatedAppointments = appointments.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Table columns
  const columns = [
    {
      Header: 'Cliente',
      accessor: 'client_name',
      sortable: true,
    },
    {
      Header: 'Servicio',
      accessor: 'service_type',
      sortable: true,
      Cell: (row) => row.service_type || 'Consulta general',
    },
    {
      Header: 'Fecha',
      accessor: 'appointment_date',
      sortable: true,
    },
    {
      Header: 'Hora',
      accessor: 'start_time',
      sortable: true,
    },
    {
      Header: 'Estado',
      accessor: 'status',
      Cell: (row) => <StatusBadge status={row.status} type="appointment" />,
    },
  ];

  const actions = (row) => (
    <>
      <Button
        variant="ghost"
        size="small"
        onClick={() => handleEditAppointment(row)}
      >
        Editar
      </Button>
      <Button
        variant="danger"
        size="small"
        onClick={() => handleDeleteAppointment(row.id)}
      >
        Cancelar
      </Button>
    </>
  );

  return (
    <div className="appointments-page">
      <div className="page-header">
        <h1>Citas</h1>
        <Button
          variant="primary"
          onClick={handleCreateAppointment}
          icon="+"
        >
          Nueva Cita
        </Button>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filters-row">
          <FormField
            label="Estado"
            type="select"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            options={[
              { value: '', label: 'Todos' },
              { value: 'pending', label: 'Pendiente' },
              { value: 'confirmed', label: 'Confirmada' },
              { value: 'completed', label: 'Completada' },
              { value: 'cancelled', label: 'Cancelada' },
              { value: 'no_show', label: 'No asistió' },
            ]}
          />

          <FormField
            label="Fecha inicio"
            type="date"
            value={filters.start_date}
            onChange={(e) => handleFilterChange('start_date', e.target.value)}
          />

          <FormField
            label="Fecha fin"
            type="date"
            value={filters.end_date}
            onChange={(e) => handleFilterChange('end_date', e.target.value)}
          />
        </div>

        <div className="quick-filters">
          <span className="quick-filters-label">Filtros rápidos:</span>
          <Button variant="ghost" size="small" onClick={() => handleQuickFilter('today')}>
            Hoy
          </Button>
          <Button variant="ghost" size="small" onClick={() => handleQuickFilter('week')}>
            Esta Semana
          </Button>
          <Button variant="ghost" size="small" onClick={() => handleQuickFilter('month')}>
            Este Mes
          </Button>
          <Button variant="ghost" size="small" onClick={() => handleQuickFilter('all')}>
            Todas
          </Button>
        </div>
      </div>

      {/* Table */}
      <Table
        columns={columns}
        data={paginatedAppointments}
        loading={loading}
        onRowClick={handleRowClick}
        actions={actions}
        emptyMessage="No hay citas programadas"
      />

      {/* Pagination */}
      {!loading && appointments.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={appointments.length}
          itemsPerPage={itemsPerPage}
        />
      )}

      {/* Modals */}
      <Modal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title={editingAppointment ? 'Editar Cita' : 'Nueva Cita'}
        size="large"
      >
        <AppointmentForm
          appointment={editingAppointment}
          onSuccess={handleFormSuccess}
          onCancel={() => setShowForm(false)}
        />
      </Modal>

      {selectedAppointment && (
        <AppointmentDetailModal
          isOpen={showDetail}
          onClose={() => setShowDetail(false)}
          appointment={selectedAppointment}
          onEdit={handleEditAppointment}
          onDelete={handleDeleteAppointment}
          onRefresh={fetchAppointments}
        />
      )}
    </div>
  );
};

export default AppointmentsPage;
