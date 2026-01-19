import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useResumeStore } from '@/stores/resumeStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
import type { EducationEntry } from '@/lib/types';
import { GraduationCap, RotateCcw, Trash2, Plus, Pencil, Save } from 'lucide-react';

export function EducationForm() {
  const { resumeData, addEducation, removeEducation, clearEducation, updateEducation } = useResumeStore();
  const { toast } = useToast();
  const { saveProfile } = useProfileSave();
  const { register, handleSubmit, reset } = useForm<EducationEntry>({
    defaultValues: {
      institution: '',
      degree: '',
      field_of_study: '',
      gpa: '',
      start_date: '',
      end_date: '',
      description: '',
    },
  });
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showClearDialog, setShowClearDialog] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (selectedIndex !== null && resumeData.education?.[selectedIndex]) {
      const education = resumeData.education[selectedIndex];
      reset({
        institution: education.institution || '',
        degree: education.degree || '',
        field_of_study: education.field_of_study || '',
        gpa: education.gpa || '',
        start_date: education.start_date || '',
        end_date: education.end_date || '',
        description: education.description || '',
      });
    }
  }, [selectedIndex, resumeData.education, reset]);

  const onSubmit = (data: EducationEntry) => {
    if (selectedIndex !== null) {
      // Update existing entry
      updateEducation(selectedIndex, data);
      toast({
        title: 'Education updated',
        description: `${data.degree} from ${data.institution} has been updated.`,
      });
      setSelectedIndex(null);
    } else {
      // Add new entry
      addEducation(data);
      toast({
        title: 'Education added',
        description: `${data.degree} from ${data.institution} has been added to your resume.`,
      });
    }
    reset();
  };

  const handleRemove = (index: number) => {
    const education = resumeData.education?.[index];
    removeEducation(index);
    if (selectedIndex === index) setSelectedIndex(null);
    toast({
      title: 'Education removed',
      description: education ? `${education.degree} from ${education.institution} has been removed.` : 'Education entry removed.',
      variant: 'destructive',
    });
  };

  const handleClearAll = () => {
    const count = resumeData.education?.length || 0;
    clearEducation();
    toast({
      title: 'All education cleared',
      description: `${count} education ${count === 1 ? 'entry' : 'entries'} removed.`,
      variant: 'destructive',
    });
  };

  const handleEdit = (index: number) => {
    setSelectedIndex(index);
    // Scroll to form if needed
    const formElement = document.getElementById('education-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleClear = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    clearEducation();
    reset();
    setSelectedIndex(null);
    setShowClearDialog(false);
    toast({
      title: 'Education cleared',
      description: 'All education entries have been cleared.',
      variant: 'destructive',
    });
  };


  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Education</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="education-form"
                  className="bg-primary"
                  size="icon"
                >
                  <Plus className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Add to History</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="education-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Row 1: Institution (2/3) + Degree (1/3) */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 space-y-2">
              <Label htmlFor="institution" className="text-xs font-semibold text-muted-foreground">
                Institution *
              </Label>
              <Input
                id="institution"
                className="text-sm"
                {...register('institution', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="degree" className="text-xs font-semibold text-muted-foreground">
                Degree *
              </Label>
              <Input
                id="degree"
                className="text-sm"
                {...register('degree', { required: true })}
              />
            </div>
          </div>

          {/* Row 2: Field (2), GPA (0.5), Start Date (1.5), End Date (1.5) */}
          <div className="grid grid-cols-4 gap-4">
            <div className="col-span-2 space-y-2">
              <Label htmlFor="field_of_study" className="text-xs font-semibold text-muted-foreground">
                Field of Study
              </Label>
              <Input
                id="field_of_study"
                className="text-sm"
                {...register('field_of_study')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gpa" className="text-xs font-semibold text-muted-foreground">
                GPA
              </Label>
              <Input
                id="gpa"
                className="text-sm"
                {...register('gpa')}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-2">
                <Label htmlFor="start_date" className="text-xs font-semibold text-muted-foreground">
                  Start
                </Label>
                <Input
                  id="start_date"
                  className="text-sm"
                  {...register('start_date')}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date" className="text-xs font-semibold text-muted-foreground">
                  End
                </Label>
                <Input
                  id="end_date"
                  className="text-sm"
                  {...register('end_date')}
                />
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

        {/* Education History */}
        <div className="space-y-4">
          <Label className="text-base font-semibold">Education History</Label>
          {!resumeData.education || resumeData.education.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
              <GraduationCap className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
              <p className="text-muted-foreground text-sm">No education history added yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {resumeData.education.map((edu, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                  >
                    <div className="flex-1 grid grid-cols-6 gap-4 items-center">
                      <div className="col-span-2">
                        <p className="text-sm font-medium">{edu.institution}</p>
                        <p className="text-xs text-muted-foreground">{edu.degree}</p>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {edu.field_of_study || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {edu.gpa || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {edu.start_date && edu.end_date ? `${edu.start_date} - ${edu.end_date}` : edu.start_date || edu.end_date || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground truncate max-w-xs">
                        {edu.description || '—'}
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
                            <p>Edit education</p>
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
                            <p>Delete education</p>
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
            <DialogTitle>Clear Education</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all education entries? This action cannot be undone.
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
              Clear Education
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

