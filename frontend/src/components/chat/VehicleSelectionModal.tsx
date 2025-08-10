'use client';

import { useState, useEffect } from 'react';
import { useLanguage, useTranslations } from '@/hooks/useLanguage';
import styles from '@/styles/vehicle-modal.module.css';

interface VehicleType {
  id: number;
  vehicleType: string;
}

interface Manufacturer {
  manufacturerId: number;
  brand: string;
}

interface Model {
  modelId: number;
  modelName: string;
  modelYearFrom?: string;
  modelYearTo?: string;
}

interface Vehicle {
  vehicleId: number;
  manufacturerName: string;
  modelName: string;
  typeEngineName: string;
  constructionIntervalStart: string;
  constructionIntervalEnd?: string;
  powerKw: string;
  powerPs: string;
  fuelType: string;
  bodyType: string;
  numberOfCylinders: number;
  capacityLt: string;
}

interface VehicleSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVehicleSelect: (vehicle: Vehicle & { 
    vehicle_type_id: number; 
    manufacturer_id: number; 
    model_id: number;
    manufacturer_name: string;
    model_name: string;
    engine_name: string;
    year: string;
  }) => void;
  vehicleTypes: VehicleType[];
  onSendMessage: (message: string) => void;
  onDataHandlerReady: (handler: (data: any) => void) => void;
}

export function VehicleSelectionModal({ 
  isOpen, 
  onClose, 
  onVehicleSelect, 
  vehicleTypes,
  onSendMessage,
  onDataHandlerReady 
}: VehicleSelectionModalProps) {
  const { language } = useLanguage();
  const { t } = useTranslations();
  
  // State for dropdown selections
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  
  // Selected values
  const [selectedVehicleType, setSelectedVehicleType] = useState<number | null>(null);
  const [selectedManufacturer, setSelectedManufacturer] = useState<number | null>(null);
  const [selectedModel, setSelectedModel] = useState<number | null>(null);
  
  // Filter states
  const [showFilters, setShowFilters] = useState(false);
  const [startYear, setStartYear] = useState<string>('');
  const [endYear, setEndYear] = useState<string>('');
  
  // Search states
  const [vehicleTypeSearch, setVehicleTypeSearch] = useState('');
  const [manufacturerSearch, setManufacturerSearch] = useState('');
  const [modelSearch, setModelSearch] = useState('');
  
  // Loading states
  const [loadingManufacturers, setLoadingManufacturers] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [loadingVehicles, setLoadingVehicles] = useState(false);

  // Set up data handler when component mounts
  useEffect(() => {
    const handleData = (data: any) => {
      try {
        if (data.type === 'MANUFACTURERS_DATA') {
          setManufacturers(data.data);
          setLoadingManufacturers(false);
        } else if (data.type === 'MODELS_DATA') {
          setModels(data.data);
          setLoadingModels(false);
        } else if (data.type === 'VEHICLES_DATA') {
          setVehicles(data.data);
          setLoadingVehicles(false);
        } else if (data.type === 'ERROR') {
          console.error('Backend error:', data.message);
          setLoadingManufacturers(false);
          setLoadingModels(false);
          setLoadingVehicles(false);
        }
      } catch (error) {
        console.error('Error handling data:', error);
      }
    };

    onDataHandlerReady(handleData);
  }, [onDataHandlerReady]);

  // Load manufacturers when vehicle type is selected
  useEffect(() => {
    if (selectedVehicleType) {
      loadManufacturers(selectedVehicleType);
    }
  }, [selectedVehicleType]);

  // Load models when manufacturer is selected
  useEffect(() => {
    if (selectedManufacturer && selectedVehicleType) {
      loadModels(selectedManufacturer, selectedVehicleType);
    }
  }, [selectedManufacturer, selectedVehicleType]);

  // Load vehicles when model is selected
  useEffect(() => {
    if (selectedModel && selectedManufacturer && selectedVehicleType) {
      loadVehicles(selectedModel, selectedManufacturer, selectedVehicleType);
    }
  }, [selectedModel, selectedManufacturer, selectedVehicleType]);

  // Apply filters when vehicles or filter values change
  useEffect(() => {
    applyFilters();
  }, [vehicles, startYear, endYear]);

  const loadManufacturers = async (typeId: number) => {
    setLoadingManufacturers(true);
    setManufacturers([]);
    setModels([]);
    setVehicles([]);
    setSelectedManufacturer(null);
    setSelectedModel(null);
    
    try {
      // Send request through chat interface to get manufacturers
      onSendMessage(`GET_MANUFACTURERS:${typeId}`);
      // Note: The actual data loading will be handled by the backend
      // and returned through the chat interface
    } catch (error) {
      console.error('Error loading manufacturers:', error);
      setLoadingManufacturers(false);
    }
  };

  const loadModels = async (manufacturerId: number, typeId: number) => {
    setLoadingModels(true);
    setModels([]);
    setVehicles([]);
    setSelectedModel(null);
    
    try {
      onSendMessage(`GET_MODELS:${manufacturerId}:${typeId}`);
    } catch (error) {
      console.error('Error loading models:', error);
      setLoadingModels(false);
    }
  };

  const loadVehicles = async (modelId: number, manufacturerId: number, typeId: number) => {
    setLoadingVehicles(true);
    setVehicles([]);
    
    try {
      onSendMessage(`GET_VEHICLES:${modelId}:${manufacturerId}:${typeId}`);
    } catch (error) {
      console.error('Error loading vehicles:', error);
      setLoadingVehicles(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...vehicles];
    
    if (startYear || endYear) {
      filtered = filtered.filter(vehicle => {
        const vehicleStartYear = parseInt(vehicle.constructionIntervalStart);
        const vehicleEndYear = vehicle.constructionIntervalEnd ? parseInt(vehicle.constructionIntervalEnd) : new Date().getFullYear();
        
        if (startYear && vehicleEndYear < parseInt(startYear)) return false;
        if (endYear && vehicleStartYear > parseInt(endYear)) return false;
        
        return true;
      });
    }
    
    setFilteredVehicles(filtered);
  };

  const handleVehicleSelect = (vehicle: Vehicle) => {
    if (!selectedVehicleType || !selectedManufacturer || !selectedModel) return;
    
    const vehicleWithIds = {
      ...vehicle,
      vehicle_type_id: selectedVehicleType,
      manufacturer_id: selectedManufacturer,
      model_id: selectedModel,
      manufacturer_name: vehicle.manufacturerName,
      model_name: vehicle.modelName,
      engine_name: vehicle.typeEngineName,
      year: vehicle.constructionIntervalStart
    };
    
    onVehicleSelect(vehicleWithIds);
    onClose();
  };

  const resetSelections = () => {
    setSelectedVehicleType(null);
    setSelectedManufacturer(null);
    setSelectedModel(null);
    setManufacturers([]);
    setModels([]);
    setVehicles([]);
    setFilteredVehicles([]);
    setStartYear('');
    setEndYear('');
    setShowFilters(false);
  };

  const filterOptions = (options: any[], searchTerm: string, labelKey: string) => {
    if (!searchTerm) return options;
    return options.filter(option => 
      option[labelKey].toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const getVehicleTypeLabel = (vehicleType: string) => {
    return t(`vehicles.vehicleTypes.${vehicleType}`) || vehicleType;
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>{t('vehicles.vehicleSelection.title')}</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.modalBody}>
          {/* Vehicle Type Selection */}
          <div className={styles.dropdownContainer}>
            <label>{t('vehicles.vehicleSelection.vehicleType')}</label>
            <input
              type="text"
              placeholder={t('vehicles.vehicleSelection.searchPlaceholder')}
              value={vehicleTypeSearch}
              onChange={(e) => setVehicleTypeSearch(e.target.value)}
              className={styles.searchInput}
            />
            <select
              value={selectedVehicleType || ''}
              onChange={(e) => setSelectedVehicleType(Number(e.target.value))}
              className={styles.dropdown}
            >
              <option value="">{t('vehicles.vehicleSelection.selectType')}</option>
              {filterOptions(vehicleTypes, vehicleTypeSearch, 'vehicleType').map(type => (
                <option key={type.id} value={type.id}>
                  {getVehicleTypeLabel(type.vehicleType)}
                </option>
              ))}
            </select>
          </div>

          {/* Manufacturer Selection */}
          {selectedVehicleType && (
            <div className={styles.dropdownContainer}>
              <label>{t('vehicles.vehicleSelection.manufacturer')}</label>
              <input
                type="text"
                placeholder={t('vehicles.vehicleSelection.searchPlaceholder')}
                value={manufacturerSearch}
                onChange={(e) => setManufacturerSearch(e.target.value)}
                className={styles.searchInput}
              />
              <select
                value={selectedManufacturer || ''}
                onChange={(e) => setSelectedManufacturer(Number(e.target.value))}
                className={styles.dropdown}
                disabled={loadingManufacturers}
              >
                <option value="">
                  {loadingManufacturers ? t('vehicles.vehicleSelection.loading') : t('vehicles.vehicleSelection.selectManufacturer')}
                </option>
                {filterOptions(manufacturers, manufacturerSearch, 'brand').map(manufacturer => (
                  <option key={manufacturer.manufacturerId} value={manufacturer.manufacturerId}>
                    {manufacturer.brand}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Model Selection */}
          {selectedManufacturer && (
            <div className={styles.dropdownContainer}>
              <label>{t('vehicles.vehicleSelection.model')}</label>
              <input
                type="text"
                placeholder={t('vehicles.vehicleSelection.searchPlaceholder')}
                value={modelSearch}
                onChange={(e) => setModelSearch(e.target.value)}
                className={styles.searchInput}
              />
              <select
                value={selectedModel || ''}
                onChange={(e) => setSelectedModel(Number(e.target.value))}
                className={styles.dropdown}
                disabled={loadingModels}
              >
                <option value="">
                  {loadingModels ? t('vehicles.vehicleSelection.loading') : t('vehicles.vehicleSelection.selectModel')}
                </option>
                {filterOptions(models, modelSearch, 'modelName').map(model => (
                  <option key={model.modelId} value={model.modelId}>
                    {model.modelName} {model.modelYearFrom && `(${model.modelYearFrom}${model.modelYearTo ? `-${model.modelYearTo}` : '+'})`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Vehicle List */}
          {selectedModel && vehicles.length > 0 && (
            <div className={styles.vehicleListContainer}>
              <div className={styles.filtersHeader}>
                <h3>{t('vehicles.vehicleSelection.selectVehicle')}</h3>
                <button 
                  className={styles.filterToggle}
                  onClick={() => setShowFilters(!showFilters)}
                >
                  {t('vehicles.vehicleSelection.filters')}
                </button>
              </div>

              {showFilters && (
                <div className={styles.filtersPanel}>
                  <h4>{t('vehicles.vehicleSelection.yearRange')}</h4>
                  <div className={styles.yearFilters}>
                    <input
                      type="number"
                      placeholder={t('vehicles.vehicleSelection.startYear')}
                      value={startYear}
                      onChange={(e) => setStartYear(e.target.value)}
                      className={styles.yearInput}
                    />
                    <input
                      type="number"
                      placeholder={t('vehicles.vehicleSelection.endYear')}
                      value={endYear}
                      onChange={(e) => setEndYear(e.target.value)}
                      className={styles.yearInput}
                    />
                  </div>
                  <button 
                    className={styles.clearFiltersButton}
                    onClick={() => {
                      setStartYear('');
                      setEndYear('');
                    }}
                  >
                    {t('vehicles.vehicleSelection.clearFilters')}
                  </button>
                </div>
              )}

              <div className={styles.vehicleList}>
                {filteredVehicles.length === 0 ? (
                  <div className={styles.noResults}>
                    {t('vehicles.vehicleSelection.noResults')}
                  </div>
                ) : (
                  filteredVehicles.map(vehicle => (
                    <div key={vehicle.vehicleId} className={styles.vehicleItem}>
                      <div className={styles.vehicleInfo}>
                        <h4>{vehicle.manufacturerName} {vehicle.modelName}</h4>
                        <p><strong>{t('vehicles.vehicleSelection.engine')}:</strong> {vehicle.typeEngineName}</p>
                        <p><strong>Year:</strong> {vehicle.constructionIntervalStart}{vehicle.constructionIntervalEnd && ` - ${vehicle.constructionIntervalEnd}`}</p>
                        <p><strong>Power:</strong> {vehicle.powerPs} PS ({vehicle.powerKw} kW)</p>
                        <p><strong>Fuel:</strong> {vehicle.fuelType}</p>
                        <p><strong>Body:</strong> {vehicle.bodyType}</p>
                        <p><strong>Capacity:</strong> {vehicle.capacityLt}L</p>
                      </div>
                      <button 
                        className={styles.selectButton}
                        onClick={() => handleVehicleSelect(vehicle)}
                      >
                        {t('vehicles.vehicleSelection.selectButton')}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {loadingVehicles && (
            <div className={styles.loading}>
              {t('vehicles.vehicleSelection.loading')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
