import React, { useState, useEffect, useCallback } from 'react';
import Table from '../components/Table';
import Modal from '../components/Modal';
import Button from '../components/Button';
import StatusBadge from '../components/StatusBadge';
import Pagination from '../components/Pagination';
import FormField from '../components/FormField';
import LeadForm from '../components/LeadForm';
import LeadDetailModal from '../components/LeadDetailModal';
import { leadsAPI } from '../services/apiService';
import './LeadsPage.css';

const LeadsPage = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [editingLead, setEditingLead] = useState(null);

  const [filters, setFilters] = useState({
    status: '',
    source: '',
    search: '',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  const fetchLeads = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;

      const response = await leadsAPI.getAll(params);
      // Manejar formato paginado o array directo
      setLeads(response.data?.items || response.data || []);
    } catch (error) {
      console.error('Error fetching leads:', error);
      setLeads([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  };

  const handleRowClick = (lead) => {
    setSelectedLead(lead);
    setShowDetail(true);
  };

  const handleCreateLead = () => {
    setEditingLead(null);
    setShowForm(true);
  };

  const handleEditLead = (lead) => {
    setEditingLead(lead);
    setShowForm(true);
    setShowDetail(false);
  };

  const handleDeleteLead = async (leadId) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este lead?')) {
      try {
        await leadsAPI.update(leadId, { status: 'lost' });
        fetchLeads();
        setShowDetail(false);
      } catch (error) {
        console.error('Error deleting lead:', error);
        alert('Error al eliminar el lead');
      }
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingLead(null);
    fetchLeads();
  };

  const totalPages = Math.ceil(leads.length / itemsPerPage);
  const paginatedLeads = leads.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const columns = [
    {
      Header: 'Nombre',
      accessor: 'name',
      sortable: true,
    },
    {
      Header: 'Email',
      accessor: 'email',
      sortable: true,
    },
    {
      Header: 'Teléfono',
      accessor: 'phone',
      Cell: (row) => row.phone || '-',
    },
    {
      Header: 'Fuente',
      accessor: 'source',
      sortable: true,
    },
    {
      Header: 'Estado',
      accessor: 'status',
      Cell: (row) => <StatusBadge status={row.status} type="lead" />,
    },
  ];

  const actions = (row) => (
    <>
      <Button
        variant="ghost"
        size="small"
        onClick={() => handleEditLead(row)}
      >
        Editar
      </Button>
      <Button
        variant="danger"
        size="small"
        onClick={() => handleDeleteLead(row.id)}
      >
        Eliminar
      </Button>
    </>
  );

  return (
    <div className="leads-page">
      <div className="page-header">
        <h1>Leads</h1>
        <Button
          variant="primary"
          onClick={handleCreateLead}
          icon="+"
        >
          Nuevo Lead
        </Button>
      </div>

      <div className="filters-section">
        <div className="filters-row">
          <FormField
            label="Estado"
            type="select"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            options={[
              { value: '', label: 'Todos' },
              { value: 'new', label: 'Nuevo' },
              { value: 'contacted', label: 'Contactado' },
              { value: 'converted', label: 'Convertido' },
              { value: 'lost', label: 'Perdido' },
            ]}
          />

          <FormField
            label="Búsqueda"
            type="text"
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            placeholder="Buscar por nombre, email o teléfono..."
          />
        </div>
      </div>

      <Table
        columns={columns}
        data={paginatedLeads}
        loading={loading}
        onRowClick={handleRowClick}
        actions={actions}
        emptyMessage="No hay leads registrados"
      />

      {!loading && leads.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={leads.length}
          itemsPerPage={itemsPerPage}
        />
      )}

      <Modal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title={editingLead ? 'Editar Lead' : 'Nuevo Lead'}
        size="medium"
      >
        <LeadForm
          lead={editingLead}
          onSuccess={handleFormSuccess}
          onCancel={() => setShowForm(false)}
        />
      </Modal>

      {selectedLead && (
        <LeadDetailModal
          isOpen={showDetail}
          onClose={() => setShowDetail(false)}
          lead={selectedLead}
          onEdit={handleEditLead}
          onDelete={handleDeleteLead}
          onRefresh={fetchLeads}
        />
      )}
    </div>
  );
};

export default LeadsPage;
