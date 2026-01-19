import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useResumeStore } from '@/stores/resumeStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useToast } from '@/components/ui/use-toast';
import type { ExperienceEntry } from '@/lib/types';
import { Briefcase, RotateCcw, Trash2, Plus, Pencil } from 'lucide-react';

export function ExperienceForm() {
  const { resumeData, addExperience, removeExperience, clearExperience, updateExperience } = useResumeStore();
  const { toast } = useToast();
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ExperienceEntry>({
    defaultValues: {
      company: '',
      position: '',
      location: '',
      start_date: '',
      end_date: '',
      description: '',
      achievements: [],
    },
  });
  const [achievementsText, setAchievementsText] = useState('');
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  // Populate form when editing
  useEffect(() => {
    if (selectedIndex !== null && resumeData.experience?.[selectedIndex]) {
      const experience = resumeData.experience[selectedIndex];
      reset({
        company: experience.company || '',
        position: experience.position || '',
        location: experience.location || '',
        start_date: experience.start_date || '',
        end_date: experience.end_date || '',
        description: experience.description || '',
        achievements: [],
      });
      setAchievementsText(
        experience.achievements?.map(a => `- ${a}`).join('\n') || ''
      );
    }
  }, [selectedIndex, resumeData.experience, reset]);

  const onSubmit = (data: ExperienceEntry) => {
    const achievements = achievementsText
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && (line.startsWith('- ') || line.startsWith('-')))
      .map(line => line.replace(/^-\s*/, ''));
    
    const experienceData = {
      ...data,
      achievements,
    };

    if (selectedIndex !== null) {
      // Update existing entry
      updateExperience(selectedIndex, experienceData);
      toast({
        title: 'Experience updated',
        description: `${data.position} at ${data.company} has been updated.`,
      });
      setSelectedIndex(null);
    } else {
      // Add new entry
      addExperience(experienceData);
      toast({
        title: 'Experience added',
        description: `${data.position} at ${data.company} has been added to your resume.`,
      });
    }
    reset();
    setAchievementsText('');
  };

  const handleRemove = (index: number) => {
    const experience = resumeData.experience?.[index];
    removeExperience(index);
    if (selectedIndex === index) setSelectedIndex(null);
    toast({
      title: 'Experience removed',
      description: experience ? `${experience.position} at ${experience.company} has been removed.` : 'Experience entry removed.',
      variant: 'destructive',
    });
  };

  const handleClearAll = () => {
    const count = resumeData.experience?.length || 0;
    clearExperience();
    toast({
      title: 'All experience cleared',
      description: `${count} experience ${count === 1 ? 'entry' : 'entries'} removed.`,
      variant: 'destructive',
    });
  };

  const handleResetForm = () => {
    reset();
    setAchievementsText('');
    setSelectedIndex(null);
    toast({
      title: 'Form reset',
      description: 'All form fields have been cleared.',
    });
  };

  const handleEdit = (index: number) => {
    setSelectedIndex(index);
    const formElement = document.getElementById('experience-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };


  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Briefcase className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Work Experience</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="experience-form"
                  className="bg-primary"
                  size="icon"
                >
                  <Plus className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{selectedIndex !== null ? 'Update entry' : 'Add to History'}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={handleResetForm}
                  className="h-8 w-8"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Reset form</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="experience-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company" className="text-xs font-semibold text-muted-foreground">
                Company *
              </Label>
              <Input
                id="company"
                className="text-sm"
                {...register('company', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="position" className="text-xs font-semibold text-muted-foreground">
                Position *
              </Label>
              <Input
                id="position"
                className="text-sm"
                {...register('position', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="location" className="text-xs font-semibold text-muted-foreground">
                Location
              </Label>
              <Input id="location" className="text-sm" {...register('location')} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date" className="text-xs font-semibold text-muted-foreground">
                  Start Date
                </Label>
                <Input id="start_date" className="text-sm" {...register('start_date')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date" className="text-xs font-semibold text-muted-foreground">
                  End Date
                </Label>
                <Input id="end_date" className="text-sm" {...register('end_date')} />
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description" className="text-xs font-semibold text-muted-foreground">
              Description
            </Label>
            <Textarea
              id="description"
              rows={3}
              className="text-sm"
              {...register('description')}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="achievements" className="text-xs font-semibold text-muted-foreground">
              Achievements (one per line, start with -)
            </Label>
            <Textarea
              id="achievements"
              rows={3}
              className="text-sm"
              value={achievementsText}
              onChange={(e) => setAchievementsText(e.target.value)}
              placeholder="- Achievement 1&#10;- Achievement 2"
            />
          </div>
        </form>

        {/* Experience History */}
        <div className="space-y-4">
          <Label className="text-base font-semibold">Experience History</Label>
          {!resumeData.experience || resumeData.experience.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
              <Briefcase className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
              <p className="text-muted-foreground text-sm">No experience history added yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {resumeData.experience.map((exp, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                  >
                    <div className="flex-1 grid grid-cols-6 gap-4 items-center">
                      <div className="col-span-2">
                        <p className="text-sm font-medium">{exp.company}</p>
                        <p className="text-xs text-muted-foreground">{exp.position}</p>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {exp.location || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {exp.start_date && exp.end_date ? `${exp.start_date} - ${exp.end_date}` : exp.start_date || exp.end_date || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground truncate max-w-xs">
                        {exp.description || '—'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {exp.achievements?.length ? `${exp.achievements.length} achievement${exp.achievements.length > 1 ? 's' : ''}` : '—'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => handleEdit(index)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Edit experience</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
                              onClick={() => handleRemove(index)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Delete experience</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClearAll}
                >
                  Clear All
                </Button>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

