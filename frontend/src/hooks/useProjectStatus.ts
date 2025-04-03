import { useState, useEffect } from 'react';
import { statusService } from '../services/status';
import { EntityStatusRecord } from '../types';

export const useProjectStatus = (projectId: string | undefined) => {
  const [statusRecords, setStatusRecords] = useState<EntityStatusRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatusRecords = async () => {
      if (!projectId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await statusService.getStatusRecords(projectId);
        setStatusRecords(response.data);
      } catch (err) {
        console.error('Error fetching status records:', err);
        setError('Failed to load status data');
      } finally {
        setLoading(false);
      }
    };

    fetchStatusRecords();
  }, [projectId]);

  return { statusRecords, loading, error };
};
