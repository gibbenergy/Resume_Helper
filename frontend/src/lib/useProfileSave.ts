import { useToast } from '@/components/ui/use-toast';
import { useResumeStore } from '@/stores/resumeStore';

const STORAGE_KEY = 'resumeHelper_savedProfiles';

export interface SavedProfile {
  id: string;
  name: string;
  timestamp: number;
  data: any;
}

export function useProfileSave() {
  const { resumeData } = useResumeStore();
  const { toast } = useToast();

  const saveProfile = () => {
    const profileName = resumeData.personal_info?.full_name || 'Untitled Profile';
    
    // Load existing profiles
    const saved = localStorage.getItem(STORAGE_KEY);
    let profiles: SavedProfile[] = [];
    try {
      profiles = saved ? JSON.parse(saved) : [];
    } catch (e) {
      profiles = [];
    }
    
    // Check if profile with same name exists
    const existingIndex = profiles.findIndex((p) => p.name === profileName);
    
    if (existingIndex >= 0) {
      // Update existing profile
      profiles[existingIndex] = {
        ...profiles[existingIndex],
        timestamp: Date.now(),
        data: resumeData,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
      toast({
        title: 'Profile updated',
        description: `"${profileName}" has been updated.`,
        variant: 'success',
      });
    } else {
      // Create new profile
      const profileId = `profile_${Date.now()}`;
      const savedProfile: SavedProfile = {
        id: profileId,
        name: profileName,
        timestamp: Date.now(),
        data: resumeData,
      };
      const updatedProfiles = [...profiles, savedProfile];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedProfiles));
      toast({
        title: 'Profile saved',
        description: `"${profileName}" has been saved to your assets.`,
        variant: 'success',
      });
    }
  };

  return { saveProfile };
}
