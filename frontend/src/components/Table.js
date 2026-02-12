import React, { useState, useMemo } from 'react';
import './Table.css';

const Table = ({
  columns,
  data,
  onRowClick,
  actions,
  loading = false,
  emptyMessage = 'No hay datos disponibles',
  searchable = false,
  searchPlaceholder = 'Buscar...',
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Filtrar datos por búsqueda
  const filteredData = useMemo(() => {
    if (!searchable || !searchTerm) return data;

    return data.filter(row =>
      columns.some(col => {
        const value = col.accessor ? row[col.accessor] : '';
        return String(value).toLowerCase().includes(searchTerm.toLowerCase());
      })
    );
  }, [data, searchTerm, columns, searchable]);

  // Ordenar datos
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData;

    const sorted = [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === bValue) return 0;

      const comparison = aValue > bValue ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [filteredData, sortConfig]);

  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const handleRowClick = (row) => {
    if (onRowClick) {
      onRowClick(row);
    }
  };

  if (loading) {
    return (
      <div className="table-container">
        <div className="table-loading">
          <div className="spinner"></div>
          <p>Cargando datos...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="table-container">
        <div className="table-empty">
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-container">
      {searchable && (
        <div className="table-search">
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="table-search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
      )}

      {/* Desktop Table View */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.accessor || col.Header}
                  className={col.sortable ? 'sortable' : ''}
                  onClick={() => col.sortable && handleSort(col.accessor)}
                >
                  <div className="th-content">
                    {col.Header}
                    {col.sortable && sortConfig.key === col.accessor && (
                      <span className="sort-indicator">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
              {actions && <th className="actions-column">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr
                key={row.id || rowIndex}
                className={onRowClick ? 'clickable' : ''}
                onClick={() => handleRowClick(row)}
              >
                {columns.map((col) => (
                  <td key={col.accessor || col.Header}>
                    {col.Cell ? col.Cell(row) : row[col.accessor]}
                  </td>
                ))}
                {actions && (
                  <td className="actions-cell" onClick={(e) => e.stopPropagation()}>
                    <div className="actions-wrapper">
                      {actions(row)}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="table-mobile">
        {sortedData.map((row, rowIndex) => (
          <div
            key={row.id || rowIndex}
            className={`mobile-card ${onRowClick ? 'clickable' : ''}`}
            onClick={() => handleRowClick(row)}
          >
            {columns.map((col) => (
              <div key={col.accessor || col.Header} className="mobile-card-row">
                <div className="mobile-card-label">{col.Header}:</div>
                <div className="mobile-card-value">
                  {col.Cell ? col.Cell(row) : row[col.accessor]}
                </div>
              </div>
            ))}
            {actions && (
              <div className="mobile-card-actions" onClick={(e) => e.stopPropagation()}>
                {actions(row)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Table;
