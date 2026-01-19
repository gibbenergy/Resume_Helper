import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useResumeStore } from '@/stores/resumeStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/components/ui/use-toast';
import { useProfileSave } from '@/lib/useProfileSave';
import type { SkillEntry } from '@/lib/types';
import { Code, RotateCcw, Trash2, Plus, Pencil, Save } from 'lucide-react';

export function SkillsForm() {
  const { resumeData, addSkill, removeSkill, clearSkills, updateSkill } = useResumeStore();
  const { toast } = useToast();
  const { saveProfile } = useProfileSave();
  const { register, handleSubmit, reset } = useForm<SkillEntry>({
    defaultValues: {
      category: '',
      name: '',
      proficiency: '',
    },
  });
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showClearDialog, setShowClearDialog] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (selectedIndex !== null && resumeData.skills?.[selectedIndex]) {
      const skill = resumeData.skills[selectedIndex];
      reset({
        category: skill.category || '',
        name: skill.name || '',
        proficiency: skill.proficiency || '',
      });
    }
  }, [selectedIndex, resumeData.skills, reset]);

  const onSubmit = (data: SkillEntry) => {
    if (selectedIndex !== null) {
      // Update existing entry
      updateSkill(selectedIndex, data);
      toast({
        title: 'Skill updated',
        description: `${data.name} has been updated.`,
      });
      setSelectedIndex(null);
    } else {
      // Add new entry
      addSkill(data);
      toast({
        title: 'Skill added',
        description: `${data.name} has been added to your resume.`,
      });
    }
    reset();
  };

  const handleRemove = (index: number) => {
    const skill = resumeData.skills?.[index];
    removeSkill(index);
    if (selectedIndex === index) setSelectedIndex(null);
    toast({
      title: 'Skill removed',
      description: skill ? `${skill.name} has been removed.` : 'Skill entry removed.',
      variant: 'destructive',
    });
  };

  const handleClearAll = () => {
    const count = resumeData.skills?.length || 0;
    clearSkills();
    toast({
      title: 'All skills cleared',
      description: `${count} skill ${count === 1 ? 'entry' : 'entries'} removed.`,
      variant: 'destructive',
    });
  };

  const handleEdit = (index: number) => {
    setSelectedIndex(index);
    const formElement = document.getElementById('skills-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleClear = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    clearSkills();
    reset();
    setSelectedIndex(null);
    setShowClearDialog(false);
    toast({
      title: 'Skills cleared',
      description: 'All skill entries have been cleared.',
      variant: 'destructive',
    });
  };


  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Code className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Skills</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="skills-form"
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
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="skills-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category" className="text-xs font-semibold text-muted-foreground">
                Category *
              </Label>
              <Input
                id="category"
                className="text-sm"
                {...register('category', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name" className="text-xs font-semibold text-muted-foreground">
                Skill Name *
              </Label>
              <Input
                id="name"
                className="text-sm"
                {...register('name', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="proficiency" className="text-xs font-semibold text-muted-foreground">
                Proficiency
              </Label>
              <Input id="proficiency" className="text-sm" {...register('proficiency')} />
            </div>
          </div>

          {/* Save & Clear Buttons - Centered */}
          <div className="flex justify-center gap-2 pt-4">
            <Button 
              type="button"
              onClick={saveProfile}
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

        {/* Skills List */}
        <div className="space-y-4">
          <Label className="text-base font-semibold">Skills List</Label>
          {!resumeData.skills || resumeData.skills.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
              <Code className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
              <p className="text-muted-foreground text-sm">No skills added yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {resumeData.skills.map((skill, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                  >
                    <div className="flex-1 grid grid-cols-3 gap-4 items-center">
                      <div className="text-sm font-medium">{skill.category}</div>
                      <div className="text-sm text-muted-foreground">{skill.name}</div>
                      <div className="text-sm text-muted-foreground">{skill.proficiency || '—'}</div>
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
                            <p>Edit skill</p>
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
                            <p>Delete skill</p>
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

      <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Skills</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all skill entries? This action cannot be undone.
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
              Clear Skills
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

