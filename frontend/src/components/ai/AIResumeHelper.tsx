import { useState, useEffect, useRef } from 'react';
import { useResumeStore } from '@/stores/resumeStore';
import { useAIStore } from '@/stores/aiStore';
import { useApplicationStore } from '@/stores/applicationStore';
import { api } from '@/lib/api';
import { formatAnalysisAsMarkdown, formatSuggestionsContent } from '@/lib/utils';
import { buttonStyles, buttonVariants } from '@/lib/styles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, RefreshCw, Search, Target, Mail, Lightbulb, Plus, RotateCcw, Sparkles, Wand2, FileText, FolderPlus, CreditCard, Settings, CheckCircle2, UserCircle, Link, HelpCircle, Pencil, X, Terminal, Cpu, MessageSquare, Save } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useToast } from '@/components/ui/use-toast';
import { ResultPalette } from './ResultPalette';
import { PDFViewerModal } from './PDFViewerModal';
import { ResumeArtifactCard } from './ResumeArtifactCard';

export function AIResumeHelper() {
  const { resumeData } = useResumeStore();
  const { createApplication } = useApplicationStore();
  const { toast } = useToast();
  const {
    provider,
    model,
    apiKey,
    availableProviders,
    availableModels,
    totalCost,
    costDisplay,
    jobAnalysis,
    tailoredResume,
    coverLetter,
    improvementSuggestions,
    matchScore,
    matchSummary,
    jobUrl: storeJobUrl,
    pdfPaths,
    editedContent,
    aiStatus,
    processingStatus,
    analyzing,
    tailoring,
    generatingCoverLetter,
    gettingSuggestions,
    testingApiKey,
    error,
    setProvider,
    setModel,
    setApiKey,
    testApiKey,
    loadProviders,
    loadModels,
    loadCost,
    updateLiteLLM,
    analyzeJob,
    tailorResume: tailorResumeAction,
    generateCoverLetter: generateCoverLetterAction,
    getImprovementSuggestions,
    setMatchScore,
    setMatchSummary,
    setJobUrl,
    setJobDescription,
    setUserPrompt,
    setPdfPath,
    setEditedContent,
    setProcessingStatus,
    updateAIStatus,
    clearError,
    clearFormInputs,
    jobDescription,
    userPrompt,
  } = useAIStore();
  const [resumeJson, setResumeJson] = useState('');
  const [isResumeSynced, setIsResumeSynced] = useState(false);
  const [pdfModalOpen, setPdfModalOpen] = useState(false);
  const [selectedResultType, setSelectedResultType] = useState<'summary' | 'tailored' | 'cover-letter' | 'suggestions'>('summary');
  const [addToTrackerSuccess, setAddToTrackerSuccess] = useState(false);
  const jobDescriptionTextareaRef = useRef<HTMLTextAreaElement>(null);
  const [isJobDescriptionExpanded, setIsJobDescriptionExpanded] = useState(false);
  const jobDescriptionDebounceRef = useRef<NodeJS.Timeout | null>(null);
  const [isJobUrlEditMode, setIsJobUrlEditMode] = useState(false);
  // User Prompt always shows as a pill (even when empty)
  // When editing, it opens an editor with a Save button
  const [isUserPromptExpanded, setIsUserPromptExpanded] = useState(false);
  const [userPromptEditValue, setUserPromptEditValue] = useState('');
  const userPromptTextareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadProviders();
    loadCost();
    // Auto-load resume JSON on mount
    setResumeJson(JSON.stringify(resumeData, null, 2));
    setIsResumeSynced(true);
    // Load persisted user prompt from localStorage on mount (if not already in store)
    const persistedPrompt = localStorage.getItem('resumeHelper_userPrompt');
    if (persistedPrompt && persistedPrompt.trim() && !userPrompt.trim()) {
      // Only set if store's userPrompt is empty and localStorage has content
      setUserPrompt(persistedPrompt);
    }
    // User Prompt always shows as pill (collapsed) by default
    setIsUserPromptExpanded(false);
  }, [loadProviders, loadCost, setUserPrompt]);

  // Note: User prompt persistence is now handled by the Save button, not automatically


  useEffect(() => {
    updateAIStatus();
  }, [provider, model, apiKey, costDisplay, updateAIStatus]);

  // Show error toast when error state changes
  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  // Track previous states to detect successful operations
  const prevAnalyzing = useRef(analyzing);
  const prevTailoring = useRef(tailoring);
  const prevGeneratingCoverLetter = useRef(generatingCoverLetter);
  const prevGettingSuggestions = useRef(gettingSuggestions);

  // Show success toast when analysis completes
  useEffect(() => {
    if (prevAnalyzing.current && !analyzing && jobAnalysis && !error) {
      toast({
        title: "Analysis Complete",
        description: "Job analysis has been generated successfully.",
        variant: "success",
      });
    }
    prevAnalyzing.current = analyzing;
  }, [analyzing, jobAnalysis, error, toast]);

  // Show success toast when tailoring completes
  useEffect(() => {
    if (prevTailoring.current && !tailoring && tailoredResume && !error) {
      toast({
        title: "Resume Tailored",
        description: "Your resume has been tailored successfully.",
        variant: "success",
      });
    }
    prevTailoring.current = tailoring;
  }, [tailoring, tailoredResume, error, toast]);

  // Show success toast when cover letter generation completes
  useEffect(() => {
    if (prevGeneratingCoverLetter.current && !generatingCoverLetter && coverLetter && !error) {
      toast({
        title: "Cover Letter Generated",
        description: "Your cover letter has been generated successfully.",
        variant: "success",
      });
    }
    prevGeneratingCoverLetter.current = generatingCoverLetter;
  }, [generatingCoverLetter, coverLetter, error, toast]);

  // Show success toast when suggestions generation completes
  useEffect(() => {
    if (prevGettingSuggestions.current && !gettingSuggestions && improvementSuggestions && !error) {
      toast({
        title: "Skill Gap Analysis Complete",
        description: "Improvement suggestions have been generated successfully.",
        variant: "success",
      });
    }
    prevGettingSuggestions.current = gettingSuggestions;
  }, [gettingSuggestions, improvementSuggestions, error, toast]);

  useEffect(() => {
    if (provider) {
      loadModels(provider);
    }
  }, [provider, loadModels]);

  // Use ref to prevent expensive JSON.stringify on every render
  const prevResumeDataRef = useRef<string>('');
  useEffect(() => {
    // Auto-update resume JSON when resume data changes (if synced)
    if (isResumeSynced) {
      const resumeDataStr = JSON.stringify(resumeData, null, 2);
      // Only update if data actually changed
      if (prevResumeDataRef.current !== resumeDataStr) {
        prevResumeDataRef.current = resumeDataStr;
        setResumeJson(resumeDataStr);
      }
    }
  }, [resumeData, isResumeSynced]);

  // Auto-resize textarea when jobDescription changes
  useEffect(() => {
    if (jobDescriptionTextareaRef.current) {
      const textarea = jobDescriptionTextareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.max(textarea.scrollHeight, 200)}px`;
    }
  }, [jobDescription]);

  // Auto-collapse job description after 1 second of inactivity
  useEffect(() => {
    if (jobDescription.trim()) {
      // Clear existing timeout
      if (jobDescriptionDebounceRef.current) {
        clearTimeout(jobDescriptionDebounceRef.current);
      }
      // Set new timeout to collapse after 1 second
      jobDescriptionDebounceRef.current = setTimeout(() => {
        setIsJobDescriptionExpanded(false);
      }, 1000);
    } else {
      // If empty, keep expanded
      setIsJobDescriptionExpanded(true);
    }

    return () => {
      if (jobDescriptionDebounceRef.current) {
        clearTimeout(jobDescriptionDebounceRef.current);
      }
    };
  }, [jobDescription]);

  // Calculate word count
  const jobDescriptionWordCount = jobDescription.trim() ? jobDescription.trim().split(/\s+/).filter(Boolean).length : 0;

  // Initialize userPromptEditValue when entering edit mode
  useEffect(() => {
    if (isUserPromptExpanded) {
      setUserPromptEditValue(userPrompt);
      // Focus textarea after expansion
      setTimeout(() => {
        userPromptTextareaRef.current?.focus();
      }, 100);
    }
  }, [isUserPromptExpanded, userPrompt]);


  const handleUpdateResume = () => {
    // Sync current resume data from all tabs
    const updatedJson = JSON.stringify(resumeData, null, 2);
    setResumeJson(updatedJson);
    setIsResumeSynced(true);
  };

  // Reset AI Operations only (clears AI results, keeps input)
  const handleResetAIOperations = () => {
    // Clear all AI results
    clearError();
    // Clear AI store results
    useAIStore.getState().clearResults();
    setProcessingStatus('');
    updateAIStatus();
  };

  // Reset Input only (clears Job URL and Job Description, keeps User Prompt)
  const handleResetInput = () => {
    setJobUrl('');
    setJobDescription('');
    // Note: userPrompt is NOT cleared - it persists across sessions
    clearFormInputs();
  };

  const handleProviderChange = async (newProvider: string) => {
    await setProvider(newProvider);
  };

  const handleTestApiKey = async () => {
    // For Ollama, skip API key requirement
    if (provider === 'Ollama (Local)') {
      setApiKey(''); // Clear any entered key
      const success = await testApiKey();
      if (success) {
        toast({
          title: "Connection Successful",
          description: "Ollama connection successful! Make sure Ollama is running on localhost:11434",
          variant: "success",
        });
      } else {
        toast({
          title: "Connection Failed",
          description: "Ollama connection failed. Please ensure Ollama is installed and running on localhost:11434",
          variant: "destructive",
        });
      }
      return;
    }
    
    if (!apiKey.trim()) {
      toast({
        title: "Error",
        description: "Please enter a valid API key",
        variant: "destructive",
      });
      return;
    }
    
    const success = await testApiKey();
    if (success) {
      toast({
        title: "Configuration Saved",
        description: "Configuration saved successfully.",
        variant: "success",
      });
    } else {
      toast({
        title: "Error",
        description: "API key test failed. Please check your key.",
        variant: "destructive",
      });
    }
  };

  const handleAnalyzeJob = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Error",
        description: "Please enter a job description",
        variant: "destructive",
      });
      return;
    }
    
    // Ensure resume is synced before analysis (matches Gradio behavior)
    if (!isResumeSynced) {
      handleUpdateResume();
    }
    
    // Use the latest resume data
    const currentResumeData = resumeData;
    if (!currentResumeData || !currentResumeData.personal_info || !currentResumeData.personal_info.full_name) {
      toast({
        title: "Error",
        description: 'Please update your resume data first by clicking "Update Resume" or fill in at least the Personal Information section (especially Full Name).',
        variant: "destructive",
      });
      return;
    }
    
    await analyzeJob(jobDescription, currentResumeData);
  };

  const handleTailorResume = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Error",
        description: "Please enter a job description",
        variant: "destructive",
      });
      return;
    }
    await tailorResumeAction(resumeData, jobDescription, userPrompt);
  };

  const handleGenerateCoverLetter = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Error",
        description: "Please enter a job description",
        variant: "destructive",
      });
      return;
    }
    await generateCoverLetterAction(resumeData, jobDescription, userPrompt);
  };

  const handleGetSuggestions = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Error",
        description: "Please enter a job description",
        variant: "destructive",
      });
      return;
    }
    await getImprovementSuggestions(resumeData, jobDescription);
  };

  const handleOpenPDFModal = (type: 'summary' | 'tailored' | 'cover-letter' | 'suggestions') => {
    setSelectedResultType(type);
    setPdfModalOpen(true);
  };

  const handleContentEdit = (type: string, content: string) => {
    switch (type) {
      case 'summary':
        setEditedContent('jobAnalysis', content);
        break;
      case 'tailored':
        setEditedContent('tailoredResume', content);
        break;
      case 'cover-letter':
        setEditedContent('coverLetter', content);
        break;
      case 'suggestions':
        setEditedContent('suggestions', content);
        break;
    }
  };

  const handleAddToApplicationTracker = async () => {
    // Validate job URL is present (matches Gradio behavior - line 1434)
    if (!storeJobUrl || !storeJobUrl.trim()) {
      toast({
        title: "Error",
        description: "Job URL is required to prevent duplicates. Please enter the job URL above.",
        variant: "destructive",
      });
      return;
    }

    // Get job details from analysis (matches Gradio's job_details_state - line 1437-1439)
    // job_details_state gets updated from analysis results (line 470: job_details.update(extracted_details))
    const jobDetails = jobAnalysis?.analysis || {};
    const company = jobDetails.company_name || 'Unknown Company';
    const position = jobDetails.position_title || 'Unknown Position';
    const location = jobDetails.location || '';
    
    // Parse estimated salary range to extract min/max
    let salaryMin: number | undefined;
    let salaryMax: number | undefined;
    const salaryRange = jobDetails.estimated_salary_range;
    
    if (salaryRange) {
      // Handle both object format (with range/reasoning OR amount/reasoning) and string format
      let salaryStr: string;
      if (typeof salaryRange === 'object' && salaryRange !== null) {
        // Try multiple property names that AI might use
        const salaryObj = salaryRange as any;
        salaryStr = salaryObj.range || salaryObj.amount || salaryObj.salary || String(salaryRange);
      } else {
        // Use as string directly
        salaryStr = typeof salaryRange === 'string' ? salaryRange : String(salaryRange);
      }
      
      const rangeMatch = salaryStr.match(/\$?([\d,]+)k?\s*[-–]\s*\$?([\d,]+)k?/i);
      
      if (rangeMatch) {
        const minStr = rangeMatch[1].replace(/,/g, '');
        const maxStr = rangeMatch[2].replace(/,/g, '');
        
        // Check if values are in thousands (k format)
        const isThousands = salaryStr.toLowerCase().includes('k');
        
        salaryMin = parseInt(minStr) * (isThousands ? 1000 : 1);
        salaryMax = parseInt(maxStr) * (isThousands ? 1000 : 1);
      } else {
        // Try single value like "$80,000" or "$80k"
        const singleMatch = salaryStr.match(/\$?([\d,]+)k?/i);
        if (singleMatch) {
          const value = parseInt(singleMatch[1].replace(/,/g, ''));
          const isThousands = salaryStr.toLowerCase().includes('k');
          salaryMin = value * (isThousands ? 1000 : 1);
        }
      }
    }
    
    // Use the formatted markdown text from the analysis tab as description (matches Gradio's job_analysis textbox - line 1452)
    // In Gradio, job_analysis is the Textbox containing the formatted markdown, not the original job description
    // This is the editable content from the analysis tab
    const jobDescText = editedContent.jobAnalysis || (jobAnalysis?.analysis ? formatAnalysisAsMarkdown(jobAnalysis.analysis) : jobDescription.trim());
    
    // Use match_score from the editable input (matches Gradio's match_score_display - line 1452)
    const scoreToUse = matchScore || jobDetails.match_score || null;

    // Matches Gradio's add_to_application_tracker function (line 585-599)
    const appData = {
      job_url: storeJobUrl.trim(),
      company: company,
      position: position,
      location: location,
      description: jobDescText.trim(),
      match_score: scoreToUse ? parseInt(String(scoreToUse)) : null,
      salary_min: salaryMin,
      salary_max: salaryMax,
      application_source: 'AI Analysis',
      status: 'Applied',
      priority: 'Medium',
      analysis_data: {
        analyzed_date: new Date().toISOString(),
        ai_extracted: true,
        estimated_salary_range: salaryRange,
      },
    };

    try {
      const newApp = await createApplication(appData);
      
      if (newApp) {
        const appId = newApp.id || 'unknown';
        setAddToTrackerSuccess(true);
        toast({
          title: "Success",
          description: `Job added to Applications Tracker. Application ID: ${appId}`,
          variant: "success",
        });
        // Reset success state after 2 seconds
        setTimeout(() => {
          setAddToTrackerSuccess(false);
        }, 2000);
      } else {
        toast({
          title: "Error",
          description: "Failed to add to Application Tracker. Please check the console for details.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error adding to application tracker:', error);
      toast({
        title: "Error",
        description: `Error adding to Application Tracker: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  };

  // Check if analysis has been completed successfully
  const hasAnalysisResults = !!jobAnalysis?.analysis;

  // Extract model name (remove provider prefix if present)
  const modelName = model ? (model.includes('/') ? model.split('/').pop() || model : model) : 'Default';
  
  // Determine status (Ready/Not Ready)
  const isReady = provider === 'Ollama (Local)' || (provider !== 'Ollama (Local)' && apiKey);

  // Detect LinkedIn URL for badge display
  const isLinkedInUrl = storeJobUrl?.toLowerCase().includes('linkedin.com');
  const isValidUrl = storeJobUrl?.trim() && (storeJobUrl.startsWith('http://') || storeJobUrl.startsWith('https://'));

  return (
    <div className="space-y-6">
      {/* AI Meta Bar - Modern System Ribbon */}
      <div className="flex items-center justify-between gap-6 bg-slate-950/50 backdrop-blur-sm border-b border-border/50 px-6 py-3">
        {/* Group A - Identity */}
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-xs">
            Model: {modelName}
          </Badge>
          <div className="flex items-center gap-2">
            <div className="relative flex h-2 w-2">
              <span className={`absolute h-2 w-2 rounded-full ${isReady ? 'bg-green-500 animate-ping' : 'bg-gray-500'}`} />
              <span className={`relative h-2 w-2 rounded-full ${isReady ? 'bg-green-500' : 'bg-gray-500'}`} />
            </div>
            <span className="text-xs text-muted-foreground">
              {isReady ? 'Ready' : 'Setup needed'}
            </span>
          </div>
        </div>

        {/* Group B - Usage */}
        <div className="flex items-center gap-2">
          <CreditCard className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">Total Cost:</span>
          <span className="text-xs font-mono text-foreground">
            {costDisplay.includes('$') ? costDisplay.substring(costDisplay.indexOf('$')) : costDisplay}
          </span>
        </div>

        {/* Group C - Actions */}
        <div className="flex items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => updateLiteLLM()}
                  className="h-8 w-8"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Update LiteLLM configuration</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <Dialog>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DialogTrigger asChild>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                </TooltipTrigger>
                <TooltipContent>
                  <p>AI Configuration Settings</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <DialogContent className="sm:max-w-4xl">
              <DialogHeader>
                <DialogTitle>AI Configuration</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-2">
                {/* AI Provider, Model, and Refresh in same row */}
                <div className="flex items-end gap-4 flex-nowrap">
                  <div className="space-y-2 min-w-[150px]">
                    <Label htmlFor="provider">AI Provider</Label>
                    <Select value={provider} onValueChange={handleProviderChange}>
                      <SelectTrigger id="provider">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {availableProviders.map((p) => (
                          <SelectItem key={p} value={p}>
                            {p}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2 min-w-[150px]">
                    <Label htmlFor="model">Model</Label>
                    <Select value={model || ''} onValueChange={setModel}>
                      <SelectTrigger id="model">
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableModels.map((m) => (
                          <SelectItem key={m} value={m}>
                            {m}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="opacity-0">Refresh</Label>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={async () => {
                        // Refresh model list first
                        await loadModels(provider);
                        // Then switch/apply the selected model (like Gradio's "Set" button)
                        // This switches the model without showing test alerts
                        const { provider: currentProvider, apiKey: currentApiKey, model: currentModel } = useAIStore.getState();
                        const keyToUse = currentProvider === 'Ollama (Local)' ? '' : currentApiKey;
                        try {
                          await api.testApiKey(currentProvider, keyToUse, currentModel || undefined);
                          // Silently switch - no alert
                          await loadCost(); // Refresh cost after switching
                        } catch (error) {
                          console.error('Failed to switch model:', error);
                        }
                      }}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh
                    </Button>
                  </div>
                  {provider !== 'Ollama (Local)' && (
                    <div className="space-y-2 flex-1 min-w-0">
                      <Label htmlFor="api-key">API Key</Label>
                      <div className="flex gap-3">
                        <Input
                          id="api-key"
                          type="password"
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          placeholder="Enter API key"
                          className="flex-1 min-w-0"
                        />
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={handleTestApiKey}
                          disabled={testingApiKey}
                          className="flex-shrink-0"
                        >
                          {testingApiKey ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Testing...
                            </>
                          ) : (
                            'Test'
                          )}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>


      {/* Split-Pane Workspace: 40/60 Layout */}
      <div className="grid grid-cols-[2fr_3fr] gap-8">
        {/* Left Column (40%): Input */}
        <div className="flex flex-col space-y-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-base">Input</CardTitle>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={handleResetInput}
                    className="h-8 w-8"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Clear input - Reset Job Link and Job Description</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Job Link Artifact */}
            {storeJobUrl.trim() && !isJobUrlEditMode ? (
              <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge
                        variant="secondary"
                        className="gap-2 px-3 py-1.5 h-auto cursor-pointer hover:bg-muted"
                        onClick={() => {
                          if (isValidUrl) {
                            window.open(storeJobUrl, '_blank');
                          }
                        }}
                      >
                        <Link className="h-4 w-4" />
                        <span className="text-sm font-medium">Job Link</span>
                        {isValidUrl && (
                          <div className="relative flex items-center justify-center ml-1">
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                            <div className="absolute h-2 w-2 rounded-full bg-emerald-500/30 animate-ping" />
                          </div>
                        )}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{isValidUrl ? 'Click to open job posting in new tab' : 'Job URL entered'}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <div className="flex items-center gap-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            setIsJobUrlEditMode(true);
                          }}
                          className="h-8 w-8"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Edit job URL</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      setJobUrl('');
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Link className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="job-url"
                    value={storeJobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    onBlur={() => {
                      if (storeJobUrl.trim()) {
                        setIsJobUrlEditMode(false);
                      }
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && storeJobUrl.trim()) {
                        setIsJobUrlEditMode(false);
                      }
                    }}
                    placeholder="https://company.com/careers/job-posting"
                    className="pl-9"
                    autoFocus={isJobUrlEditMode}
                  />
                </div>
                {storeJobUrl.trim() && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setIsJobUrlEditMode(false);
                    }}
                    className="h-8 w-8"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            )}

            {/* Job Description - Collapsible Preview */}
            {jobDescription.trim() && !isJobDescriptionExpanded ? (
              <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge variant="secondary" className="gap-2 px-3 py-1.5 h-auto">
                        <FileText className="h-4 w-4" />
                        <span className="text-sm font-medium">
                          Job Description
                        </span>
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Job description ingested and ready for AI processing</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <div className="flex items-center gap-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => {
                            setIsJobDescriptionExpanded(true);
                            // Focus textarea after expansion
                            setTimeout(() => {
                              jobDescriptionTextareaRef.current?.focus();
                            }, 100);
                          }}
                          className="h-8 w-8"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Click to edit raw description</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => {
                      setJobDescription('');
                      setIsJobDescriptionExpanded(true);
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <Textarea
                ref={jobDescriptionTextareaRef}
                id="job-description"
                value={jobDescription}
                onChange={(e) => {
                  setJobDescription(e.target.value);
                  setIsJobDescriptionExpanded(true);
                  // Clear debounce timeout when user is typing
                  if (jobDescriptionDebounceRef.current) {
                    clearTimeout(jobDescriptionDebounceRef.current);
                  }
                  // Auto-resize textarea
                  const textarea = e.target;
                  textarea.style.height = 'auto';
                  textarea.style.height = `${Math.max(textarea.scrollHeight, 200)}px`;
                }}
                onBlur={() => {
                  // Debounce will handle collapse after 1 second
                  // This ensures smooth UX without immediate collapse
                }}
                placeholder="Paste the job description here to begin tailoring..."
                className="min-h-[200px] leading-relaxed p-4 resize-none"
              />
            )}

            {/* Optional User Prompt - Always shows as pill, uses Save button when editing */}
            {!isUserPromptExpanded ? (
              <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge variant="secondary" className="gap-2 px-3 py-1.5 h-auto">
                        <MessageSquare className="h-4 w-4" />
                        <span className="text-sm font-medium">
                          User Prompt
                        </span>
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Custom instructions for AI processing (persists across sessions)</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <div className="flex items-center gap-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => {
                            setIsUserPromptExpanded(true);
                          }}
                          className="h-8 w-8"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Click to edit user prompt</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  {userPrompt.trim() && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
                      onClick={() => {
                        setUserPrompt('');
                        localStorage.removeItem('resumeHelper_userPrompt');
                        toast({
                          title: 'User prompt cleared',
                          description: 'Your custom instructions have been removed.',
                        });
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Textarea
                  ref={userPromptTextareaRef}
                  id="user-prompt"
                  value={userPromptEditValue}
                  onChange={(e) => {
                    setUserPromptEditValue(e.target.value);
                  }}
                  placeholder="e.g. 'Use energetic tone', 'Highlight leadership skills'"
                  className="min-h-[80px] leading-relaxed p-4 resize-none"
                  rows={3}
                />
                <div className="flex items-center justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsUserPromptExpanded(false);
                      setUserPromptEditValue(userPrompt);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="button"
                    variant="default"
                    size="sm"
                    onClick={() => {
                      setUserPrompt(userPromptEditValue);
                      localStorage.setItem('resumeHelper_userPrompt', userPromptEditValue);
                      setIsUserPromptExpanded(false);
                      toast({
                        title: 'User prompt saved',
                        description: 'Your custom instructions have been saved and will persist across sessions.',
                      });
                    }}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Active Resume Artifact */}
        <ResumeArtifactCard
          resumeData={resumeData}
          isSynced={isResumeSynced}
          resumeJson={resumeJson}
          onUpdate={handleUpdateResume}
        />

        {/* AI Operations */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-base">AI Operations</CardTitle>
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={handleResetAIOperations}
                    className="h-8 w-8"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Clear AI results - Reset analysis and generated artifacts</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Primary Action: Analyze */}
            <Button
              onClick={handleAnalyzeJob}
              disabled={analyzing || !jobDescription.trim()}
              className={`w-full ${buttonStyles.primary} ${
                analyzing || !jobDescription.trim() ? buttonStyles.disabled : ''
              }`}
            >
              {analyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  <span className="text-sm">Analyzing...</span>
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  <span className="text-sm">Analyze</span>
                </>
              )}
            </Button>
            
            {/* Secondary Actions: Tailor, Cover Letter, Skill Gap */}
            <div className="flex flex-row gap-2">
              <Button
                onClick={handleTailorResume}
                disabled={!jobAnalysis || tailoring || !jobDescription.trim()}
                variant={buttonVariants.secondary}
                className={`flex-1 ${buttonStyles.secondary} ${
                  !jobAnalysis ? buttonStyles.disabled : ''
                }`}
              >
                {tailoring ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    <span className="text-sm">Tailor</span>
                  </>
                )}
              </Button>
              <Button
                onClick={handleGenerateCoverLetter}
                disabled={!jobAnalysis || generatingCoverLetter || !jobDescription.trim()}
                variant={buttonVariants.secondary}
                className={`flex-1 ${buttonStyles.secondary} ${
                  !jobAnalysis ? buttonStyles.disabled : ''
                }`}
              >
                {generatingCoverLetter ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    <span className="text-sm">Cover Letter</span>
                  </>
                )}
              </Button>
              <Button
                onClick={handleGetSuggestions}
                disabled={!jobAnalysis || gettingSuggestions || !jobDescription.trim()}
                variant={buttonVariants.secondary}
                className={`flex-1 ${buttonStyles.secondary} ${
                  !jobAnalysis ? buttonStyles.disabled : ''
                }`}
              >
                {gettingSuggestions ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Lightbulb className="mr-2 h-4 w-4" />
                    <span className="text-sm">Skill Gap</span>
                  </>
                )}
              </Button>
            </div>

            {error && (
              <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                {error}
              </div>
            )}
          </CardContent>
        </Card>
        </div>

        {/* Right Column (60%): AI Results */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">AI Results</CardTitle>
            {hasAnalysisResults && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      onClick={handleAddToApplicationTracker}
                      variant="outline"
                      size="sm"
                      className={`transition-all ${
                        addToTrackerSuccess
                          ? 'bg-green-500/10 border-green-500/50 text-green-600 dark:text-green-400'
                          : 'hover:bg-primary/10 hover:text-accent-foreground'
                      }`}
                    >
                      {addToTrackerSuccess ? (
                        <>
                          <CheckCircle2 className="mr-2 h-4 w-4" />
                          Added!
                        </>
                      ) : (
                        <>
                          <FolderPlus className="mr-2 h-4 w-4" />
                          + Add to Tracker
                        </>
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Save this job and analysis to your Application Tracker</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </CardHeader>
          <CardContent>
            {!hasAnalysisResults ? (
              <div className="flex items-center justify-center h-[500px] border-2 border-dashed border-muted rounded-lg">
                <div className="text-center space-y-2">
                  <Search className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
                  <p className="text-muted-foreground">Click "Analyze" to see results</p>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Match Score - Large Display */}
                <div className="flex flex-col items-center justify-center py-6 border-b">
                  <Label className="text-sm font-normal text-muted-foreground mb-2">Match Score</Label>
                  <div className="relative">
                    {/* Circular Gauge Effect */}
                    <div className="w-32 h-32 rounded-full border-8 border-muted flex items-center justify-center"
                      style={{
                        borderTopColor: matchScore >= 80 ? '#22c55e' : matchScore >= 60 ? '#eab308' : '#ef4444',
                        borderRightColor: matchScore >= 80 ? '#22c55e' : matchScore >= 60 ? '#eab308' : '#ef4444',
                        borderBottomColor: matchScore >= 80 ? '#22c55e' : matchScore >= 60 ? '#eab308' : '#ef4444',
                        borderLeftColor: matchScore >= 80 ? '#22c55e' : matchScore >= 60 ? '#eab308' : '#ef4444',
                      }}
                    >
                      <div className="text-center">
                        <p className="text-4xl font-bold" style={{ color: matchScore >= 80 ? '#22c55e' : matchScore >= 60 ? '#eab308' : '#ef4444' }}>
                          {matchScore || 0}
                        </p>
                        <p className="text-xs text-muted-foreground">%</p>
                      </div>
                    </div>
                  </div>
                  {matchSummary && (
                    <p className="text-sm text-muted-foreground mt-4 text-center max-w-md">{matchSummary}</p>
                  )}
                </div>

                {/* Detailed Match Breakdown */}
                {(jobAnalysis?.analysis?.skills_match !== undefined || 
                  jobAnalysis?.analysis?.experience_match !== undefined || 
                  jobAnalysis?.analysis?.education_match !== undefined) && (
                  <div className="space-y-4 py-4 border-b">
                    <Label className="text-base font-semibold">Match Breakdown</Label>
                    <div className="space-y-3">
                      {jobAnalysis?.analysis?.skills_match !== undefined && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Skills Match</span>
                            <span className="font-medium">{jobAnalysis.analysis.skills_match}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="h-2 rounded-full transition-all"
                              style={{
                                width: `${jobAnalysis.analysis.skills_match}%`,
                                backgroundColor: jobAnalysis.analysis.skills_match >= 80 ? '#22c55e' : jobAnalysis.analysis.skills_match >= 60 ? '#eab308' : '#ef4444',
                              }}
                            />
                          </div>
                        </div>
                      )}
                      {jobAnalysis?.analysis?.experience_match !== undefined && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Experience Match</span>
                            <span className="font-medium">{jobAnalysis.analysis.experience_match}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="h-2 rounded-full transition-all"
                              style={{
                                width: `${jobAnalysis.analysis.experience_match}%`,
                                backgroundColor: jobAnalysis.analysis.experience_match >= 80 ? '#22c55e' : jobAnalysis.analysis.experience_match >= 60 ? '#eab308' : '#ef4444',
                              }}
                            />
                          </div>
                        </div>
                      )}
                      {jobAnalysis?.analysis?.education_match !== undefined && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Education Match</span>
                            <span className="font-medium">{jobAnalysis.analysis.education_match}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="h-2 rounded-full transition-all"
                              style={{
                                width: `${jobAnalysis.analysis.education_match}%`,
                                backgroundColor: jobAnalysis.analysis.education_match >= 80 ? '#22c55e' : jobAnalysis.analysis.education_match >= 60 ? '#eab308' : '#ef4444',
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Estimated Salary Range */}
                {jobAnalysis?.analysis?.estimated_salary_range && (
                  <div className="space-y-3 py-4 border-b">
                    <Label className="text-base font-semibold">Estimated Salary Range</Label>
                    <div className="p-4 bg-muted/50 rounded-lg border">
                      {typeof jobAnalysis.analysis.estimated_salary_range === 'string' ? (
                        <p className="text-lg font-medium text-foreground">
                          {jobAnalysis.analysis.estimated_salary_range}
                        </p>
                      ) : typeof jobAnalysis.analysis.estimated_salary_range === 'object' ? (
                        <div className="space-y-2">
                          {Object.entries(jobAnalysis.analysis.estimated_salary_range).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-sm font-semibold text-muted-foreground capitalize">
                                {key.replace(/_/g, ' ')}:{' '}
                              </span>
                              <span className="text-lg font-medium text-foreground">
                                {String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-lg font-medium text-foreground">
                          {String(jobAnalysis.analysis.estimated_salary_range)}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Result Palette */}
                <ResultPalette
                  onResultClick={handleOpenPDFModal}
                  jobAnalysis={jobAnalysis}
                  tailoredResume={tailoredResume}
                  coverLetter={coverLetter}
                  improvementSuggestions={improvementSuggestions}
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      {/* PDF Viewer Modal */}
      <PDFViewerModal
        open={pdfModalOpen}
        onClose={() => setPdfModalOpen(false)}
        type={selectedResultType}
        data={
          selectedResultType === 'summary' ? jobAnalysis :
          selectedResultType === 'tailored' ? tailoredResume :
          selectedResultType === 'cover-letter' ? coverLetter :
          improvementSuggestions
        }
        resumeData={resumeData}
        jobAnalysis={jobAnalysis}
        editedContent={editedContent}
        onContentEdit={handleContentEdit}
      />
    </div>
  );
}

