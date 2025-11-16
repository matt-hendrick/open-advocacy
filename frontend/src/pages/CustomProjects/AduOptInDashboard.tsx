import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../../services/projects';
import ProjectDetail from '../ProjectDetail';
import { Project } from '../../types';

const STATUS_DISPLAY_NAMES: Record<string, string> = {
  solid_approval: 'Opted In',
  leaning_approval: 'Not Eligible',
  neutral: 'Neutral',
  leaning_disapproval: 'Leaning Disagree',
  solid_disapproval: 'Strongly Opposed',
  unknown: 'Unknown',
};

const ADU_PROJECT_NAME = 'ADU Opt-In Dashboard';

const AduOptInDashboard: React.FC = () => {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjectId = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await projectService.getProjectByName(ADU_PROJECT_NAME);
        if (response.data) {
          setProjectId(response.data.id);
        } else {
          setError('ADU Opt-In project not found');
        }
      } catch (err) {
        setError('Failed to load ADU Opt-In project');
      } finally {
        setLoading(false);
      }
    };
    fetchProjectId();
  }, []);

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  if (error || !projectId) {
    return (
      <div>
        <p>{error || 'Project not found.'}</p>
        <button onClick={() => navigate('/projects')}>Back to Projects</button>
      </div>
    );
  }

  return (
    <ProjectDetail
      projectId={projectId}
      statusDisplayNames={STATUS_DISPLAY_NAMES}
      isDashboard={true}
    />
  );
};

export default AduOptInDashboard;
