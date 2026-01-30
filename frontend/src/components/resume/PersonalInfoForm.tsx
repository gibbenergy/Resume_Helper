import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useResumeStore } from '@/stores/resumeStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useToast } from '@/components/ui/use-toast';
import { api } from '@/lib/api';
import { UserCircle, Save, RotateCcw, FileCode, Briefcase, X } from 'lucide-react';
import { SaveProfileDialog } from './SaveProfileDialog';

interface SavedProfile {
  id: string;
  name: string;
  timestamp: number;
  data: any;
}

export function PersonalInfoForm() {
  const { resumeData, updatePersonalInfo, setResumeData, resetResume, setActiveProfileName } = useResumeStore();
  const { toast } = useToast();
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [savedProfiles, setSavedProfiles] = useState<SavedProfile[]>([]);
  const { register, handleSubmit, setValue, watch, reset } = useForm({
    defaultValues: resumeData.personal_info,
  });

  // Load saved profiles from database on mount
  useEffect(() => {
    const loadProfiles = async () => {
      try {
        const response = await api.getProfiles();
        if (response.success && Array.isArray(response.profiles)) {
          setSavedProfiles(response.profiles);
        }
      } catch (e) {
        console.error('Error loading saved profiles:', e);
        setSavedProfiles([]);
      }
    };
    loadProfiles();
  }, []);

  // Sync form with store when personal_info changes (e.g., after reset or loading profile)
  // Use useRef to prevent infinite loops and expensive JSON.stringify calls
  const prevPersonalInfoRef = useRef<string>('');
  const isInitialMount = useRef(true);
  const isExternalUpdate = useRef(false);

  useEffect(() => {
    // Skip on initial mount to avoid unnecessary reset
    if (isInitialMount.current) {
      isInitialMount.current = false;
      const personalInfo = resumeData.personal_info || {};
      reset(personalInfo);
      if (!personalInfo.name_prefix) {
        setValue('name_prefix', 'none');
      }
      prevPersonalInfoRef.current = JSON.stringify(personalInfo);
      return;
    }

    const personalInfoStr = JSON.stringify(resumeData.personal_info || {});
    // Only reset if personal_info actually changed from external source
    if (prevPersonalInfoRef.current !== personalInfoStr) {
      prevPersonalInfoRef.current = personalInfoStr;
      isExternalUpdate.current = true;
      const personalInfo = resumeData.personal_info || {};
      reset(personalInfo);

      // Handle name_prefix conversion for the select
      if (!personalInfo.name_prefix) {
        setValue('name_prefix', 'none');
      }
      isExternalUpdate.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeData.personal_info]);

  // Auto-sync form changes to the store (so changes persist when switching tabs)
  const formValues = watch();
  const prevFormValuesRef = useRef<string>('');

  useEffect(() => {
    // Skip if this is an external update (from loading profile, reset, etc.)
    if (isExternalUpdate.current) return;

    const formValuesStr = JSON.stringify(formValues);
    // Only update store if form values actually changed
    if (prevFormValuesRef.current && prevFormValuesRef.current !== formValuesStr) {
      // Convert 'none' back to empty string for storage
      const dataToStore = { ...formValues };
      if (dataToStore.name_prefix === 'none') {
        dataToStore.name_prefix = '';
      }
      updatePersonalInfo(dataToStore);
      prevPersonalInfoRef.current = JSON.stringify(dataToStore);
    }
    prevFormValuesRef.current = formValuesStr;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formValues]);

  const onSubmit = async (data: any) => {
    // Update the store with current form data
    updatePersonalInfo(data);
    // Open the save dialog to let user choose/customize profile name
    setShowSaveDialog(true);
  };

  const handleSaveProfile = async (profileName: string) => {
    const updatedResumeData = {
      ...resumeData,
      personal_info: resumeData.personal_info,
    };

    try {
      // Check if profile with same name exists (case-insensitive)
      const existingProfile = savedProfiles.find(
        (p) => p.name.toLowerCase() === profileName.toLowerCase()
      );

      const response = await api.saveProfile(
        profileName,
        updatedResumeData,
        existingProfile?.id
      );

      if (response.success) {
        // Set the active profile name so other tabs can save to the same profile
        setActiveProfileName(profileName);

        // Refresh profiles from database
        const profilesResponse = await api.getProfiles();
        if (profilesResponse.success) {
          setSavedProfiles(profilesResponse.profiles);
        }

        toast({
          title: existingProfile ? 'Profile updated' : 'Profile saved',
          description: existingProfile
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

  const loadSavedProfile = (profile: SavedProfile) => {
    setResumeData(profile.data);

    // Set the active profile name so other tabs can save to the same profile
    setActiveProfileName(profile.name);

    // Update form values using reset to properly sync form state
    const personalInfo = profile.data.personal_info || {};
    const formData: any = {};
    Object.keys(personalInfo).forEach((key) => {
      const value = (personalInfo as any)[key];
      if (key === 'name_prefix' && !value) {
        formData[key] = 'none';
      } else {
        formData[key] = value || '';
      }
    });
    reset(formData);

    toast({
      title: 'Profile loaded',
      description: `"${profile.name}" has been loaded successfully.`,
      variant: 'success',
    });
  };

  const deleteSavedProfile = async (profileId: string) => {
    try {
      const response = await api.deleteProfile(profileId);
      
      if (response.success) {
        // Refresh profiles from database
        const profilesResponse = await api.getProfiles();
        if (profilesResponse.success) {
          setSavedProfiles(profilesResponse.profiles);
        }
        
        toast({
          title: 'Profile deleted',
          description: 'The saved profile has been removed.',
          variant: 'destructive',
        });
      } else {
        throw new Error(response.message || 'Failed to delete profile');
      }
    } catch (error) {
      console.error('Error deleting profile:', error);
      toast({
        title: 'Error deleting profile',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    }
  };

  const handleClear = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    // Reset all resume data (all sections) - this will trigger useEffect to sync form
    resetResume();
    
    // Also explicitly reset the form to ensure it's cleared immediately
    const emptyData = {
      name_prefix: 'none',
      email: '',
      full_name: '',
      phone: '',
      current_address: '',
      location: '',
      citizenship: '',
      linkedin_url: '',
      github_url: '',
      portfolio_url: '',
      summary: '',
    };
    reset(emptyData);
    
    // Update the ref to prevent useEffect from re-triggering
    prevPersonalInfoRef.current = JSON.stringify(emptyData);
    
    setShowClearDialog(false);
    toast({
      title: 'Resume data cleared',
      description: 'All resume data has been cleared successfully.',
      variant: 'destructive',
    });
  };

  const loadExample = async (type: 'software' | 'process') => {
    try {
      const response =
        type === 'software'
          ? await api.loadSoftwareDeveloperExample()
          : await api.loadProcessEngineerExample();
      
      if (response.success && response.data) {
        // The backend returns a flat array, not a structured object
        // Array structure: [name_prefix, email, full_name, phone, current_address, location, 
        // citizenship, linkedin_url, github_url, portfolio_url, summary, status_msg,
        // empty strings..., education_table, empty strings..., work_table, empty strings...,
        // skills_table, empty strings..., projects_table, empty strings..., certs_table, others]
        const flatArray = response.data;
        
        if (!Array.isArray(flatArray)) {
          toast({
            title: 'Error loading example',
            description: 'Invalid data format received from server.',
            variant: 'destructive',
          });
          return;
        }
        
        // Extract personal info (indices 0-10)
        const personalInfo = {
          name_prefix: flatArray[0] || '',
          email: flatArray[1] || '',
          full_name: flatArray[2] || '',
          phone: flatArray[3] || '',
          current_address: flatArray[4] || '',
          location: flatArray[5] || '',
          citizenship: flatArray[6] || '',
          linkedin_url: flatArray[7] || '',
          github_url: flatArray[8] || '',
          portfolio_url: flatArray[9] || '',
          summary: flatArray[10] || '',
        };
        
        // Extract tables (indices from backend code analysis)
        // education_table is at index 19
        // work_table is at index 27
        // skills_table is at index 31
        // projects_table is at index 38
        // certs_table is at index 44
        // others is at index 45
        
        const educationTable = Array.isArray(flatArray[19]) ? flatArray[19] : [];
        const workTable = Array.isArray(flatArray[27]) ? flatArray[27] : [];
        const skillsTable = Array.isArray(flatArray[31]) ? flatArray[31] : [];
        const projectsTable = Array.isArray(flatArray[38]) ? flatArray[38] : [];
        const certsTable = Array.isArray(flatArray[44]) ? flatArray[44] : [];
        const others = flatArray[45] || {};
        
        // Convert table arrays to structured objects
        const education = educationTable.map((row: any[]) => ({
          institution: row[0] || '',
          degree: row[1] || '',
          field_of_study: row[2] || '',
          gpa: row[3] || '',
          start_date: row[4] || '',
          end_date: row[5] || '',
          description: row[6] || '',
        })).filter((edu: any) => edu.institution || edu.degree);
        
        const experience = workTable.map((row: any[]) => {
          const achievementsText = row[6] || '';
          let achievements: string[] = [];
          if (achievementsText.trim()) {
            if (achievementsText.includes('-')) {
              achievements = achievementsText.split('\n')
                .map((line: string) => line.trim())
                .filter((line: string) => line)
                .map((line: string) => line.replace(/^-\s*/, ''));
            } else {
              achievements = [achievementsText];
            }
          }
          return {
            company: row[0] || '',
            position: row[1] || '',
            location: row[2] || '',
            start_date: row[3] || '',
            end_date: row[4] || '',
            description: row[5] || '',
            achievements,
          };
        }).filter((exp: any) => exp.company || exp.position);
        
        const skills = skillsTable.map((row: any[]) => ({
          category: row[0] || '',
          name: row[1] || '',
          proficiency: row[2] || '',
        })).filter((skill: any) => skill.name);
        
        const projects = projectsTable.map((row: any[]) => ({
          name: row[0] || '',
          description: row[1] || '',
          technologies: row[2] || '',
          url: row[3] || '',
          start_date: row[4] || '',
          end_date: row[5] || '',
        })).filter((proj: any) => proj.name);
        
        const certifications = certsTable.map((row: any[]) => ({
          name: row[0] || '',
          issuer: row[1] || '',
          date_obtained: row[2] || '',
          credential_id: row[3] || '',
          url: row[4] || '',
        })).filter((cert: any) => cert.name);
        
        // Build the structured resume data
        const normalizedData = {
          personal_info: personalInfo,
          education,
          experience,
          skills,
          projects,
          certifications,
          others: others || {},
        };
        
        // Set the entire resume data (all sections)
        setResumeData(normalizedData);
        
        // Also update the form values for personal info
        Object.keys(personalInfo).forEach((key) => {
          const value = (personalInfo as any)[key];
          // Handle name_prefix conversion (empty string to 'none')
          if (key === 'name_prefix' && !value) {
            setValue('name_prefix', 'none');
          } else {
            setValue(key as any, value || '');
          }
        });
        
        toast({
          title: 'Example loaded',
          description: `The ${type === 'software' ? 'Software Developer' : 'Process Engineer'} example has been loaded successfully.`,
          variant: 'success',
        });
      } else {
        toast({
          title: 'Error loading example',
          description: 'Response was not successful or missing data.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error loading example',
        description: 'Failed to load example data from server.',
        variant: 'destructive',
      });
    }
  };

  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <UserCircle className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Personal Information</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="personal-info-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name_prefix" className="text-xs font-semibold text-muted-foreground">
                Name Prefix (Optional)
              </Label>
              <Select
                value={watch('name_prefix') || 'none'}
                onValueChange={(value) => setValue('name_prefix', value)}
              >
                <SelectTrigger className="text-sm">
                  <SelectValue placeholder="Select prefix" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="Dr.">Dr.</SelectItem>
                  <SelectItem value="Prof.">Prof.</SelectItem>
                  <SelectItem value="Mr.">Mr.</SelectItem>
                  <SelectItem value="Mrs.">Mrs.</SelectItem>
                  <SelectItem value="Ms.">Ms.</SelectItem>
                  <SelectItem value="Mx.">Mx.</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="full_name" className="text-xs font-semibold text-muted-foreground">
                Full Name *
              </Label>
              <Input
                id="full_name"
                className="text-sm"
                {...register('full_name', { required: true })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-xs font-semibold text-muted-foreground">
                Email
              </Label>
              <Input id="email" type="email" className="text-sm" {...register('email')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone" className="text-xs font-semibold text-muted-foreground">
                Phone
              </Label>
              <Input id="phone" type="tel" className="text-sm" {...register('phone')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="current_address" className="text-xs font-semibold text-muted-foreground">
                Current Address
              </Label>
              <Input id="current_address" className="text-sm" {...register('current_address')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="location" className="text-xs font-semibold text-muted-foreground">
                Location
              </Label>
              <Input id="location" className="text-sm" {...register('location')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="citizenship" className="text-xs font-semibold text-muted-foreground">
                Citizenship
              </Label>
              <Input id="citizenship" className="text-sm" {...register('citizenship')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="linkedin_url" className="text-xs font-semibold text-muted-foreground">
                LinkedIn URL
              </Label>
              <Input id="linkedin_url" type="text" className="text-sm" {...register('linkedin_url')} placeholder="linkedin.com/in/username" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="github_url" className="text-xs font-semibold text-muted-foreground">
                GitHub URL
              </Label>
              <Input id="github_url" type="text" className="text-sm" {...register('github_url')} placeholder="github.com/username" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="portfolio_url" className="text-xs font-semibold text-muted-foreground">
                Portfolio URL
              </Label>
              <Input id="portfolio_url" type="text" className="text-sm" {...register('portfolio_url')} placeholder="yourwebsite.com" />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="summary" className="text-xs font-semibold text-muted-foreground">
              Professional Summary
            </Label>
            <Textarea
              id="summary"
              rows={4}
              className="text-sm"
              {...register('summary')}
              placeholder="Write a brief professional summary..."
            />
          </div>

          {/* Action Buttons - Centered */}
          <div className="flex justify-center gap-2 pt-4">
            <Button 
              type="submit"
            >
              <Save className="mr-2 h-4 w-4" />
              Save
            </Button>
            <Button 
              type="button" 
              variant="destructive"
              onClick={handleClear}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Clear
            </Button>
          </div>
        </form>

        {/* Assets Section */}
        <div className="space-y-4 pt-4 border-t border-border/50">
          <Label className="text-base font-semibold">Assets</Label>
          
          {/* Example Templates */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold text-muted-foreground">Templates</Label>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="secondary"
                onClick={() => loadExample('software')}
              >
                <FileCode className="mr-2 h-4 w-4" />
                Software Engineer Example
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => loadExample('process')}
              >
                <Briefcase className="mr-2 h-4 w-4" />
                Process Engineer Example
              </Button>
            </div>
          </div>

          {/* Saved Profiles */}
          {savedProfiles.length > 0 && (
            <div className="space-y-2">
              <Label className="text-xs font-semibold text-muted-foreground">Saved Profiles</Label>
              <div className="flex flex-wrap gap-2">
                {savedProfiles.map((profile) => (
                  <div key={profile.id} className="flex items-center gap-1">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => loadSavedProfile(profile)}
                    >
                      <UserCircle className="mr-2 h-4 w-4" />
                      {profile.name}
                    </Button>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => deleteSavedProfile(profile.id)}
                            className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Delete saved profile</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>

      <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear All Resume Data</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear ALL resume data? This will clear Personal Info, Education, Experience, Skills, Projects, Certifications, and Others. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowClearDialog(false)}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={confirmClear}
            >
              Clear All
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <SaveProfileDialog
        open={showSaveDialog}
        onOpenChange={setShowSaveDialog}
        defaultName={resumeData.personal_info?.full_name || 'Untitled Profile'}
        existingProfiles={savedProfiles}
        onSave={handleSaveProfile}
      />
    </Card>
  );
}

 
