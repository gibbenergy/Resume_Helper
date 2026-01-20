import { useState, useRef } from 'react';
import { useResumeStore } from '@/stores/resumeStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useToast } from '@/components/ui/use-toast';
import { api } from '@/lib/api';
import { 
  UploadCloud, 
  DownloadCloud, 
  FileJson, 
  FileText, 
  Loader2, 
  Wand2, 
  Download, 
  RotateCcw,
  Info,
  Plus,
  CheckCircle2
} from 'lucide-react';

export function PDFGenerator() {
  const { resumeData, setResumeData } = useResumeStore();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [exportFormat, setExportFormat] = useState<'pdf' | 'json' | 'docx'>('pdf');
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);

  const processFile = async (file: File) => {
    if (!file) return;

    setLoading(true);
    setUploadedFileName(file.name);

    try {
      let response;
      if (file.name.endsWith('.json')) {
        response = await api.loadFromJson(file);
      } else if (file.name.endsWith('.pdf')) {
        response = await api.loadFromPDF(file);
      } else if (file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
        response = await api.loadFromDOCX(file);
      } else {
        toast({
          title: 'Unsupported format',
          description: 'Only JSON, PDF, and DOCX files are supported for import.',
          variant: 'destructive',
        });
        setLoading(false);
        return;
      }

      if (response.success && response.data) {
        // Update the resume store with imported data
        setResumeData(response.data);
        
        toast({
          title: 'Resume imported',
          description: 'Resume data has been imported successfully.',
          variant: 'success',
        });
      } else {
        toast({
          title: 'Import failed',
          description: response.error || 'Failed to import resume',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Import error',
        description: error instanceof Error ? error.message : 'Failed to import file',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      await processFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      await processFile(file);
    }
  };

  const handleClearFile = () => {
    setUploadedFileName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setIsGenerated(false);

    try {
      if (exportFormat === 'json') {
        const blob = await api.generateJson(resumeData);
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        setFileName('resume.json');
        setIsGenerated(true);
        toast({
          title: 'Resume generated',
          description: 'JSON resume generated successfully.',
          variant: 'success',
        });
      } else if (exportFormat === 'pdf') {
        const blob = await api.generateResumePDF(resumeData);
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        setFileName('resume.pdf');
        setIsGenerated(true);
        toast({
          title: 'Resume generated',
          description: 'PDF resume generated successfully.',
          variant: 'success',
        });
      } else if (exportFormat === 'docx') {
        const blob = await api.generateResumeDOCX(resumeData);
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        setFileName('resume.docx');
        setIsGenerated(true);
        toast({
          title: 'Resume generated',
          description: 'Word document generated successfully.',
          variant: 'success',
        });
      }
    } catch (error) {
      toast({
        title: 'Generation failed',
        description: error instanceof Error ? error.message : 'Failed to generate resume',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast({
        title: 'Download started',
        description: `${fileName} is being downloaded.`,
        variant: 'success',
      });
    }
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Import Card */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div className="flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-base">Ingestion</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleClearFile}
                    disabled={!uploadedFileName}
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Clear file</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Supported formats: JSON (Resume Helper exports), PDF, DOCX/DOC</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardHeader>
        <CardContent>
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-12
              transition-colors cursor-pointer
              ${isDragOver ? 'border-primary bg-primary/5' : 'border-muted hover:border-muted-foreground/50'}
              ${uploadedFileName ? 'border-primary/50 bg-primary/5' : ''}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.pdf,.docx,.doc"
              onChange={handleFileUpload}
              disabled={loading}
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-3">
              {uploadedFileName ? (
                <>
                  <CheckCircle2 className="h-12 w-12 text-primary" />
                  <p className="text-sm font-medium">{uploadedFileName}</p>
                </>
              ) : (
                <>
                  <Plus className="h-12 w-12 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Drop file here or click to browse</p>
                </>
              )}
            </div>
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded-lg">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Export Card */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <DownloadCloud className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-base">Generation</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Select value={exportFormat} onValueChange={(value: 'pdf' | 'json' | 'docx') => setExportFormat(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    PDF Document
                  </div>
                </SelectItem>
                <SelectItem value="json">
                  <div className="flex items-center gap-2">
                    <FileJson className="h-4 w-4" />
                    JSON Data
                  </div>
                </SelectItem>
                <SelectItem value="docx">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Word Document (.docx)
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Button
              onClick={handleGenerate}
              disabled={loading}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="mr-2 h-4 w-4" />
                  Generate Resume
                </>
              )}
            </Button>
            <Button
              onClick={handleDownload}
              disabled={!downloadUrl || loading || !isGenerated}
              variant="ghost"
              size="icon"
              className="h-10 w-10"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>

          {isGenerated && downloadUrl && (
            <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-md">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <p className="text-xs text-muted-foreground truncate">{fileName}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

 
