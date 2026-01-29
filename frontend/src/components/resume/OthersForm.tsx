import { useState, useEffect } from 'react';
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
import { Pagination } from '@/components/ui/pagination';
import { Layers, RotateCcw, Trash2, Plus, Pencil, Save, ChevronUp, ChevronDown } from 'lucide-react';

const COMMON_SECTIONS = [
  'Awards & Honors',
  'Publications',
  'Volunteer Work',
  'Professional Memberships',
  'Conferences & Events',
  'Languages',
  'Hobbies & Interests',
  'Additional Information',
  'References',
  'Patents',
  'Speaking Engagements',
  'Community Involvement',
];

interface OtherItem {
  title: string;
  organization: string;
  date: string;
  location: string;
  description: string;
  url: string;
}

export function OthersForm() {
  const { resumeData, updateOthers, moveOthersItemUp, moveOthersItemDown } = useResumeStore();
  const { toast } = useToast();
  const { saveProfile } = useProfileSave();
  const [selectedSection, setSelectedSection] = useState<string>(COMMON_SECTIONS[0]);
  const [customSectionName, setCustomSectionName] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [editingItem, setEditingItem] = useState<{ sectionName: string; index: number } | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10); // Pagination appears when total items > 10
  const [showClearDialog, setShowClearDialog] = useState(false);
  
  const { register, handleSubmit, reset } = useForm<OtherItem>({
    defaultValues: {
      title: '',
      organization: '',
      date: '',
      location: '',
      description: '',
      url: '',
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (editingItem) {
      const sectionName = editingItem.sectionName;
      const index = editingItem.index;
      const currentSections = resumeData.others || {};
      const sectionItems = currentSections[sectionName] || [];
      const item = sectionItems[index];
      
      if (item) {
        reset({
          title: item.title || '',
          organization: item.organization || '',
          date: item.date || '',
          location: item.location || '',
          description: item.description || '',
          url: item.url || '',
        });
        setSelectedSection(sectionName);
        setShowCustomInput(false);
      }
    }
  }, [editingItem, resumeData.others, reset]);

  const onSubmit = (data: OtherItem) => {
    const sectionName = showCustomInput && customSectionName ? customSectionName : selectedSection;
    const currentSections = resumeData.others || {};
    const sectionItems = currentSections[sectionName] || [];
    
    if (editingItem && editingItem.sectionName === sectionName) {
      // Update existing item
      const updated = [...sectionItems];
      updated[editingItem.index] = data;
      updateOthers({
        ...currentSections,
        [sectionName]: updated,
      });
      toast({
        title: 'Item updated',
        description: `${data.title || 'Item'} has been updated in ${sectionName}.`,
      });
      setEditingItem(null);
    } else {
      // Add new item
      updateOthers({
        ...currentSections,
        [sectionName]: [...sectionItems, data],
      });
      toast({
        title: 'Item added',
        description: `${data.title || 'Item'} has been added to ${sectionName}.`,
      });
    }
    reset();
  };

  const removeItem = (sectionName: string, index: number) => {
    const currentSections = resumeData.others || {};
    const sectionItems = currentSections[sectionName] || [];
    const item = sectionItems[index];
    const updated = sectionItems.filter((_: any, i: number) => i !== index);
    
    // Clear editing state if the removed item was being edited
    if (editingItem && editingItem.sectionName === sectionName && editingItem.index === index) {
      setEditingItem(null);
      reset();
    } else if (editingItem && editingItem.sectionName === sectionName && editingItem.index > index) {
      // Adjust index if an item before the edited item was removed
      setEditingItem({ ...editingItem, index: editingItem.index - 1 });
    }
    
    // Reset to page 1 if current page would be empty after deletion
    const allItems = Object.values({ ...currentSections, [sectionName]: updated }).flat();
    const totalItems = allItems.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    } else if (totalItems === 0) {
      setCurrentPage(1);
    }
    
    updateOthers({
      ...currentSections,
      [sectionName]: updated,
    });
    toast({
      title: 'Item removed',
      description: item ? `${item.title || 'Item'} has been removed from ${sectionName}.` : 'Item removed.',
      variant: 'destructive',
    });
  };

  const handleEdit = (sectionName: string, index: number) => {
    setEditingItem({ sectionName, index });
    const formElement = document.getElementById('others-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleSectionChange = (value: string) => {
    if (value === '➕ Create New Section...') {
      setShowCustomInput(true);
      setSelectedSection('');
    } else {
      setShowCustomInput(false);
      setSelectedSection(value);
    }
  };

  const createCustomSection = () => {
    if (customSectionName.trim()) {
      setSelectedSection(customSectionName);
      setShowCustomInput(false);
      setCustomSectionName('');
    }
  };

  const allSections = [...COMMON_SECTIONS, '➕ Create New Section...'];

  const handleClearResume = () => {
    setShowClearDialog(true);
  };

  const confirmClear = () => {
    updateOthers({});
    reset();
    setEditingItem(null);
    setShowClearDialog(false);
    toast({
      title: 'Others cleared',
      description: 'All other section entries have been cleared.',
      variant: 'destructive',
    });
  };

  return (
    <Card className="bg-slate-900/50 border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-base">Other Sections</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="submit"
                  form="others-form"
                  className="bg-primary"
                  size="icon"
                >
                  <Plus className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{editingItem !== null ? 'Update entry' : 'Add to History'}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="others-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="section" className="text-xs font-semibold text-muted-foreground">
              Select Section
            </Label>
            <Select value={selectedSection} onValueChange={handleSectionChange}>
              <SelectTrigger className="text-sm">
                <SelectValue placeholder="Select a section" />
              </SelectTrigger>
              <SelectContent>
                {allSections.map((section) => (
                  <SelectItem key={section} value={section}>
                    {section}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {showCustomInput && (
            <div className="flex gap-2">
              <Input
                placeholder="New section name (e.g., Research Projects)"
                value={customSectionName}
                onChange={(e) => setCustomSectionName(e.target.value)}
                className="text-sm"
              />
              <Button type="button" onClick={createCustomSection} variant="outline">
                Create
              </Button>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-xs font-semibold text-muted-foreground">
                Title/Name
              </Label>
              <Input id="title" className="text-sm" {...register('title')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="organization" className="text-xs font-semibold text-muted-foreground">
                Organization/Publisher
              </Label>
              <Input id="organization" className="text-sm" {...register('organization')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date" className="text-xs font-semibold text-muted-foreground">
                Date
              </Label>
              <Input id="date" className="text-sm" {...register('date')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="location" className="text-xs font-semibold text-muted-foreground">
                Location
              </Label>
              <Input id="location" className="text-sm" {...register('location')} />
            </div>
            <div className="space-y-2 col-span-2">
              <Label htmlFor="description" className="text-xs font-semibold text-muted-foreground">
                Description
              </Label>
              <Textarea id="description" rows={3} className="text-sm" {...register('description')} />
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
              onClick={handleClearResume}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Clear
            </Button>
          </div>
        </form>

        {/* Other Sections List */}
        <div className="space-y-6">
          {(() => {
            // Flatten all items from all sections with their section info
            const allItemsWithSection: Array<{ sectionName: string; item: OtherItem; originalIndex: number }> = [];
            Object.entries(resumeData.others || {}).forEach(([sectionName, items]) => {
              const sectionItems = Array.isArray(items) ? items : [];
              sectionItems.forEach((item: OtherItem, index: number) => {
                allItemsWithSection.push({ sectionName, item, originalIndex: index });
              });
            });

            const totalItems = allItemsWithSection.length;
            const totalPages = Math.ceil(totalItems / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const paginatedItems = allItemsWithSection.slice(startIndex, endIndex);

            // Group paginated items by section for display
            const itemsBySection: Record<string, Array<{ item: OtherItem; originalIndex: number }>> = {};
            paginatedItems.forEach(({ sectionName, item, originalIndex }) => {
              if (!itemsBySection[sectionName]) {
                itemsBySection[sectionName] = [];
              }
              itemsBySection[sectionName].push({ item, originalIndex });
            });

            // Get total counts per section for display
            const sectionTotals: Record<string, number> = {};
            Object.entries(resumeData.others || {}).forEach(([sectionName, items]) => {
              sectionTotals[sectionName] = Array.isArray(items) ? items.length : 0;
            });

            if (totalItems === 0) {
              return (
                <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-muted rounded-lg">
                  <Layers className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
                  <p className="text-muted-foreground text-sm">No sections created yet. Add items to create sections.</p>
                </div>
              );
            }

            return (
              <>
                {Object.entries(itemsBySection).map(([sectionName, sectionItems]) => (
                  <div key={sectionName} className="space-y-4">
                    <Label className="text-base font-semibold">
                      {sectionName} ({sectionTotals[sectionName] || 0})
                    </Label>
                    <div className="space-y-2">
                      {sectionItems.map(({ item, originalIndex }, displayIndex) => (
                        <div
                          key={`${sectionName}-${originalIndex}-${displayIndex}`}
                          className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                        >
                          <div className="flex-1 grid grid-cols-5 gap-4 items-center">
                            <div className="col-span-2">
                              <p className="text-sm font-medium">{item.title || '—'}</p>
                              <p className="text-xs text-muted-foreground">{item.organization || '—'}</p>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {item.date || '—'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {item.location || '—'}
                            </div>
                            <div className="text-sm text-muted-foreground truncate max-w-xs">
                              {item.description || '—'}
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
                                    onClick={() => moveOthersItemUp(sectionName, originalIndex)}
                                    disabled={originalIndex === 0}
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
                                    onClick={() => moveOthersItemDown(sectionName, originalIndex)}
                                    disabled={originalIndex === (sectionTotals[sectionName] || 0) - 1}
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
                                    onClick={() => handleEdit(sectionName, originalIndex)}
                                  >
                                    <Pencil className="h-4 w-4" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Edit item</p>
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
                                    onClick={() => removeItem(sectionName, originalIndex)}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Delete item</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                {totalItems > itemsPerPage && (
                  <div className="pt-4">
                    <Pagination
                      currentPage={currentPage}
                      totalPages={totalPages}
                      onPageChange={setCurrentPage}
                      itemsPerPage={itemsPerPage}
                      totalItems={totalItems}
                    />
                  </div>
                )}
              </>
            );
          })()}
        </div>
      </CardContent>

      <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Other Sections</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all entries in Other Sections? This action cannot be undone.
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
              Clear Others
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}



 
