import { Project, ProjectStatus } from '../types';

export const mockProjects: Project[] = [
  {
    id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    title: "Local Park Renovation",
    description: "Advocating for the renovation of Lincoln Park with improved playground equipment and better accessibility features.",
    status: ProjectStatus.ACTIVE,
    active: true,
    created_by: "admin",
    created_at: "2023-01-15T10:00:00",
    updated_at: "2023-01-20T14:30:00",
    vote_count: 352
  },
  {
    id: "6d4ec78e-edc1-4c85-b3e8-42c886f971fb",
    title: "Public Library Funding",
    description: "Supporting increased funding for public libraries to expand digital services and educational programs.",
    status: ProjectStatus.ACTIVE,
    active: true,
    created_by: "admin",
    created_at: "2023-02-05T09:15:00",
    updated_at: "2023-02-10T11:45:00",
    vote_count: 289
  },
  {
    id: "9c8f6e5d-4b3a-2c1d-0e9f-8a7b6c5d4e3f",
    title: "Traffic Calming Measures",
    description: "Advocating for speed bumps and improved signage to reduce speeding in residential neighborhoods.",
    status: ProjectStatus.DRAFT,
    active: true,
    created_by: "admin",
    created_at: "2023-03-01T16:20:00",
    updated_at: "2023-03-01T16:20:00",
    vote_count: 0
  }
];