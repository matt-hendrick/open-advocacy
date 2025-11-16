import React from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Entity, EntityStatusRecord } from '../../types';
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
  centerPoint = [41.8781, -87.6298], // Default to Chicago coordinates
}) => {
  // Map entity_id to status
  const statusMap = statusRecords.reduce(
    (acc, record) => {
      acc[record.entity_id] = record.status;
      return acc;
    },
    {} as Record<string, string>
  );

  // Map district_name to entity status
  const districtStatus: Record<string, string> = {};
  entities.forEach(entity => {
    if (entity.district_name) {
      districtStatus[entity.district_name] = statusMap[entity.id] || 'unknown';
    }
  });

  return (
    <MapContainer center={centerPoint} zoom={10} style={{ height: 400, width: '100%' }}>
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {Object.entries(geojsonByDistrict).map(([districtName, geojson]) => (
        <GeoJSON
          key={districtName}
          data={geojson}
          style={() => ({
            color: '#333',
            weight: 1,
            fillColor: getStatusColor(districtStatus[districtName] as any),
            fillOpacity: 0.7,
          })}
        />
      ))}
    </MapContainer>
  );
};

export default EntityDistrictMap;
