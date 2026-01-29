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
import type { CertificationEntry } from '@/lib/types';
import { Award, RotateCcw, Trash2, Plus, Pencil, Save, ChevronUp, ChevronDown } from 'lucide-react';

export function CertificationsForm() {
  const { resumeData, addCertification, removeCertification, clearCertifications, updateCertification, moveCertificationUp, moveCertificationDown } = useResumeStore();
  const { toast } = useToast();
  const { saveProfile } = useProfileSave();
  const { register, handleSubmit, reset } = useForm<CertificationEntry>({
    defaultValues: {
      name: '',
      issuer: '',
      date_obtained: '',
      credential_id: '',
      url: '',
    },
  });
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showClearDialog, setShowClearDialog] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (selectedIndex !== null && resumeData.certifications?.[selectedIndex]) {
      const cert = resumeData.certifications[selectedIndex];
      reset({
        name: cert.name || '',
        issuer: cert.issuer || '',
        date_obtained: cert.date_obtained || '',
        credential_id: cert.credential_id || '',
        url: cert.url || '',
      });
    }
  }, [selectedIndex, resumeData.certifications, reset]);

  const onSubmit = (data: CertificationEntry) => {
    if (selectedIndex !== null) {
      // Update existing entry
      updateCertification(selectedIndex, data);
      toast({
        title: 'Certification updated',
        description: `${data.name} has been updated.`,
      });
      setSelectedIndex(null);
    } else {
      // Add new entry
      addCertification(data);
      toast({
        title: 'Certification added',
        description: `${data.name} has been added to your resume.`,
      });
    }
    reset();
  };

  const handleRemove = (index: number) => {
    const cert = resumeData.certifications?.[index];
    removeCertification(index);
    if (selectedIndex === index) setSelectedIndex(null);
    toast({
      title: 'Certification removed',
      description: cert ? `${cert.name} has been removed.` : 'Certification entry removed.',
      variant: 'destructive',
    });
  };

  const handleClearAll = () => {
    const count = resumeData.certifications?.length || 0;
    clearCertifications();
    toast({
      title: 'All certifications cleared',
      description: `${count} certification ${count === 1 ? 'entry' : 'entries'} removed.`,
      variant: 'destructive',
    });
  };

  const handleEdit = (index: number) => {
    setSelectedIndex(index);
    const formElement = document.getElementById('certifications-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleClear = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    clearCertifications();
    reset();
    setSelectedIndex(null);
    setShowClearDialog(false);
    toast({
      title: 'Certifications cleared',
      description: 'All certification entries have been cleared.',
      variant: 'destructive',
    });
  };


  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Award className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Certifications</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="certifications-form"
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
        <form id="certifications-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-xs font-semibold text-muted-foreground">
                Certification Name *
              </Label>
              <Input
                id="name"
                className="text-sm"
                {...register('name', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="issuer" className="text-xs font-semibold text-muted-foreground">
                Issuer *
              </Label>
              <Input
                id="issuer"
                className="text-sm"
                {...register('issuer', { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date_obtained" className="text-xs font-semibold text-muted-foreground">
                Date Obtained
              </Label>
              <Input id="date_obtained" className="text-sm" {...register('date_obtained')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="credential_id" className="text-xs font-semibold text-muted-foreground">
                Credential ID
              </Label>
              <Input id="credential_id" className="text-sm" {...register('credential_id')} />
            </div>
            <div className="space-y-2 col-span-2">
              <Label htmlFor="url" className="text-xs font-semibold text-muted-foreground">
                URL
              </Label>
              <Input id="url" type="url" className="text-sm" {...register('url')} />
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

        {/* Certifications List */}
        <div className="space-y-4">
          <Label className="text-base font-semibold">Certifications List</Label>
          {!resumeData.certifications || resumeData.certifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
              <Award className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
              <p className="text-muted-foreground text-sm">No certifications added yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {resumeData.certifications.map((cert, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                  >
                    <div className="flex-1 grid grid-cols-5 gap-4 items-center">
                      <div className="col-span-2">
                        <p className="text-sm font-medium">{cert.name}</p>
                        <p className="text-xs text-muted-foreground">{cert.issuer}</p>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {cert.date_obtained || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {cert.credential_id || '—'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {cert.url ? (
                          <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                            View
                          </a>
                        ) : '—'}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 ml-4">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => moveCertificationUp(index)}
                              disabled={index === 0}
                            >
                              <ChevronUp className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Move up</p>
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
                              className="h-8 w-8"
                              onClick={() => moveCertificationDown(index)}
                              disabled={index === (resumeData.certifications?.length || 0) - 1}
                            >
                              <ChevronDown className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Move down</p>
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
                              className="h-8 w-8"
                              onClick={() => handleEdit(index)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Edit certification</p>
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
                            <p>Delete certification</p>
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
            <DialogTitle>Clear Certifications</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all certification entries? This action cannot be undone.
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
              Clear Certifications
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

 
