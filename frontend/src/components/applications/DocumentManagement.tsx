import { useState, useRef, useEffect } from 'react';
import { useApplicationStore } from '@/stores/applicationStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Upload, Download, Trash2, FileText } from 'lucide-react';
import type { ApplicationDocument } from '@/lib/types';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface DocumentManagementProps {
  appId: string;
}

export function DocumentManagement({ appId }: DocumentManagementProps) {
  const {
    selectedApplication,
    fetchApplication,
    uploadDocument,
    downloadDocument,
    deleteDocument,
    loading,
  } = useApplicationStore();

  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<ApplicationDocument | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<ApplicationDocument | null>(null);

  useEffect(() => {
    if (!selectedApplication || selectedApplication.id !== appId) {
      fetchApplication(appId);
    }
  }, [appId, selectedApplication, fetchApplication]);

  const documents = selectedApplication?.documents || [];

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const success = await uploadDocument(appId, file);
    setUploading(false);

    if (success) {
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (!file) return;

    setUploading(true);
    const success = await uploadDocument(appId, file);
    setUploading(false);

    if (success) {
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleDownload = async (doc: ApplicationDocument) => {
    await downloadDocument(appId, doc.id);
  };

  const handleDelete = async (doc: ApplicationDocument) => {
    setDocToDelete(doc);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (docToDelete) {
      await deleteDocument(appId, docToDelete.id);
      if (selectedDoc?.id === docToDelete.id) {
        setSelectedDoc(null);
      }
      setDocToDelete(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    if (mb >= 0.01) {
      return `${mb.toFixed(2)} MB`;
    }
    const kb = bytes / 1024;
    return `${kb.toFixed(2)} KB`;
  };

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toISOString().split('T')[0];
    } catch {
      return 'Unknown';
    }
  };

  const getFileStatus = (doc: ApplicationDocument): string => {
    // In a real implementation, we might check if file exists
    // For now, assume all documents are available
    return '✅ Available';
  };

  return (
    <Accordion type="single" collapsible className="w-full">
      <AccordionItem value="documents">
        <AccordionTrigger>Documents</AccordionTrigger>
        <AccordionContent>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Upload Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-muted transition-colors"
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drop file here or click to upload
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supports: PDF, DOC, images, code files, archives, etc.
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    onChange={handleFileSelect}
                    disabled={uploading || loading}
                  />
                </div>
                {uploading && (
                  <p className="text-sm text-muted-foreground mt-2 text-center">
                    Uploading...
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Your Documents ({documents.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <div className="text-center p-8 text-muted-foreground">
                    No documents uploaded yet
                  </div>
                ) : (
                  <div className="border rounded-md">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Document Name</TableHead>
                          <TableHead>Upload Date</TableHead>
                          <TableHead>File Size</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {documents.map((doc) => (
                          <TableRow
                            key={doc.id}
                            className={selectedDoc?.id === doc.id ? 'bg-muted' : ''}
                            onClick={() => setSelectedDoc(doc)}
                          >
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-muted-foreground" />
                                {doc.name}
                              </div>
                            </TableCell>
                            <TableCell>{formatDate(doc.upload_date)}</TableCell>
                            <TableCell>{formatFileSize(doc.size)}</TableCell>
                            <TableCell>{getFileStatus(doc)}</TableCell>
                            <TableCell>
                              <div className="flex gap-1">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownload(doc);
                                  }}
                                >
                                  <Download className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(doc);
                                  }}
                                >
                                  <Trash2 className="h-4 w-4 text-destructive" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </AccordionContent>
      </AccordionItem>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirmOpen}
        onOpenChange={setDeleteConfirmOpen}
        onConfirm={confirmDelete}
        title="Delete Document"
        description={`Are you sure you want to delete "${docToDelete?.name}"?`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
      />
    </Accordion>
  );
}



