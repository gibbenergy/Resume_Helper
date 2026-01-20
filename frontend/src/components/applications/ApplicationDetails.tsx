import { useState, useEffect } from 'react';
import * as React from 'react';
import { useApplicationStore } from '@/stores/applicationStore';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Trash2, Calendar, FileText, Eye, Upload, Save, Edit, Maximize2, Minimize2, ExternalLink } from 'lucide-react';
import { InterviewManagement } from './InterviewManagement';
import { toTitleCase, formatDate } from '@/lib/utils';
import { api } from '@/lib/api';
import type { Application } from '@/lib/types';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface ApplicationDetailsProps {
  appId: string;
  open: boolean;
  onClose: () => void;
  onEdit: () => void;
}

const getStatusBadge = (status: string | undefined) => {
  if (!status) return null;
  
  const statusLower = status.toLowerCase();
  if (statusLower === 'applied') {
    return <Badge variant="ghost" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/20">Applied</Badge>;
  } else if (statusLower === 'offer' || statusLower === 'interviewing' || statusLower === 'accepted') {
    return <Badge className="bg-yellow-500 text-yellow-950 hover:bg-yellow-600 border-yellow-500">Interviewing</Badge>;
  } else if (statusLower === 'rejected' || statusLower === 'withdrawn') {
    return <Badge variant="destructive">Rejected</Badge>;
  }
  return <Badge variant="ghost">{status}</Badge>;
};

export function ApplicationDetails({ appId, open, onClose, onEdit }: ApplicationDetailsProps) {
  const { selectedApplication, fetchApplication, deleteApplication, updateApplication, uploadDocument, downloadDocument, deleteDocument } = useApplicationStore();
  const [showInterviews, setShowInterviews] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [editedData, setEditedData] = useState<Partial<Application>>({});
  const [isDirty, setIsDirty] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteDocConfirmOpen, setDeleteDocConfirmOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);

  // Initialize edited data when application loads
  useEffect(() => {
    if (open && selectedApplication && String(selectedApplication.id) === appId) {
      setEditedData({
        company: selectedApplication.company,
        position: selectedApplication.position,
        job_url: selectedApplication.job_url,
        location: selectedApplication.location,
        date_applied: selectedApplication.date_applied,
        status: selectedApplication.status,
        priority: selectedApplication.priority,
        match_score: selectedApplication.match_score,
        application_source: selectedApplication.application_source,
        salary_min: selectedApplication.salary_min,
        salary_max: selectedApplication.salary_max,
        hr_contact: selectedApplication.hr_contact,
        hiring_manager: selectedApplication.hiring_manager,
        recruiter: selectedApplication.recruiter,
        referral: selectedApplication.referral,
        notes: selectedApplication.notes,
      });
      setIsEditing(false);
      setIsDirty(false);
    }
  }, [open, selectedApplication, appId]);

  // Load PDF URL when application loads (uses cached PDF if available)
  useEffect(() => {
    if (!open) {
      // Don't load PDF if dialog is closed
      setPdfUrl(null);
      return;
    }
    
    if (selectedApplication && String(selectedApplication.id) === appId && selectedApplication.description) {
      setLoadingPdf(true);
      // Use cached PDF endpoint - it will generate if needed
      const pdfUrl = api.getJobDescriptionPDFUrl(appId);
      setPdfUrl(pdfUrl);
      setLoadingPdf(false);
    } else {
      setPdfUrl(null);
      setLoadingPdf(false);
    }
  }, [open, appId, selectedApplication?.id, selectedApplication?.description]);

  const handleDelete = async () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    const success = await deleteApplication(appId);
    if (success) {
      onClose();
    }
  };

  const handleSave = async () => {
    if (appId) {
      await updateApplication(appId, editedData);
      setIsDirty(false);
      // Refresh application data - this will trigger PDF regeneration if description changed
      await fetchApplication(appId);
      // If description was updated, clear PDF URL to force regeneration
      if (editedData.description !== undefined) {
        setPdfUrl(null);
        setLoadingPdf(true);
        // Small delay to ensure backend has updated
        setTimeout(() => {
          const newPdfUrl = api.getJobDescriptionPDFUrl(appId);
          setPdfUrl(newPdfUrl);
          setLoadingPdf(false);
        }, 500);
      }
    }
  };

  const handleFieldChange = (field: keyof Application, value: any) => {
    setEditedData((prev) => ({ ...prev, [field]: value }));
    setIsDirty(true);
  };

  // Format display value for string fields - converts underscores to title case
  const getDisplayValue = (field: keyof Application, value: any): string => {
    if (!value) return '—';
    if (typeof value === 'string') {
      // Apply pretty printing to all string fields
      if (field === 'company' || field === 'position' || field === 'location' || field === 'application_source' || field === 'status') {
        return toTitleCase(value);
      }
    }
    return String(value);
  };

  const handleEditClick = () => {
    setIsEditing(true);
    onEdit();
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setIsDirty(false);
    // Reset edited data to original
    if (selectedApplication && String(selectedApplication.id) === appId) {
      setEditedData({
        company: selectedApplication.company,
        position: selectedApplication.position,
        job_url: selectedApplication.job_url,
        location: selectedApplication.location,
        date_applied: selectedApplication.date_applied,
        status: selectedApplication.status,
        priority: selectedApplication.priority,
        match_score: selectedApplication.match_score,
        application_source: selectedApplication.application_source,
        salary_min: selectedApplication.salary_min,
        salary_max: selectedApplication.salary_max,
        hr_contact: selectedApplication.hr_contact,
        hiring_manager: selectedApplication.hiring_manager,
        recruiter: selectedApplication.recruiter,
        referral: selectedApplication.referral,
        notes: selectedApplication.notes,
      });
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && appId) {
      await uploadDocument(appId, file);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDownload = async (docId: number) => {
    if (appId) {
      await downloadDocument(appId, docId);
    }
  };

  const handleDeleteDoc = async (docId: number) => {
    setDocToDelete(String(docId));
    setDeleteDocConfirmOpen(true);
  };

  const confirmDeleteDocument = async () => {
    if (docToDelete && appId) {
      await deleteDocument(appId, Number(docToDelete));
      setDocToDelete(null);
    }
  };

  // Initialize editedData when dialog opens or application changes
  React.useEffect(() => {
    if (open && selectedApplication && String(selectedApplication.id) === appId) {
      setEditedData({
        company: selectedApplication.company,
        position: selectedApplication.position,
        job_url: selectedApplication.job_url,
        location: selectedApplication.location,
        date_applied: selectedApplication.date_applied,
        status: selectedApplication.status,
        priority: selectedApplication.priority,
        match_score: selectedApplication.match_score,
        application_source: selectedApplication.application_source,
        salary_min: selectedApplication.salary_min,
        salary_max: selectedApplication.salary_max,
        hr_contact: selectedApplication.hr_contact,
        hiring_manager: selectedApplication.hiring_manager,
        recruiter: selectedApplication.recruiter,
        referral: selectedApplication.referral,
        notes: selectedApplication.notes,
      });
      setIsEditing(false);
      setIsDirty(false);
    }
  }, [open, selectedApplication, appId]);

  if (!selectedApplication || String(selectedApplication.id) !== appId) {
    fetchApplication(appId);
    return null;
  }

  const app = selectedApplication;
  const documents = (app as any).documents || [];

  return (
    <Dialog open={open} onOpenChange={(newOpen) => {
      // Only close if explicitly requested via onClose() (X button, Manage Interviews)
      // onInteractOutside will prevent outside clicks from triggering this
      if (!newOpen) {
        onClose();
      }
    }}>
      <DialogContent 
        className="max-w-5xl h-[80vh] flex flex-col overflow-hidden"
        onInteractOutside={(e) => {
          // Prevent closing when clicking outside the dialog
          e.preventDefault();
        }}
      >
        {!showInterviews ? (
          <div className={`grid ${isFullscreen ? 'grid-cols-1' : 'grid-cols-[2fr_3fr]'} gap-6 flex-1 overflow-hidden min-h-0`}>
          {/* Left Column: Company Info & Documents */}
          {!isFullscreen && (
            <div className="flex flex-col h-full overflow-hidden p-6">
              {/* Header aligned with right column */}
              <div className="flex items-center justify-center mb-4 flex-shrink-0">
                <h3 className="text-lg font-semibold">Company</h3>
              </div>
              {/* Scrollable content area */}
              <div className="flex-1 overflow-y-auto pr-2 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Company</Label>
                    {isEditing ? (
                      <div className="relative mt-1.5">
                        <Input
                          value={editedData.company || ''}
                          onChange={(e) => handleFieldChange('company', e.target.value)}
                          className="text-base font-bold pr-10"
                        />
                        {editedData.job_url && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                            onClick={() => window.open(editedData.job_url, '_blank', 'noopener,noreferrer')}
                            title="Open job posting in new tab"
                          >
                            <ExternalLink className="h-4 w-4 text-blue-500" />
                          </Button>
                        )}
                      </div>
                    ) : (
                      <div className="relative mt-1.5">
                        <p className="text-base text-muted-foreground">{getDisplayValue('company', app.company)}</p>
                        {app.job_url && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-0 top-1/2 -translate-y-1/2 h-7 w-7"
                            onClick={() => window.open(app.job_url, '_blank', 'noopener,noreferrer')}
                            title="Open job posting in new tab"
                          >
                            <ExternalLink className="h-4 w-4 text-blue-500" />
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Position</Label>
                    {isEditing ? (
                      <Input
                        value={editedData.position || ''}
                        onChange={(e) => handleFieldChange('position', e.target.value)}
                        className="text-base font-bold mt-1.5"
                      />
                    ) : (
                      <p className="text-base text-muted-foreground mt-1.5">{getDisplayValue('position', app.position)}</p>
                    )}
                  </div>
                  {/* Tier 1: Match Score & Status (Hero + High Focus) */}
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Match Score</Label>
                  {isEditing ? (
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={editedData.match_score || ''}
                      onChange={(e) => handleFieldChange('match_score', e.target.value ? parseInt(e.target.value) : undefined)}
                      className="text-base font-bold mt-1.5"
                    />
                  ) : (
                      <p className="text-2xl font-bold text-green-500 mt-1.5">{app.match_score ? `${app.match_score}%` : '—'}</p>
                    )}
                  </div>
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Status</Label>
                  {isEditing ? (
                    <Select
                      value={editedData.status || 'Applied'}
                      onValueChange={(value) => handleFieldChange('status', value)}
                    >
                      <SelectTrigger className="mt-1.5 font-bold">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Applied">Applied</SelectItem>
                        <SelectItem value="Offer">Offer</SelectItem>
                        <SelectItem value="Accepted">Accepted</SelectItem>
                        <SelectItem value="Rejected">Rejected</SelectItem>
                        <SelectItem value="Withdrawn">Withdrawn</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <div className="mt-1.5">{getStatusBadge(getDisplayValue('status', app.status))}</div>
                  )}
                  </div>
                  {/* Tier 2: Location (High Focus) */}
                  <div className="col-span-2">
                    <Label className="text-xs font-normal text-muted-foreground">Location</Label>
                  {isEditing ? (
                    <Input
                      value={editedData.location || ''}
                      onChange={(e) => handleFieldChange('location', e.target.value)}
                      className="text-base font-semibold mt-1.5"
                    />
                  ) : (
                      <p className="text-base font-semibold mt-1.5">{getDisplayValue('location', app.location)}</p>
                    )}
                  </div>
                  {/* Tier 3: Date Applied & Priority (Standard Info) */}
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Date Applied</Label>
                  {isEditing ? (
                    <Input
                      type="date"
                      value={editedData.date_applied || ''}
                      onChange={(e) => handleFieldChange('date_applied', e.target.value)}
                      className="text-base mt-1.5"
                    />
                  ) : (
                      <p className="text-base mt-1.5">{formatDate(app.date_applied)}</p>
                    )}
                  </div>
                  <div>
                    <Label className="text-xs font-normal text-muted-foreground">Priority</Label>
                  {isEditing ? (
                    <Select
                      value={editedData.priority || 'Medium'}
                      onValueChange={(value) => handleFieldChange('priority', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="High">High</SelectItem>
                        <SelectItem value="Medium">Medium</SelectItem>
                        <SelectItem value="Low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                      <p className="text-base mt-1.5">{app.priority || '—'}</p>
                    )}
                  </div>
                  {((isEditing ? editedData.salary_min || editedData.salary_max : app.salary_min || app.salary_max) && (
                  <div className="col-span-2">
                    <Label className="text-xs font-normal text-muted-foreground">Salary Range</Label>
                    {isEditing ? (
                      <div className="grid grid-cols-2 gap-2 mt-1.5">
                        <Input
                          type="number"
                          placeholder="Min"
                          value={editedData.salary_min || ''}
                          onChange={(e) => handleFieldChange('salary_min', e.target.value ? parseInt(e.target.value) : undefined)}
                          className="text-base font-bold"
                        />
                        <Input
                          type="number"
                          placeholder="Max"
                          value={editedData.salary_max || ''}
                          onChange={(e) => handleFieldChange('salary_max', e.target.value ? parseInt(e.target.value) : undefined)}
                          className="text-base font-bold"
                        />
                      </div>
                    ) : (
                      <p className="text-base text-muted-foreground mt-1.5">
                        {app.salary_min && app.salary_max
                          ? `$${app.salary_min.toLocaleString()} - $${app.salary_max.toLocaleString()}`
                          : app.salary_min
                            ? `$${app.salary_min.toLocaleString()}+`
                            : `Up to $${app.salary_max?.toLocaleString()}`}
                      </p>
                    )}
                  </div>
                  ))}
                  <Accordion type="multiple" className="col-span-2 mt-4">
                  <AccordionItem value="contact-info">
                    <AccordionTrigger className="text-xs font-normal text-muted-foreground py-2">
                      Contact Information
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        <div>
                          <Label className="text-xs font-normal text-muted-foreground">HR Contact</Label>
                          {isEditing ? (
                            <Input
                              value={editedData.hr_contact || ''}
                              onChange={(e) => handleFieldChange('hr_contact', e.target.value)}
                              className="text-sm font-semibold mt-1.5"
                            />
                          ) : (
                            <p className="text-sm font-semibold mt-1.5">{app.hr_contact || '—'}</p>
                          )}
                        </div>
                        <div>
                          <Label className="text-xs font-normal text-muted-foreground">Hiring Manager</Label>
                          {isEditing ? (
                            <Input
                              value={editedData.hiring_manager || ''}
                              onChange={(e) => handleFieldChange('hiring_manager', e.target.value)}
                              className="text-sm font-semibold mt-1.5"
                            />
                          ) : (
                            <p className="text-sm font-semibold mt-1.5">{app.hiring_manager || '—'}</p>
                          )}
                        </div>
                        <div>
                          <Label className="text-xs font-normal text-muted-foreground">Recruiter</Label>
                          {isEditing ? (
                            <Input
                              value={editedData.recruiter || ''}
                              onChange={(e) => handleFieldChange('recruiter', e.target.value)}
                              className="text-sm font-semibold mt-1.5"
                            />
                          ) : (
                            <p className="text-sm font-semibold mt-1.5">{app.recruiter || '—'}</p>
                          )}
                        </div>
                        <div>
                          <Label className="text-xs font-normal text-muted-foreground">Referral</Label>
                          {isEditing ? (
                            <Input
                              value={editedData.referral || ''}
                              onChange={(e) => handleFieldChange('referral', e.target.value)}
                              className="text-sm font-semibold mt-1.5"
                            />
                          ) : (
                            <p className="text-sm font-semibold mt-1.5">{app.referral || '—'}</p>
                          )}
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="notes">
                    <AccordionTrigger className="text-xs font-normal text-muted-foreground py-2">
                      Notes
                    </AccordionTrigger>
                    <AccordionContent>
                      {isEditing ? (
                        <Textarea
                          value={editedData.notes || ''}
                          onChange={(e) => handleFieldChange('notes', e.target.value)}
                          className="text-sm font-semibold mt-2 min-h-[100px]"
                          placeholder="Add notes about this application..."
                        />
                      ) : (
                        <p className="text-sm font-semibold mt-2 whitespace-pre-wrap min-h-[100px]">{app.notes || '—'}</p>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                  </Accordion>
                </div>

                {/* Documents Section */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Documents</h3>
                    <div>
                      <input
                        ref={fileInputRef}
                        type="file"
                        id="document-upload"
                        className="hidden"
                        onChange={handleFileUpload}
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="mr-2 h-4 w-4" />
                        Upload
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {documents.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No documents uploaded</p>
                    ) : (
                      documents.map((doc: any) => (
                        <div
                          key={doc.id}
                          className="flex items-center justify-between p-3 bg-muted/30 rounded-md hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="text-sm truncate">{doc.name}</span>
                          </div>
                          <div className="flex gap-2 flex-shrink-0">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => handleDownload(doc.id)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 hover:text-destructive"
                              onClick={() => handleDeleteDoc(doc.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Right Column: Job Description PDF */}
          <div className="bg-muted/30 p-6 rounded-lg overflow-hidden flex flex-col h-full" style={{ minWidth: 0 }}>
            {/* Header aligned with left column */}
            <div className="flex items-center justify-center mb-4 relative flex-shrink-0">
              <h3 className="text-lg font-semibold">Job</h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="h-8 w-8 absolute right-0"
              >
                {isFullscreen ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </Button>
            </div>
            {/* Scrollable content area */}
            <div className="flex-1 overflow-hidden">
              {loadingPdf ? (
                <div className="flex items-center justify-center h-full">
                  <p className="text-sm text-muted-foreground">Generating PDF...</p>
                </div>
              ) : pdfUrl ? (
                <div className="h-full overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-muted/50 [&::-webkit-scrollbar-thumb]:bg-muted-foreground/30 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:hover:bg-muted-foreground/50">
                  <iframe
                    src={pdfUrl}
                    className="w-full h-full min-h-[600px] border-0 rounded"
                    title="Job Description PDF"
                  />
                </div>
              ) : app.description ? (
                <div className="h-full overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-muted/50 [&::-webkit-scrollbar-thumb]:bg-muted-foreground/30 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:hover:bg-muted-foreground/50">
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    {app.description.includes('<') && app.description.includes('>') ? (
                      <div dangerouslySetInnerHTML={{ __html: app.description }} />
                    ) : (
                      <div className="whitespace-pre-wrap">{app.description}</div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No job description available</p>
              )}
            </div>
          </div>
        </div>
        ) : (
          <div className="flex-1 overflow-hidden flex flex-col">
            {/* Hero Header with Status & Match Score */}
            <div className="flex items-center justify-between p-6 border-b bg-muted/30">
              <div className="flex items-center gap-6">
                <div>
                  <Label className="text-xs font-normal text-muted-foreground">Match Score</Label>
                  <p className="text-2xl font-bold text-green-500 mt-1">{app.match_score ? `${app.match_score}%` : '—'}</p>
                </div>
                <div>
                  <Label className="text-xs font-normal text-muted-foreground">Status</Label>
                  <div className="mt-1">{getStatusBadge(getDisplayValue('status', app.status))}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold">{getDisplayValue('company', app.company)}</div>
                <div className="text-xs text-muted-foreground mt-1">{getDisplayValue('location', app.location)}</div>
              </div>
            </div>
            <InterviewManagement 
              appId={appId} 
              onClose={() => setShowInterviews(false)}
              dateApplied={app.date_applied}
            />
          </div>
        )}

        {!showInterviews && (
          <DialogFooter>
            {isEditing ? (
              <>
                <Button variant="outline" onClick={handleCancelEdit}>
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={!isDirty}>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
              </>
            ) : (
              <Button variant="outline" onClick={handleEditClick}>
                <Edit className="mr-2 h-4 w-4" />
                Edit Details
              </Button>
            )}
            <Button onClick={() => setShowInterviews(!showInterviews)}>
              <Calendar className="mr-2 h-4 w-4" />
              Manage Interviews
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </DialogFooter>
        )}
      </DialogContent>

      {/* Delete Application Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirmOpen}
        onOpenChange={setDeleteConfirmOpen}
        onConfirm={confirmDelete}
        title="Delete Application"
        description="Are you sure you want to delete this application?"
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
      />

      {/* Delete Document Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDocConfirmOpen}
        onOpenChange={setDeleteDocConfirmOpen}
        onConfirm={confirmDeleteDocument}
        title="Delete Document"
        description="Are you sure you want to delete this document?"
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
      />
    </Dialog>
  );
}
