import { useState, useEffect } from 'react';
import { useApplicationStore } from '@/stores/applicationStore';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Plus, Search, Trash2 } from 'lucide-react';
import type { ApplicationCreateRequest } from '@/lib/types';
import { ApplicationDetails } from './ApplicationDetails';
import { toTitleCase, formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Pagination } from '@/components/ui/pagination';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface ApplicationTrackerProps {
  isActive?: boolean;
}

export function ApplicationTracker({ isActive = true }: ApplicationTrackerProps) {
  const {
    applications,
    loading,
    error,
    fetchApplications,
    createApplication,
    updateApplication,
    deleteApplication,
    setSelectedApplication,
    settings,
    fetchSettings,
  } = useApplicationStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date_applied');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [statusFilter, setStatusFilter] = useState('All');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingApp, setEditingApp] = useState<string | null>(null);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(15); // Show 15 items per page for better UX
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [appToDelete, setAppToDelete] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<ApplicationCreateRequest>>({
    job_url: '',
    company: '',
    position: '',
    location: '',
    date_applied: new Date().toISOString().split('T')[0],
    status: 'Applied',
    priority: 'Medium',
  });

  useEffect(() => {
    fetchApplications();
    if (!settings) {
      fetchSettings();
    }
  }, [fetchApplications, settings, fetchSettings]);

  // Auto-refresh when tab becomes active
  useEffect(() => {
    if (isActive) {
      fetchApplications();
    }
  }, [isActive, fetchApplications]);

  // Reset to first page when search or filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter]);

  const filteredApplications = applications.filter((app) => {
    const matchesSearch =
      !searchQuery ||
      app.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.position.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'All' || app.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getCurrentRound = (app: typeof applications[0]): string => {
    const pipeline = app.interview_pipeline || {};
    const roundNames = settings?.default_interview_rounds || [
      'phone_screen',
      'technical',
      'panel',
      'manager',
      'culture_fit',
      'final_round',
    ];

    if (!pipeline || Object.keys(pipeline).length === 0) {
      return 'Not Started';
    }

    for (const roundName of roundNames) {
      const roundData = pipeline[roundName] || { status: 'not_started' };
      const status = roundData.status || 'not_started';

      if (status === 'scheduled') {
        return roundName.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
      } else if (status === 'completed') {
        const outcome = roundData.outcome || '';
        if (outcome !== 'passed') {
          return roundName.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
        }
      } else if (status === 'cancelled' || status === 'on_hold') {
        return roundName.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
      }
    }

    // Check if first round is not started
    if (roundNames.length > 0) {
      const firstRound = roundNames[0];
      const firstRoundData = pipeline[firstRound] || { status: 'not_started' };
      if (firstRoundData.status === 'not_started') {
        return firstRound.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
      }
    }

    return 'All Completed';
  };

  // Get sortable value for current round (returns index in round order, or -1 for special cases)
  const getCurrentRoundSortValue = (app: typeof applications[0]): number => {
    const pipeline = app.interview_pipeline || {};
    const roundNames = settings?.default_interview_rounds || [
      'phone_screen',
      'technical',
      'panel',
      'manager',
      'culture_fit',
      'final_round',
    ];

    if (!pipeline || Object.keys(pipeline).length === 0) {
      return -1; // "Not Started" comes first
    }

    for (let i = 0; i < roundNames.length; i++) {
      const roundName = roundNames[i];
      const roundData = pipeline[roundName] || { status: 'not_started' };
      const status = roundData.status || 'not_started';

      if (status === 'scheduled' || status === 'in_progress') {
        return i;
      } else if (status === 'completed') {
        const outcome = roundData.outcome || '';
        if (outcome !== 'passed') {
          return i;
        }
      } else if (status === 'cancelled' || status === 'on_hold') {
        return i;
      }
    }

    // Check if first round is not started
    if (roundNames.length > 0) {
      const firstRound = roundNames[0];
      const firstRoundData = pipeline[firstRound] || { status: 'not_started' };
      if (firstRoundData.status === 'not_started') {
        return 0;
      }
    }

    return roundNames.length; // "All Completed" comes last
  };

  const getStatusBadge = (status: string | undefined) => {
    if (!status) return <span>—</span>;
    
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

  const sortedApplications = [...filteredApplications].sort((a, b) => {
    let aVal: any = a[sortBy as keyof typeof a];
    let bVal: any = b[sortBy as keyof typeof b];

    // Handle special sorting for status
    if (sortBy === 'status') {
      const statusOrder = {
        Accepted: 0,
        Offer: 1,
        Applied: 2,
        Rejected: 3,
        Withdrawn: 4,
      };
      aVal = statusOrder[aVal as keyof typeof statusOrder] ?? 2;
      bVal = statusOrder[bVal as keyof typeof statusOrder] ?? 2;
    }
    // Handle special sorting for priority
    else if (sortBy === 'priority') {
      const priorityOrder = { High: 0, Medium: 1, Low: 2 };
      aVal = priorityOrder[aVal as keyof typeof priorityOrder] ?? 1;
      bVal = priorityOrder[bVal as keyof typeof priorityOrder] ?? 1;
    }
    // Handle special sorting for current_round
    else if (sortBy === 'current_round') {
      aVal = getCurrentRoundSortValue(a);
      bVal = getCurrentRoundSortValue(b);
    }
    // Handle match_score - treat null/undefined as 0
    else if (sortBy === 'match_score') {
      aVal = aVal ?? 0;
      bVal = bVal ?? 0;
    }
    // Handle salary_range - use average of min/max, or min if max is missing
    else if (sortBy === 'salary_range') {
      // Calculate average salary or use min if max is not available
      const aMin = a.salary_min ?? 0;
      const aMax = a.salary_max ?? aMin;
      const bMin = b.salary_min ?? 0;
      const bMax = b.salary_max ?? bMin;
      
      aVal = aMin && aMax ? (aMin + aMax) / 2 : 0;
      bVal = bMin && bMax ? (bMin + bMax) / 2 : 0;
    }
    // Handle company - case-insensitive string comparison
    else if (sortBy === 'company') {
      aVal = (aVal || '').toString().toLowerCase();
      bVal = (bVal || '').toString().toLowerCase();
    }
    // Handle date_applied - convert to comparable format
    else if (sortBy === 'date_applied') {
      aVal = aVal ? new Date(aVal).getTime() : 0;
      bVal = bVal ? new Date(bVal).getTime() : 0;
    }

    // Handle null/undefined values
    if (aVal == null && bVal == null) return 0;
    if (aVal == null) return 1; // null values go to end
    if (bVal == null) return -1; // null values go to end

    // Compare values
    if (aVal === bVal) return 0;
    const comparison = aVal > bVal ? 1 : -1;
    return sortOrder === 'desc' ? -comparison : comparison;
  });

  const handleOpenDialog = (app?: typeof applications[0]) => {
    if (app) {
      setEditingApp(String(app.id));
      setFormData({
        job_url: app.job_url,
        company: app.company,
        position: app.position,
        location: app.location || '',
        date_applied: app.date_applied || '',
        status: app.status || 'Applied',
        priority: app.priority || 'Medium',
        application_source: app.application_source || 'Other',
        description: app.description || '',
        notes: app.notes || '',
        match_score: app.match_score,
        salary_min: app.salary_min,
        salary_max: app.salary_max,
        hr_contact: app.hr_contact || '',
        hiring_manager: app.hiring_manager || '',
        recruiter: app.recruiter || '',
        referral: app.referral || '',
      });
    } else {
      setEditingApp(null);
      setFormData({
        job_url: '',
        company: '',
        position: '',
        location: '',
        date_applied: new Date().toISOString().split('T')[0],
        status: 'Applied',
        priority: 'Medium',
        application_source: 'Other',
      });
    }
    setIsDialogOpen(true);
  };

  const handleViewDetails = (app: typeof applications[0]) => {
    setSelectedApplication(app);
    setSelectedAppId(String(app.id));
  };

  const handleSave = async () => {
    if (!formData.company || !formData.position || !formData.job_url) {
      alert('Please fill in required fields: Company, Position, and Job URL');
      return;
    }

    if (editingApp) {
      await updateApplication(editingApp, formData);
    } else {
      await createApplication(formData as ApplicationCreateRequest);
    }
    setIsDialogOpen(false);
    fetchApplications();
  };

  const handleDelete = async (appId: string) => {
    setAppToDelete(appId);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (appToDelete) {
      await deleteApplication(appToDelete);
      fetchApplications();
      // Reset to first page if current page would be empty after deletion
      const remainingItems = sortedApplications.length - 1;
      const totalPages = Math.ceil(remainingItems / itemsPerPage);
      if (currentPage > totalPages && totalPages > 0) {
        setCurrentPage(totalPages);
      } else if (remainingItems === 0) {
        setCurrentPage(1);
      }
      setAppToDelete(null);
    }
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      // Toggle order if clicking the same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with default descending order
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  // Spotify-style triangle icon component
  const TriangleIcon = ({ direction }: { direction: 'up' | 'down' }) => (
    <svg
      width="8"
      height="6"
      viewBox="0 0 8 6"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0 ml-1"
      style={{ color: '#22c55e' }}
    >
      {direction === 'down' ? (
        <path d="M4 6L0 0H8L4 6Z" fill="currentColor" />
      ) : (
        <path d="M4 0L8 6H0L4 0Z" fill="currentColor" />
      )}
    </svg>
  );

  const SortableHeader = ({ field, label }: { field: string; label: string }) => {
    const isActive = sortBy === field;
    
    return (
      <TableHead
        className={`cursor-pointer select-none hover:bg-muted/50 transition-colors ${isActive ? 'text-white' : ''}`}
        onClick={(e) => {
          e.stopPropagation();
          handleSort(field);
        }}
        style={{ userSelect: 'none' }}
      >
        <button
          type="button"
          className="flex items-center gap-1 w-full text-left bg-transparent border-none p-0 cursor-pointer"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handleSort(field);
          }}
        >
          <span className={isActive ? 'text-white' : ''}>{label}</span>
          {isActive && (
            <TriangleIcon direction={sortOrder === 'asc' ? 'up' : 'down'} />
          )}
        </button>
      </TableHead>
    );
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <Card>
        <CardContent className="space-y-4 pt-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search by company, position..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status-filter">Filter by Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger id="status-filter">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All</SelectItem>
                  <SelectItem value="Applied">Applied</SelectItem>
                  <SelectItem value="Offer">Offer</SelectItem>
                  <SelectItem value="Accepted">Accepted</SelectItem>
                  <SelectItem value="Rejected">Rejected</SelectItem>
                  <SelectItem value="Withdrawn">Withdrawn</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={() => handleOpenDialog()} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Add Application
              </Button>
            </div>
          </div>
          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-md">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Applications Table */}
      <Card>
        <CardHeader>
          <CardTitle>Applications ({sortedApplications.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center p-8">Loading applications...</div>
          ) : sortedApplications.length === 0 ? (
            <div className="text-center p-8 text-muted-foreground">
              No applications found. Click "Add Application" to get started.
            </div>
          ) : (
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    <SortableHeader field="company" label="Company" />
                    <TableHead className="max-w-[180px]">Position</TableHead>
                    <SortableHeader field="date_applied" label="Date" />
                    <SortableHeader field="match_score" label="Match" />
                    <SortableHeader field="salary_range" label="Salary" />
                    <SortableHeader field="status" label="Status" />
                    <SortableHeader field="priority" label="Priority" />
                    <SortableHeader field="current_round" label="Round" />
                    <TableHead>Docs</TableHead>
                    <TableHead className="w-[80px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedApplications
                    .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                    .map((app) => (
                    <TableRow
                      key={app.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleViewDetails(app)}
                    >
                      <TableCell className="font-medium">{toTitleCase(app.company)}</TableCell>
                      <TableCell className="max-w-[180px] truncate" title={toTitleCase(app.position)}>
                        {toTitleCase(app.position)}
                      </TableCell>
                      <TableCell className="whitespace-nowrap">{formatDate(app.date_applied)}</TableCell>
                      <TableCell>{app.match_score ? `${app.match_score}%` : '—'}</TableCell>
                      <TableCell className="whitespace-nowrap text-sm">
                        {app.salary_min && app.salary_max
                          ? `$${(app.salary_min / 1000).toFixed(0)}k-${(app.salary_max / 1000).toFixed(0)}k`
                          : app.salary_min
                          ? `$${(app.salary_min / 1000).toFixed(0)}k+`
                          : '—'}
                      </TableCell>
                      <TableCell>{getStatusBadge(app.status)}</TableCell>
                      <TableCell>{app.priority}</TableCell>
                      <TableCell className="whitespace-nowrap">{getCurrentRound(app)}</TableCell>
                      <TableCell>
                        {(app as any).documents && (app as any).documents.length > 0
                          ? `${(app as any).documents.length}`
                          : '—'}
                      </TableCell>
                      <TableCell onClick={(e) => e.stopPropagation()} className="w-[80px]">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(String(app.id))}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {sortedApplications.length > itemsPerPage && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={Math.ceil(sortedApplications.length / itemsPerPage)}
                  onPageChange={setCurrentPage}
                  itemsPerPage={itemsPerPage}
                  totalItems={sortedApplications.length}
                  onItemsPerPageChange={(newItemsPerPage) => {
                    setItemsPerPage(newItemsPerPage);
                    setCurrentPage(1); // Reset to first page when changing items per page
                  }}
                />
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingApp ? 'Edit Application' : 'Add Application'}</DialogTitle>
            <DialogDescription>
              {editingApp ? 'Update application details' : 'Add a new job application to track'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="company">Company *</Label>
                <Input
                  id="company"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="position">Position *</Label>
                <Input
                  id="position"
                  value={formData.position}
                  onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="job_url">Job URL *</Label>
                <Input
                  id="job_url"
                  value={formData.job_url}
                  onChange={(e) => setFormData({ ...formData, job_url: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date_applied">Date Applied</Label>
                <Input
                  id="date_applied"
                  type="date"
                  value={formData.date_applied}
                  onChange={(e) => setFormData({ ...formData, date_applied: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger id="status">
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
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(value) => setFormData({ ...formData, priority: value })}
                >
                  <SelectTrigger id="priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="High">High</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="Low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="match_score">Match Score</Label>
                <Input
                  id="match_score"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.match_score || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, match_score: parseInt(e.target.value) || undefined })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="application_source">Application Source</Label>
                <Select
                  value={formData.application_source || 'Other'}
                  onValueChange={(value) => setFormData({ ...formData, application_source: value })}
                >
                  <SelectTrigger id="application_source">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(settings?.application_sources || [
                      'LinkedIn',
                      'Indeed',
                      'Company Website',
                      'Referral',
                      'Other',
                    ]).map((source: string) => (
                      <SelectItem key={source} value={source}>
                        {source}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary_min">Salary Min</Label>
                <Input
                  id="salary_min"
                  type="number"
                  value={formData.salary_min || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      salary_min: parseInt(e.target.value) || undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary_max">Salary Max</Label>
                <Input
                  id="salary_max"
                  type="number"
                  value={formData.salary_max || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      salary_max: parseInt(e.target.value) || undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="description">Job Description</Label>
                <Textarea
                  id="description"
                  rows={4}
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Contact Information</Label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="hr_contact">HR Contact</Label>
                    <Input
                      id="hr_contact"
                      value={formData.hr_contact || ''}
                      onChange={(e) => setFormData({ ...formData, hr_contact: e.target.value })}
                      placeholder="hr@company.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="hiring_manager">Hiring Manager</Label>
                    <Input
                      id="hiring_manager"
                      value={formData.hiring_manager || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, hiring_manager: e.target.value })
                      }
                      placeholder="manager@company.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="recruiter">Recruiter</Label>
                    <Input
                      id="recruiter"
                      value={formData.recruiter || ''}
                      onChange={(e) => setFormData({ ...formData, recruiter: e.target.value })}
                      placeholder="recruiter@company.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="referral">Referral Contact</Label>
                    <Input
                      id="referral"
                      value={formData.referral || ''}
                      onChange={(e) => setFormData({ ...formData, referral: e.target.value })}
                      placeholder="friend@company.com"
                    />
                  </div>
                </div>
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  rows={3}
                  value={formData.notes || ''}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Application Details Sheet */}
      {selectedAppId && (
        <ApplicationDetails
          appId={selectedAppId}
          open={!!selectedAppId}
          onClose={() => {
            setSelectedAppId(null);
            setSelectedApplication(null);
            fetchApplications(); // Refresh after closing details
          }}
          onEdit={() => {
            const app = applications.find((a) => String(a.id) === selectedAppId);
            if (app) {
              setSelectedAppId(null);
              handleOpenDialog(app);
            }
          }}
        />
      )}

      {/* Delete Confirmation Dialog */}
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
    </div>
  );
}

 
