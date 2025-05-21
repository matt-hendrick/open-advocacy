import api from './api';
import { UserProfile, PasswordChangeData, UserRoleChangeData } from '../types';

export const userService = {
  async getUsersInGroup(groupId: string): Promise<UserProfile[]> {
    const response = await api.get<UserProfile[]>(`/users/group/${groupId}`);
    return response.data;
  },

  async updateUserRole(data: UserRoleChangeData): Promise<UserProfile> {
    const response = await api.patch<UserProfile>(`/users/${data.user_id}/role`, {
      role: data.new_role,
    });
    return response.data;
  },

  async updateUserPassword(data: PasswordChangeData): Promise<{ success: boolean }> {
    const response = await api.patch<{ success: boolean }>(`/users/${data.user_id}/password`, {
      password: data.new_password,
    });
    return response.data;
  },
};
