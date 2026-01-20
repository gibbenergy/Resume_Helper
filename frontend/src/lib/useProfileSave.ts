import { useToast } from '@/components/ui/use-toast';
import { useResumeStore } from '@/stores/resumeStore';
import { api } from '@/lib/api';

export interface SavedProfile {
  id: string;
  name: string;
  timestamp: number;
  data: any;
}

export function useProfileSave() {
  const { resumeData } = useResumeStore();
  const { toast } = useToast();

  const saveProfile = async () => {
    const profileName = resumeData.personal_info?.full_name || 'Untitled Profile';
    
    try {
      const response = await api.saveProfile(profileName, resumeData);
      
      if (response.success) {
        const isUpdate = response.profile?.updated_at !== response.profile?.created_at;
        toast({
          title: isUpdate ? 'Profile updated' : 'Profile saved',
          description: isUpdate 
            ? `"${profileName}" has been updated.`
            : `"${profileName}" has been saved.`,
          variant: 'success',
        });
      } else {
        throw new Error(response.message || 'Failed to save profile');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      toast({
        title: 'Error saving profile',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    }
  };

  return { saveProfile };
}
