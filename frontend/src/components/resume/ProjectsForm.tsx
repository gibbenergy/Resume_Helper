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
import type { ProjectEntry } from '@/lib/types';
import { FolderKanban, RotateCcw, Trash2, Plus, Pencil, Save } from 'lucide-react';

export function ProjectsForm() {
  const { resumeData, addProject, removeProject, clearProjects, updateProject } = useResumeStore();
  const { toast } = useToast();
  const { saveProfile } = useProfileSave();
  const { register, handleSubmit, reset } = useForm<ProjectEntry>({
    defaultValues: {
      name: '',
      description: '',
      technologies: '',
      url: '',
      start_date: '',
      end_date: '',
    },
  });
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showClearDialog, setShowClearDialog] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (selectedIndex !== null && resumeData.projects?.[selectedIndex]) {
      const project = resumeData.projects[selectedIndex];
      reset({
        name: project.name || '',
        description: project.description || '',
        technologies: project.technologies || '',
        url: project.url || '',
        start_date: project.start_date || '',
        end_date: project.end_date || '',
      });
    }
  }, [selectedIndex, resumeData.projects, reset]);

  const onSubmit = (data: ProjectEntry) => {
    if (selectedIndex !== null) {
      // Update existing entry
      updateProject(selectedIndex, data);
      toast({
        title: 'Project updated',
        description: `${data.name} has been updated.`,
      });
      setSelectedIndex(null);
    } else {
      // Add new entry
      addProject(data);
      toast({
        title: 'Project added',
        description: `${data.name} has been added to your resume.`,
      });
    }
    reset();
  };

  const handleRemove = (index: number) => {
    const project = resumeData.projects?.[index];
    removeProject(index);
    if (selectedIndex === index) setSelectedIndex(null);
    toast({
      title: 'Project removed',
      description: project ? `${project.name} has been removed.` : 'Project entry removed.',
      variant: 'destructive',
    });
  };

  const handleClearAll = () => {
    const count = resumeData.projects?.length || 0;
    clearProjects();
    toast({
      title: 'All projects cleared',
      description: `${count} project ${count === 1 ? 'entry' : 'entries'} removed.`,
      variant: 'destructive',
    });
  };

  const handleEdit = (index: number) => {
    setSelectedIndex(index);
    const formElement = document.getElementById('projects-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleClear = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    clearProjects();
    reset();
    setSelectedIndex(null);
    setShowClearDialog(false);
    toast({
      title: 'Projects cleared',
      description: 'All project entries have been cleared.',
      variant: 'destructive',
    });
  };


  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <FolderKanban className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Projects</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="projects-form"
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
        <form id="projects-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-xs font-semibold text-muted-foreground">
                Project Title *
              </Label>
              <Input
                id="name"
                className="text-sm"
                {...register('name', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="url" className="text-xs font-semibold text-muted-foreground">
                URL
              </Label>
              <Input id="url" type="url" className="text-sm" {...register('url')} />
            </div>
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
          <div className="space-y-2">
            <Label htmlFor="description" className="text-xs font-semibold text-muted-foreground">
              Description *
            </Label>
            <Textarea
              id="description"
              rows={3}
              className="text-sm"
              {...register('description', { required: true })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="technologies" className="text-xs font-semibold text-muted-foreground">
              Technologies
            </Label>
            <Input id="technologies" className="text-sm" {...register('technologies')} />
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

        {/* Projects List */}
        <div className="space-y-4">
          <Label className="text-base font-semibold">Projects List</Label>
          {!resumeData.projects || resumeData.projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
              <FolderKanban className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
              <p className="text-muted-foreground text-sm">No projects added yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {resumeData.projects.map((project, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                  >
                    <div className="flex-1 grid grid-cols-6 gap-4 items-center">
                      <div className="col-span-2">
                        <p className="text-sm font-medium">{project.name}</p>
                        {project.url && (
                          <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline">
                            View Project
                          </a>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground truncate max-w-xs">
                        {project.description || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {project.technologies || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {project.start_date && project.end_date ? `${project.start_date} - ${project.end_date}` : project.start_date || project.end_date || '—'}
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
                            <p>Edit project</p>
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
                            <p>Delete project</p>
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
            <DialogTitle>Clear Projects</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all project entries? This action cannot be undone.
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
              Clear Projects
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

 
