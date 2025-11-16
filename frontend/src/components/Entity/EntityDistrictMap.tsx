import React from 'react';
import { MapContainer, TileLayer, GeoJSON, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Entity, EntityStatus, EntityStatusRecord } from '../../types';
import { getStatusColor } from '@/utils/statusColors';

interface EntityDistrictMapProps {
  entities: Entity[];
  statusRecords: EntityStatusRecord[];
  geojsonByDistrict: { [districtName: string]: any };
  centerPoint?: [number, number];
}

const EntityDistrictMap: React.FC<EntityDistrictMapProps> = ({
  entities,
  statusRecords,
  geojsonByDistrict,
  centerPoint = [41.8781, -87.6298],
}) => {
  const statusMap = statusRecords.reduce(
    (acc, record) => {
      acc[record.entity_id] = record.status;
      return acc;
    },
    {} as Record<string, EntityStatus>
  );

  const entityByDistrict: Record<string, Entity | undefined> = {};
  entities.forEach(entity => {
    if (entity.district_name) {
      entityByDistrict[entity.district_name] = entity;
    }
  });

  // TODO: Make this more generic to things beyond wards
  function onEachFeature(feature: any, layer: any) {
    // Get ward number from geojson
    const wardNumber = feature.properties?.ward;
    // Build the district name string to match your entities
    const districtName = wardNumber ? `Ward ${wardNumber}` : undefined;
    const entity = districtName ? entityByDistrict[districtName] : undefined;
    const status = entity ? statusMap[entity.id] : EntityStatus.NEUTRAL;
    let tooltipContent = `<strong>${districtName || 'Unknown Ward'}</strong>`;
    if (entity) {
      tooltipContent += `<br/>${entity.name} (${entity.title || ''})<br/>Status: ${status}`;
    }
    layer.bindTooltip(tooltipContent, { sticky: true });
  }

  return (
    <MapContainer center={centerPoint} zoom={10} style={{ height: 400, width: '100%' }}>
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {Object.entries(geojsonByDistrict).map(([districtName, geojson]) => {
        const wardNumber = districtName.match(/\d+/)?.[0];
        const lookupName = wardNumber ? `Ward ${wardNumber}` : districtName;
        return (
          <GeoJSON
            key={districtName}
            data={geojson}
            style={() => ({
              color: '#333',
              weight: 1,
              fillColor: getStatusColor(
                entityByDistrict[lookupName]
                  ? statusMap[entityByDistrict[lookupName]!.id]
                  : EntityStatus.NEUTRAL
              ),
              fillOpacity: 0.7,
            })}
            onEachFeature={onEachFeature}
          />
        );
      })}
    </MapContainer>
  );
};

export default EntityDistrictMap;
