import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Edit2, RefreshCw, Download, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { formatAnalysisAsMarkdown, formatSuggestionsContent, parseMarkdownToAnalysis } from '@/lib/utils';
import type { ResumeData } from '@/lib/types';
import type { JobAnalysisResult, TailoredResumeResult, CoverLetterResult, ImprovementSuggestionsResult } from '@/lib/types';

interface PDFViewerModalProps {
  open: boolean;
  onClose: () => void;
  type: 'summary' | 'tailored' | 'cover-letter' | 'suggestions';
  data: JobAnalysisResult | TailoredResumeResult | CoverLetterResult | ImprovementSuggestionsResult | undefined;
  resumeData: ResumeData;
  jobAnalysis?: JobAnalysisResult;
  editedContent?: Record<string, string | null>;
  onContentEdit?: (type: string, content: string) => void;
}

export function PDFViewerModal({
  open,
  onClose,
  type,
  data,
  resumeData,
  jobAnalysis,
  editedContent,
  onContentEdit,
}: PDFViewerModalProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [editContent, setEditContent] = useState<string>('');

  // Get the editable content based on type
  const getEditableContent = (): string => {
    if (!data) return '';

    switch (type) {
      case 'summary':
        if ('analysis' in data && data.analysis) {
          return editedContent?.jobAnalysis || formatAnalysisAsMarkdown(data.analysis);
        }
        return '';
      case 'tailored':
        if ('tailored_resume' in data && data.tailored_resume) {
          return editedContent?.tailoredResume || JSON.stringify(data.tailored_resume, null, 2);
        }
        return '';
      case 'cover-letter':
        if ('body_content' in data && data.body_content) {
          return editedContent?.coverLetter || data.body_content;
        }
        return '';
      case 'suggestions':
        if ('content' in data && data.content) {
          const rawContent = data.content;
          const formattedContent = formatSuggestionsContent(rawContent);
          return editedContent?.suggestions && editedContent.suggestions !== rawContent
            ? editedContent.suggestions
            : formattedContent;
        }
        return '';
      default:
        return '';
    }
  };

  // Generate PDF based on type
  const generatePDF = async (contentToUse?: string) => {
    if (!data) return;

    setIsGenerating(true);
    try {
      let blob: Blob;

      switch (type) {
        case 'summary':
          if ('analysis' in data && data.analysis) {
            // Parse edited markdown back to analysis object or use original
            const originalAnalysis = typeof data.analysis === 'object' ? data.analysis : {};
            const analysisData = contentToUse 
              ? { ...originalAnalysis, sections: parseMarkdownToAnalysis(contentToUse).sections }
              : data.analysis;
            
            blob = await api.generateJobAnalysisPDF(analysisData);
          } else {
            throw new Error('No analysis data available');
          }
          break;

        case 'tailored':
          if ('tailored_resume' in data && data.tailored_resume) {
            const personalInfo = resumeData.personal_info || data.tailored_resume.personal_info || {};
            let tailoredData = data.tailored_resume;
            
            // If edited content is provided, parse JSON and use it
            if (contentToUse) {
              try {
                tailoredData = JSON.parse(contentToUse);
              } catch (e) {
                // If parsing fails, use original data
                console.warn('Failed to parse edited tailored resume JSON, using original:', e);
              }
            }
            
            const tailoredWithPersonalInfo: any = {
              ...tailoredData,
              full_name: personalInfo.full_name || tailoredData.full_name || '',
              name_prefix: personalInfo.name_prefix || tailoredData.name_prefix || '',
              email: personalInfo.email || tailoredData.email || '',
              phone: personalInfo.phone || tailoredData.phone || '',
              current_address: personalInfo.current_address || tailoredData.current_address || '',
              location: personalInfo.location || tailoredData.location || '',
              linkedin_url: personalInfo.linkedin_url || tailoredData.linkedin_url || '',
              github_url: personalInfo.github_url || tailoredData.github_url || '',
              portfolio_url: personalInfo.portfolio_url || tailoredData.portfolio_url || '',
              summary: tailoredData.summary || personalInfo.summary || '',
              personal_info: personalInfo,
            };
            blob = await api.generateTailoredResumePDF(tailoredWithPersonalInfo);
          } else {
            throw new Error('No tailored resume data available');
          }
          break;

        case 'cover-letter':
          if ('body_content' in data && data.body_content) {
            const personalInfo = resumeData.personal_info || {};
            const resumeDict: any = {
              ...resumeData,
              full_name: personalInfo.full_name || '',
              name_prefix: personalInfo.name_prefix || '',
              email: personalInfo.email || '',
              phone: personalInfo.phone || '',
              current_address: personalInfo.current_address || '',
              location: personalInfo.location || '',
              linkedin_url: personalInfo.linkedin_url || '',
              github_url: personalInfo.github_url || '',
              portfolio_url: personalInfo.portfolio_url || '',
              personal_info: personalInfo,
            };
            const content = contentToUse || editedContent?.coverLetter || data.body_content;
            blob = await api.generateCoverLetterPDF(resumeDict, { body_content: content }, jobAnalysis?.analysis);
          } else {
            throw new Error('No cover letter data available');
          }
          break;

        case 'suggestions':
          if ('content' in data && data.content) {
            const fullName = resumeData.personal_info?.full_name || '';
            const analysisObj = typeof jobAnalysis?.analysis === 'object' ? jobAnalysis.analysis : {};
            const company = (analysisObj as any)?.company_name || 'company';
            const jobPosition = (analysisObj as any)?.position_title || '';
            const content = contentToUse || editedContent?.suggestions || formatSuggestionsContent(data.content);
            blob = await api.generateSuggestionsPDF(content, fullName, company, jobPosition);
          } else {
            throw new Error('No suggestions data available');
          }
          break;

        default:
          throw new Error('Unknown result type');
      }

      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (error) {
      alert(`Failed to generate PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Regenerate PDF with edited content
  const handleRegeneratePDF = async () => {
    setIsRegenerating(true);
    try {
      // Revoke old PDF URL before generating new one
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
      // Regenerate with the edited content
      await generatePDF(editContent);
    } catch (error) {
      alert(`Failed to regenerate PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsRegenerating(false);
    }
  };

  // Download PDF
  const handleDownload = () => {
    if (!pdfUrl) return;

    const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '');
    let filename = '';

    const analysisObj = typeof jobAnalysis?.analysis === 'object' ? jobAnalysis.analysis as any : {};
    
    switch (type) {
      case 'summary':
        filename = `job_analysis_${timestamp}.pdf`;
        break;
      case 'tailored':
        const company = (data && 'tailored_resume' in data && data.tailored_resume?.company_name) || 'company';
        filename = `${String(company).toLowerCase().replace(/\s+/g, '_')}_resume_${timestamp}.pdf`;
        break;
      case 'cover-letter':
        const coverCompany = (data && 'company_name' in data && (data as any).company_name) || 'company';
        filename = `${String(coverCompany).toLowerCase().replace(/\s+/g, '_')}_cover_letter_${timestamp}.pdf`;
        break;
      case 'suggestions':
        const suggCompany = analysisObj?.company_name || 'company';
        filename = `${String(suggCompany).toLowerCase().replace(/\s+/g, '_')}_suggestions_${timestamp}.pdf`;
        break;
    }

    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Initialize content and generate PDF when modal opens
  useEffect(() => {
    if (open && data) {
      const content = getEditableContent();
      setEditContent(content);
      generatePDF();
    }
  }, [open, data, type]);

  // Cleanup PDF URL on unmount
  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  const getTitle = (): string => {
    switch (type) {
      case 'summary':
        return 'Job Analysis';
      case 'tailored':
        return 'Tailored Resume';
      case 'cover-letter':
        return 'Cover Letter';
      case 'suggestions':
        return 'Skill Gap Analysis';
      default:
        return 'Result';
    }
  };

  if (!data) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl w-full h-[90vh] flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle>{getTitle()}</DialogTitle>
        </DialogHeader>

        <div className="flex-1 flex overflow-hidden">
          {/* PDF Viewer - Left Side */}
          <div className="flex-1 border-r overflow-hidden bg-muted/50">
            {isGenerating ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                  <p className="text-sm text-muted-foreground">Generating PDF...</p>
                </div>
              </div>
            ) : pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-full border-0"
                title="PDF Viewer"
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">No PDF available</p>
              </div>
            )}
          </div>

          {/* Text Editor - Right Side */}
          <div className="flex-1 flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <Label>Content Editor</Label>
              <div className="flex gap-2">
                {!isEditing ? (
                  <Button
                    onClick={() => setIsEditing(true)}
                    variant="outline"
                    size="sm"
                  >
                    <Edit2 className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                ) : (
                  <>
                    <Button
                      onClick={() => {
                        setIsEditing(false);
                        if (onContentEdit) {
                          onContentEdit(type, editContent);
                        }
                      }}
                      variant="outline"
                      size="sm"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={async () => {
                        if (onContentEdit) {
                          onContentEdit(type, editContent);
                        }
                        await handleRegeneratePDF();
                        setIsEditing(false);
                      }}
                      variant="default"
                      size="sm"
                      disabled={isRegenerating}
                    >
                      {isRegenerating ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="mr-2 h-4 w-4" />
                      )}
                      Regenerate PDF
                    </Button>
                  </>
                )}
              </div>
            </div>

            <div className="flex-1 overflow-auto p-4">
              {isEditing ? (
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="w-full h-full min-h-[400px] font-mono text-sm whitespace-pre-wrap"
                  placeholder="Edit content here..."
                />
              ) : (
                <div className="whitespace-pre-wrap font-mono text-sm p-4 bg-muted/50 rounded border min-h-[400px]">
                  {editContent || 'No content available'}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer with Download Button */}
        <div className="px-6 py-4 border-t flex justify-end">
          <Button onClick={handleDownload} disabled={!pdfUrl || isGenerating}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
